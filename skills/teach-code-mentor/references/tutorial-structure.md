# Tutorial Structure

Use this structure when the user wants a code walkthrough or tutorial document.

## Recommended Skeleton

1. Title
2. Entry and goal
3. Runtime chunks in execution order
4. End-to-end flow summary
5. Validation commands and platform notes

## Per-Chunk Template

For each chunk, include all of the following unless the code is trivial:

### 1. What problem this chunk solves

State the job of the chunk in one short paragraph.

### 2. Complete code for this chunk

Prefer one complete block copied from the current implementation rather than tiny fragments.

### 3. Control flow

Explain the branch order, loop shape, and when this chunk runs.

### 4. Data flow

Show how the important values change form:

```text
input -> intermediate representation -> output
```

### 5. Why it is written this way

Explain the local design reason:

- correctness
- performance
- stability
- alignment with tests or spec

### 6. Common mistakes

Call out mistakes the learner is likely to make when reimplementing it.

### 7. How it connects to the next chunk

State what this chunk produces for the next stage.

## Global Rules

- Explain code in execution order.
- Prefer concrete examples over abstract prose.
- If a helper exists but is not on the main runtime path, say that explicitly.
- Keep code identifiers in English; explain them in Chinese.
- Do not silently switch to a simpler alternative implementation unless the user asked for a rewrite.
