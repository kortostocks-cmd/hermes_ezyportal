# Spell Discovery — Session Log

## 2026-06-24

### lumos — VERIFIED OK (not rebuilt from scratch)
- Script still missing on disk; verified manually via execute_code
- **Critical bug found**: previous comparison used `stockTotal` (does NOT exist) → `itemStockTotal` (correct)
- This caused a false "44 stock mismatches" report — everything was actually in sync
- Manual verification workflow used:
  1. curl portal items page 1+2 with `X-Api-Key: ten_VUIZ7CfBTQ3x02H4MhDrFnRjXDRFPGlBYHYCUL6et3g`
  2. `google_api.py sheets get` to read sheet
  3. Python compare with `normalize()` matching
- Result: 121 portal, 121 sheet rows, 0 stock mismatches
- One stale row cleared: `APIO POTE 140" PROMOCION HASTA 14 DE JUNIO`
  - Cleared via: `sheets update Sheet1!A14:D14 --values '[["","","",""]]'`
- lumos needs script rebuilt for production use (not ad-hoc execute_code)

### alohomora — PARTIAL (pending Airtable PAT)
- Partial script written to `/tmp/alohomora.py` — NOT complete
- Missing: Airtable PAT (user's `pat...` key, starts with `pat`)
- Table IDs confirmed from Airtable URL pattern `tbl...`:
  - Items: `tblTXfSmRyVPV6Tv1`
  - BusinessPartners: `tblXKTjY4kjgnPdTb`
- Backup_date format: ISO `YYYY-MM-DD`
- Command: `alohomora update` (manual, no cron)

### Key API finding this session
- Portal item stock field: `itemStockTotal` — NOT `stockTotal`
- `stockTotal` key does not exist in the API response and returns None silently