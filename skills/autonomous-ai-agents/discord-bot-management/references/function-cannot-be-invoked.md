# "Function Cannot Be Invoked" — Model Doesn't Support Tool Use

## Observed pattern

User on Discord DM said "hola", bot replied with **"Function cannot be invoked"** (or similar tool-use rejection). The gateway logs showed `inbound message` → `response ready` (2xx), so the pipeline *ran* — the error came from the LLM model itself, not from Discord.

## Root cause

The profile's `config.yaml` had:

```yaml
model:
  default: nvidia/nemotron-3-ultra-550b-a55b
```

That model **does not support function calling / tool use**. The Hermes gateway passes the system prompt with tool definitions, but Nemotron either can't parse them or rejects them with a generic error like `Function cannot be invoked`.

The error message varies by provider:
- NVIDIA Nemotron series → "Function cannot be invoked"
- Some OpenAI-compatible endpoints → "tool_use not supported" or "tools parameter ignored"
- Some local models → returns text but never calls tools

## Fix

1. Change the profile's default model to one that supports OpenAI-compatible function calling:

```bash
hermes config set model.default "deepseek-ai/deepseek-v4-flash"
```

2. Restart the gateway:

```bash
hermes gateway stop
hermes gateway run --replace   # in background
```

3. Verify: send a DM to the bot. It should respond normally.

## Why this user hit it

The profile was originally set up with Nemotron for CLI chat. When the Discord gateway launched, it inherited the same default model. The CLI chat was switched mid-session to deepseek-v4-flash via the `/model` parameter, but the **config.yaml `model.default`** stayed on Nemotron — so every new gateway session (including the Discord bot) kept loading the wrong model.

## Key lessons

1. `model.default` in config.yaml controls what the **gateway** loads. Per-chat model overrides (`/model` or `--model` flag) only affect that specific CLI session. If you switch models in chat, you must also `hermes config set model.default <new_model>` for the gateway to pick it up.

2. **Stale gateway process**: after changing `model.default` and running `hermes gateway run --replace`, the old background process may still be alive and keep failing with the old model. Always `stop` first, confirm the process is dead, then `start`. Avoid `run --replace` in background mode when switching models — the old process's `notify_on_complete` notification will arrive mid-session and confuse the user with stale errors.

## Prevention

When setting up a Discord bot for a profile:
1. Ensure `model.default` points to a **function-calling-capable** model.
2. Test with a quick curl against the model's API: does it accept `tools` / `functions` in the request body?
3. Document in the skill that Nemotron, older Llama variants, and some API proxies may not support tool use.