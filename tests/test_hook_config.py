"""Tests for scripts/hook_config.py and hooks/session_context.py. Every test works in a temporary directory."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import hook_config as hc
import session_context as sc

SCRIPT = Path("/repo/hooks/session_context.py")
OTHER_SETTINGS = {
    "theme": "dark",
    "hooks": {
        "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "gk hook"}]}],
        "Stop": [{"hooks": [{"type": "command", "command": "notify"}]}],
    },
}


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def commands(config: dict[str, object], event: str) -> list[str]:
    """Return every handler command for `event`, in order."""
    groups = config.get("hooks", {}).get(event, [])  # type: ignore[union-attr]
    return [entry["command"] for group in groups for entry in group["hooks"]]


def test_with_managed_adds_hooks_and_keeps_other_settings() -> None:
    result = hc.with_managed(OTHER_SETTINGS, SCRIPT)

    assert result["theme"] == "dark"
    assert commands(result, "UserPromptSubmit") == ["gk hook", f'python3 "{SCRIPT}" time']
    assert commands(result, "Stop") == ["notify"]
    assert result["hooks"]["SessionStart"] == [  # type: ignore[index]
        {"matcher": "compact", "hooks": [{"type": "command", "command": f'python3 "{SCRIPT}" style'}]},
    ]


def test_with_managed_is_idempotent_and_replaces_an_old_script_path() -> None:
    old = hc.with_managed(OTHER_SETTINGS, Path("/old/place/hooks/session_context.py"))

    once = hc.with_managed(old, SCRIPT)

    assert hc.with_managed(once, SCRIPT) == once
    assert commands(once, "UserPromptSubmit") == ["gk hook", f'python3 "{SCRIPT}" time']
    assert len(commands(once, "SessionStart")) == 1


def test_without_managed_restores_the_original() -> None:
    assert hc.without_managed(hc.with_managed(OTHER_SETTINGS, SCRIPT)) == OTHER_SETTINGS
    assert hc.without_managed(hc.with_managed({}, SCRIPT)) == {}


def test_sync_writes_both_tools_and_backs_up_existing_file(tmp_path: Path) -> None:
    claude = hc.HookFile("claude", tmp_path / "claude" / "settings.json")
    codex = hc.HookFile("codex", tmp_path / "codex" / "hooks.json")
    write_json(claude.path, OTHER_SETTINGS)

    lines = hc.sync_hooks([claude, codex], dry_run=False, script=SCRIPT)

    assert json.loads(claude.path.read_text()) == hc.with_managed(OTHER_SETTINGS, SCRIPT)
    assert json.loads(codex.path.read_text()) == hc.with_managed({}, SCRIPT)
    assert len(list(claude.path.parent.glob("settings.json.bak-*"))) == 1
    assert any("/hooks" in line for line in lines)
    assert hc.sync_hooks([claude, codex], dry_run=False, script=SCRIPT) == []


def test_sync_dry_run_changes_nothing(tmp_path: Path) -> None:
    codex = hc.HookFile("codex", tmp_path / "hooks.json")

    lines = hc.sync_hooks([codex], dry_run=True, script=SCRIPT)

    assert not codex.path.exists()
    assert lines == [f"[dry run] codex  hooks: would update {codex.path}"]


def test_sync_skips_a_file_that_is_not_a_json_object(tmp_path: Path) -> None:
    claude = hc.HookFile("claude", tmp_path / "settings.json")
    claude.path.write_text("[1, 2]")

    lines = hc.sync_hooks([claude], dry_run=False, script=SCRIPT)

    assert "SKIPPED" in lines[0]
    assert claude.path.read_text() == "[1, 2]"


def test_remove_deletes_a_codex_file_that_held_only_these_hooks(tmp_path: Path) -> None:
    claude = hc.HookFile("claude", tmp_path / "settings.json")
    codex = hc.HookFile("codex", tmp_path / "hooks.json")
    hc.sync_hooks([claude, codex], dry_run=False)
    write_json(claude.path, hc.with_managed(OTHER_SETTINGS))

    hc.remove_hooks([claude, codex], dry_run=False)

    assert not codex.path.exists()
    assert json.loads(claude.path.read_text()) == OTHER_SETTINGS


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        (hc.with_managed({}, SCRIPT), "installed"),
        ({}, "missing"),
        (hc.with_managed({}, Path("/old/hooks/session_context.py")), "stale"),
    ],
)
def test_hook_state(tmp_path: Path, config: dict[str, object], expected: str) -> None:
    hook_file = hc.HookFile("codex", tmp_path / "hooks.json")
    write_json(hook_file.path, config)

    assert hc.hook_state(hook_file, SCRIPT) == expected


def test_time_line_names_weekday_date_time_and_zone() -> None:
    now = datetime(2026, 9, 28, 21, 40, tzinfo=timezone(timedelta(hours=-7), "PDT"))

    assert sc.time_line(now) == "User message sent Mon 2026-09-28 21:40 PDT"


def test_style_reminder_includes_the_style_text(tmp_path: Path) -> None:
    style = tmp_path / "style.md"
    style.write_text("## How to communicate\n\n- Lead with the answer.\n")

    reminder = sc.style_reminder(style)

    assert reminder.startswith(sc.STYLE_HEADER)
    assert reminder.endswith("- Lead with the answer.")
    assert sc.style_reminder(tmp_path / "missing.md") == ""


def test_main_prints_time_and_ignores_unknown_commands(capsys: pytest.CaptureFixture[str]) -> None:
    assert sc.main(["time"]) == 0
    assert capsys.readouterr().out.startswith("User message sent ")
    assert sc.main(["nonsense"]) == 0
    assert capsys.readouterr().out == ""


def test_hook_script_path_points_at_the_real_script() -> None:
    assert hc.HOOK_SCRIPT.is_file()
    assert hc.HOOK_MARKER in str(hc.HOOK_SCRIPT)
