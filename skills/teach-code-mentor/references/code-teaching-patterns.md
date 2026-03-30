# Code Teaching Patterns

Use these rules when turning implementation code into a learning-oriented explanation.

## 1. Teach the actual code first

If the repository already has a working implementation:

- explain the current implementation first
- only compare against a simpler version when it clarifies motivation
- do not replace the current design in the explanation unless the user asked for an alternative implementation

## 2. Follow execution, not file order

Good teaching order:

```text
entrypoint -> preprocessing -> main loop -> output -> validation
```

Bad teaching order:

```text
top of file -> next function -> next function
```

unless the file order already matches the runtime path.

## 3. Separate three layers of explanation

For important sections, distinguish:

1. What the code explicitly does
2. Why the author likely wrote it that way
3. What would break if it were written differently

## 4. Explain optimized code with contrast

When the code contains performance structures like caches, reverse indices, memoization, or batched updates:

- name the naive version first in one sentence
- state the bottleneck
- show what extra data structure was introduced
- explain how the update becomes local instead of global

Keep this contrast short; do not turn the whole tutorial into a second implementation unless requested.

## 5. Map code back to the assignment or tests

For coursework:

- mention which test or spec requirement this chunk satisfies
- call out tie-breaking rules, serialization format, or platform assumptions that are easy to miss

## 6. Treat platform limitations correctly

If a test or tool behaves differently on Windows, Linux, macOS, CPU, CUDA, or MPS:

- state the exact limitation
- explain whether it is a code bug or an environment constraint
- provide the correct verification path for the user’s platform

## 7. End with action

After a long explanation, end with something usable:

- commands to run
- a suggested implementation order
- a short checklist
- or the next function to study
