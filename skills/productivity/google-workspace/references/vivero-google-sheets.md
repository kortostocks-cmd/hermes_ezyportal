# Vivero Google Sheets — Specialized Skill

Skill: `vivero-google-sheets` (productivity/vivero-google-sheets)

Purpose: Dedicated wrapper for the vivero Google Sheet (`1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`) with automated OAuth and simple CLI for the `plantas_nuevas` tab (41 plants, PL-* codes, COST_HACIENDA/COST_SARA price lists).

## Why a separate skill?

- Profile-scoped token management (uses `~/.hermes/profiles/ezy_portal_expert/google_token.json`)
- Fixed sheet ID and tab name — no config needed
- Simpler CLI than generic `google_api.py` (read/append/write/add-sheet only)
- Delegates OAuth to `google-workspace` skill's `setup.py` but with correct profile HERMES_HOME

## Quick Commands

```bash
VSETUP="python ~/.hermes/profiles/ezy_portal_expert/skills/productivity/vivero-google-sheets/scripts/setup.py"
VAPI="python ~/.hermes/profiles/ezy_portal_expert/skills/productivity/vivero-google-sheets/scripts/sheets_api.py"

$VSETUP --check              # Verify auth
$VAPI read plantas_nuevas    # Read all plants
$VAPI append plantas_nuevas '[["PL-NEW","NEW","COST_HACIENDA","10","","Desc"]]'
```

## OAuth Note

Uses Desktop app OAuth client (`installed` type). **Redirect URI must be `http://localhost` (no port)** — fixed in `google-workspace/scripts/setup.py` (line 62). If user gets "redirect_uri_mismatch" or "bad request", verify their Google Cloud Console OAuth client is "Desktop app" type and has `http://localhost` in authorized redirects (auto-added by Google for Desktop apps).

## Related

- Main skill: `google-workspace` (generic Gmail/Calendar/Drive/Sheets)
- This skill: `vivero-google-sheets` (vivero-specific, profile-scoped)