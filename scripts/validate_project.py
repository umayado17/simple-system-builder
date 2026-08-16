#!/usr/bin/env python3
"""Validate the minimal project control files created by this skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List


REQUIRED_FILES = [
    "README.md",
    "docs/requirements.md",
    "docs/architecture.md",
    "docs/data-ux.md",
    "docs/complexity-boundaries.md",
    "docs/enterprise-path.md",
    "docs/operations.md",
    ".chatdev/project-state.json",
    ".chatdev/autonomy-policy.json",
    ".chatdev/open-questions.md",
]

REQUIRED_ARCHITECTURE_HEADINGS = [
    "## 選択した構成",
    "## なぜ最小十分か",
    "## 複雑さの境界",
    "## 現時点で採用しないもの",
]

REQUIRED_STATE_KEYS = [
    "project",
    "purpose",
    "phase",
    "status",
    "current_task",
    "next_action",
    "baselines",
    "blockers",
    "updated_at",
]

PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Simple System Builder project")
    parser.add_argument("--root", required=True, help="Project root directory")
    return parser.parse_args()


def check_json(path: Path, required_keys: List[str], errors: List[str]) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid JSON in {path}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"JSON root must be an object: {path}")
        return {}
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing key '{key}' in {path}")
    return data


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    errors: List[str] = []
    warnings: List[str] = []

    if not root.exists() or not root.is_dir():
        print(f"error: project root not found: {root}", file=sys.stderr)
        return 1

    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            errors.append(f"Missing required file: {relative}")

    state_path = root / ".chatdev" / "project-state.json"
    if state_path.exists():
        state = check_json(state_path, REQUIRED_STATE_KEYS, errors)
        blockers = state.get("blockers")
        if blockers is not None and not isinstance(blockers, list):
            errors.append("project-state.json 'blockers' must be an array")
        baselines = state.get("baselines")
        if baselines is not None and not isinstance(baselines, dict):
            errors.append("project-state.json 'baselines' must be an object")

    policy_path = root / ".chatdev" / "autonomy-policy.json"
    if policy_path.exists():
        policy = check_json(policy_path, ["default_mode", "collaborate", "gate", "auto"], errors)
        for key in ("collaborate", "gate", "auto"):
            if key in policy and not isinstance(policy[key], list):
                errors.append(f"autonomy-policy.json '{key}' must be an array")

    architecture_path = root / "docs" / "architecture.md"
    if architecture_path.exists():
        text = architecture_path.read_text(encoding="utf-8")
        for heading in REQUIRED_ARCHITECTURE_HEADINGS:
            if heading not in text:
                errors.append(f"Missing architecture heading: {heading}")

    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists() or path.suffix.lower() not in {".md", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER_RE.search(text):
            errors.append(f"Unrendered template placeholder in {relative}")
        if "TODO" in text:
            warnings.append(f"Unresolved TODO remains in {relative}")

    result = {
        "root": str(root),
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
