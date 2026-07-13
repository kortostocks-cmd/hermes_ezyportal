# Spell Commands — Vivero EZY Portal

Automations named as Harry Potter spells. Convention: cast by user saying the spell name.

## Spells (Jul 2026)

| Spell | Direction | Trigger | Status |
|-------|-----------|---------|--------|
| **lumos** | portal → Google Sheet | "lumos" | WORKING (via `scripts/lumos.py`) |
| **avada kedavra** | full sheet update (3 tabs) | "avada kedavra" | MANUAL (composed workflow) |
| **stupefy** | sheet → portal | "stupefy" | AD-HOC |
| **alohomora** | portal → Airtable | "alohomora" | MISSING (no working script) |

## lumos (portal → sheet)

Sync portal stock + SALE_EXTRA prices → Google Sheet INVENTARIO tab.

- **Sheet ID**: `1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`
- **Key field**: `itemStockTotal` (NOT `stockTotal`)
- **Run using Hermes venv**:
  ```
  ~/.hermes/hermes-agent/venv/bin/python3 ~/.hermes/profiles/ezy_portal_expert/skills/software-development/ezy-portal-api/scripts/lumos.py
  ```
- **IMPORTANT**: Ensure the Google OAuth token is fresh before running. Re-auth via `--auth-url` → `--auth-code` if needed.
- **After lumos**: always run `check_sheet_gaps.py` to find portal items missing from the sheet.
- **Tierras ordering**: after sync, TIERRA-NEGRA, ABONO-ORGANICO, CASCARILLA-DE-ARROZ must be the LAST rows in INVENTARIO.

## avada kedavra (full 3-tab update)

Updates INVENTARIO, REPORTS, and SOLD_AMOUNT tabs. **Not a single script** — composed of:
1. **lumos** sync (portal stock + prices → INVENTARIO)
2. **Formula recalculation** for REPORTS (margin %, cost ranges)
3. **SOLD_AMOUNT** tab review (trailing space in tab name: `'SOLD_AMOUNT '`)

**Pre-run checklist**:
- Confirm with user first: "¿Corro Avada Kedavra?" — they may say "no metas los costos todavía"
- Review COST_SARACELY column for errors before updating
- Known issues to check/fix:
  - MONSTERA ADANSONII duplicated in REPORTS
  - Range costs (`$0.8-$1`) in REPORTS instead of single values
  - Tierras/abonos with costs in COST_SARACELY (should be empty)
  - SOLD_AMOUNT tab queried with trailing space in name

## stupefy (sheet → portal)

Create/update portal items from Google Sheet rows. No pre-made script — run ad-hoc.

**Full workflow**: See `references/bulk-creation-workflow.md` and main SKILL.md.

## alohomora (portal → Airtable)

Manual backup. Currently no working script on disk.

- **Airtable base**: `appIQ4f4j6c2bMPlb`
- **Tables**: Items + BusinessPartners
- **Run**: `alohomora update` (intentional no-cron — user-initiated)