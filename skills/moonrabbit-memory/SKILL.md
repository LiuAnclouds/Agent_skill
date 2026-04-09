---
name: moonrabbit-memory
description: Companion memory skill for MoonRabbit and other contact-centric chat agents. Use when the agent needs stable per-contact memory, personality summaries, mode preference, mute and wake-passphrase state, and compressed conversation threads across sessions or channels.
license: MIT
---

# MoonRabbit Memory

This is a companion skill, not the main chat persona.

Use it whenever MoonRabbit needs durable memory for a person.

## Core Goal

Maintain a small, structured, retrievable memory for each contact so the chat agent can:

- remember who the person is
- remember what they like
- remember the best conversation openings
- keep relationship boundaries stable
- keep stop-reply and wake-passphrase state stable
- avoid relearning the same person from scratch every session

## Storage Principles

- The repository ships only the rules, schema, and examples.
- Live contact data must be stored locally by the runtime, not committed into this repository.
- Use one stable contact key per person.
- Prefer structured fields over long raw transcripts.
- Store compressed summaries, not everything.
- Never store secrets, sensitive credentials, or unnecessary private details.

## Stable Contact Key

Use this shape:

```text
{channel}:{contact_id}
```

Examples:

- `openclaw-weixin:o9cq808BMatKAKKxzXaO7DY8uVDU@im.wechat`
- `telegram:123456789`
- `discord:2849201920`

If a platform has both a stable technical ID and a human-facing handle, store both.

## Minimum Memory Payload

Keep at least:

- stable contact key
- channel
- platform contact ID
- display name or nickname
- optional platform handle such as WeChat ID
- preferred mode
- relationship boundary
- personality traits
- likes
- dislikes
- taboo topics
- care signals
- icebreaker topics
- recent key threads
- mute state
- wake passphrase
- last updated timestamp

Read `references/contact-memory-schema.md` for a concrete schema example.

## Update Rules

Update the contact memory when:

- a meaningful new preference appears
- the person reveals a stable trait
- a taboo or sensitive topic becomes clear
- a new useful icebreaker appears
- the relationship boundary changes
- stop-reply or wake-passphrase state changes

Do not update memory for trivial noise.

## Compression Rules

For `recent_key_threads`:

- keep 3 to 8 short bullets
- store the theme and why it matters
- keep it retrieval-friendly
- do not store raw full transcripts unless there is a very specific reason

For personality and interest summaries:

- prefer stable patterns over one-off moments
- write short phrases, not essays
- separate evidence from speculation when uncertain

## Relationship Boundary

Use a small controlled set:

- `normal`
- `care`
- `flirt_safe`

Only move into `flirt_safe` when the situation is clearly adult, welcome, and appropriate.

If uncertain, fall back to `normal` or `care`.

## Stop-Reply State Machine

Use this state machine:

- `active`: MoonRabbit can reply normally.
- `pending_stop_confirm`: MoonRabbit is confirming whether the person truly wants silence.
- `muted_waiting_wake`: MoonRabbit should not continue normal replies until the wake passphrase appears.

Required behavior:

1. Detect stop intent.
2. Confirm the intent.
3. Ask for or propose a wake passphrase.
4. Persist both state and wake passphrase.
5. Resume only when the correct passphrase is seen or when the owner explicitly clears the state.

## Safety Interaction

If the main MoonRabbit skill hits the safety red line:

- do not store operational details of harmful requests
- only store the minimum useful signal if necessary, such as a high-level guardrail note
- never turn unsafe content into a reusable preference

## References

Read these only when needed:

- `references/contact-memory-schema.md` for the schema template
- `references/openclaw-weixin-example.md` for a concrete OpenClaw / WeChat mapping
