# Confidence

How to reason about evidence that is historical, fragmentary, and sometimes contradictory, and how to say it without flattening it into false certainty.

Code doesn't carry its own motivation. The reasons live in commits, pull requests, tickets, docs, and conversations, all of them incomplete and sometimes missing. Pretending otherwise produces confident-sounding guesses that mislead the reader.

## Grades

Every claim in the answer gets one of these grades. The grade decides where the claim goes and how it's worded.

**1. Direct.** Someone wrote down the reason, and you can cite it. Not "the code does X, so the author must have wanted X".

- A PR description: "this fixes the bug where users with more than 1000 items couldn't paginate".
- A ticket: "adding this because the customer requested it in their security review".
- A code comment: "clamp to 100 because the upstream API rejects larger values".
- A design doc: "we chose A over B because we need persistence across restarts".
- A chat message from the author explaining the change.

Wording: plain and confident, with the citation. "This exists because X (PR #123)."

**2. Supported.** Several pieces of indirect evidence agree. No single source states it, but together they make it likely.

- The PR title says "improve performance", the ticket is labeled `perf`, and the surrounding commits all touch the same hot path.
- Tests added with the change all exercise very large inputs.

Wording: confident but visibly derived. "The evidence points strongly to X: [the specific pieces]."

**3. Inferred.** A reasonable reading of the context that nothing states outright. The reader should see it's your interpretation.

- The PR doesn't say why, but the error was happening in production at the time and the fix merged the same day, so it was likely a hotfix.

Wording: hedged, with the chain of reasoning. "Given A and B, C seems likely because D."

**4. Speculative.** Plausible, but the evidence is thin and other explanations fit as well.

- "This might work around a browser bug that has since been fixed, but we found no evidence of that."

Wording: explicitly a guess. "One possibility is X, but there's no direct evidence." It usually belongs under competing hypotheses.

**5. Unknown.** You looked and couldn't find out. This is a valid, useful outcome.

Wording: say exactly what was searched. Not "we couldn't find out", but "we searched the ticket tracker for A and B, read the 6 PRs that touched this file since 2023, and searched the repo for the threshold value. None gave a reason."

## Wording

**Words that claim certainty** need a citation right next to them: "because", "the reason is", "was designed to", "fixes", "the team decided".

**Hedging words** belong to inferences: "appears to", "likely", "suggests", "is consistent with", "one reading is", "may have been".

**Words to avoid:** "obviously" and "clearly" (if it were obvious, nobody would ask), "of course", and a dismissive "just" ("it's just for performance"), which usually hides uncertainty.

## Traps

**Rationalizing.** Code that makes sense today may have been written for reasons that no longer apply, or were wrong at the time. Don't assume the author did the right thing and work backward to justify it. Don't assume a consistent pattern was intentional: it may be copy and paste. Don't turn an absence of evidence into evidence of absence ("nobody mentioned security, so it wasn't a concern").

**Confirming the user's guess.** A question like "why do we do it this way, I assume for performance?" contains a hypothesis. Check it independently. If the evidence supports it, say so with citations. If not, say so and present what the evidence does support.

**Code as evidence of its own intent.** "The function is named X" or "the author chose a functional style" describes the code, not the reason for it.

## Contradictions

When two sources disagree (the ticket says "needed for a customer's compliance requirement", the PR says "cleaning up tech debt"), show both with their citations. Both may be true, or one may be wrong. Don't pick the one that makes a tidier story.

## Missing evidence

An honest "we don't know" tells the reader the answer isn't in the obvious places, and who to ask next. Filling the gap with a confident guess is worse, because the reader will act on it. Name each gap: the question, the sources searched, what you searched for, and what turned up.

## Check before answering

1. Does every Direct or Supported claim have a citation? If not, add one or move the claim to Inferred.
2. Does each claim's wording match its grade? A Direct claim may say "because". An Inferred claim may not.
3. Did you cite the code as evidence for its own intent? Remove it.
4. Did you surface contradictions, or quietly pick one side?
5. If the question contained a guess, did you check it rather than confirm it?
6. Does the answer name what's unknown? Historical questions almost always have gaps. An answer with none is suspicious.
