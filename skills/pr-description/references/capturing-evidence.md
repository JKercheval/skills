# Capturing evidence of a change

Tools an agent can use to screenshot or record a change, and how the files reach the pull request. Checked against the tools' docs on 2026-11-02.

## Web UI

- **Claude Code with the Claude in Chrome extension.** Start with `claude --chrome`, or turn on "Enabled by default" with `/chrome`. Ask for a screenshot saved to disk, or for a GIF of a flow; Claude reports the file path. The recording captures everything visible in the tab, including account details on logged-in pages. Needs Chrome or Edge, the extension, and a claude.ai login, not an API key.
- **Playwright CLI, for any agent.** `npm install -g @playwright/cli@latest`, then `playwright-cli install --skills -g` so the agent has the commands as a skill. `playwright-cli open <url>`, `screenshot --filename=<path>.png`, and `video-start <path>.webm` ... `video-chapter "<step>"` ... `video-stop` for a recording with a title card per step. Works for Codex as well as Claude Code.
- **Playwright MCP** gives snapshots and screenshots, not video, as of this check.

## Terminal

- A pasted transcript, the command and its output, is usually the clearest evidence for a CLI change.
- **VHS** (charmbracelet) renders a GIF or mp4 from a `.tape` script, so the recording can be rerun. Needs `vhs`, `ttyd`, and `ffmpeg`.

## Attaching to the pull request

- `gh pr create --body-file <file> --attach <path>` uploads each file and replaces a local path referenced in the body (`![alt](<path>)`) with the uploaded URL. Unreferenced attachments go at the end. `gh pr edit --attach` and `gh pr comment --attach` do the same for an open PR. Needs `gh` 2.99.0 or later; not on GitHub Enterprise Server.
- Formats: PNG, JPEG, GIF, WebP, SVG, MP4, MOV, WebM. Limits: 10 MB for images and GIFs; video 10 MB on free plans and 100 MB on paid ones.
- An uploaded file's URL is viewable without logging in, even on a private repository. Don't attach a capture that shows private data.
- Keep captures out of the repository: a gitignored folder the description names.
