# Filtering findings

Apply every criterion to every finding. A finding becomes a proposed edit only if it passes all of them.

Keep the list short enough to review. More than about seven proposed edits usually means you aren't filtering hard enough. When cutting, keep the ones more than one lens raised.

- **Durable:** still true in six months, after paths, commit hashes, tool versions, and code have changed.
- **Specific:** broad enough to apply across tasks, precise enough that a future agent recognizes when to use it. Reject platitudes ("write good code") and one-off facts ("this skill's description is 175 characters").
- **Changes a decision:** a future agent would do something differently because of the edit, not just read more text.
- **Existing home first:** propose a new skill only when no existing skill or file is a real home, the pattern recurs, and the topic deserves its own skill.
- **Agreement:** a finding raised by two or more lenses is stronger. A finding from one lens must clear a higher bar on the other criteria.
- **The session used the target:** the edit targets a skill, file, or tool the session actually used. If a skill should have triggered and didn't, propose tuning its description instead.
- **Not already covered:** read the target before accepting. If it already says this clearly and prominently, reject the finding: the problem was following it, not the text. If the guidance exists but is buried or easy to skip, propose moving or rewording it, not adding a second copy.
- **A mechanism beats prose:** if a lint rule, script, check, test, or validator could enforce the lesson, put it in the backlog as that mechanism, not in a skill as text (see [encode lessons in structure](../../engineering-principles/references/encode-lessons-in-structure.md)).

## Examples

Drop, because they go stale:

- "The linter at commit bd91aa7 estimates tokens as characters divided by 4."
- "This skill's description is 175 characters over the limit."

Keep, because they generalize:

- "Put a skill's trigger words first in its description, because both tools shorten descriptions when many skills are installed."
- "Scripts bundled with a skill need their dependencies stated, because the skill folder isn't a Python project."
