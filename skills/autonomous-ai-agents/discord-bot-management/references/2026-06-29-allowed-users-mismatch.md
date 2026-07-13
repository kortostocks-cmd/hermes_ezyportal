# Session Notes — DISCORD_ALLOWED_USERS Mismatch (2026-06-29)

**Profile**: `ezy_portal_expert`
**Bot**: `hermes_ezy#4822` (App ID: `1516446271055855856`)
**User**: Korto (Discord User ID: `1516171714424471595`)

## Failure pattern

Bot connected successfully (`gateway_state.json: connected`, logs: `Connected as HERMES_EZY#4822`) but did **not** respond to DMs from the authorized user.

## Root cause

`.env` had:
```bash
DISCORD_ALLOWED_USERS=1516446271055855856
```

This is the **bot's Application ID** (decoded from the first segment of the bot token: `MTUxNjQ0NjI3MTA1NTg1NTg1Ng` → base64 → `1516446271055855856`).

But `DISCORD_ALLOWED_USERS` must contain the **human user's Discord ID** (`1516171714424471595` for Korto).

## Why this happens

- Discord bot tokens are formatted: `<base64_app_id>.<random_suffix>`
- The first segment is the Application ID base64-encoded
- Users often confuse "bot ID" with "my user ID"
- The skill's diagnostic checklist (§5, item 3) mentions this but it's easy to miss

## Fix

```bash
# In .env, replace with YOUR Discord user ID (right-click name in Discord → Copy User ID)
DISCORD_ALLOWED_USERS=1516171714424471595
hermes gateway restart --profile ezy_portal_expert
```

## Verification

Decode bot token App ID for reference:
```python
import base64
token_part = 'MTUxNjQ0NjI3MTA1NTg1NTg1Ng'
token_part += '=' * (-len(token_part) % 4)
print(base64.b64decode(token_part).decode())  # → 1516446271055855856
```

## Lesson for future sessions

When bot is `connected` but silent:
1. Check `DISCORD_ALLOWED_USERS` in `.env` — must be **human user ID**, not bot App ID
2. Get user ID: Discord → Settings → Advanced → Developer Mode → right-click user → Copy User ID
3. The bot token's first segment is a RED HERRING for this config