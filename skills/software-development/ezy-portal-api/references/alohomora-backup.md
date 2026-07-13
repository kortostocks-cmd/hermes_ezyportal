# alohomora — EZY Portal Backup to Airtable

**Base**: `appIQ4f4j6c2bMPlb` ("Vivero Backup")
**Tables**: Items (`tblTXfSmRyVPV6Tv1`), BusinessPartners (`tblXKTjY4kjgnPdTb`)

## Setup (one-time in Airtable UI)

1. Create base "Vivero Backup" at airtable.com
2. In the default table (rename to **Items**): add fields:
   - `itemCode` (single line text)
   - `stock` (number, 0 decimals)
   - `precio` (currency, symbol `$`)
   - `categoria` (single line text)
3. Add second table **BusinessPartners** with fields:
   - `code` (single line text)
   - `roles` (single line text) — stores "customer, vendor" or "unknown"

Airtable base creation via PAT API is NOT supported — must be done in Airtable UI.

## Script

```bash
python3 scripts/alohomora.py <portal_api_key>
```

- Fetches all active items (paginated, `expand=prices`)
- Fetches all active business partners
- Upserts to Airtable by `itemCode` (Items) or `code` (BusinessPartners)
- Airtable batch limit: 10 records per PATCH request
- Rate limit: 5 req/sec per base — 0.25s sleep between batches

## Airtable API Notes

- **PATCH** with `performUpsert` = upsert (create or update by merge field)
- Upsert field: `itemCode` for Items, `code` for BusinessPartners
- Fields not in Airtable table → **422 UNKNOWN_FIELD_NAME** error — add missing fields manually in Airtable UI
- `businessPartners` endpoint in portal may return `[]` — not an error, just no BPs configured yet
- Default Airtable fields (Notes, Assignee, Status, Attachment Summary) are ignored by the script — safe to leave
- **CRITICAL `pageSize` vs `maxRecords`**: `maxRecords` does NOT paginate — always returns `offset=null` after first page. Use `pageSize=100` instead, which returns a proper offset token. With `maxRecords=100`, Airtable returns exactly 100 records but no cursor to fetch the next page. With `pageSize=100`, the response includes `offset=itr...` for continuation. Always use `pageSize` for paginated reads. Affects both list and filterByFormula calls.

## Cron (weekly)

Job ID: `35acdf4398c0` — runs every Sunday at 9:00am (schedule: `0 9 * * 0`)

Run manually:
```bash
/Users/abrahamkortovich/.hermes/hermes-agent/venv/bin/python3 \
  /Users/abrahamkortovich/.hermes/profiles/ezy_portal_expert/skills/software-development/ezy-portal-api/scripts/alohomora.py \
  ten_YrYLEy8rbp6rCujH1emWh2SZBJOtVemuj4YfF0MFu3I
```