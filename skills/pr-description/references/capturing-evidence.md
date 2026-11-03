# Capturing evidence of a change

Tools for screenshots and recordings, and how the files reach the pull request. Checked by running every command on 2026-11-02 with Playwright CLI 1.59 and gh 2.103.

## Default: the Playwright CLI

Use it in Claude Code and in Codex. It runs its own browser from shell commands, needs no login, and shows nothing from the user's own browser sessions.

- Check it is installed with `playwright-cli --help`. If the command is missing, say so in the description rather than skip the screenshot. To install: `npm install -g @playwright/cli@latest`.
- Serve the page over HTTP before opening it: the CLI refuses `file:` URLs, and a screenshot taken after a refused open is a blank page. For a static page, `python3 -m http.server 8765` from the folder that holds it.
- Open: `playwright-cli open http://localhost:8765`.
- To click or type, first run `playwright-cli snapshot`. It writes the page's elements with refs such as `e7` to a file under `.playwright-cli/` and prints that path. Then `playwright-cli click e7` or `playwright-cli fill e6 "<text>"`. The commands take refs, not CSS selectors.
- Screenshot: `playwright-cli screenshot --filename=<path>.png`.
- Recording: `playwright-cli video-start`, then the clicks and typing, then `playwright-cli video-stop --filename=<path>.webm`. The file name goes on `video-stop`; `video-start` takes no arguments.
- To look at a recording, extract frames with `ffmpeg -i <path>.webm -vf fps=5 <folder>/%03d.png` when ffmpeg is installed, and view them.
- When done: `playwright-cli close`, stop the server you started, and delete `.playwright-cli/` from the repository's folder. The CLI writes snapshots and console logs there, and git shows the folder as untracked.
- In Codex, the default sandbox blocks the browser and `git fetch`. Switchboard runs Codex without the sandbox. In a Codex session started by hand, approve the escalation when Codex asks for it.

## Only when a screenshot needs the user's logged-in session: Claude in Chrome

Claude Code only. Start with `claude --chrome`, or turn on "Enabled by default" with `/chrome`. Ask for a screenshot saved to disk, or a GIF of a flow; the reply gives the file path. It drives the user's own Chrome, so a screenshot of a logged-in page shows their account details. Look at it before referencing it.

## Terminal

Paste the command and its output into the description. That is clearer than a recording. When a recording is wanted anyway, VHS (charmbracelet) renders a GIF or mp4 from a `.tape` script. It needs `vhs`, `ttyd`, and `ffmpeg`.

## Where the files go

- `.pr-evidence/<branch>/` in the repository's folder.
- Exclude it from git without changing the repo: `echo '.pr-evidence/' >> "$(git rev-parse --git-path info/exclude)"`. Run it once per repository; its worktrees share the exclude list.
- Leave only the files the description references in that folder. Delete extra recordings, frame sheets, and anything else made while checking.

## Attaching to the pull request

- `gh pr create --title "<title>" --body-file <file> --attach <path>` uploads each file and replaces a local path referenced in the body as `![alt](<path>)` with the uploaded file. Paths in the body resolve against the body file's folder first and the working directory second, so run it from the repository's root folder. `gh pr edit --attach` and `gh pr comment --attach` do the same for an open PR. Up to 50 files per command.
- Needs `gh` 2.99.0 or later (`gh --version`) and write access to the repository. Not available on GitHub Enterprise Server.
- Formats: PNG, JPEG, GIF, WebP, SVG, MP4, MOV, WebM. Limits: 10 MB for images and GIFs; video 10 MB on free plans and 100 MB on paid ones.
- If some uploads fail, the PR is still created with the ones that succeeded, and the command exits non-zero after printing the PR's URL.
- Anyone with the uploaded file's URL can view it without logging in, even on a private repository.
