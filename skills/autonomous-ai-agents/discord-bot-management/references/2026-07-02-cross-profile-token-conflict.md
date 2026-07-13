# Cross-Profile Token Conflict (2026-07-02)

## Observed scenario

Two Hermes profiles (`default` and `ezy_portal_expert`) shared the same Discord bot token. The `default` profile's gateway started first (PID 595), then `ezy_portal_expert` tried to start and got:

```
gateway_state.json → state: "fatal", error_code: "discord-bot-token_lock"
error_message: "Discord bot token already in use (PID 595). Stop the other gateway first."
```

## Root cause

`gateway_state.json` in `ezy_portal_expert` had been showing `connected` from a previous session, but the process was dead. When attempting a restart, the gateway found the `default` profile's gateway already holding the same token.

## Resolution

1. Stopped the other profile's gateway: `hermes gateway stop --profile default`
2. Started the target profile: `hermes gateway start --profile ezy_portal_expert`
3. After restart, discovered the token itself was actually expired (`Improper token has been passed`)

## Lesson

- Two profiles sharing one token is not allowed — Discord only permits one WebSocket connection per token.
- The `token_lock` error is a **fatal** state, not a retryable one — don't wait for retries, fix the conflict.
- After resolving the conflict, underlying token issues (expired/revoked) may still exist — check the logs.

## User preference

"Un bot por agente" — each agent profile gets its own Discord bot, never share tokens across profiles.