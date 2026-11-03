---
name: teach
description: Teaches a change, subsystem, or concept so the user actually understands it, rather than summarizing it. Gathers facts with the user's how and why skills, starts from a plain definition, gives the smallest complete answer first, and builds diagrams up one piece at a time, going deeper as the user asks. Use when the user invokes /teach or $teach.
disable-model-invocation: true
---

# Teach

Explain what a thing is, how it works, and why it's built that way, at the user's pace. The goal is that they understand it, not that anything changes.

What to teach is what the user typed after the skill name, or else what the conversation is about.

## 1. Decide what they should walk away with

Pick the few things the user should understand by the end. Judge them from why they're asking (about to change it, reviewing it, debugging it, new to it) and what they already know, both read from the conversation. Don't quiz them to find out. Skip what they plainly already know, and put the depth where their question is.

## 2. Gather the facts

Read the code yourself to get oriented. Then follow two of the user's skills: [how](../how/SKILL.md) for how it works, and [why](../why/SKILL.md) for why it's that way. Read each file and follow it, resolving its relative links from its own folder. Size this to the question: both for a subsystem, maybe only one for a small change. Keep the `why` search narrow (git history and a source or two) unless the reasons are the point of the question.

Reword freely for teaching, with one exception: keep `why`'s confidence wording intact. Its hedges are findings, not style.

## 3. Explain

- **Start with a plain definition.** Name the thing and say what it is in general terms, the way a senior engineer would say it out loud, with its common name if it has one. Then tie it to the case at hand ("here, we use it to ...") and build from there: how it works, the deeper reasons, the edge cases.
- **Explain so it clicks:** the problem each part solves, and how it actually works. When it helps, walk through what happens as the user does the thing ("when you open a long chat..."). Listing functions and constants is reference material, not teaching.
- **Give the smallest complete answer first,** a sentence or two, then stop. Add layers when the user asks.
- **Keep it a conversation, not a lecture.** Offer to go deeper or move on, and follow the user's lead. No quizzes, no asking them to repeat it back. Don't announce what's important, hard, or subtle ("this is the tricky part", "the key insight", "the subtle pair"); just say it. When you would pause, stop and let them respond. If there's no live user, deliver it cleanly and put the offer to go deeper at the end.

## 4. Show, and build the picture up

- **Open the diff, the code, or a debugger** when that's the fastest way to make the point.
- **Draw when a picture lands faster than words.** For anything with three or more moving parts, don't draw one diagram with everything in it. Draw a short series, each redrawing the last with one part added, so the user watches the system assemble. To teach a flow from A to B to C: first A to B, then redraw with C added, then add the return path or the next piece. One all-at-once diagram, especially saved for the end, is reference material, not teaching. This applies when there's no live user too: a flowchart with more than three or four boxes should arrive as a series, with the prose between each step.
- **Match the medium to the idea.** Mermaid (or ASCII) suits a flow or structure where the labels carry the meaning. For a spatial idea (layout, overlap, scroll position, before and after), generate an image if an image tool is available, drawn like a whiteboard sketch with a few short labels. A single simple point needs no figure.

## Reply

The reply is the explanation itself, never a report about what you did. Lead with the main point, then what it is, how it works, and why, then the threads worth pulling on next.
