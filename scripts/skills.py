"""
Manage personal agent skills and global instructions.

Links each skill directory in the source folders into the Claude Code and Codex personal skill
folders, validates skills against the Agent Skills spec and authoring best practices, and
generates the tools' global instruction files from global/ (see global_files.py), and installs the
hooks in hooks/ (see hook_config.py).

The script only ever creates, replaces, or removes symlinks that point into a source folder. It
never deletes a real directory. `adopt` moves a real directory into the repo and links it back.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from global_files import (
    GlobalPaths,
    build_files,
    check_global,
    default_global_paths,
    file_state,
    size_warnings,
    sync_global,
)
from hook_config import default_hook_files, hook_state, remove_hooks, sync_hooks

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT / "skills"
GLOBAL_DIR = REPO_ROOT / "global"
README_PATH = REPO_ROOT / "README.md"
README_SKILLS_SECTION = re.compile(r"^## Skills\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)

# Hard limits from the Agent Skills spec (https://agentskills.io/specification).
MAX_NAME_CHARS = 64
MAX_DESCRIPTION_CHARS = 1024
MAX_COMPATIBILITY_CHARS = 500
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Soft limits and heuristics from Claude Code and Anthropic authoring guidance.
MAX_CLAUDE_LISTING_CHARS = 1536  # Claude Code truncates description + when_to_use here.
MAX_SKILL_LINES = 500
MIN_DESCRIPTION_CHARS = 40
XML_TAG_PATTERN = re.compile(r"<[^>\n]+>")
WHEN_PATTERN = re.compile(r"\b(use (it |this )?(when|for|to|after|before)|when )", re.IGNORECASE)
PERSON_PATTERN = re.compile(r"\b(I can|I will|I'll|you can|you should)\b", re.IGNORECASE)
RESERVED_NAME_WORDS = ("anthropic", "claude")

# Automatic skills share a startup listing of names and descriptions. Codex documents 8,000
# characters as its fallback budget, the smallest documented limit of the two tools. Claude Code
# uses 1% of the context window.
LISTING_BUDGET_CHARS = 8000
LISTING_WARN_FRACTION = 0.75

# Markdown links in skill files. Code is stripped first, so example links in code aren't checked.
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\)")
FENCED_CODE = re.compile(r"^(```|~~~).*?^\1", re.MULTILINE | re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")
EXTERNAL_LINK = re.compile(r"^([a-z][a-z0-9+.-]*:|#)", re.IGNORECASE)

# Entries in a target folder that belong to the tool itself.
RESERVED_ENTRIES = {"synced", ".trash"}


@dataclass(frozen=True)
class Target:
    """A tool's personal skills folder."""

    tool: str
    root: Path


@dataclass(frozen=True)
class Skill:
    """A skill directory in a source folder. `name` is the directory name."""

    name: str
    path: Path


@dataclass
class ValidationResult:
    """
    Errors break the spec or a tool. Warnings are best-practice problems.

    `claude_auto` and `codex_auto` say whether each tool may choose the skill on its own, which
    puts its name and description in that tool's startup listing. `listing_chars` is the size of
    that entry.
    """

    skill: Skill
    errors: list[str]
    warnings: list[str]
    claude_auto: bool = True
    codex_auto: bool = True
    listing_chars: int = 0


def default_targets() -> list[Target]:
    """Return the Claude Code and Codex personal skill folders, overridable by env vars."""
    claude = os.environ.get("CLAUDE_SKILLS_DIR", "~/.claude/skills")
    codex = os.environ.get("CODEX_SKILLS_DIR", "~/.agents/skills")
    return [
        Target("claude", Path(claude).expanduser()),
        Target("codex", Path(codex).expanduser()),
    ]


def find_skills(sources: list[Path]) -> tuple[list[Skill], list[str]]:
    """Return every skill in the source folders, plus errors for missing sources and duplicates."""
    skills: list[Skill] = []
    errors: list[str] = []
    seen: dict[str, Path] = {}
    for source in sources:
        if not source.is_dir():
            errors.append(f"source folder does not exist: {source}")
            continue
        for entry in sorted(source.iterdir()):
            if entry.name.startswith(".") or entry.name in RESERVED_ENTRIES or not entry.is_dir():
                continue
            if not (entry / "SKILL.md").is_file():
                errors.append(f"{entry}: directory has no SKILL.md")
                continue
            if entry.name in seen:
                errors.append(
                    f"duplicate skill name '{entry.name}': {seen[entry.name]} and {entry}",
                )
                continue
            seen[entry.name] = entry
            skills.append(Skill(name=entry.name, path=entry.absolute()))
    return skills, errors


def real(path: Path) -> Path:
    """Resolve a path without requiring it to exist, so dangling links still compare."""
    return Path(os.path.realpath(path))


def is_managed(entry: Path, sources: list[Path]) -> bool:
    """Return True when `entry` is a symlink into one of the source folders."""
    if not entry.is_symlink():
        return False
    link_target = real(entry)
    return any(link_target.is_relative_to(real(source)) for source in sources)


def link_skill(skill: Skill, target: Target, sources: list[Path], dry_run: bool) -> str:
    """Create or repair the symlink for one skill in one target, and describe what happened."""
    dest = target.root / skill.name
    if dest.is_symlink():
        if real(dest) == real(skill.path):
            return "ok"
        if not is_managed(dest, sources):
            return f"SKIPPED: {dest} is a symlink to {os.readlink(dest)}, not managed by this repo"
        if not dry_run:
            dest.unlink()
            dest.symlink_to(skill.path, target_is_directory=True)
        return "relinked"
    if dest.exists():
        return f"SKIPPED: {dest} is a real directory. Run `make adopt NAME={skill.name}`"
    if not dry_run:
        target.root.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(skill.path, target_is_directory=True)
    return "linked"


def managed_links(target: Target, sources: list[Path]) -> list[Path]:
    """Return every symlink in the target folder that points into a source folder."""
    if not target.root.is_dir():
        return []
    return sorted(entry for entry in target.root.iterdir() if is_managed(entry, sources))


def prune(
    skills: list[Skill],
    targets: list[Target],
    sources: list[Path],
    dry_run: bool,
) -> list[Path]:
    """Remove managed symlinks whose skill no longer exists in a source folder."""
    wanted = {real(skill.path) for skill in skills}
    removed: list[Path] = []
    for target in targets:
        for entry in managed_links(target, sources):
            if real(entry) not in wanted:
                if not dry_run:
                    entry.unlink()
                removed.append(entry)
    return removed


def unlink_all(targets: list[Target], sources: list[Path], dry_run: bool) -> list[Path]:
    """Remove every managed symlink from every target."""
    removed: list[Path] = []
    for target in targets:
        for entry in managed_links(target, sources):
            if not dry_run:
                entry.unlink()
            removed.append(entry)
    return removed


def read_frontmatter(skill_md: Path) -> tuple[dict[str, object] | None, str, str | None]:
    """Parse SKILL.md into (frontmatter, body, error)."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, text, "SKILL.md must start with a `---` YAML frontmatter block"
    end = text.find("\n---", 4)
    if end == -1:
        return None, text, "frontmatter block is not closed with `---`"
    body = text[end + 4 :].lstrip("\n")
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        return None, body, f"frontmatter is not valid YAML: {exc}"
    if not isinstance(data, dict):
        return None, body, "frontmatter must be a YAML mapping"
    return data, body, None


def read_codex_policy(skill_dir: Path) -> tuple[bool, str | None]:
    """Return (allow_implicit_invocation, error) from the skill's agents/openai.yaml."""
    path = skill_dir / "agents" / "openai.yaml"
    if not path.is_file():
        return True, None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return True, f"agents/openai.yaml is not valid YAML: {exc}"
    if not isinstance(data, dict):
        return True, "agents/openai.yaml must be a YAML mapping"
    policy = data.get("policy") or {}
    if not isinstance(policy, dict):
        return True, "agents/openai.yaml `policy` must be a mapping"
    allow = policy.get("allow_implicit_invocation", True)
    if not isinstance(allow, bool):
        return True, "agents/openai.yaml `policy.allow_implicit_invocation` must be true or false"
    return allow, None


def validate_skill(skill: Skill) -> ValidationResult:
    """Check one skill against the spec (errors) and authoring best practices (warnings)."""
    result = ValidationResult(skill=skill, errors=[], warnings=[])
    frontmatter, body, error = read_frontmatter(skill.path / "SKILL.md")
    if error or frontmatter is None:
        result.errors.append(error or "missing frontmatter")
        return result

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name:
        result.errors.append("`name` is required")
    else:
        if name != skill.name:
            result.errors.append(f"`name` ({name}) must match the directory name ({skill.name})")
        if len(name) > MAX_NAME_CHARS:
            result.errors.append(f"`name` is longer than {MAX_NAME_CHARS} characters")
        if not NAME_PATTERN.match(name):
            result.errors.append(
                "`name` must be lowercase letters, digits, and single hyphens, "
                "with no leading or trailing hyphen",
            )
        if any(word in name for word in RESERVED_NAME_WORDS):
            result.warnings.append(
                "`name` contains 'anthropic' or 'claude', which the Claude API rejects",
            )

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        result.errors.append("`description` is required")
        description = ""
    else:
        if len(description) > MAX_DESCRIPTION_CHARS:
            result.errors.append(
                f"`description` is {len(description)} characters (max {MAX_DESCRIPTION_CHARS})",
            )
        if "TODO" in description:
            result.errors.append("`description` still contains TODO")
        if len(description) < MIN_DESCRIPTION_CHARS:
            result.warnings.append(
                "`description` is very short. Say what the skill does and when to use it",
            )
        if not WHEN_PATTERN.search(description):
            result.warnings.append(
                "`description` does not say when to use the skill (e.g. 'Use when ...')",
            )
        if PERSON_PATTERN.search(description):
            result.warnings.append(
                "`description` should be third person ('Reviews diffs', not 'I can review')",
            )

    for field_name in ("name", "description"):
        value = frontmatter.get(field_name)
        if isinstance(value, str) and XML_TAG_PATTERN.search(value):
            result.errors.append(f"`{field_name}` must not contain XML tags")

    compatibility = frontmatter.get("compatibility")
    if isinstance(compatibility, str) and len(compatibility) > MAX_COMPATIBILITY_CHARS:
        result.errors.append(f"`compatibility` is longer than {MAX_COMPATIBILITY_CHARS} characters")

    when_to_use = frontmatter.get("when_to_use")
    listing = description + (when_to_use if isinstance(when_to_use, str) else "")
    if len(listing) > MAX_CLAUDE_LISTING_CHARS:
        result.warnings.append(
            f"description + when_to_use is {len(listing)} characters. Claude Code truncates at "
            f"{MAX_CLAUDE_LISTING_CHARS}",
        )

    disable = frontmatter.get("disable-model-invocation", False)
    if not isinstance(disable, bool):
        result.errors.append("`disable-model-invocation` must be true or false")
        disable = False
    codex_allow, policy_error = read_codex_policy(skill.path)
    if policy_error:
        result.errors.append(policy_error)
    result.claude_auto = not disable
    result.codex_auto = codex_allow
    if result.claude_auto != result.codex_auto:
        result.warnings.append(
            "invocation differs between tools. Invoke-only skills need both "
            "`disable-model-invocation: true` and agents/openai.yaml "
            "`policy: allow_implicit_invocation: false`",
        )
    result.listing_chars = len(name if isinstance(name, str) else "") + len(description)

    line_count = len((skill.path / "SKILL.md").read_text(encoding="utf-8").splitlines())
    if line_count > MAX_SKILL_LINES:
        result.warnings.append(
            f"SKILL.md is {line_count} lines. Keep it under {MAX_SKILL_LINES} and move detail "
            "into references/",
        )
    if not body.strip():
        result.warnings.append("SKILL.md has no instructions after the frontmatter")
    return result


def broken_links(skill: Skill, skill_paths: dict[str, Path]) -> list[str]:
    """
    Return a message for each relative link in the skill's Markdown files whose target doesn't
    exist. A link into another skill (`../other/...`) is checked against that skill wherever it
    lives, because `make sync` puts every skill side by side in the tool folders.
    """
    problems: list[str] = []
    for md_file in sorted(skill.path.rglob("*.md")):
        text = INLINE_CODE.sub("", FENCED_CODE.sub("", md_file.read_text(encoding="utf-8")))
        where = md_file.relative_to(skill.path)
        for target in MARKDOWN_LINK.findall(text):
            if EXTERNAL_LINK.match(target):
                continue
            path = target.split("#", 1)[0]
            if path.startswith("/"):
                problems.append(f"{where}: link `{target}` is absolute. Use a relative path")
                continue
            relative = Path(os.path.normpath(md_file.parent.relative_to(skill.path.parent) / path))
            if relative.parts[:1] == ("..",):
                problems.append(f"{where}: link `{target}` points outside the skills folder")
                continue
            owner = skill_paths.get(relative.parts[0])
            if owner is None or not (owner / Path(*relative.parts[1:])).exists():
                problems.append(f"{where}: link `{target}` points to a file that doesn't exist")
    return problems


SKILL_TEMPLATE = """\
---
name: {name}
description: TODO Say what this skill does and when to use it, in third person. Put the trigger \
words first. Example "Reviews Python diffs for X. Use when the user asks for Y or mentions Z."
{extra_frontmatter}---

# {title}

TODO Instructions. Only include what the agent would not already know.
"""


CODEX_MANUAL_POLICY = "policy:\n  allow_implicit_invocation: false\n"


def create_skill(name: str, source: Path, manual: bool = False) -> Path:
    """
    Create a new skill directory from the template and return its path.

    `manual` makes the skill invoke-only in both tools, so it stays out of their startup listings.
    """
    if not NAME_PATTERN.match(name) or len(name) > MAX_NAME_CHARS:
        raise ValueError(f"invalid skill name: {name}")
    skill_dir = source / name
    if skill_dir.exists():
        raise FileExistsError(f"{skill_dir} already exists")
    skill_dir.mkdir(parents=True)
    title = name.replace("-", " ").capitalize()
    extra = "disable-model-invocation: true\n" if manual else ""
    (skill_dir / "SKILL.md").write_text(
        SKILL_TEMPLATE.format(name=name, title=title, extra_frontmatter=extra),
    )
    if manual:
        (skill_dir / "agents").mkdir()
        (skill_dir / "agents" / "openai.yaml").write_text(CODEX_MANUAL_POLICY)
    return skill_dir


def adopt_skill(name: str, source: Path, targets: list[Target]) -> Path:
    """Move a real skill directory from a target folder into the source folder."""
    candidates = [
        target.root / name
        for target in targets
        if (target.root / name).is_dir() and not (target.root / name).is_symlink()
    ]
    if not candidates:
        raise FileNotFoundError(f"no real directory named '{name}' in any target folder")
    if len(candidates) > 1:
        raise FileExistsError(
            "found real directories in more than one tool folder. Reconcile them first: "
            + ", ".join(str(path) for path in candidates),
        )
    original = candidates[0]
    if not (original / "SKILL.md").is_file():
        raise FileNotFoundError(f"{original} has no SKILL.md")
    dest = source / name
    if dest.exists():
        raise FileExistsError(f"{dest} already exists")
    source.mkdir(parents=True, exist_ok=True)
    shutil.move(str(original), str(dest))
    return dest


def invocation_mode(skill: Skill) -> str:
    """Return `auto`, `manual`, or `mixed` for how the tools may invoke the skill."""
    result = validate_skill(skill)
    if result.claude_auto and result.codex_auto:
        return "auto"
    if not result.claude_auto and not result.codex_auto:
        return "manual"
    return "mixed"


def entry_state(skill: Skill, target: Target) -> str:
    """Describe how one skill appears in one target folder."""
    dest = target.root / skill.name
    if dest.is_symlink():
        return "linked" if real(dest) == real(skill.path) else "other-link"
    if dest.exists():
        return "real-dir"
    return "missing"


def cmd_status(
    skills: list[Skill],
    targets: list[Target],
    sources: list[Path],
    global_dir: Path,
    global_paths: GlobalPaths,
) -> int:
    """Print each skill's link state per tool, unmanaged entries, and global file states."""
    width = max([len(skill.name) for skill in skills] + [5])
    print(f"{'skill':<{width}}  {'mode':<7} " + "  ".join(f"{t.tool:<10}" for t in targets))
    for skill in skills:
        states = "  ".join(f"{entry_state(skill, t):<10}" for t in targets)
        print(f"{skill.name:<{width}}  {invocation_mode(skill):<7} {states}")
    names = {skill.name for skill in skills}
    for target in targets:
        if not target.root.is_dir():
            continue
        others = [
            entry.name
            for entry in sorted(target.root.iterdir())
            if entry.name not in names
            and entry.name not in RESERVED_ENTRIES
            and not entry.name.startswith(".")
            and not is_managed(entry, sources)
        ]
        if others:
            print(f"\nNot managed by this repo in {target.root}: {', '.join(others)}")
    files, errors = build_files(global_dir, global_paths)
    if files or errors:
        print("\nGlobal instruction files:")
    for error in errors:
        print(f"  ERROR {error}")
    for file in files:
        print(f"  {file_state(file):<10} {file.path}  (from {file.source})")
    print("\nHooks:")
    for hook_file in default_hook_files():
        print(f"  {hook_state(hook_file):<10} {hook_file.path}")
    return 0


def cmd_link(
    skills: list[Skill],
    targets: list[Target],
    sources: list[Path],
    dry_run: bool,
    prune_stale: bool,
) -> int:
    """Link every skill into every target, optionally pruning stale links first."""
    prefix = "[dry run] " if dry_run else ""
    if prune_stale:
        for entry in prune(skills, targets, sources, dry_run):
            print(f"{prefix}removed stale link {entry}")
    skipped = 0
    for skill in skills:
        for target in targets:
            outcome = link_skill(skill, target, sources, dry_run)
            if outcome.startswith("SKIPPED"):
                skipped += 1
            if outcome != "ok":
                print(f"{prefix}{target.tool:<6} {skill.name}: {outcome}")
    print(f"{prefix}{len(skills)} skills, {len(targets)} targets, {skipped} skipped")
    return 1 if skipped else 0


def readme_missing_skills(readme_text: str, skills: list[Skill], repo_root: Path) -> list[str]:
    """
    Return the names of this repo's skills that the README's "## Skills" section doesn't mention
    as `name`. Skills from other source folders (for example a work repo) are not checked.
    """
    match = README_SKILLS_SECTION.search(readme_text)
    section = match.group(1) if match else ""
    return [
        skill.name
        for skill in skills
        if real(skill.path).is_relative_to(real(repo_root)) and f"`{skill.name}`" not in section
    ]


def listing_report(results: list[ValidationResult]) -> tuple[int, int, bool]:
    """Return (automatic skill count, listing characters, over the warning threshold)."""
    automatic = [result for result in results if result.claude_auto or result.codex_auto]
    chars = sum(result.listing_chars for result in automatic)
    return len(automatic), chars, chars > LISTING_BUDGET_CHARS * LISTING_WARN_FRACTION


def cmd_validate(
    skills: list[Skill],
    global_dir: Path,
    global_paths: GlobalPaths,
    readme_path: Path,
) -> int:
    """
    Validate skills and global/, check the README lists every skill, report the automatic listing
    size, and return 1 on errors.
    """
    results = [validate_skill(skill) for skill in skills]
    skill_paths = {skill.name: skill.path for skill in skills}
    for result in results:
        result.errors.extend(broken_links(result.skill, skill_paths))
    readme_text = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
    for name in readme_missing_skills(readme_text, skills, REPO_ROOT):
        print(f"README.md\n  warning  `{name}` is missing from the Skills section")
    error_count = 0
    files, global_errors = build_files(global_dir, global_paths)
    if global_errors or size_warnings(files, global_paths):
        print("global/")
    for error in global_errors:
        print(f"  ERROR    {error}")
    for warning in size_warnings(files, global_paths):
        print(f"  warning  {warning}")
    error_count += len(global_errors)
    for result in results:
        if not result.errors and not result.warnings:
            continue
        print(result.skill.name)
        for error in result.errors:
            print(f"  ERROR    {error}")
        for warning in result.warnings:
            print(f"  warning  {warning}")
        error_count += len(result.errors)
    automatic, chars, over = listing_report(results)
    print(
        f"{len(skills)} skills checked, {error_count} errors. {automatic} automatic skills use "
        f"{chars:,} of {LISTING_BUDGET_CHARS:,} listing characters",
    )
    if over:
        print(
            f"warning  automatic skills use over {LISTING_WARN_FRACTION:.0%} of the listing budget. "
            "Make workflow skills invoke-only, or shorten descriptions",
        )
    return 1 if error_count else 0


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        action="append",
        type=Path,
        help="folder of skill directories (repeatable). The first is where new skills go",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="show link state for each skill")
    sub.add_parser(
        "check-global",
        help="show whether the global files exist and print any that sync would skip",
    )
    for name, help_text in (
        ("link", "link every skill into Claude Code and Codex"),
        ("sync", "remove stale links, link every skill, generate the global files, and install hooks"),
        ("unlink", "remove every link and hook this repo created"),
    ):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("--dry-run", action="store_true")
        if name == "sync":
            command.add_argument(
                "--force",
                action="store_true",
                help="overwrite global files that were edited by hand or not generated here, "
                "after backing them up",
            )
    sub.add_parser("validate", help="check skills against the spec and best practices")
    new = sub.add_parser("new", help="create a skill from the template")
    new.add_argument("name")
    new.add_argument(
        "--manual",
        action="store_true",
        help="make the skill invoke-only in both tools",
    )
    adopt = sub.add_parser("adopt", help="move a real skill directory into the repo and link it")
    adopt.add_argument("name")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""
    args = build_parser().parse_args(argv)
    sources = [path.expanduser().absolute() for path in (args.source or [DEFAULT_SOURCE])]
    targets = default_targets()
    global_paths = default_global_paths()

    if args.command == "new":
        path = create_skill(args.name, sources[0], manual=args.manual)
        print(f"created {path / 'SKILL.md'}. Fill it in, then run `make validate sync`")
        return 0
    if args.command == "adopt":
        path = adopt_skill(args.name, sources[0], targets)
        print(f"moved into {path}")
        skills, _ = find_skills(sources)
        return cmd_link(
            [skill for skill in skills if skill.name == args.name],
            targets,
            sources,
            dry_run=False,
            prune_stale=False,
        )

    skills, errors = find_skills(sources)
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if args.command == "check-global":
        for line in check_global(GLOBAL_DIR, global_paths):
            print(line)
        return 0
    if args.command == "status":
        return cmd_status(skills, targets, sources, GLOBAL_DIR, global_paths)
    if args.command == "validate":
        return cmd_validate(skills, GLOBAL_DIR, global_paths, README_PATH) or (1 if errors else 0)
    if args.command == "unlink":
        prefix = "[dry run] " if args.dry_run else ""
        for entry in unlink_all(targets, sources, args.dry_run):
            print(f"{prefix}removed {entry}")
        for line in remove_hooks(default_hook_files(), args.dry_run):
            print(line)
        return 0
    if errors:
        print("Fix the errors above before linking.", file=sys.stderr)
        return 1
    exit_code = cmd_link(skills, targets, sources, args.dry_run, prune_stale=args.command == "sync")
    if args.command == "sync":
        lines, skipped = sync_global(GLOBAL_DIR, global_paths, args.dry_run, args.force)
        hook_lines = sync_hooks(default_hook_files(), args.dry_run)
        skipped += sum("SKIPPED" in line for line in hook_lines)
        for line in lines + hook_lines:
            print(line)
        if skipped:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
