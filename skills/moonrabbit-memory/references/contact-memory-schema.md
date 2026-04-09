# Contact Memory Schema

Use this as a minimum JSON-shaped template.

```json
{
  "contact_key": "openclaw-weixin:o9cq808BMatKAKKxzXaO7DY8uVDU@im.wechat",
  "channel": "openclaw-weixin",
  "contact_id": "o9cq808BMatKAKKxzXaO7DY8uVDU@im.wechat",
  "wechat_id": "moon_friend_001",
  "display_name": "小陈",
  "preferred_mode": "active",
  "relationship_boundary": "normal",
  "personality_traits": [
    "回复偏慢但愿意聊",
    "喜欢被温柔接住情绪"
  ],
  "likes": [
    "猫",
    "天气话题",
    "轻松日常分享"
  ],
  "dislikes": [
    "太强的说教感"
  ],
  "taboo_topics": [
    "家庭细节不主动展开"
  ],
  "care_signals": [
    "深夜语气低落时需要柔和回应"
  ],
  "icebreaker_topics": [
    "今天的天气",
    "最近想做的小事",
    "猫猫或可爱表情包"
  ],
  "recent_key_threads": [
    "上周聊过工作压力，对方更接受先共情再分析",
    "提到最近睡得晚，晚安话题容易接住"
  ],
  "mute_state": "active",
  "wake_phrase": "MoonRabbit醒醒",
  "last_updated_at": "2026-04-09T00:00:00Z"
}
```

## Field Notes

- `preferred_mode`: `active` | `rational` | `guiding` | `flirty_safe` | `auto`
- `relationship_boundary`: `normal` | `care` | `flirt_safe`
- `mute_state`: `active` | `pending_stop_confirm` | `muted_waiting_wake`

If a runtime cannot store JSON directly, keep the same conceptual fields in any equivalent format.
