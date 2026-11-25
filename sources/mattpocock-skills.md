# mattpocock/skills

- Repo: https://github.com/mattpocock/skills
- Skills path: `skills/`, in five folders: `engineering/` and `productivity/` (the ones his plugin ships), `in-progress/` (beta), `misc/` (rarely used), and `deprecated/` (empty at this commit).
- Author: Matt Pocock. Built for Claude Code, with Codex metadata beside every skill. Examples are in TypeScript. MIT license.
- Last reviewed commit: `6f7f7831a625f040a8e06a0e7954826b87ce775a` (2026-11-25, "Merge pull request #1485 from mattpocock/glossary-bold-terms")
- Last reviewed on: 2026-11-25

## How the repo is built

- One flow runs through most of the engineering skills: an interview (`grilling`), a spec (`to-spec`), tickets (`to-tickets`), a build (`implement` or `implement-spec`), a review (`code-review`), a PR body (`pr`), and a look back (`retro`). The flow reads and writes an issue tracker, which `setup-matt-pocock-skills` configures once per repo. Our plan flow (`my-implementation-plan`, its review, its execute skill, and the review skills) covers the same ground with plan files instead of tickets.
- Skills reach each other with "Call the Skill tool with X". That only works for skills the model may invoke. Our skills link each other's files by relative path, because Claude Code blocks invoking an invoke-only skill.
- Many skills read a per-repo `GLOSSARY.md` (domain terms, each with the synonyms to avoid) and `docs/adr/` (short decision records). `domain-modeling` writes both.
- Every skill that starts a subagent says to start it with a fresh context window, because Codex gives a subagent a copy of the parent conversation by default. Tested here on 2026-11-25 with Codex 0.170.0: a subagent started with no such instruction had the parent's messages in its session file and repeated a code word from them. With "start it with a fresh context window" in the request, Codex passed `fork_turns: none` and the subagent had only its own prompt.

## Decisions

The first review recommended the decisions below. They are `undecided` until the user confirms each one.

| Upstream skill | Recommendation | Reason | Decision | Local name |
|---|---|---|---|---|
| diagnosing-bugs | port | A method for bugs whose cause isn't known: build one command that fails on this bug before forming any theory, shrink the reproduction, rank three to five testable hypotheses, change one thing at a time, tag debug logs so they can be removed, and add the regression test where it exercises the real failure. We have only the eight bullets in `fix-root-causes.md`, and `my-tdd` covers bugs with a cheap test path. Drop the glossary line and make the examples language-neutral | undecided | |
| writing-for-agents | adapt | Rules for text an agent follows (skills, `AGENTS.md`, saved prompts): delete an instruction that doesn't change what the agent does by default, say what to do instead of what not to do, end each step with a condition the agent can check, keep each fact in one place, and don't restate what one command would show. Our `AGENTS.md` covers skill mechanics, not these. Rewrite in plain words and drop the coined vocabulary ("context load", "leading word", "sediment") and the router-skill section | undecided | |
| grilling (with its wrappers grill-me and grill-with-docs) | adapt | An interview that settles open decisions before a plan: ask every question that can be answered now in one numbered round, each with a recommended answer worded so "yes" accepts it, hold back questions that depend on an open one, look up facts instead of asking for them, and don't act until the user confirms nothing is assumed. Nothing here runs that interview. Invoke-only, with a plain name and no emoji | undecided | |
| improve-codebase-architecture | adapt | Surveys a codebase for places where the design causes friction, starting from the files that change most in git history, and rates each candidate. Nothing here looks at a whole codebase. Report in Markdown instead of an HTML page that loads Tailwind and Mermaid from a CDN, use our principle files instead of his vocabulary, and hand the chosen candidate to `my-architect` | undecided | |
| to-questionnaire | adapt, for the work setup | Turns decisions the user can't make alone into a short document for the one person who can, with the most important question first. It writes a file and sends nothing. It fits design docs whose decisions other people own | undecided | |
| prototype | skip for now | A throwaway demo that answers one design question. The logic branch (one HTML file where a non-developer clicks through a state model, with guided scenarios) is the useful part. The UI branch assumes a web app with routes. Any agent can build such a file when asked, so the skill adds rules, not ability | undecided | |
| handoff | skip | Writes a summary so a fresh session can continue. Plan files and Switchboard agents already carry state between sessions here, and each tool compacts its own conversation | undecided | |
| teach | skip | A course workspace kept over many sessions: a mission file, HTML lessons, quizzes, and learning records. It solves a different problem from `my-teach`, which explains code in conversation and rules out quizzes. Revisit if the user wants to study a new subject over weeks | undecided | |
| tdd | skip, borrow three points | `my-tdd` already covers the loop. See the borrow table for the points worth taking | undecided | |
| code-review | skip | Two reviewers, one checking coding standards and a fixed list of twelve code smells, one checking the diff against the spec. `my-review-code` and `my-review-adversarial` cover the first, and `my-review-pre-pr` checks the branch against the plan. A fixed smell list is the checklist `my-review-code` says not to be | undecided | |
| pr | skip, borrow one point | `my-pr-description` covers the body. See the borrow table | undecided | |
| retro | skip, borrow one point | `my-reflect` covers lessons from a session. See the borrow table | undecided | |
| codebase-design | skip, borrow one point | A fixed vocabulary for module design ("depth", "seam", "leverage") with a rule to use those words and no others. `minimize-reader-load.md`, `design-it-twice.md`, and `my-architect` hold the same ideas in plain words. See the borrow table | undecided | |
| domain-modeling | skip | Maintains `GLOSSARY.md` and decision records during design talks. It is a per-project convention more than a skill. Worth trying in one project where agents keep renaming things before deciding anything here | undecided | |
| to-spec | skip | Writes a spec from the conversation and publishes it to the issue tracker with a label. `my-implementation-plan` is our version, and it doesn't post anywhere | undecided | |
| to-tickets | skip, borrow one point | Splits a spec into tickets on the issue tracker. See the borrow table for its slicing rule | undecided | |
| implement | skip | Six lines that chain `tdd`, `code-review`, and a commit. `my-implementation-plan-execute` does this with a stop after each milestone | undecided | |
| implement-spec | skip | Runs one implementer subagent per ticket in its own worktree, plus a merger subagent, and may open a draft PR. Switchboard is how the user runs several agents, and opening a PR needs the user's say | undecided | |
| wayfinder | skip | Plans a very large effort as decision tickets on an issue tracker, with labels and assignees. `my-project-plan` and the orchestrator's plan mode cover large efforts without a tracker | undecided | |
| triage | skip | Moves incoming issues through labels, posts comments, and closes issues. It acts on a tracker on its own, and the user's repos don't get a stream of outside issues | undecided | |
| research | skip | Three lines: a background agent researches from primary sources and writes a cited file. The orchestrator already briefs research agents | undecided | |
| wizard | skip | Generates a bash script that walks a person through steps only they can do, such as creating credentials, and writes the values to `.env` and GitHub secrets. Well made, and the agent never sees the secrets, but the need is rare here. Revisit when setting up a service with many secrets | undecided | |
| ask-matt | skip | A guide to which of his skills to use when. The Workflows section of our README does this job | undecided | |
| setup-matt-pocock-skills | skip | Configures a repo's issue tracker and labels for his flow | undecided | |
| wait-what | skip | One line asking the agent to explain its last message again. `my-unslop` with no text does this | undecided | |
| chief-of-staff (beta) | skip | Delegates work to subagents and keeps a dated wiki. `my-switchboard-orchestrator` covers delegation in far more detail | undecided | |
| claude-handoff (beta) | skip | Starts a background Claude Code session from a summary. Claude Code only | undecided | |
| loop-me (beta) | skip | Interviews the user about recurring routines and writes a spec for automating each | undecided | |
| software-factory (beta) | skip | Vocabulary for designing a system of agents on remote machines triggered by tickets and schedules. Not how the user runs agents | undecided | |
| setup-ts-deep-modules (beta) | skip | TypeScript only | undecided | |
| writing-fragments, writing-beats, writing-shape (beta) | skip | Three skills for writing an article: collect raw notes, then build the piece one paragraph at a time. Revisit if the user starts writing long articles with an agent | undecided | |
| git-guardrails-claude-code | skip | A Claude Code hook that blocks `git push`, `git reset --hard`, and similar by matching text in the command. It blocks every push, which conflicts with pushing after each commit, and it does nothing in Codex | undecided | |
| setup-pre-commit | skip | Husky and Prettier for JavaScript repos | undecided | |
| migrate-to-shoehorn | skip | TypeScript test library | undecided | |
| scaffold-exercises | skip | Scaffolding for his course repos | undecided | |

## Ideas to borrow into existing skills

Each is a small edit to a file we already have. None is applied.

| Idea | From | Where it would go | Decision |
|---|---|---|---|
| Tell every subagent to start with a fresh context. `delegate-to-subagents.md` says a subagent "starts with nothing but its brief", which the test above shows is false in Codex unless the request asks for it. A reviewer that has read the main agent's whole conversation is not independent, and it pays to reread that conversation | the repo's `CLAUDE.md` | `my-engineering-principles/references/delegate-to-subagents.md` | undecided |
| Look for instructions to remove, not only to add: a line in a loaded skill or rules file that changed nothing in the session, or that the session shows is out of date. Also look for a check that exists but nothing runs | retro | `my-reflect/references/lenses.md` | undecided |
| A test whose expected value is computed with the same formula as the code can never disagree with the code. Our file names `f(x) == f(x)` but not this case | tdd | `my-engineering-principles/references/test-behavior-not-implementation.md` | undecided |
| Replace only what the code doesn't own with a fake: outside services, time, and randomness. Don't fake the project's own modules | tdd (`mocking.md`) | the same file | undecided |
| For a new feature, write one test, make it pass, then write the next. Tests written all at once describe behavior nobody has seen yet | tdd | `my-tdd` | undecided |
| The deletion test: imagine removing a module. If its complexity disappears, it only passed calls through. If the complexity reappears in every caller, it earns its place | codebase-design | `my-engineering-principles/references/minimize-reader-load.md` | undecided |
| Prefer milestones that each make one behavior work end to end over milestones that each finish one layer, so each can be run and checked. The exception is one mechanical change with callers everywhere: add the new form beside the old, move callers in batches, then delete the old form | to-tickets | `my-implementation-plan` | undecided |
| Say whether a merge can be cheaply undone. A migration, a deletion, or a published interface cannot | pr | `my-pr-description`, under Notes for the reviewer | undecided |
