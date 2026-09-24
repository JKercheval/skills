# Script the work

When work is repetitive or needs to be checkable, build the tool that does it or proves it (a script, codemod, generator, or rerunnable check) instead of doing it by hand.

**Why:** A script does the work the same way every time and costs nothing to rerun. It is also something a reviewer can read and rerun, which turns "trust me" into "run this". Hand-made changes can only be verified by redoing them.

- Do the first unit by hand to learn the recipe, then script it. Check the script by rerunning it on that unit and comparing the result.
- Make the script safe to rerun (see [make operations idempotent](make-operations-idempotent.md)).
- A deterministic script beats parallel agents applying the same edit by hand.
- Build the smallest script that does the job, never a framework.
- Keep the script with the change when the work will outlive the session.

**Skip it** when the change is a few obvious edits you can check at a glance.
