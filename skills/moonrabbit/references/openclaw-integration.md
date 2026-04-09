# OpenClaw Integration Notes

Use this file when MoonRabbit is installed into OpenClaw and especially when the conversation comes from WeChat.

## Recommended Skill Placement

Shared install:

```text
~/.openclaw/skills/moonrabbit/
~/.openclaw/skills/moonrabbit-memory/
```

Workspace-local install is also valid when you want one agent or one workspace to own the behavior:

```text
<workspace>/skills/moonrabbit/
<workspace>/skills/moonrabbit-memory/
```

## Recommended Agent Allowlist

In `~/.openclaw/openclaw.json`, expose the skills explicitly when you want a chat-facing agent to use MoonRabbit:

```json
{
  "agents": {
    "defaults": {
      "skills": ["moonrabbit", "moonrabbit-memory"]
    }
  }
}
```

## WeChat Contact Key Example

For OpenClaw WeChat sessions, use a stable contact key shaped like:

```text
openclaw-weixin:<wechat_user_id>
```

If both a user ID and a visible handle exist, keep both:

- `contact_id`: stable technical ID
- `wechat_id`: visible account / handle if available
- `display_name`: best human-readable display name

## Stop / Wake Mapping

Persist these states per contact:

- `active`
- `pending_stop_confirm`
- `muted_waiting_wake`

Persist one wake passphrase per contact. When the passphrase matches, clear mute state and return control to the normal MoonRabbit router.

## Runtime Storage Suggestion

Do not store live contact data in this repository.

For OpenClaw, prefer a local workspace or state path such as:

```text
~/.openclaw/workspace/memory/moonrabbit/
```

or a shared host path such as:

```text
~/.openclaw/data/moonrabbit/
```

The exact file layout is implementation-specific. The stable requirement is that the contact key remains durable across sessions.
