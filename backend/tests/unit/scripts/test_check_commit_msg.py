from pathlib import Path

import pytest

from scripts.check_commit_msg import main, offending_lines

SCISSORS = "# ------------------------ >8 ------------------------"


@pytest.mark.parametrize(
    "message",
    [
        "Add SQL validator\n",
        "Update .claude/commands for new backend paths\n",
        "Move .Claude/settings.json and .claude/commands/review.md\n",
        "Fix thing\n# Please enter the commit message. Claude\n",
        # `git commit -v` appends the diff below the scissors line.
        f"Fix thing\n{SCISSORS}\ndiff --git a/.claude/x b/.claude/x\n+Co-Authored-By: Claude\n",
        # Scissors line with a custom core.commentChar.
        f"Fix thing\n{SCISSORS.replace('#', ';', 1)}\n+Claude\n",
    ],
)
def test_allowed_messages(message: str) -> None:
    assert offending_lines(message) == []


@pytest.mark.parametrize(
    "message",
    [
        "Add validator\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n",
        "Add validator\n\nGenerated with Claude Code\n",
        "Ask CLAUDE to fix it\n",
        "Rename CLAUDE.md\n",
        # Mentions above the scissors line still count.
        f"Add validator\nclaude wrote this\n{SCISSORS}\ndiff\n",
    ],
)
def test_rejected_messages(message: str) -> None:
    assert offending_lines(message) != []


def test_main_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = tmp_path / "good"
    good.write_text("Update .claude/settings.json\n")
    bad = tmp_path / "bad"
    bad.write_text("Fix\n\nCo-Authored-By: Claude\n")

    assert main([str(good)]) == 0
    assert main([str(bad)]) == 1
    assert "Co-Authored-By: Claude" in capsys.readouterr().err
