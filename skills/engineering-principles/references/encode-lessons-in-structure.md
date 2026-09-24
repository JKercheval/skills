# Encode lessons in structure

When the same correction comes up a second time, turn it into a mechanism (a lint rule, a type, a check, a script) instead of another written instruction.

**Why:** Written instructions depend on someone noticing, remembering, and complying. A mechanism enforces the rule without cooperation.

1. When you catch yourself writing the same instruction twice, ask whether it could be a lint rule, a type constraint, a runtime check, a test, or a script.
2. If it can, build that and delete the instruction.
3. If it needs judgment, make the instruction more prominent and add an example of the mistake.

**Choose the strongest mechanism that fits,** roughly in this order: a type that makes the mistake impossible to write, then a lint rule or test that fails CI, then a shared helper, then a runtime check. People and agents copy what the surrounding code already does, so a weak guard becomes the next template.

**Close the loop.** When a correction happens, decide whether it's a one-off or a pattern, and either apply the fix now or record a concrete follow-up. "I'll keep that in mind" doesn't persist.
