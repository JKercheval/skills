---
name: unslop
description: Edits existing text to remove AI-writing patterns (filler, hedging, chatbot phrases, inflated wording, forced structure) and make it plain and specific, keeping the meaning. Use when the user asks to unslop, de-slop, clean up, tighten, or edit a draft, or to make text sound less AI-written or more human.
license: MIT. Adapted from pstack by Lauren Tan. See sources/pstack-LICENSE.txt in the skills repo
metadata:
  source: "cursor/plugins pstack/skills/unslop @ 12d587d"
---

# Unslop

Edit text to remove AI-writing patterns. Keep the meaning and the intended tone.

1. Scan the text for the patterns below.
2. Rewrite what you find. Change only what the patterns cover, and don't add content.
3. If the user asked for an edit, return the edited text. If they asked for a review, list each problem with its fix.

## Content

- **Superficial "-ing" phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...". Delete them, or replace them with the actual point.
- **Vague attributions.** "Experts believe", "some argue". Name the source or delete the claim.
- **Generic conclusions.** "The future looks bright." State the specific plan or fact, or end without one.

## Wording

- **Inflated words.** Use the plain word the reader would use. If a word sounds technical but isn't the real name of anything ("leverage", "facilitate", "robust"), replace it. Established terms are fine: "test harness" and "API surface" name real things.
- **Fancy ways to say "is".** "serves as", "stands as", "boasts". Say "is" or "has".
- **"Not just X, but Y."** State the point directly.
- **Forced groups of three.** Use the natural number of items.
- **Switching synonyms.** Calling one thing by several names. Pick one name and repeat it.
- **False ranges.** "from X to Y" where X and Y aren't on a real scale. List the things directly.
- **Say what it does, not how it feels.** "types that follow your schema" names a feeling. "A column rename fails the build" names a mechanism. If a sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it.
- **Weak verb plus adverb.** "runs quickly" becomes "is fast" or the number. "significantly improves" becomes the measured change.
- **Mannered prose.** Aphorisms, rhetorical fragments, personified code ("the plan holds it"), figurative verbs ("rides along"). Say it literally.

## Structure and punctuation

- **Em dashes and en dashes.** Remove them. Use a period, a comma, a colon, or parentheses.
- **Dense sentences.** If a reader has to backtrack to parse a sentence, split it or drop clauses.
- **Over-compression.** Dropped articles, verbless fragments, arrows, and unexplained abbreviations. "Parser rejects bad date → exit 2, no write" becomes "The parser rejects a bad date, exits with code 2, and writes nothing."
- **Passive voice.** Name the actor: "the loader parses the file". Keep the passive only when the actor is unknown or doesn't matter.
- **Bold overuse.** Don't bold every term.
- **Inline-header lists.** A bold label that restates the line ("**Performance:** Performance improved...") becomes prose. A bold lead-in followed by genuinely new detail is fine.
- **Title Case Headings.** Use sentence case.
- **Decorative emoji** in headings and bullets. Remove them.
- **Curly quotes.** Use straight quotes.

## Tone

- **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Certainly!", "Great question!" Remove them.
- **Sycophancy.** "You're absolutely right!" Respond to the substance.
- **Thinking out loud.** Sentences that record the writer's process, word choices, or self-imposed limits: "'Adopt' was the wrong word", "what follows is only what survived", "I cite it, I do not rebuild it". Delete them, or keep only the result.
- **Filler.** "In order to" becomes "to". "Due to the fact that" becomes "because". "It is important to note that" is deleted.
- **Stacked hedging.** "could potentially possibly" becomes "may". Keep one hedge where the uncertainty is real.
