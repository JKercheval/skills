"""Tests for skills/my-reflect/scripts/transcript.py, using small synthetic transcripts."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

import transcript as tr


def claude_lines() -> list[str]:
    """A small Claude Code transcript: user text, injected reminder, assistant text, tool use."""
    records = [
        {"type": "user", "timestamp": "2026-09-28T10:00:00Z", "message": {"content": "Fix the bug in slug.py"}},
        {
            "type": "user",
            "timestamp": "2026-09-28T10:00:01Z",
            "message": {"content": "<system-reminder>Injected context.</system-reminder>"},
        },
        {
            "type": "user",
            "timestamp": "2026-09-28T10:00:02Z",
            "message": {"content": "Also <system-reminder>noise</system-reminder>keep this part"},
        },
        {
            "type": "assistant",
            "timestamp": "2026-09-28T10:00:03Z",
            "message": {
                "content": [
                    {"type": "thinking", "thinking": "private reasoning"},
                    {"type": "text", "text": "I'll read the file first."},
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/repo/slug.py"}},
                    {"type": "tool_use", "name": "Skill", "input": {"skill": "tdd", "args": "slugify"}},
                ],
            },
        },
        {
            "type": "user",
            "timestamp": "2026-09-28T10:00:04Z",
            "message": {"content": [{"type": "tool_result", "content": "x" * 5000}]},
        },
        {
            "type": "assistant",
            "isSidechain": True,
            "timestamp": "2026-09-28T10:00:05Z",
            "message": {"content": [{"type": "text", "text": "subagent chatter"}]},
        },
        {"type": "attachment", "timestamp": "2026-09-28T10:00:06Z"},
        "not json",
    ]
    return [record if isinstance(record, str) else json.dumps(record) for record in records]


def codex_lines(cwd: str = "/repo") -> list[str]:
    """A small Codex transcript: session header, injected context, user and assistant messages, tool calls."""

    def message(role: str, text: str, part_type: str) -> dict[str, object]:
        return {
            "type": "response_item",
            "timestamp": "2026-09-28T11:00:00Z",
            "payload": {"type": "message", "role": role, "content": [{"type": part_type, "text": text}]},
        }

    records = [
        {"type": "session_meta", "payload": {"cwd": cwd}},
        message("developer", "<skills_instructions>...</skills_instructions>", "input_text"),
        message("user", "# AGENTS.md instructions\n\n<INSTRUCTIONS>\nglobal rules\n</INSTRUCTIONS>", "input_text"),
        message("user", "# AGENTS.md instructions for /repo\n\n<INSTRUCTIONS>\nrepo rules\n</INSTRUCTIONS>", "input_text"),
        message("user", "<environment_context>\n<cwd>/repo</cwd>\n</environment_context>", "input_text"),
        message("user", "<recommended_plugins>\nDropbox\n</recommended_plugins>", "input_text"),
        message("user", "What could commit abc123 break?", "input_text"),
        message("assistant", "I'll use the my-blast-radius skill.", "output_text"),
        {
            "type": "response_item",
            "timestamp": "2026-09-28T11:00:01Z",
            "payload": {"type": "function_call", "name": "shell", "arguments": json.dumps({"command": ["git", "show", "abc123"]})},
        },
        {
            "type": "response_item",
            "timestamp": "2026-09-28T11:00:02Z",
            "payload": {"type": "custom_tool_call", "name": "exec", "input": "cat SKILL.md\n  && ls"},
        },
        {"type": "response_item", "payload": {"type": "function_call_output", "output": "y" * 5000}},
        {"type": "event_msg", "payload": {"type": "token_count"}},
    ]
    return [json.dumps(record) for record in records]


def test_parse_claude_keeps_conversation_and_one_line_per_tool_call() -> None:
    entries = tr.parse_claude(claude_lines())

    assert [(entry.kind, entry.text) for entry in entries] == [
        ("USER", "Fix the bug in slug.py"),
        ("USER", "Also keep this part"),
        ("ASSISTANT", "I'll read the file first."),
        ("TOOL", "Read: /repo/slug.py"),
        ("TOOL", "Skill: tdd"),
    ]


def test_parse_codex_drops_injected_context_and_tool_output() -> None:
    entries = tr.parse_codex(codex_lines())

    assert [(entry.kind, entry.text) for entry in entries] == [
        ("USER", "What could commit abc123 break?"),
        ("ASSISTANT", "I'll use the my-blast-radius skill."),
        ("TOOL", "shell: git show abc123"),
        ("TOOL", "exec: cat SKILL.md && ls"),
    ]


def test_clean_user_text_keeps_pasted_tags_that_are_not_injected() -> None:
    pasted = "<harness>my pasted config</harness>"

    assert tr.clean_user_text(pasted) == pasted


def test_summarize_tool_truncates_long_details_with_an_ellipsis() -> None:
    summary = tr.summarize_tool("Bash", {"command": "echo " + "a" * 500})

    assert summary.startswith("Bash: echo aaa")
    assert summary.endswith("…")
    assert len(summary) == len("Bash: ") + tr.TOOL_SUMMARY_CHARS + 1


def test_summarize_tool_leaves_short_details_untouched() -> None:
    assert tr.summarize_tool("Bash", {"command": "make test"}) == "Bash: make test"


@pytest.mark.parametrize(
    "command",
    [
        "cd /very/long/path/to/some/repo && make validate",
        "cd '/path with spaces/repo'; make validate",
        'cd "/a/b" && cd sub && make validate',
    ],
)
def test_summarize_tool_strips_leading_cd(command: str) -> None:
    assert tr.summarize_tool("Bash", {"command": command}) == "Bash: make validate"


def test_summarize_tool_extracts_command_from_codex_javascript() -> None:
    js = 'text(await tools.exec_command({cmd:"cd /repo && git show abc123 --stat","max_output_tokens":6000}));'

    assert tr.summarize_tool("exec", js) == "exec: git show abc123 --stat"


def test_summarize_tool_without_known_argument_is_just_the_name() -> None:
    assert tr.summarize_tool("TodoWrite", {"todos": []}) == "TodoWrite"


def test_detect_format() -> None:
    assert tr.detect_format(codex_lines()) == "codex"
    assert tr.detect_format(claude_lines()) == "claude"
    assert tr.detect_format([]) == "claude"


def test_claude_project_dir_replaces_every_non_alphanumeric() -> None:
    folder = tr.claude_project_dir(Path("/Users/me/Application Support/my.repo"), Path("/home/.claude"))

    assert folder == Path("/home/.claude/projects/-Users-me-Application-Support-my-repo")


def write_file(path: Path, lines: list[str], mtime: float) -> Path:
    """Write transcript lines to `path` and set its modification time."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
    os.utime(path, (mtime, mtime))
    return path


def test_find_claude_transcript_picks_newest_in_project_folder(tmp_path: Path) -> None:
    cwd = Path("/work/repo")
    folder = tr.claude_project_dir(cwd, tmp_path)
    now = time.time()
    write_file(folder / "old.jsonl", claude_lines(), now - 100)
    newest = write_file(folder / "new.jsonl", claude_lines(), now)

    assert tr.find_claude_transcript(cwd, tmp_path) == newest
    assert tr.find_claude_transcript(Path("/other"), tmp_path) is None


def test_find_codex_transcript_matches_session_cwd(tmp_path: Path) -> None:
    now = time.time()
    sessions = tmp_path / "sessions" / "2026" / "09" / "28"
    mine = write_file(sessions / "rollout-a.jsonl", codex_lines("/work/repo"), now - 50)
    write_file(sessions / "rollout-b.jsonl", codex_lines("/other/repo"), now)

    assert tr.find_codex_transcript(Path("/work/repo"), tmp_path) == mine
    assert tr.find_codex_transcript(Path("/nowhere"), tmp_path) is None


@pytest.mark.parametrize(("tool", "expected"), [("auto", "codex"), ("claude", "claude"), ("codex", "codex")])
def test_choose_transcript_picks_newest_for_requested_tool(tmp_path: Path, tool: str, expected: str) -> None:
    cwd = Path("/work/repo")
    now = time.time()
    claude_home = tmp_path / "claude"
    codex_home = tmp_path / "codex"
    claude_file = write_file(tr.claude_project_dir(cwd, claude_home) / "s.jsonl", claude_lines(), now - 100)
    codex_file = write_file(codex_home / "sessions" / "rollout-x.jsonl", codex_lines(str(cwd)), now)

    chosen = tr.choose_transcript(cwd, tool, claude_home, codex_home)

    assert chosen == {"claude": claude_file, "codex": codex_file}[expected]


def test_main_writes_condensed_file(tmp_path: Path) -> None:
    source = write_file(tmp_path / "t.jsonl", claude_lines(), time.time())
    out = tmp_path / "out.txt"

    exit_code = tr.main(["--path", str(source), "--out", str(out)])

    text = out.read_text()
    assert exit_code == 0
    assert text.startswith(f"# Condensed claude transcript: {source}\n# 5 entries\n")
    assert "[2026-09-28 10:00] USER: Fix the bug in slug.py" in text
    assert "x" * 100 not in text


def test_main_reports_missing_transcript(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLAUDE_HOME", str(tmp_path / "claude"))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))

    assert tr.main(["--cwd", str(tmp_path)]) == 1


def test_parse_claude_reads_text_parts_and_skips_injected_skill_content() -> None:
    records = [
        {"type": "user", "message": {"content": [{"type": "text", "text": "<system-reminder>x</system-reminder>claude rc"}]}},
        {"type": "user", "isMeta": True, "message": {"content": [{"type": "text", "text": "Base directory for this skill: /s"}]}},
        {"type": "user", "message": {"content": [{"type": "text", "text": "[Request interrupted by user]"}]}},
    ]

    entries = tr.parse_claude([json.dumps(record) for record in records])

    assert [entry.text for entry in entries] == ["claude rc", "[Request interrupted by user]"]


def test_exchanges_pair_each_user_message_with_the_last_reply_before_it() -> None:
    entries = [
        tr.Entry("t1", "USER", "Fix it"),
        tr.Entry("t2", "ASSISTANT", "Looking."),
        tr.Entry("t3", "TOOL", "Read: a.py"),
        tr.Entry("t4", "ASSISTANT", "Fixed, with a dense summary."),
        tr.Entry("t5", "USER", "Not following."),
        tr.Entry("t6", "USER", "Hello?"),
    ]

    assert tr.exchanges(entries) == [
        tr.Exchange("t1", "", "Fix it"),
        tr.Exchange("t5", "Fixed, with a dense summary.", "Not following."),
        tr.Exchange("t6", "", "Hello?"),
    ]


def claude_session(entrypoint: str, text: str) -> list[str]:
    """A Claude Code transcript started from `entrypoint`, with one user message and one reply."""
    records = [
        {"type": "user", "entrypoint": entrypoint, "cwd": "/work/repo", "timestamp": "2026-09-28T10:00:00Z",
         "message": {"content": text}},
        {"type": "assistant", "timestamp": "2026-09-28T10:01:00Z", "message": {"content": [{"type": "text", "text": "Done."}]}},
        {"type": "user", "timestamp": "2026-09-28T10:02:00Z", "message": {"content": "TLDR?"}},
    ]
    return [json.dumps(record) for record in records]


def codex_session(originator: str) -> list[str]:
    """A Codex transcript whose header names `originator`."""
    header = json.loads(codex_lines("/work/repo")[0])
    header["payload"]["originator"] = originator
    return [json.dumps(header), *codex_lines("/work/repo")[1:]]


def test_interactive_sessions_skip_scripted_runs_and_old_sessions(tmp_path: Path) -> None:
    now = time.time()
    claude_home = tmp_path / "claude"
    codex_home = tmp_path / "codex"
    projects = claude_home / "projects" / "-work-repo"
    typed = write_file(projects / "typed.jsonl", claude_session("claude-desktop", "Hi"), now - 10)
    write_file(projects / "scripted.jsonl", claude_session("sdk-cli", "Hi"), now - 10)
    write_file(projects / "old.jsonl", claude_session("cli", "Hi"), now - 90 * 86400)
    write_file(projects / "typed" / "subagents" / "agent.jsonl", claude_session("cli", "Hi"), now - 10)
    sessions = codex_home / "sessions" / "2026" / "09" / "28"
    codex_typed = write_file(sessions / "rollout-a.jsonl", codex_session("codex-tui"), now - 5)
    write_file(sessions / "rollout-b.jsonl", codex_session("codex_exec"), now - 5)

    found = tr.interactive_sessions(now - 30 * 86400, claude_home, codex_home)

    assert found == [typed, codex_typed]


def test_main_since_days_writes_exchanges_from_interactive_sessions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    claude_home = tmp_path / "claude"
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))
    write_file(claude_home / "projects" / "-work-repo" / "s.jsonl", claude_session("cli", "Fix the bug"), time.time())
    out = tmp_path / "out.txt"
    # The fixture's messages are dated 2026-09-28, so pin "now" to that day; with the
    # real clock, the 7-day window would drop them once the fixture is a week old.
    monkeypatch.setattr(tr.time, "time", lambda: datetime(2026, 9, 28, 12, tzinfo=timezone.utc).timestamp())

    assert tr.main(["--since-days", "7", "--out", str(out)]) == 0

    text = out.read_text()
    assert text.startswith("# 1 interactive sessions, 2 user messages\n")
    assert "## claude session in /work/repo (s.jsonl)" in text
    assert "REPLY: Done.\n[2026-09-28 10:02] USER: TLDR?" in text


def test_collect_exchanges_drops_messages_sent_before_the_window(tmp_path: Path) -> None:
    claude_home = tmp_path / "claude"
    lines = claude_session("cli", "Old question")
    old = json.loads(lines[0])
    old["timestamp"] = "2020-01-01T00:00:00Z"
    write_file(claude_home / "projects" / "-work-repo" / "s.jsonl", [json.dumps(old), *lines[1:]], time.time())
    since = datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp()

    text, sessions, messages = tr.collect_exchanges(since, claude_home, tmp_path / "codex")

    assert (sessions, messages) == (1, 1)
    assert "Old question" not in text
    assert "TLDR?" in text


@pytest.mark.parametrize("extra", [["--tool", "codex"], ["--cwd", "/work/repo"], ["--path", "t.jsonl"]])
def test_main_since_days_rejects_options_it_would_ignore(extra: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        tr.main(["--since-days", "7", *extra])

    assert "can't be combined" in capsys.readouterr().err
