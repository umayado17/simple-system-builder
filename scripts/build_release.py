#!/usr/bin/env python3
"""Validate and package simple-system-builder as an installable skill.zip."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

MAX_ZIP_BYTES = 25 * 1024 * 1024
REQUIRED_FILES = (Path("SKILL.md"), Path("agents/openai.yaml"))
INCLUDE_ROOTS = (
    Path("SKILL.md"),
    Path("LICENSE"),
    Path("agents"),
    Path("assets"),
    Path("references"),
    Path("scripts"),
)
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")

    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not closed")

    values: dict[str, str] = {}
    for raw_line in text[4:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Unsupported frontmatter line: {raw_line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        values[key] = value

    allowed = {"name", "description"}
    extra = set(values) - allowed
    if extra:
        raise ValueError(
            "SKILL.md frontmatter may contain only name and description; "
            f"found: {', '.join(sorted(extra))}"
        )
    if not values.get("name"):
        raise ValueError("SKILL.md frontmatter requires name")
    if not values.get("description"):
        raise ValueError("SKILL.md frontmatter requires description")
    if not SKILL_NAME_RE.fullmatch(values["name"]):
        raise ValueError(
            "Skill name must be lowercase words separated by hyphens: "
            f"{values['name']}"
        )
    return values


def iter_package_files(root: Path):
    for entry in INCLUDE_ROOTS:
        path = root / entry
        if not path.exists():
            continue
        if path.is_file():
            yield path
            continue
        for file_path in sorted(path.rglob("*")):
            if file_path.is_file() and "__pycache__" not in file_path.parts:
                yield file_path


def build(root: Path, output: Path) -> None:
    root = root.resolve()
    output = output.resolve()

    for required in REQUIRED_FILES:
        if not (root / required).is_file():
            raise ValueError(f"Missing required skill file: {required}")

    metadata = parse_frontmatter(root / "SKILL.md")
    package_root = metadata["name"]
    files = list(iter_package_files(root))
    if not files:
        raise ValueError("No files selected for packaging")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            relative = file_path.relative_to(root)
            archive.write(file_path, Path(package_root) / relative)

    size = output.stat().st_size
    if size > MAX_ZIP_BYTES:
        output.unlink(missing_ok=True)
        raise ValueError(
            f"Package is {size / 1024 / 1024:.2f} MB; skill.zip must be 25 MB or smaller"
        )

    print(f"Validated skill: {metadata['name']}")
    print(f"Packaged {len(files)} files -> {output}")
    print(f"Archive size: {size / 1024:.1f} KiB")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Skill repository root",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/skill.zip"),
        help="Output ZIP path",
    )
    args = parser.parse_args()

    try:
        build(args.root, args.output)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
