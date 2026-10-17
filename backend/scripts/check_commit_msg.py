"""commit-msg hook: reject commit messages that mention Claude.

Usage (run by pre-commit at the commit-msg stage):
    python backend/scripts/check_commit_msg.py PATH_TO_COMMIT_MSG

Ignored:
    - git's editor comments (lines starting with '#')
    - everything below the scissors line that `git commit -v` adds before the diff
    - `.claude/` paths, so a message can name files in the project's .claude/ directory
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# git writes this line above the diff in verbose mode; the comment char can be configured.
SCISSORS = re.compile(r"^\S -{24} >8 -{24}$")
CLAUDE_DIR = re.compile(r"\.claude/", re.IGNORECASE)
CLAUDE = re.compile(r"claude", re.IGNORECASE)


def offending_lines(message: str) -> list[str]:
    """Return the message lines that mention Claude, ignoring comments, the diff, and `.claude/`."""
    found: list[str] = []
    for line in message.splitlines():
        if SCISSORS.match(line):
            break
        if line.startswith("#"):
            continue
        if CLAUDE.search(CLAUDE_DIR.sub("", line)):
            found.append(line)
    return found


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: check_commit_msg.py PATH_TO_COMMIT_MSG", file=sys.stderr)
        return 2
    lines = offending_lines(Path(args[0]).read_text(encoding="utf-8"))
    for line in lines:
        print(f"Commit message must not mention Claude: {line}", file=sys.stderr)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
