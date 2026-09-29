"""
Install this repo's hooks into Claude Code and Codex.

Both tools read hooks from a JSON file with the same shape: `{"hooks": {<event>: [<group>, ...]}}`,
where a group has an optional `matcher` and a list of handlers. Claude Code keeps them in
~/.claude/settings.json next to its other settings. Codex reads ~/.codex/hooks.json.

A handler belongs to this repo when its command runs hooks/session_context.py. Sync replaces those
handlers and leaves every other setting and hook as it was. Codex runs a new or changed hook only
after the user approves it once in its `/hooks` screen.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from global_files import backup

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_SCRIPT = REPO_ROOT / "hooks" / "session_context.py"
HOOK_MARKER = "hooks/session_context.py"


@dataclass(frozen=True)
class HookFile:
    """A tool's hook configuration file."""

    tool: str
    path: Path


def default_hook_files() -> list[HookFile]:
    """Return the real hook files, honoring CLAUDE_HOME and CODEX_HOME if set."""
    claude_home = Path(os.environ.get("CLAUDE_HOME", "~/.claude")).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    return [
        HookFile("claude", claude_home / "settings.json"),
        HookFile("codex", codex_home / "hooks.json"),
    ]


def handler(argument: str, script: Path = HOOK_SCRIPT) -> dict[str, str]:
    """Return a command handler that runs the hook script with `argument`."""
    return {"type": "command", "command": f'python3 "{script}" {argument}'}


def managed_groups(script: Path = HOOK_SCRIPT) -> dict[str, list[dict[str, object]]]:
    """Return this repo's hook groups by event: the send time on every message, the style after compaction."""
    return {
        "UserPromptSubmit": [{"hooks": [handler("time", script)]}],
        "SessionStart": [{"matcher": "compact", "hooks": [handler("style", script)]}],
    }


def is_managed(entry: object) -> bool:
    """Return True if a handler runs this repo's hook script."""
    return isinstance(entry, dict) and HOOK_MARKER in str(entry.get("command", ""))


def without_managed(config: dict[str, object]) -> dict[str, object]:
    """Return a copy of `config` with this repo's handlers removed, and groups or events left empty by that."""
    result = json.loads(json.dumps(config))
    hooks = result.get("hooks")
    if not isinstance(hooks, dict):
        return result
    for event in list(hooks):
        groups = hooks[event] if isinstance(hooks[event], list) else []
        kept = []
        for group in groups:
            if isinstance(group, dict) and isinstance(group.get("hooks"), list):
                handlers = [entry for entry in group["hooks"] if not is_managed(entry)]
                if not handlers:
                    continue
                group["hooks"] = handlers
            kept.append(group)
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    if not hooks:
        del result["hooks"]
    return result


def with_managed(config: dict[str, object], script: Path = HOOK_SCRIPT) -> dict[str, object]:
    """Return a copy of `config` with this repo's handlers installed exactly once."""
    result = without_managed(config)
    hooks = result.setdefault("hooks", {})
    for event, groups in managed_groups(script).items():
        hooks.setdefault(event, []).extend(groups)
    return result


def read_config(path: Path) -> dict[str, object]:
    """Read a hook file, or return {} if it doesn't exist. Raises ValueError if it isn't a JSON object."""
    if not path.exists():
        return {}
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"{path} is not a JSON object")
    return config


def update_file(hook_file: HookFile, install: bool, dry_run: bool, script: Path = HOOK_SCRIPT) -> str:
    """Install or remove this repo's hooks in one file, and describe what happened."""
    try:
        current = read_config(hook_file.path)
    except ValueError as error:
        return f"SKIPPED {hook_file.path}: {error}"
    updated = with_managed(current, script) if install else without_managed(current)
    if updated == current:
        return "ok"
    if dry_run:
        return f"would update {hook_file.path}"
    if hook_file.path.exists():
        backup(hook_file.path)
    if not updated and not install:
        hook_file.path.unlink()
        return f"removed {hook_file.path}"
    hook_file.path.parent.mkdir(parents=True, exist_ok=True)
    hook_file.path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    return f"updated {hook_file.path}"


def hook_state(hook_file: HookFile, script: Path = HOOK_SCRIPT) -> str:
    """Return `installed`, `missing`, or `stale` (installed with a different command) for one file."""
    try:
        current = read_config(hook_file.path)
    except ValueError:
        return "unreadable"
    if current == with_managed(current, script):
        return "installed"
    return "stale" if current != without_managed(current) else "missing"


def sync_hooks(hook_files: list[HookFile], dry_run: bool, script: Path = HOOK_SCRIPT) -> list[str]:
    """Install this repo's hooks in every tool. Return a line for each file that changed or was skipped."""
    lines = []
    prefix = "[dry run] " if dry_run else ""
    for hook_file in hook_files:
        outcome = update_file(hook_file, install=True, dry_run=dry_run, script=script)
        if outcome != "ok":
            lines.append(f"{prefix}{hook_file.tool:<6} hooks: {outcome}")
        if outcome.startswith("updated") and hook_file.tool == "codex":
            lines.append("       Codex runs the new hooks after you approve them: run `codex`, then `/hooks`")
    return lines


def remove_hooks(hook_files: list[HookFile], dry_run: bool) -> list[str]:
    """Remove this repo's hooks from every tool. Return a line for each file that changed."""
    prefix = "[dry run] " if dry_run else ""
    lines = []
    for hook_file in hook_files:
        outcome = update_file(hook_file, install=False, dry_run=dry_run)
        if outcome != "ok":
            lines.append(f"{prefix}{hook_file.tool:<6} hooks: {outcome}")
    return lines
