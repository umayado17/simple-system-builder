#!/usr/bin/env python3
"""Safely update .chatdev/project-state.json."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_state(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Project state not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Project state must be a JSON object")
    return data


def parse_baseline(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Baseline must be KEY=STATUS")
    key, status = value.split("=", 1)
    key = key.strip()
    status = status.strip()
    if not key or not status:
        raise argparse.ArgumentTypeError("Baseline must be KEY=STATUS")
    return key, status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update the Chat development project state")
    parser.add_argument("--root", required=True, help="Project root directory")
    parser.add_argument("--phase")
    parser.add_argument("--status")
    parser.add_argument("--current-task")
    parser.add_argument("--next-action")
    parser.add_argument("--set-baseline", action="append", default=[], type=parse_baseline, metavar="KEY=STATUS")
    parser.add_argument("--add-blocker", action="append", default=[])
    parser.add_argument("--clear-blocker", action="append", default=[])
    parser.add_argument("--clear-all-blockers", action="store_true")
    parser.add_argument("--event", help="Short history entry describing the update")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.root).expanduser().resolve() / ".chatdev" / "project-state.json"

    try:
        state = load_state(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    changes: Dict[str, Any] = {}
    for key, value in (
        ("phase", args.phase),
        ("status", args.status),
        ("current_task", args.current_task),
        ("next_action", args.next_action),
    ):
        if value is not None:
            state[key] = value
            changes[key] = value

    baselines = state.setdefault("baselines", {})
    if not isinstance(baselines, dict):
        print("error: baselines must be a JSON object", file=sys.stderr)
        return 1
    for key, value in args.set_baseline:
        baselines[key] = value
        changes.setdefault("baselines", {})[key] = value

    blockers = state.setdefault("blockers", [])
    if not isinstance(blockers, list):
        print("error: blockers must be a JSON array", file=sys.stderr)
        return 1
    if args.clear_all_blockers:
        blockers.clear()
        changes["blockers_cleared"] = "all"
    for blocker in args.clear_blocker:
        blockers[:] = [item for item in blockers if item != blocker]
    for blocker in args.add_blocker:
        if blocker not in blockers:
            blockers.append(blocker)
    if args.add_blocker or args.clear_blocker:
        changes["blockers"] = blockers

    now = utc_now()
    state["updated_at"] = now
    history = state.setdefault("history", [])
    if not isinstance(history, list):
        history = []
        state["history"] = history
    event = args.event or "project state updated"
    history.append({"at": now, "event": event, "changes": changes})
    state["history"] = history[-50:]

    try:
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
