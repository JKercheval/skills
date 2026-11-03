# Rationale template

The shape of the reply in step 5. About one page, with sentence-case headings. Replace each note with real content, and drop a section only when it genuinely doesn't apply.

## Problem

One paragraph: what we're building, and what about the existing system or its constraints makes the shape non-obvious. Name the constraints from grounding (existing types to work with, callers that can't break, invariants that cross the boundary) so the reader sees what you saw.

## Usage

The caller's view: a README-style snippet and two or three realistic call sites for the chosen design. The shape below is derived from this, and the two must agree.

## Shape

The recommended design. Data structures first, then how data flows through the signatures, with the key types and signatures inline. Name the decisions everything else rests on: which invariants the types encode, where validation happens, and what the design deliberately doesn't do. Say what complexity the public interface hides, what it still exposes, and why it's no larger than it needs to be.

## Why this shape over the other candidates

Which candidate became the base and why, what was borrowed from the others, and what was rejected and why. If the candidates converged, say so.

## Tradeoffs accepted

One bullet per tradeoff, in the form "we accept X in exchange for Y". Include anything a future reader might mistake for an oversight.

## Open questions and risks

What the user needs to decide, and risks worth flagging before implementation. Phrase them as questions, so the user's answer resolves them.

## First implementation step

One sentence: the first thing to build once the design is agreed.
