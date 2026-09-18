# Example 12 — Unrelated question: no false activation

## Setup

The user asks something outside the skill's scope, e.g.:

- "Help me write a quicksort in Python."
- "What is the capital of Mongolia?"
- "Draft my SOP for a U.S. master's application."
- "What is my chance of admission to School X?"

## Expected behavior

The skill does **not** activate. It is scoped to *offer choice* — deciding
which already-received offer to accept for a specific user and goal. It does
not run for:

- admissions-probability prediction;
- application / SOP / CV writing alone;
- general university trivia or ranking questions;
- career planning that does not hinge on a concrete offer decision.

The trigger keywords (`offer selection`, `compare graduate programs`,
`留学选校`, `硕士 offer 对比`, etc.) reflect that scope, and the `description`
explicitly says: "Do not use for admission-chance prediction or application
writing alone."

## What this is NOT

- Not a keyword blacklist. The engine judges *whether offer choice is the
  actual decision*, not whether a magic word appeared. A genuine offer
  comparison framed informally should still activate; an SOP request that
  mentions "offer" in passing should not.

## Lesson

A skill that fires on every prompt is worse than useless. Correct scoping is
part of the product: it stays quiet when it cannot help, so its answers stay
trustworthy when it can.
