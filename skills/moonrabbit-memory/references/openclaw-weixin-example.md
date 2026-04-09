# OpenClaw WeChat Example

This file gives one concrete mapping for OpenClaw + WeChat.

## Suggested Contact Key

```text
openclaw-weixin:<from_user_id>
```

## Suggested Local Storage Path

```text
~/.openclaw/workspace/memory/moonrabbit/contacts/
```

One file per contact is usually the simplest starting point:

```text
~/.openclaw/workspace/memory/moonrabbit/contacts/openclaw-weixin__o9cq808BMatKAKKxzXaO7DY8uVDU@im.wechat.json
```

## Suggested Lookup Order

For each inbound WeChat message:

1. Build the stable contact key from the technical sender ID.
2. Load that contact's memory file if it exists.
3. Apply stop-reply state first.
4. Apply explicit mode override second.
5. Apply automatic MoonRabbit routing next.
6. After the reply, update compressed memory only if the conversation added something durable.

## Suggested Stop / Wake Behavior

- If the contact sends a stop phrase, move to `pending_stop_confirm`.
- After confirmation and passphrase agreement, move to `muted_waiting_wake`.
- When the wake phrase arrives from the same contact key, switch back to `active`.
