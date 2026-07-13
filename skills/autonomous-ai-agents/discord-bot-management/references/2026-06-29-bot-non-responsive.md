# Session Notes — Discord Bot Non-Responsive (2026-06-29)

**Profile**: `ezy_portal_expert`
**App ID**: `1516446271055855856` (`hermes_ezy#4822`)

## Failure pattern

Bot connected successfully (`gateway_state.json: connected`, logs: `Connected as HERMES_EZY#4822`) but did **not** respond to messages.

## Root cause

Discord Developer Portal had **Privileged Gateway Intents disabled** for the `hermes_ezy` application. The Hermes adapter requests `message_content`, `dm_messages`, and `guild_messages` locally, but Discord strips those events server-side unless the intents are enabled in the portal.

## Fix

1. Developer Portal → Application → Bot → Privileged Gateway Intents
2. Enable all three:
   - PRESENCE INTENT
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT
3. Restart gateway.

## Token replacement corruption
When updating `DISCORD_BOT_TOKEN` via regex/replacement strings, using wildcards or truncated values (`*** text produces a mangled token that remains syntactically similar to the real format but is rejected by Discord with `401 Unauthorized` / `Improper token has been passed`.

Always use the **complete** token in the replacement string.

## Shell heredoc / quoting failure
Inline `python3 -c \"...\"` or heredoc-based edits through `terminal()` can fail with shell syntax errors on macOS due to quoting mismatches. **Workaround**: write the edit script to `/tmp/update_discord_token.py`, run it with `python3 /tmp/...`, then `rm` the file.

## Repeated 401 loop
If multiple freshly-provided tokens still return `401 Unauthorized`, the user is likely copying the wrong credential type from the Developer Portal. Remind them:
- **Bot Token** = Application → Bot → Reset Token
- **Client Secret** = OAuth2 → General → Client Secret (wrong source)
- **User Token** = never use these for bot intents

Pre-validation with `curl` (see skill §2) catches this before consuming a restart cycle.

## Secondary observation

`sessions/sessions.json` retained a DM session keyed to the **previous** application ID (`1516454788055961862`, display name `kortobot`). These stale sessions are harmless but confusing during diagnosis. They persist across gateway restarts because the session DB is not cleared on platform changes.

If the user says "olvida todo" or wants a fresh start for a different application, delete `sessions/` to drop stale application-bound sessions.

## Launchd desync

`hermes gateway restart` sometimes leaves `gateway_state.json` at `running` while `launchd` reports `not loaded`. The reliable recovery is:

```bash
hermes gateway stop --profile <profile> || true
hermes gateway start --profile <profile>
```

Output `Could not find service ... reloading service definition` followed by `✓ Service started` is normal bootstrap recovery.
