---
name: review-followup
description: Drafts a prompt the user can hand to another agent for a follow-up review of a plan or code, listing what to read, what's already decided and why, what changed since the last review, and where to focus. Use when the user invokes /review-followup or $review-followup.
disable-model-invocation: true
---

# Draft a follow-up review prompt

Draft a prompt the user will give to another agent to review a plan or code. Don't review anything yourself, and don't change any files. The deliverable is the prompt, as one block the user can copy.

If the user said what should be reviewed or where to focus, after the skill name or in the conversation, use that. Otherwise take both from this conversation, and ask if it's unclear.

## What the prompt contains

1. **The review to run.** If one of the user's review skills fits, name it at the top of the block, with the file's absolute path, so the reviewer gets the full review method: the reviewer's user starts their message with `/<name>` in Claude Code or `$<name>` in Codex and pastes the rest of the block after it.
   - `implementation-plan-review`: a plan for code changes.
   - `project-plan-review`: a plan for any other project.
   - `review-code`: a code change.
   - `review-pre-pr`: a whole branch before a pull request.

   If none fits, or the reviewer won't have these skills (a chat app, for example), say what kind of review you want in plain words instead.
2. **What to read:** the exact files the reviewer needs for full context, each as an absolute path. The reviewer may run in another tool or folder, where a relative path points nowhere.
3. **What changed since the last review,** if there was one: what changed and why, so the reviewer can check the fixes.
4. **What's decided, and why.** Closed decisions the reviewer should not re-raise, each with a brief reason, so the reviewer understands why it was decided, not just that it was. Include findings from earlier reviews that were rejected, with the reason. Include tradeoffs that were accepted, so the reviewer doesn't rediscover and re-argue them.
5. **Where to focus:** the open questions, risks, or areas where you're least confident and a fresh perspective would help most. For each, say what kind of feedback you want, for example "Is this the right boundary?", "Are edge cases missing?", or "Will this actually work with the tool?". Always include: flag anything the plan or code is silent on that would block whoever does the work.

## Guidelines for the prompt

- The reviewer has no context from this conversation. It has to understand the goal, the constraints, and the current state from the files plus your framing. Define any term or label coined in this conversation.
- Be specific about what good feedback looks like. "Review for quality" gets vague feedback.
- Don't ask the reviewer to validate decisions already made. Point it at where you're least confident.
