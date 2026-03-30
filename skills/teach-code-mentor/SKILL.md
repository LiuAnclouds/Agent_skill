---
name: teach-code-mentor
description: Structured code-teaching skill for coursework, algorithm implementations, local repositories, and assignment code. Use when the user wants code explained step by step, grouped by execution flow or data flow, with complete code blocks, function-by-function explanations, validation guidance, or a tutorial-style document. Trigger for requests like "逐步讲代码", "按运行流程解释", "把这个实现写成教程", "教我从 0 理解这段作业代码", or when turning an implementation into learning-oriented notes.
---

# Teach Code Mentor

## Overview

Explain code as a teaching artifact, not just a summary. Prefer Chinese explanation, keep code identifiers in English, organize explanation by actual execution path, and make the result suitable for coursework or self-study.

Read [references/tutorial-structure.md](references/tutorial-structure.md) before drafting a long tutorial. Read [references/code-teaching-patterns.md](references/code-teaching-patterns.md) when choosing how much detail, contrast, and validation guidance to include.

## Workflow

1. Read the target code, likely entrypoints, and relevant tests before explaining anything.
2. Reconstruct the real runtime path:
   - Where execution starts
   - Which helpers are on the main path
   - How data changes shape at each step
   - Which functions are supporting only, or not on the hot path
3. Split the explanation into runtime-meaningful chunks instead of visually arbitrary chunks.
4. For each chunk, include:
   - What problem this chunk solves
   - The complete code block for that chunk
   - Control-flow explanation
   - Data-flow explanation
   - Why the code is written this way
   - Common mistakes or misconceptions
5. End with:
   - An overall execution-flow summary
   - Concrete validation commands
   - Platform caveats if relevant

## Output Style

- Default to Chinese prose with English code identifiers.
- Prefer execution-order explanation over visual-order explanation.
- Prefer complete code blocks for each teaching chunk over tiny fragmented snippets.
- When the code is optimized, explain the current implementation first; mention simpler alternatives only if they clarify motivation or tradeoffs.
- Distinguish clearly:
  - What the code explicitly does
  - What is an inference about design intent
  - What is a platform/tooling limitation rather than a code bug

## Validation Guidance

- Always provide exact commands when the user asks how to run or verify code.
- If tests behave differently across operating systems, call that out explicitly.
- Prefer repo-local truth:
  - actual test files
  - actual entrypoints
  - actual environment constraints
- Do not claim a test is broken unless you can point to the concrete platform or dependency reason.

## Resource Usage

- Use `references/tutorial-structure.md` for the stable tutorial template.
- Use `references/code-teaching-patterns.md` for teaching heuristics, especially when explaining optimized code, assignment code, or platform-specific test behavior.
