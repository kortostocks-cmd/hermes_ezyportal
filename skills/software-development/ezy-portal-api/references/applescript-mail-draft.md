# AppleScript Mail Draft — Fallback when cua-driver is unavailable

When cua-driver (computer_use) is not installed or lacks macOS permissions, AppleScript can still control Mail to create draft emails programmatically.

**Limitation**: AppleScript can create drafts and set properties, but cannot auto-send without user interaction.

## Create a draft with subject and body (no recipient)

```bash
osascript -e '
tell application "Mail"
    set theMessage to make new outgoing message with properties {subject:"SUBJECT HERE", content:"BODY TEXT HERE", visible:true}
    activate
end tell
'
```

**Params**:
- `subject` — email subject line
- `content` — plain text body (no HTML formatting via AppleScript)
- `visible:true` — shows the draft window so user can review before sending
- `visible:false` — creates draft silently in background

**To set sender**: add `sender:"abe@refahpharm.com"` to properties (if multiple accounts configured).

**To add recipient programmatically**: AppleScript Mail is limited — best practice is to create the draft visible and let the user fill in the To: field, or use `make new to recipient` before activating.

## Full example with recipient

```bash
osascript -e '
tell application "Mail"
    set theMessage to make new outgoing message with properties {subject:"Vivero Rose — Presentación", content:"Cuerpo del email aqui...", sender:"abe@refahpharm.com", visible:true}
    tell theMessage
        make new to recipient at end of to recipients with properties {address:"cliente@ejemplo.com", name:"Cliente Ejemplo"}
    end tell
    activate
end tell
'
```

## Prerequisites

- Mail.app must be signed in to the sender account
- AppleScript permissions for Mail must be granted (System Settings → Privacy & Security → Automation)
- No cua-driver installation needed — works with vanilla macOS

## When to use this vs cua-driver

| Scenario | Tool |
|----------|------|
| Need to click/interact with existing Mail UI | cua-driver (requires install) |
| Create draft programmatically | AppleScript (always available) |
| macOS permissions not granted for cua-driver | AppleScript fallback |
| Bulk draft creation with personalization | AppleScript in loop |