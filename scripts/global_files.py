"""
Generate the tools' global instruction files from the repo's global/ folder.

Both tools get the same text: global/rules.md, then global/style.md. The files are written as
copies, not symlinks. Claude Code skips a symlinked ~/.claude/CLAUDE.md in Cowork sessions, and
Codex has no way to import one file into another, so each tool's single global file has to hold
the rules and the style together.

Another repo's rules (for example a work repo on a work machine) are included by naming the file in
GLOBAL_EXTRA in local.mk, not appended by that repo, so the two syncs never overwrite each other.

Each generated file carries a marker with a hash of what was written. When a file no longer matches
what sync last wrote (a hand edit or Claude Code's memory commands), sync backs the file up, replaces
it, and shows what changed, so nothing is lost silently.
"""

from __future__ import annotations

import difflib
import hashlib
import os
import re
import shutil
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

MARKER_PATTERN = re.compile(
    r"^<!-- Generated from the skills repo \(([^)]*)\)\. Edit it there and run `make sync`\. "
    r"sha256:([0-9a-f]{64}) -->\n",
    re.MULTILINE,
)

# Codex stops reading AGENTS.md content past project_doc_max_bytes (32 KiB by default).
CODEX_MAX_BYTES = 32 * 1024
# Claude Code's memory docs target under 200 lines per CLAUDE.md for adherence.
CLAUDE_MD_MAX_LINES = 200


@dataclass(frozen=True)
class GlobalPaths:
    """Where each tool reads its global instructions."""

    claude_md: Path
    codex_agents_md: Path


@dataclass(frozen=True)
class GeneratedFile:
    """One file to write, and the repo files it comes from."""

    path: Path
    source: str
    body: str


def default_global_paths() -> GlobalPaths:
    """Return the tools' global file locations, honoring CLAUDE_HOME and CODEX_HOME."""
    claude_home = Path(os.environ.get("CLAUDE_HOME", "~/.claude")).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    return GlobalPaths(
        claude_md=claude_home / "CLAUDE.md",
        codex_agents_md=codex_home / "AGENTS.md",
    )


def build_files(
    global_dir: Path,
    paths: GlobalPaths,
    extra: Sequence[Path] = (),
) -> tuple[list[GeneratedFile], list[str]]:
    """
    Return the files to generate, plus errors. The body is global/rules.md, then each extra file
    (another repo's rules, named in local.mk), then global/style.md. No global/ folder means none.
    """
    if not global_dir.is_dir():
        return [], []
    rules_path = global_dir / "rules.md"
    if not rules_path.is_file():
        return [], ["global/rules.md is missing"]
    missing = [f"{display_path(path)} is missing (listed in GLOBAL_EXTRA in local.mk)" for path in extra if not path.is_file()]
    if missing:
        return [], missing
    parts = [rules_path.read_text(encoding="utf-8").strip("\n")]
    sources = ["global/rules.md"]
    for path in extra:
        text = path.read_text(encoding="utf-8").strip("\n")
        if text:
            parts.append(text)
            sources.append(display_path(path))
    style_path = global_dir / "style.md"
    if style_path.is_file():
        style = style_path.read_text(encoding="utf-8").strip("\n")
        if style:
            parts.append(style)
            sources.append("global/style.md")
    body = "\n\n".join(parts)
    source = sources[0] if len(sources) == 1 else ", ".join(sources[:-1]) + f" and {sources[-1]}"
    return [
        GeneratedFile(paths.claude_md, source, body),
        GeneratedFile(paths.codex_agents_md, source, body),
    ], []


def display_path(path: Path) -> str:
    """A path with the home folder shown as ~, for messages and the marker."""
    home = Path.home()
    return f"~/{path.relative_to(home)}" if path.is_relative_to(home) else str(path)


@dataclass(frozen=True)
class Difference:
    """A global file that differed from what sync writes, the backup of it, and the diff."""

    path: Path
    backup: Path | None
    diff: list[str]


def digest(body: str) -> str:
    """Hash of everything a generated file holds except its marker line."""
    return hashlib.sha256(body.encode()).hexdigest()


def render(file: GeneratedFile) -> str:
    """Return the full text to write for a generated file."""
    marker = (
        f"<!-- Generated from the skills repo ({file.source}). Edit it there and run `make sync`. "
        f"sha256:{digest(file.body)} -->\n"
    )
    return f"{marker}\n{file.body}\n"


def parse_generated(text: str) -> tuple[str, str] | None:
    """Split a generated file into (body, recorded hash), or None if it has no marker."""
    match = MARKER_PATTERN.match(text)
    if match is None:
        return None
    body = text[match.end() :].removeprefix("\n").removesuffix("\n")
    return body, match.group(2)


def file_state(file: GeneratedFile) -> str:
    """
    Return one of:
    `missing`, `ok` (matches the source), `stale` (generated and untouched, but the source
    changed), `edited` (generated, then changed by hand), or `unmanaged` (not generated by us).
    """
    if not file.path.exists():
        return "missing"
    text = file.path.read_text(encoding="utf-8")
    if text == render(file):
        return "ok"
    parsed = parse_generated(text)
    if parsed is None:
        return "unmanaged"
    body, recorded = parsed
    if digest(body) != recorded:
        return "edited"
    return "stale"


def backup(path: Path) -> Path:
    """Copy a file next to itself with a timestamp suffix and return the copy's path."""
    copy = path.with_name(f"{path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    shutil.copy2(path, copy)
    return copy


def write_file(file: GeneratedFile, dry_run: bool) -> tuple[str, Difference | None]:
    """
    Write one generated file and describe what happened. A file that differs from what sync last
    wrote is backed up first, and the returned Difference holds the backup and the diff.
    """
    state = file_state(file)
    if state == "ok":
        return "ok", None
    difference = None
    if state in ("edited", "unmanaged"):
        current = file.path.read_text(encoding="utf-8").splitlines()
        diff = list(
            difflib.unified_diff(current, render(file).splitlines(), "before sync", "after sync", lineterm=""),
        )
        backup_path = None if dry_run else backup(file.path)
        difference = Difference(file.path, backup_path, diff)
    if not dry_run:
        file.path.parent.mkdir(parents=True, exist_ok=True)
        file.path.write_text(render(file), encoding="utf-8")
    outcome = {"missing": "written", "stale": "updated"}.get(state, "replaced")
    if difference is not None and difference.backup is not None:
        outcome += f" (backup: {difference.backup})"
    return outcome, difference


def size_warnings(files: list[GeneratedFile], paths: GlobalPaths) -> list[str]:
    """Warn when a generated file is past a size its tool handles well."""
    warnings: list[str] = []
    for file in files:
        text = render(file)
        if file.path == paths.codex_agents_md and len(text.encode()) > CODEX_MAX_BYTES:
            warnings.append(
                f"{file.path} would be {len(text.encode()):,} bytes. Codex reads only the first "
                f"{CODEX_MAX_BYTES:,} by default",
            )
        if file.path == paths.claude_md and len(text.splitlines()) > CLAUDE_MD_MAX_LINES:
            warnings.append(
                f"{file.path} would be {len(text.splitlines())} lines. Claude Code's docs target "
                f"under {CLAUDE_MD_MAX_LINES} for adherence",
            )
    return warnings


def sync_global(
    global_dir: Path,
    paths: GlobalPaths,
    dry_run: bool,
    extra: Sequence[Path] = (),
) -> tuple[list[str], list[Difference]]:
    """Generate every global file. Return printable lines and the files that had differed."""
    files, errors = build_files(global_dir, paths, extra)
    if errors:
        return [f"ERROR {error}" for error in errors], []
    prefix = "[dry run] " if dry_run else ""
    lines: list[str] = []
    differences: list[Difference] = []
    for file in files:
        outcome, difference = write_file(file, dry_run)
        if difference is not None:
            differences.append(difference)
        if outcome != "ok":
            lines.append(f"{prefix}{file.path}: {outcome}")
    lines.extend(f"warning  {warning}" for warning in size_warnings(files, paths))
    return lines, differences


def review_differences(
    differences: list[Difference],
    interactive: bool,
    ask: Callable[[str], str] = input,
    show: Callable[[str], None] = print,
) -> None:
    """
    Show each difference, then decide its backup. In a terminal, ask whether to delete it, after
    the diff is on screen. Without one, keep it and tell the agent that ran sync what to report.
    """
    for difference in differences:
        show(
            f"warning  {difference.path} differed from what sync writes. Lines starting with - were "
            "in the file and are gone now:",
        )
        for line in ["", *difference.diff, ""]:
            show(line)
        if difference.backup is None:
            show("[dry run] sync would back the file up and replace it.")
            continue
        if not interactive:
            show(
                f"No terminal, so the backup was kept: {difference.backup}. Tell the user that "
                f"{difference.path} differed from what sync writes, show them the diff above and the "
                "backup path, and ask whether to delete the backup.",
            )
            continue
        answer = ask(f"Delete the backup {difference.backup}? [y/N] ")
        if answer.strip().lower() in ("y", "yes"):
            difference.backup.unlink()
            show(f"deleted {difference.backup}")
        else:
            show(f"kept {difference.backup}")


STATE_EXPLANATIONS = {
    "missing": "doesn't exist. `make sync` will create it.",
    "ok": "was written by this repo and is up to date. Nothing to keep.",
    "stale": "was written by this repo. `make sync` will update it. Nothing to keep.",
    "edited": (
        "was written by this repo, then changed. `make sync` will back it up and replace it. How it "
        "differs from what sync would write (lines starting with - are only in the current file):"
    ),
    "unmanaged": (
        "wasn't written by this repo. `make sync` will back it up and replace it, so move anything "
        "worth keeping into global/ first. Its contents:"
    ),
}


def check_global(global_dir: Path, paths: GlobalPaths, extra: Sequence[Path] = ()) -> list[str]:
    """
    Describe each global file before a sync: whether it exists, whether this repo wrote it, and
    how any changed file differs from what sync writes, so the user can see what's worth keeping.
    """
    files, errors = build_files(global_dir, paths, extra)
    if errors:
        return [f"ERROR {error}" for error in errors]
    lines: list[str] = []
    for file in files:
        state = file_state(file)
        lines.append(f"{file.path} {STATE_EXPLANATIONS[state]}")
        if state == "unmanaged":
            lines.extend(["", *file.path.read_text(encoding="utf-8").splitlines(), ""])
        elif state == "edited":
            current = file.path.read_text(encoding="utf-8").splitlines()
            diff = difflib.unified_diff(current, render(file).splitlines(), "current", "sync would write", lineterm="")
            lines.extend(["", *diff, ""])
    return lines
