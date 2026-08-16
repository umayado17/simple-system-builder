#!/usr/bin/env python3
"""Create a minimal GitHub-ready project control plane for the skill."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "assets" / "project-template"
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".gitignore"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def render_text(text: str, replacements: Dict[str, str]) -> str:
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def is_text_file(path: Path) -> bool:
    return path.name == ".gitignore" or path.suffix.lower() in TEXT_SUFFIXES


def copy_templates(root: Path, replacements: Dict[str, str], force: bool) -> Dict[str, List[str]]:
    created: List[str] = []
    skipped: List[str] = []
    overwritten: List[str] = []

    if not TEMPLATE_ROOT.exists():
        raise FileNotFoundError(f"Template directory not found: {TEMPLATE_ROOT}")

    for source in sorted(TEMPLATE_ROOT.rglob("*")):
        relative = source.relative_to(TEMPLATE_ROOT)
        target = root / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        existed = target.exists()
        if existed and not force:
            skipped.append(str(relative))
            continue

        if is_text_file(source):
            text = source.read_text(encoding="utf-8")
            target.write_text(render_text(text, replacements), encoding="utf-8")
        else:
            shutil.copy2(source, target)

        if existed:
            overwritten.append(str(relative))
        else:
            created.append(str(relative))

    return {"created": created, "skipped": skipped, "overwritten": overwritten}


def write_project_state(root: Path, name: str, purpose: str, force: bool) -> str:
    path = root / ".chatdev" / "project-state.json"
    if path.exists() and not force:
        return "skipped"

    now = utc_now()
    state = {
        "project": name,
        "purpose": purpose,
        "phase": "foundation",
        "status": "active",
        "current_task": "confirm data-ux and infrastructure-permission baselines",
        "next_action": "select the smallest vertical slice",
        "baselines": {
            "requirements": "draft",
            "data_ux": "draft",
            "infrastructure_permissions": "draft",
            "architecture": "draft"
        },
        "blockers": [],
        "created_at": now,
        "updated_at": now,
        "history": [
            {
                "at": now,
                "event": "project scaffold created"
            }
        ]
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return "overwritten" if force else "created"


def maybe_git_init(root: Path) -> str:
    if (root / ".git").exists():
        return "already-initialized"
    try:
        subprocess.run(
            ["git", "init", str(root)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return "initialized"
    except FileNotFoundError:
        return "git-not-found"
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or "git init failed"
        return f"failed: {message}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create minimal project docs and Chat development state without overwriting existing work by default."
    )
    parser.add_argument("--root", required=True, help="Project root directory")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--purpose", default="Purpose to be confirmed", help="One-sentence project purpose")
    parser.add_argument("--force", action="store_true", help="Overwrite template-managed files")
    parser.add_argument("--git-init", action="store_true", help="Initialize a local Git repository if needed")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    replacements = {
        "PROJECT_NAME": args.name.strip(),
        "PURPOSE": args.purpose.strip(),
        "CREATED_AT": utc_now(),
    }

    try:
        result = copy_templates(root, replacements, args.force)
        state_result = write_project_state(root, args.name.strip(), args.purpose.strip(), args.force)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output = {
        "root": str(root),
        "project": args.name.strip(),
        "templates": result,
        "project_state": state_result,
    }
    if args.git_init:
        output["git"] = maybe_git_init(root)

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
