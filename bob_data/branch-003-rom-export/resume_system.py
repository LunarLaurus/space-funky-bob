#!/usr/bin/env python3
"""
Autonomous Resume Subsystem for Space Funky B.O.B. Level Editor
Stores session state for seamless resume after conversation compaction.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

STATE_DIR = Path(__file__).parent / "state"
CURRENT_STATE = STATE_DIR / "current.json"
HISTORY_DIR = STATE_DIR / "history"

PROJECT_ROOT = Path(__file__).parent.parent

TASKS = {
    "001-lz77": {"status": "complete", "branch": "branch-001-lz77"},
    "002-level-pointers": {"status": "complete", "branch": "branch-002-level-pointers"},
    "003-rom-export": {"status": "complete", "branch": "branch-003-rom-export"},
    "004-ui-enhancements": {"status": "complete", "branch": "branch-004-ui"},
    "005-data-mapping": {"status": "complete", "branch": "branch-005-data"},
    "006-testing": {"status": "complete", "branch": "branch-006-tests"},
}

CURRENT_BRANCH = "003-rom-export"


class ResumeState:
    def __init__(self):
        self.state_dir = STATE_DIR
        self.state_dir.mkdir(exist_ok=True)
        self.history_dir = HISTORY_DIR
        self.history_dir.mkdir(exist_ok=True)
        self.load()

    def load(self):
        if CURRENT_STATE.exists():
            with open(CURRENT_STATE) as f:
                self.data = json.load(f)
        else:
            self.data = self._default_state()

    def _default_state(self):
        return {
            "session_start": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "current_task": "rom-export",
            "task_status": "in_progress",
            "branch": CURRENT_BRANCH,
            "completed_milestones": [],
            "pending_actions": [],
            "files_modified": [],
            "server_status": "running",
            "editor_url": "http://localhost:8000",
            "rom_path": str(PROJECT_ROOT / "B.O.B._edit.smc"),
            "todo_progress": {},
        }

    def save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(CURRENT_STATE, "w") as f:
            json.dump(self.data, f, indent=2)

    def checkpoint(self, task_name, status, details=None):
        self.data["pending_actions"].append(
            {
                "task": task_name,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "details": details or {},
            }
        )
        self.save()

    def complete_task(self, task_id):
        if task_id not in self.data["completed_milestones"]:
            self.data["completed_milestones"].append(task_id)
        self.data["pending_actions"] = [
            a for a in self.data["pending_actions"] if a.get("task") != task_id
        ]
        self.save()

    def archive_session(self, reason=""):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = HISTORY_DIR / f"session_{timestamp}.json"

        archive_data = self.data.copy()
        archive_data["archive_reason"] = reason
        archive_data["archived_at"] = datetime.now().isoformat()

        with open(archive_name, "w") as f:
            json.dump(archive_data, f, indent=2)

        self.data = self._default_state()
        self.save()
        return archive_name

    def get_resume_instructions(self):
        lines = [
            "# Resume Instructions for Space Funky B.O.B. Level Editor",
            "",
            f"Last updated: {self.data['last_updated']}",
            f"Current branch: {self.data['branch']}",
            "",
            "## Project Status",
            "",
        ]

        for milestone in self.data["completed_milestones"]:
            if milestone in TASKS:
                lines.append(f"- [x] {TASKS[milestone].get('branch', milestone)}")

        lines.extend(
            [
                "",
                "## Pending Actions",
                "",
            ]
        )

        for action in self.data["pending_actions"]:
            status_emoji = {"todo": "[ ]", "in_progress": "[~]", "done": "[x]"}.get(
                action.get("status", "todo"), "[ ]"
            )
            lines.append(f"- {status_emoji} {action.get('task', 'unknown')}")

        lines.extend(
            [
                "",
                "## Quick Resume Commands",
                "",
                "```bash",
                "# Start editor server",
                "cd /usr/workspace/space-funky-bob/editor && python3 server.py",
                "",
                "# Run tests",
                "cd /usr/workspace/space-funky-bob && python3 run_tests.py",
                "",
                "# Archive branch",
                "cd /usr/workspace/space-funky-bob && tar -czvf branch-003-rom-export.tar.gz branch-003-rom-export/",
                "```",
                "",
                "## Editor Access",
                f"- URL: {self.data.get('editor_url', 'http://localhost:8000')}",
                f"- ROM: {self.data.get('rom_path', 'B.O.B._edit.smc')}",
            ]
        )

        return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Resume state manager")
    parser.add_argument(
        "command",
        choices=["save", "checkpoint", "complete", "archive", "resume", "status"],
    )
    parser.add_argument("--task", help="Task name/ID")
    parser.add_argument("--status", help="Status (todo/in_progress/done)")
    parser.add_argument("--details", help="JSON details")
    parser.add_argument("--reason", help="Archive reason")

    args = parser.parse_args()
    state = ResumeState()

    if args.command == "save":
        state.save()
        print("State saved")

    elif args.command == "checkpoint":
        details = json.loads(args.details) if args.details else None
        state.checkpoint(args.task, args.status, details)
        print(f"Checkpoint: {args.task} -> {args.status}")

    elif args.command == "complete":
        state.complete_task(args.task)
        print(f"Completed: {args.task}")

    elif args.command == "archive":
        reason = args.reason or "manual"
        archive = state.archive_session(reason)
        print(f"Archived to: {archive}")

    elif args.command == "resume":
        print(state.get_resume_instructions())

    elif args.command == "status":
        print(json.dumps(state.data, indent=2))


if __name__ == "__main__":
    main()
