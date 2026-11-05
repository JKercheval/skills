---
name: my-unslop
description: Edits or reviews text against the writing rules in the global instructions, removing AI-writing patterns (slogans, inflated wording, filler, hedging, forced structure) while keeping the meaning. Use when the user asks to unslop, de-slop, clean up, tighten, or edit a draft, to review text for AI-writing patterns, or says your own last reply or document didn't follow the writing rules.
license: MIT. Adapted from pstack by Lauren Tan. See sources/pstack-LICENSE.txt in the skills repo
metadata:
  source: "cursor/plugins pstack/skills/unslop @ 12d587d"
---

# Unslop

The rules live in your global instructions, under "How to write". This skill applies them to one text.

1. **Pick the text.** Use the text the user gave or named. If they named none, use your own last reply, or the document you last wrote. When it's your own, the user invoked this because the text broke the rules, so reread "How to write" before anything else.
2. **Scan it** for the patterns those rules and their example pairs rule out. The ones that slip through most:
   - slogans, aphorisms, personified things, and figurative verbs
   - a reply or section whose first sentence is not the answer or the point
   - sentences that don't say the point: they lead up to it with a story, describe it by its effect on someone, or stay vague where the writer knows the specific. Ask what the writer would say if the reader asked "what do you mean?"
   - "it", "this", or "one" where the reader needs the noun
   - the present tense for something that is only proposed
   - vague verbs, inflated words, and "serves as" for "is"
   - "not just X, but Y" and forced groups of three
   - one thing called by several names
   - fragments, dropped articles, and arrow chains
   - narration of your own process or of the text itself ("I verified", "this section covers")
   - em dashes, curly quotes, emoji, and bold that marks nothing essential
   - filler, chatbot phrases, stacked hedges, and closing summaries
3. **Rewrite only what the rules cover.** Keep the meaning and the intended tone, and don't add content.
4. **Return the result.** If the user asked for an edit, or the text is your own, return the edited text. If they asked for a review, or the text is their own writing and they didn't ask you to change it, list each problem with its fix and leave the wording alone.
