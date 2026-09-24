"""
Generate the tools' global instruction files from the repo's global/ folder.

The files are written as copies, not symlinks. Claude Code skips a symlinked ~/.claude/CLAUDE.md
in Cowork sessions, and Codex has no way to import one file into another, so its single global
file has to hold the rules and the style together.

Each generated file carries a marker with a hash of what was written. A later sync overwrites the
file only when the hash still matches, so hand edits (for example from Claude Code's memory
commands) are never lost silently.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

MARKER_PATTERN = re.compile(
    r"^<!-- Generated from the skills repo \(([^)]*)\)\. Edit it there and run `make sync`\. "
    r"sha256:([0-9a-f]{64}) -->\n",
    re.MULTILINE,
)
STYLE_NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Codex stops reading AGENTS.md content past project_doc_max_bytes (32 KiB by default).
CODEX_MAX_BYTES = 32 * 1024
# Claude Code's memory docs target under 200 lines per CLAUDE.md for adherence.
CLAUDE_MD_MAX_LINES = 200


@dataclass(frozen=True)
class GlobalPaths:
    """Where each tool reads its global instructions."""

    claude_md: Path
    output_styles: Path
    codex_agents_md: Path


@dataclass(frozen=True)
class Style:
    """The communication style from global/style.md."""

    name: str
    description: str
    body: str


@dataclass(frozen=True)
class GeneratedFile:
    """
    One file to write. `frontmatter` goes before the marker, because output styles need their
    frontmatter at the top of the file.
    """

    path: Path
    source: str
    body: str
    frontmatter: str = ""


def default_global_paths() -> GlobalPaths:
    """Return the tools' global file locations, honoring CLAUDE_HOME and CODEX_HOME."""
    claude_home = Path(os.environ.get("CLAUDE_HOME", "~/.claude")).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    return GlobalPaths(
        claude_md=claude_home / "CLAUDE.md",
        output_styles=claude_home / "output-styles",
        codex_agents_md=codex_home / "AGENTS.md",
    )


def read_style(path: Path) -> tuple[Style | None, list[str]]:
    """Parse global/style.md. A missing file means no style, which is not an error."""
    if not path.is_file():
        return None, []
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or text.find("\n---", 4) == -1:
        return None, ["global/style.md must start with a `---` frontmatter block"]
    end = text.find("\n---", 4)
    try:
        frontmatter = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as exc:
        return None, [f"global/style.md frontmatter is not valid YAML: {exc}"]
    if not isinstance(frontmatter, dict):
        return None, ["global/style.md frontmatter must be a YAML mapping"]
    errors: list[str] = []
    name = frontmatter.get("name")
    if not isinstance(name, str) or not STYLE_NAME_PATTERN.match(name):
        errors.append("global/style.md needs a `name` of lowercase letters, digits, and hyphens")
    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        errors.append("global/style.md `description` must be a string")
    if frontmatter.get("keep-coding-instructions") is False:
        errors.append(
            "global/style.md must not set keep-coding-instructions to false. The generated style "
            "always keeps Claude Code's engineering instructions",
        )
    body = text[end + 4 :].strip("\n")
    if not body:
        errors.append("global/style.md has no instructions after the frontmatter")
    if errors:
        return None, errors
    return Style(name=str(name), description=str(description), body=body), []


def build_files(global_dir: Path, paths: GlobalPaths) -> tuple[list[GeneratedFile], list[str]]:
    """Return the files to generate from global/, plus errors. No global/ folder means none."""
    if not global_dir.is_dir():
        return [], []
    rules_path = global_dir / "rules.md"
    if not rules_path.is_file():
        return [], ["global/rules.md is missing"]
    rules = rules_path.read_text(encoding="utf-8").strip("\n")
    style, errors = read_style(global_dir / "style.md")
    if errors:
        return [], errors

    files = [GeneratedFile(paths.claude_md, "global/rules.md", rules)]
    codex_body = rules
    codex_source = "global/rules.md"
    if style is not None:
        frontmatter = (
            f"---\nname: {style.name}\ndescription: {style.description}\n"
            "keep-coding-instructions: true\n---\n\n"
        )
        files.append(
            GeneratedFile(
                paths.output_styles / f"{style.name}.md",
                "global/style.md",
                style.body,
                frontmatter,
            ),
        )
        codex_body = f"{rules}\n\n{style.body}"
        codex_source = "global/rules.md and global/style.md"
    files.append(GeneratedFile(paths.codex_agents_md, codex_source, codex_body))
    return files, []


def digest(frontmatter: str, body: str) -> str:
    """Hash of everything a generated file holds except its marker line."""
    return hashlib.sha256(f"{frontmatter}\0{body}".encode()).hexdigest()


def render(file: GeneratedFile) -> str:
    """Return the full text to write for a generated file."""
    marker = (
        f"<!-- Generated from the skills repo ({file.source}). Edit it there and run `make sync`. "
        f"sha256:{digest(file.frontmatter, file.body)} -->\n"
    )
    return f"{file.frontmatter}{marker}\n{file.body}\n"


def parse_generated(text: str) -> tuple[str, str, str] | None:
    """Split a generated file into (frontmatter, body, recorded hash), or None if unmarked."""
    match = MARKER_PATTERN.search(text)
    if match is None:
        return None
    frontmatter = text[: match.start()]
    body = text[match.end() :].removeprefix("\n").removesuffix("\n")
    return frontmatter, body, match.group(2)


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
    frontmatter, body, recorded = parsed
    if digest(frontmatter, body) != recorded:
        return "edited"
    return "stale"


def backup(path: Path) -> Path:
    """Copy a file next to itself with a timestamp suffix and return the copy's path."""
    copy = path.with_name(f"{path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    shutil.copy2(path, copy)
    return copy


def write_file(file: GeneratedFile, dry_run: bool, force: bool) -> str:
    """Write one generated file if it is safe to, and describe what happened."""
    state = file_state(file)
    if state == "ok":
        return "ok"
    if state in ("edited", "unmanaged") and not force:
        reason = (
            "was edited by hand since the last sync"
            if state == "edited"
            else "exists and was not generated by this repo"
        )
        return (
            f"SKIPPED: {file.path} {reason}. Move anything worth keeping into {file.source}, "
            "then run `make sync FORCE=1` (it backs the file up first)"
        )
    note = ""
    if not dry_run:
        if state in ("edited", "unmanaged"):
            note = f" (backup: {backup(file.path)})"
        file.path.parent.mkdir(parents=True, exist_ok=True)
        file.path.write_text(render(file), encoding="utf-8")
    return {"missing": "written", "stale": "updated"}.get(state, "replaced") + note


def stale_output_styles(paths: GlobalPaths, files: list[GeneratedFile]) -> list[Path]:
    """Return generated, unedited output styles that no longer match global/style.md's name."""
    if not paths.output_styles.is_dir():
        return []
    current = {file.path for file in files}
    stale: list[Path] = []
    for path in sorted(paths.output_styles.glob("*.md")):
        if path in current:
            continue
        parsed = parse_generated(path.read_text(encoding="utf-8"))
        if parsed is not None and digest(parsed[0], parsed[1]) == parsed[2]:
            stale.append(path)
    return stale


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
    force: bool,
) -> tuple[list[str], int]:
    """Generate every global file. Return printable lines and the count of skipped files."""
    files, errors = build_files(global_dir, paths)
    if errors:
        return [f"ERROR {error}" for error in errors], len(errors)
    prefix = "[dry run] " if dry_run else ""
    lines: list[str] = []
    skipped = 0
    for file in files:
        outcome = write_file(file, dry_run, force)
        if outcome.startswith("SKIPPED"):
            skipped += 1
        if outcome != "ok":
            lines.append(f"{prefix}{file.path}: {outcome}")
    for path in stale_output_styles(paths, files):
        if not dry_run:
            path.unlink()
        lines.append(f"{prefix}removed old output style {path}")
    lines.extend(f"warning  {warning}" for warning in size_warnings(files, paths))
    return lines, skipped
