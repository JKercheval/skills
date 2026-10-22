"""Tests for scripts/global_files.py. Every test works in a temporary directory, never in $HOME."""

from __future__ import annotations

from pathlib import Path

import pytest

import global_files as gf
from global_files import GlobalPaths

RULES = "- Always use type hints.\n- Commit in small commits."
STYLE = "The first sentence answers the question."


@pytest.fixture
def paths(tmp_path: Path) -> GlobalPaths:
    return GlobalPaths(
        claude_md=tmp_path / "home" / ".claude" / "CLAUDE.md",
        codex_agents_md=tmp_path / "home" / ".codex" / "AGENTS.md",
    )


def make_global(tmp_path: Path, rules: str | None = RULES, style: str | None = None) -> Path:
    """Create a global/ folder with the given rules.md and style.md contents."""
    global_dir = tmp_path / "repo" / "global"
    global_dir.mkdir(parents=True)
    if rules is not None:
        (global_dir / "rules.md").write_text(rules)
    if style is not None:
        (global_dir / "style.md").write_text(style)
    return global_dir


def test_no_global_folder_generates_nothing(tmp_path: Path, paths: GlobalPaths) -> None:
    files, errors = gf.build_files(tmp_path / "missing", paths)

    assert files == []
    assert errors == []


def test_missing_rules_is_an_error(tmp_path: Path, paths: GlobalPaths) -> None:
    files, errors = gf.build_files(make_global(tmp_path, rules=None), paths)

    assert files == []
    assert errors == ["global/rules.md is missing"]


def test_rules_only_writes_same_text_to_both_tools(tmp_path: Path, paths: GlobalPaths) -> None:
    lines, differences = gf.sync_global(make_global(tmp_path), paths, dry_run=False)

    assert differences == []
    assert len(lines) == 2
    assert paths.claude_md.read_text() == paths.codex_agents_md.read_text()
    assert paths.claude_md.read_text().endswith(f"\n\n{RULES}\n")


def test_style_follows_rules_in_both_tools(tmp_path: Path, paths: GlobalPaths) -> None:
    gf.sync_global(make_global(tmp_path, style=STYLE), paths, dry_run=False)

    for path in (paths.claude_md, paths.codex_agents_md):
        text = path.read_text()
        assert text.endswith(f"\n\n{RULES}\n\n{STYLE}\n")
        assert "(global/rules.md and global/style.md)" in text.splitlines()[0]


def test_empty_style_is_ignored(tmp_path: Path, paths: GlobalPaths) -> None:
    files, errors = gf.build_files(make_global(tmp_path, style="\n\n"), paths)

    assert errors == []
    assert all(file.body == RULES for file in files)
    assert all(file.source == "global/rules.md" for file in files)


def test_generated_file_starts_with_marker_naming_its_source(tmp_path: Path, paths: GlobalPaths) -> None:
    gf.sync_global(make_global(tmp_path), paths, dry_run=False)

    first_line = paths.claude_md.read_text().splitlines()[0]

    assert first_line.startswith("<!-- Generated from the skills repo (global/rules.md).")


# A file generated from RULES, exactly as `make sync` writes it. Files on other machines were
# written in this format, so if it changes they no longer read as generated-and-untouched, and
# every machine's next sync refuses to overwrite them. Change this literal only on purpose.
PINNED_OUTPUT = (
    "<!-- Generated from the skills repo (global/rules.md). Edit it there and run `make sync`. "
    "sha256:c5836ab7d452f2ff5b314adc0826d982c28e1d499e11f5b090b0e890c0a5a6ed -->\n"
    "\n"
    "- Always use type hints.\n"
    "- Commit in small commits.\n"
)


def test_file_in_the_pinned_format_reads_as_up_to_date(tmp_path: Path, paths: GlobalPaths) -> None:
    files, _ = gf.build_files(make_global(tmp_path), paths)
    paths.claude_md.parent.mkdir(parents=True)
    paths.claude_md.write_text(PINNED_OUTPUT)

    assert gf.file_state(files[0]) == "ok"


def test_file_in_the_pinned_format_reads_as_stale_after_a_source_change(
    tmp_path: Path,
    paths: GlobalPaths,
) -> None:
    files, _ = gf.build_files(make_global(tmp_path, rules="- A new rule."), paths)
    paths.claude_md.parent.mkdir(parents=True)
    paths.claude_md.write_text(PINNED_OUTPUT)

    assert gf.file_state(files[0]) == "stale"


def test_sync_is_idempotent(tmp_path: Path, paths: GlobalPaths) -> None:
    global_dir = make_global(tmp_path, style=STYLE)
    gf.sync_global(global_dir, paths, dry_run=False)

    lines, differences = gf.sync_global(global_dir, paths, dry_run=False)

    assert lines == []
    assert differences == []


def test_source_change_updates_untouched_generated_file(tmp_path: Path, paths: GlobalPaths) -> None:
    global_dir = make_global(tmp_path)
    gf.sync_global(global_dir, paths, dry_run=False)
    (global_dir / "rules.md").write_text("- A new rule.")

    lines, differences = gf.sync_global(global_dir, paths, dry_run=False)

    assert differences == []
    assert "- A new rule." in paths.claude_md.read_text()
    assert any("updated" in line for line in lines)


def test_hand_edited_file_is_backed_up_and_replaced(tmp_path: Path, paths: GlobalPaths) -> None:
    global_dir = make_global(tmp_path)
    gf.sync_global(global_dir, paths, dry_run=False)
    paths.claude_md.write_text(paths.claude_md.read_text() + "- Added by /memory.\n")
    (global_dir / "rules.md").write_text("- A new rule.")

    lines, differences = gf.sync_global(global_dir, paths, dry_run=False)

    assert "- A new rule." in paths.claude_md.read_text()
    assert "- Added by /memory." not in paths.claude_md.read_text()
    assert [difference.path for difference in differences] == [paths.claude_md]
    backup = differences[0].backup
    assert backup is not None
    assert "- Added by /memory." in backup.read_text()
    assert "-- Added by /memory." in differences[0].diff
    assert any("replaced (backup:" in line for line in lines)


def test_unmanaged_file_is_backed_up_and_replaced(tmp_path: Path, paths: GlobalPaths) -> None:
    paths.claude_md.parent.mkdir(parents=True)
    paths.claude_md.write_text("- My handwritten rule.\n")

    lines, differences = gf.sync_global(make_global(tmp_path), paths, dry_run=False)

    backups = list(paths.claude_md.parent.glob("CLAUDE.md.bak-*"))
    assert len(backups) == 1
    assert backups[0].read_text() == "- My handwritten rule.\n"
    assert RULES in paths.claude_md.read_text()
    assert [difference.backup for difference in differences] == backups
    assert "-- My handwritten rule." in differences[0].diff


def test_dry_run_reports_a_difference_without_backing_up(tmp_path: Path, paths: GlobalPaths) -> None:
    paths.claude_md.parent.mkdir(parents=True)
    paths.claude_md.write_text("- My handwritten rule.\n")

    lines, differences = gf.sync_global(make_global(tmp_path), paths, dry_run=True)

    assert paths.claude_md.read_text() == "- My handwritten rule.\n"
    assert list(paths.claude_md.parent.glob("CLAUDE.md.bak-*")) == []
    assert len(differences) == 1
    assert differences[0].backup is None


def make_difference(tmp_path: Path) -> gf.Difference:
    """A difference whose backup file exists on disk."""
    backup = tmp_path / "CLAUDE.md.bak-20261022-100000"
    backup.write_text("- Old text.\n")
    return gf.Difference(tmp_path / "CLAUDE.md", backup, ["-- Old text.", "+- New text."])


def test_review_shows_the_diff_and_deletes_the_backup_on_yes(tmp_path: Path) -> None:
    difference = make_difference(tmp_path)
    questions: list[str] = []

    lines = gf.review_differences([difference], interactive=True, ask=lambda q: questions.append(q) or "y")

    assert "-- Old text." in lines
    assert not difference.backup.exists()
    assert len(questions) == 1
    assert any("deleted" in line for line in lines)


def test_review_keeps_the_backup_unless_the_answer_is_yes(tmp_path: Path) -> None:
    difference = make_difference(tmp_path)

    lines = gf.review_differences([difference], interactive=True, ask=lambda q: "")

    assert difference.backup.exists()
    assert any("kept" in line for line in lines)


def test_review_without_a_terminal_keeps_the_backup_and_tells_the_agent(tmp_path: Path) -> None:
    difference = make_difference(tmp_path)

    def never_ask(question: str) -> str:
        raise AssertionError("asked a question without a terminal")

    lines = gf.review_differences([difference], interactive=False, ask=never_ask)

    text = "\n".join(lines)
    assert difference.backup.exists()
    assert "-- Old text." in lines
    assert "Tell the user" in text
    assert str(difference.backup) in text
    assert "sync again" in text


def test_review_of_a_dry_run_shows_the_diff_and_asks_nothing(tmp_path: Path) -> None:
    difference = gf.Difference(tmp_path / "CLAUDE.md", None, ["-- Old text."])

    def never_ask(question: str) -> str:
        raise AssertionError("asked a question during a dry run")

    lines = gf.review_differences([difference], interactive=True, ask=never_ask)

    assert "-- Old text." in lines


def test_dry_run_writes_nothing(tmp_path: Path, paths: GlobalPaths) -> None:
    lines, _ = gf.sync_global(make_global(tmp_path, style=STYLE), paths, dry_run=True)

    assert not paths.claude_md.exists()
    assert not paths.codex_agents_md.exists()
    assert all(line.startswith("[dry run]") for line in lines)


def test_size_warnings_flag_long_files(tmp_path: Path, paths: GlobalPaths) -> None:
    long_rules = "\n".join(f"- Rule number {index} " + "x" * 200 for index in range(210))
    files, _ = gf.build_files(make_global(tmp_path, rules=long_rules), paths)

    warnings = gf.size_warnings(files, paths)

    assert any("CLAUDE.md would be" in warning for warning in warnings)
    assert any("Codex reads only the first" in warning for warning in warnings)


def test_default_paths_honor_tool_home_env_vars(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CLAUDE_HOME", str(tmp_path / "c"))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "x"))

    result = gf.default_global_paths()

    assert result == GlobalPaths(tmp_path / "c" / "CLAUDE.md", tmp_path / "x" / "AGENTS.md")


def test_check_global_reports_missing_files(tmp_path: Path, paths: GlobalPaths) -> None:
    lines = gf.check_global(make_global(tmp_path), paths)

    assert lines == [
        f"{paths.claude_md} {gf.STATE_EXPLANATIONS['missing']}",
        f"{paths.codex_agents_md} {gf.STATE_EXPLANATIONS['missing']}",
    ]


def test_check_global_prints_a_file_this_repo_did_not_write(tmp_path: Path, paths: GlobalPaths) -> None:
    paths.claude_md.parent.mkdir(parents=True)
    paths.claude_md.write_text("# Work notes\n- Use the company VPN.\n")

    lines = gf.check_global(make_global(tmp_path), paths)

    assert lines[0] == f"{paths.claude_md} {gf.STATE_EXPLANATIONS['unmanaged']}"
    assert "- Use the company VPN." in lines
    assert lines[-1] == f"{paths.codex_agents_md} {gf.STATE_EXPLANATIONS['missing']}"


def test_check_global_shows_hand_edits_to_a_generated_file(tmp_path: Path, paths: GlobalPaths) -> None:
    global_dir = make_global(tmp_path)
    gf.sync_global(global_dir, paths, dry_run=False)
    paths.claude_md.write_text(paths.claude_md.read_text() + "- Added by hand.\n")

    lines = gf.check_global(global_dir, paths)

    assert lines[0] == f"{paths.claude_md} {gf.STATE_EXPLANATIONS['edited']}"
    assert "-- Added by hand." in lines
    assert lines[-1] == f"{paths.codex_agents_md} {gf.STATE_EXPLANATIONS['ok']}"


def test_check_global_prints_nothing_extra_for_files_this_repo_wrote(tmp_path: Path, paths: GlobalPaths) -> None:
    global_dir = make_global(tmp_path)
    gf.sync_global(global_dir, paths, dry_run=False)

    lines = gf.check_global(global_dir, paths)

    assert lines == [
        f"{paths.claude_md} {gf.STATE_EXPLANATIONS['ok']}",
        f"{paths.codex_agents_md} {gf.STATE_EXPLANATIONS['ok']}",
    ]
