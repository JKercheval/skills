"""Tests for scripts/skills.py. Every test works in a temporary directory, never in $HOME."""

from __future__ import annotations

from pathlib import Path

import pytest

import skills as cli
from skills import Skill, Target

VALID_DESCRIPTION = "Reviews Python diffs for type-hint gaps. Use when the user asks for a review."


def write_skill(source: Path, name: str, frontmatter: str | None = None, body: str = "Do X.\n") -> Path:
    """Create a skill directory with a SKILL.md and return the directory."""
    skill_dir = source / name
    skill_dir.mkdir(parents=True)
    if frontmatter is None:
        frontmatter = f"name: {name}\ndescription: {VALID_DESCRIPTION}\n"
    (skill_dir / "SKILL.md").write_text(f"---\n{frontmatter}---\n\n{body}")
    return skill_dir


@pytest.fixture
def source(tmp_path: Path) -> Path:
    path = tmp_path / "repo" / "skills"
    path.mkdir(parents=True)
    return path


@pytest.fixture
def targets(tmp_path: Path) -> list[Target]:
    return [
        Target("claude", tmp_path / "home" / ".claude" / "skills"),
        Target("codex", tmp_path / "home" / ".agents" / "skills"),
    ]


def test_find_skills_returns_skill_directories(source: Path) -> None:
    write_skill(source, "alpha")
    write_skill(source, "beta")
    (source / "notes.md").write_text("not a skill")
    (source / ".hidden").mkdir()

    skills, errors = cli.find_skills([source])

    assert [skill.name for skill in skills] == ["alpha", "beta"]
    assert errors == []


def test_find_skills_reports_directory_without_skill_md(source: Path) -> None:
    (source / "empty").mkdir()

    skills, errors = cli.find_skills([source])

    assert skills == []
    assert len(errors) == 1
    assert "has no SKILL.md" in errors[0]


def test_find_skills_reports_duplicate_names_across_sources(tmp_path: Path, source: Path) -> None:
    other = tmp_path / "clerk" / "skills"
    write_skill(source, "shared")
    write_skill(other, "shared")

    skills, errors = cli.find_skills([source, other])

    assert [skill.path for skill in skills] == [(source / "shared").absolute()]
    assert len(errors) == 1
    assert "duplicate skill name 'shared'" in errors[0]


def test_find_skills_reports_missing_source(tmp_path: Path) -> None:
    skills, errors = cli.find_skills([tmp_path / "nope"])

    assert skills == []
    assert errors == [f"source folder does not exist: {tmp_path / 'nope'}"]


def test_link_creates_symlinks_in_every_target(source: Path, targets: list[Target]) -> None:
    write_skill(source, "alpha")
    skills, _ = cli.find_skills([source])

    exit_code = cli.cmd_link(skills, targets, [source], dry_run=False, prune_stale=False)

    assert exit_code == 0
    for target in targets:
        link = target.root / "alpha"
        assert link.is_symlink()
        assert link.resolve() == (source / "alpha").resolve()


def test_link_is_idempotent(source: Path, targets: list[Target]) -> None:
    write_skill(source, "alpha")
    skills, _ = cli.find_skills([source])
    cli.cmd_link(skills, targets, [source], dry_run=False, prune_stale=False)

    assert cli.link_skill(skills[0], targets[0], [source], dry_run=False) == "ok"


def test_link_dry_run_changes_nothing(source: Path, targets: list[Target]) -> None:
    write_skill(source, "alpha")
    skills, _ = cli.find_skills([source])

    outcome = cli.link_skill(skills[0], targets[0], [source], dry_run=True)

    assert outcome == "linked"
    assert not (targets[0].root / "alpha").exists()


def test_link_never_replaces_real_directory(source: Path, targets: list[Target]) -> None:
    write_skill(source, "alpha")
    real_dir = write_skill(targets[0].root, "alpha", body="original content\n")
    skills, _ = cli.find_skills([source])

    exit_code = cli.cmd_link(skills, targets, [source], dry_run=False, prune_stale=False)

    assert exit_code == 1
    assert not real_dir.is_symlink()
    assert "original content" in (real_dir / "SKILL.md").read_text()
    assert (targets[1].root / "alpha").is_symlink()


def test_link_never_replaces_unmanaged_symlink(tmp_path: Path, source: Path, targets: list[Target]) -> None:
    write_skill(source, "alpha")
    elsewhere = write_skill(tmp_path / "elsewhere", "alpha")
    targets[0].root.mkdir(parents=True)
    (targets[0].root / "alpha").symlink_to(elsewhere)
    skills, _ = cli.find_skills([source])

    outcome = cli.link_skill(skills[0], targets[0], [source], dry_run=False)

    assert outcome.startswith("SKIPPED")
    assert (targets[0].root / "alpha").resolve() == elsewhere.resolve()


def test_link_repairs_managed_symlink_pointing_at_old_location(source: Path, targets: list[Target]) -> None:
    old = write_skill(source, "old-name")
    write_skill(source, "alpha")
    targets[0].root.mkdir(parents=True)
    (targets[0].root / "alpha").symlink_to(old)
    skills, _ = cli.find_skills([source])
    alpha = next(skill for skill in skills if skill.name == "alpha")

    outcome = cli.link_skill(alpha, targets[0], [source], dry_run=False)

    assert outcome == "relinked"
    assert (targets[0].root / "alpha").resolve() == (source / "alpha").resolve()


def test_sync_removes_links_to_deleted_skills(source: Path, targets: list[Target]) -> None:
    write_skill(source, "alpha")
    doomed = write_skill(source, "doomed")
    skills, _ = cli.find_skills([source])
    cli.cmd_link(skills, targets, [source], dry_run=False, prune_stale=False)
    (doomed / "SKILL.md").unlink()
    doomed.rmdir()
    skills, _ = cli.find_skills([source])

    cli.cmd_link(skills, targets, [source], dry_run=False, prune_stale=True)

    for target in targets:
        assert not (target.root / "doomed").is_symlink()
        assert (target.root / "alpha").is_symlink()


def test_prune_leaves_unmanaged_entries(tmp_path: Path, source: Path, targets: list[Target]) -> None:
    targets[0].root.mkdir(parents=True)
    real_dir = write_skill(targets[0].root, "handmade")
    synced = targets[0].root / "synced"
    synced.mkdir()
    foreign = write_skill(tmp_path / "elsewhere", "foreign")
    (targets[0].root / "foreign").symlink_to(foreign)

    removed = cli.prune([], targets, [source], dry_run=False)

    assert removed == []
    assert real_dir.is_dir()
    assert synced.is_dir()
    assert (targets[0].root / "foreign").is_symlink()


def test_unlink_removes_only_managed_links(tmp_path: Path, source: Path, targets: list[Target]) -> None:
    write_skill(source, "alpha")
    skills, _ = cli.find_skills([source])
    cli.cmd_link(skills, targets, [source], dry_run=False, prune_stale=False)
    real_dir = write_skill(targets[0].root, "handmade")

    removed = cli.unlink_all(targets, [source], dry_run=False)

    assert sorted(removed) == sorted(target.root / "alpha" for target in targets)
    assert real_dir.is_dir()
    assert (source / "alpha" / "SKILL.md").is_file()


def test_validate_accepts_good_skill(source: Path) -> None:
    skill = Skill("alpha", write_skill(source, "alpha"))

    result = cli.validate_skill(skill)

    assert result.errors == []
    assert result.warnings == []


@pytest.mark.parametrize(
    ("frontmatter", "expected_error"),
    [
        (f"description: {VALID_DESCRIPTION}\n", "`name` is required"),
        (f"name: other\ndescription: {VALID_DESCRIPTION}\n", "must match the directory name"),
        ("name: alpha\n", "`description` is required"),
        ("name: alpha\ndescription: ''\n", "`description` is required"),
        (f"name: alpha\ndescription: {'x' * 1025}\n", "max 1024"),
        ("name: alpha\ndescription: TODO fill in. Use when needed.\n", "still contains TODO"),
        ("name: alpha\ndescription: Uses <tag> things. Use when needed.\n", "must not contain XML tags"),
        (f"name: alpha\ndescription: {VALID_DESCRIPTION}\ncompatibility: {'x' * 501}\n", "`compatibility`"),
        ("name: alpha\ndescription: [unclosed\n", "not valid YAML"),
    ],
)
def test_validate_reports_spec_errors(source: Path, frontmatter: str, expected_error: str) -> None:
    skill = Skill("alpha", write_skill(source, "alpha", frontmatter=frontmatter))

    result = cli.validate_skill(skill)

    assert any(expected_error in error for error in result.errors), result.errors


@pytest.mark.parametrize("name", ["Bad-Name", "-bad", "bad-", "bad--name", "a" * 65])
def test_validate_rejects_bad_names(source: Path, name: str) -> None:
    skill = Skill(name, write_skill(source, name, frontmatter=f"name: {name}\ndescription: {VALID_DESCRIPTION}\n"))

    result = cli.validate_skill(skill)

    assert result.errors != []


def test_validate_rejects_missing_frontmatter(source: Path) -> None:
    skill_dir = source / "alpha"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# no frontmatter\n")

    result = cli.validate_skill(Skill("alpha", skill_dir))

    assert result.errors == ["SKILL.md must start with a `---` YAML frontmatter block"]


@pytest.mark.parametrize(
    ("description", "expected_warning"),
    [
        ("Deep Research Requires: topic.", "very short"),
        ("Coding guidelines for general (language-agnostic) software development.", "does not say when"),
        ("I can review your Python code. Use when asked for a review.", "third person"),
    ],
)
def test_validate_warns_on_weak_descriptions(source: Path, description: str, expected_warning: str) -> None:
    skill = Skill("alpha", write_skill(source, "alpha", frontmatter=f"name: alpha\ndescription: '{description}'\n"))

    result = cli.validate_skill(skill)

    assert result.errors == []
    assert any(expected_warning in warning for warning in result.warnings), result.warnings


def test_validate_warns_on_long_skill_file(source: Path) -> None:
    skill = Skill("alpha", write_skill(source, "alpha", body="line\n" * 600))

    result = cli.validate_skill(skill)

    assert any("under 500" in warning for warning in result.warnings)


def test_validate_warns_when_claude_listing_is_truncated(source: Path) -> None:
    frontmatter = f"name: alpha\ndescription: {VALID_DESCRIPTION}\nwhen_to_use: {'x' * 1500}\n"
    skill = Skill("alpha", write_skill(source, "alpha", frontmatter=frontmatter))

    result = cli.validate_skill(skill)

    assert any("truncates at 1536" in warning for warning in result.warnings)


def test_create_skill_writes_template_that_fails_validation_until_filled(source: Path) -> None:
    skill_dir = cli.create_skill("my-skill", source)

    result = cli.validate_skill(Skill("my-skill", skill_dir))

    assert (skill_dir / "SKILL.md").read_text().startswith("---\nname: my-skill\n")
    assert any("TODO" in error for error in result.errors)


def test_create_skill_refuses_existing_and_invalid_names(source: Path) -> None:
    write_skill(source, "alpha")

    with pytest.raises(FileExistsError):
        cli.create_skill("alpha", source)
    with pytest.raises(ValueError):
        cli.create_skill("Bad Name", source)


def test_adopt_moves_real_directory_into_source(source: Path, targets: list[Target]) -> None:
    original = write_skill(targets[0].root, "handmade", body="keep me\n")

    dest = cli.adopt_skill("handmade", source, targets)

    assert dest == source / "handmade"
    assert "keep me" in (dest / "SKILL.md").read_text()
    assert not original.exists()


def test_adopt_refuses_when_both_tools_have_real_copies(source: Path, targets: list[Target]) -> None:
    first = write_skill(targets[0].root, "handmade")
    second = write_skill(targets[1].root, "handmade")

    with pytest.raises(FileExistsError):
        cli.adopt_skill("handmade", source, targets)
    assert first.is_dir()
    assert second.is_dir()


def test_adopt_refuses_when_repo_already_has_skill(source: Path, targets: list[Target]) -> None:
    write_skill(source, "handmade")
    original = write_skill(targets[0].root, "handmade")

    with pytest.raises(FileExistsError):
        cli.adopt_skill("handmade", source, targets)
    assert original.is_dir()


def test_main_adopt_then_links_into_every_target(
    monkeypatch: pytest.MonkeyPatch,
    source: Path,
    targets: list[Target],
) -> None:
    monkeypatch.setenv("CLAUDE_SKILLS_DIR", str(targets[0].root))
    monkeypatch.setenv("CODEX_SKILLS_DIR", str(targets[1].root))
    write_skill(targets[0].root, "handmade")

    exit_code = cli.main(["--source", str(source), "adopt", "handmade"])

    assert exit_code == 0
    for target in targets:
        assert (target.root / "handmade").is_symlink()
        assert (target.root / "handmade").resolve() == (source / "handmade").resolve()


def write_codex_policy(skill_dir: Path, content: str) -> None:
    """Write agents/openai.yaml for a skill."""
    (skill_dir / "agents").mkdir(exist_ok=True)
    (skill_dir / "agents" / "openai.yaml").write_text(content)


def test_validate_treats_skill_without_flags_as_automatic_in_both_tools(source: Path) -> None:
    result = cli.validate_skill(Skill("alpha", write_skill(source, "alpha")))

    assert result.claude_auto is True
    assert result.codex_auto is True
    assert result.listing_chars == len("alpha") + len(VALID_DESCRIPTION)


def test_validate_accepts_invoke_only_skill_configured_for_both_tools(source: Path) -> None:
    frontmatter = f"name: alpha\ndescription: {VALID_DESCRIPTION}\ndisable-model-invocation: true\n"
    skill_dir = write_skill(source, "alpha", frontmatter=frontmatter)
    write_codex_policy(skill_dir, "policy:\n  allow_implicit_invocation: false\n")

    result = cli.validate_skill(Skill("alpha", skill_dir))

    assert result.errors == []
    assert result.warnings == []
    assert result.claude_auto is False
    assert result.codex_auto is False
    assert cli.invocation_mode(Skill("alpha", skill_dir)) == "manual"


def test_validate_warns_when_only_claude_is_invoke_only(source: Path) -> None:
    frontmatter = f"name: alpha\ndescription: {VALID_DESCRIPTION}\ndisable-model-invocation: true\n"
    skill_dir = write_skill(source, "alpha", frontmatter=frontmatter)

    result = cli.validate_skill(Skill("alpha", skill_dir))

    assert any("invocation differs between tools" in warning for warning in result.warnings)
    assert cli.invocation_mode(Skill("alpha", skill_dir)) == "mixed"


def test_validate_warns_when_only_codex_is_invoke_only(source: Path) -> None:
    skill_dir = write_skill(source, "alpha")
    write_codex_policy(skill_dir, "policy:\n  allow_implicit_invocation: false\n")

    result = cli.validate_skill(Skill("alpha", skill_dir))

    assert any("invocation differs between tools" in warning for warning in result.warnings)


@pytest.mark.parametrize(
    ("content", "expected_error"),
    [
        ("policy: [unclosed\n", "not valid YAML"),
        ("- a list\n", "must be a YAML mapping"),
        ("policy: nope\n", "`policy` must be a mapping"),
        ("policy:\n  allow_implicit_invocation: maybe\n", "must be true or false"),
    ],
)
def test_validate_reports_bad_codex_policy(source: Path, content: str, expected_error: str) -> None:
    skill_dir = write_skill(source, "alpha")
    write_codex_policy(skill_dir, content)

    result = cli.validate_skill(Skill("alpha", skill_dir))

    assert any(expected_error in error for error in result.errors), result.errors


def test_validate_reports_non_boolean_disable_flag(source: Path) -> None:
    frontmatter = f"name: alpha\ndescription: {VALID_DESCRIPTION}\ndisable-model-invocation: yes please\n"

    result = cli.validate_skill(Skill("alpha", write_skill(source, "alpha", frontmatter=frontmatter)))

    assert "`disable-model-invocation` must be true or false" in result.errors


def test_listing_report_counts_only_automatic_skills(source: Path) -> None:
    auto = cli.validate_skill(Skill("auto-one", write_skill(source, "auto-one")))
    manual_dir = write_skill(
        source,
        "manual-one",
        frontmatter=f"name: manual-one\ndescription: {VALID_DESCRIPTION}\ndisable-model-invocation: true\n",
    )
    write_codex_policy(manual_dir, "policy:\n  allow_implicit_invocation: false\n")
    manual = cli.validate_skill(Skill("manual-one", manual_dir))

    count, chars, over = cli.listing_report([auto, manual])

    assert count == 1
    assert chars == len("auto-one") + len(VALID_DESCRIPTION)
    assert over is False


def test_listing_report_flags_listing_near_budget(source: Path) -> None:
    description = "Handles a task. Use when needed. " + "x" * 950
    results = []
    for index in range(7):
        name = f"skill-{index}"
        skill_dir = write_skill(source, name, frontmatter=f"name: {name}\ndescription: {description}\n")
        results.append(cli.validate_skill(Skill(name, skill_dir)))

    _, chars, over = cli.listing_report(results)

    assert chars > cli.LISTING_BUDGET_CHARS * cli.LISTING_WARN_FRACTION
    assert over is True


def test_create_manual_skill_is_invoke_only_in_both_tools(source: Path) -> None:
    skill_dir = cli.create_skill("my-skill", source, manual=True)

    result = cli.validate_skill(Skill("my-skill", skill_dir))

    assert result.claude_auto is False
    assert result.codex_auto is False
    assert not any("invocation differs" in warning for warning in result.warnings)


README = """# repo

## Skills

| Skill | Mode |
|---|---|
| `alpha` | Automatic |

## Workflows

Mentions `beta` here, outside the Skills section.
"""


def test_readme_missing_skills_reports_skills_absent_from_skills_section(tmp_path: Path) -> None:
    source = tmp_path / "skills"
    skills = [Skill("alpha", write_skill(source, "alpha")), Skill("beta", write_skill(source, "beta"))]

    missing = cli.readme_missing_skills(README, skills, tmp_path)

    assert missing == ["beta"]


def test_readme_missing_skills_ignores_skills_from_other_repos(tmp_path: Path) -> None:
    other = write_skill(tmp_path / "work-repo" / "skills", "gamma")

    missing = cli.readme_missing_skills(README, [Skill("gamma", other)], tmp_path / "repo")

    assert missing == []


def test_readme_missing_skills_without_skills_section_reports_all(tmp_path: Path) -> None:
    skills = [Skill("alpha", write_skill(tmp_path / "skills", "alpha"))]

    missing = cli.readme_missing_skills("# repo\n\nNo sections.\n", skills, tmp_path)

    assert missing == ["alpha"]


def test_broken_links_accepts_links_that_resolve(source: Path) -> None:
    other = write_skill(source, "other")
    (other / "references").mkdir()
    (other / "references" / "guide.md").write_text("Guide.\n")
    body = (
        "Read [the guide](../other/references/guide.md#usage) and [notes](references/notes.md).\n"
        "See [the docs](https://example.com/x.md) and [below](#usage).\n"
    )
    skill_dir = write_skill(source, "alpha", body=body)
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "notes.md").write_text("Back to [the skill](../SKILL.md).\n")
    skills = [Skill("alpha", skill_dir), Skill("other", other)]

    assert cli.broken_links(skills[0], {skill.name: skill.path for skill in skills}) == []


def test_broken_links_finds_links_into_a_skill_in_another_source(tmp_path: Path, source: Path) -> None:
    work = tmp_path / "work"
    other = write_skill(work, "other")
    skill_dir = write_skill(source, "alpha", body="Read [other](../other/SKILL.md).\n")

    assert cli.broken_links(Skill("alpha", skill_dir), {"alpha": skill_dir, "other": other}) == []


@pytest.mark.parametrize(
    ("link", "expected"),
    [
        ("references/missing.md", "doesn't exist"),
        ("../renamed-skill/SKILL.md", "doesn't exist"),
        ("../../outside.md", "outside the skills folder"),
        ("/Users/me/notes.md", "is absolute"),
    ],
)
def test_broken_links_reports_bad_links(source: Path, link: str, expected: str) -> None:
    skill_dir = write_skill(source, "alpha", body=f"Read [this]({link}).\n")

    problems = cli.broken_links(Skill("alpha", skill_dir), {"alpha": skill_dir})

    assert len(problems) == 1
    assert problems[0].startswith(f"SKILL.md: link `{link}`")
    assert expected in problems[0]


def test_broken_links_checks_reference_files_relative_to_their_folder(source: Path) -> None:
    skill_dir = write_skill(source, "alpha")
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "a.md").write_text("See [b](b.md).\n")

    problems = cli.broken_links(Skill("alpha", skill_dir), {"alpha": skill_dir})

    assert problems == ["references/a.md: link `b.md` points to a file that doesn't exist"]


def test_broken_links_ignores_links_in_code(source: Path) -> None:
    body = "Write `[x](missing.md)` like this:\n\n```markdown\n[y](also-missing.md)\n```\n"
    skill_dir = write_skill(source, "alpha", body=body)

    assert cli.broken_links(Skill("alpha", skill_dir), {"alpha": skill_dir}) == []


def test_main_sync_fails_when_global_rules_are_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    source: Path,
    targets: list[Target],
) -> None:
    monkeypatch.setenv("CLAUDE_SKILLS_DIR", str(targets[0].root))
    monkeypatch.setenv("CODEX_SKILLS_DIR", str(targets[1].root))
    monkeypatch.setenv("CLAUDE_HOME", str(tmp_path / "claude"))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))
    global_dir = tmp_path / "global"
    global_dir.mkdir()
    monkeypatch.setattr(cli, "GLOBAL_DIR", global_dir)

    exit_code = cli.main(["--source", str(source), "sync"])

    assert exit_code == 1
