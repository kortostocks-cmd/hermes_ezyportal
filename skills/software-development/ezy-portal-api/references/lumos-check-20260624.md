# lumos — portal stock → Google Sheet sync

## Sheet access

```bash
/Users/abrahamkortovich/.hermes/hermes-agent/venv/bin/python3 \
  /Users/abrahamkortovich/.hermes/profiles/ezy_portal_expert/skills/productivity/google-workspace/scripts/google_api.py \
  sheets get <SHEET_ID> Sheet1!A1:D300
```

NOT via `hermes sheets` (that subcommand doesn't exist on this CLI).

## CRITICAL: Sheet data format

`google_api.py sheets get` returns **JSON array of arrays** — NOT tab-separated. Parse with `json.loads()`:

```python
result = subprocess.run([...google_api.py, "sheets", "get", sheet_id, "Sheet1!A1:D300"], capture_output=True, text=True)
sheet_data = json.loads(result.stdout)  # NOT split('\t')
for row in sheet_data:
    name = row[0]
    photo = row[1] if len(row) > 1 else ''
    stock = row[2] if len(row) > 2 else ''
    price = row[3] if len(row) > 3 else ''
```

## Portal field

Always use `itemStockTotal` (integer). Never use `stockTotal` (does not exist in API response — silently returns `None`).

## Normalize function

Strip accents, uppercase, remove `()[]` and trailing VR/EN POTE/BOLSA/PDB/MCL/VCG/19Z/GEOTEXTIL suffixes.

## Normalize false positive (Jun 25 2026)

Items with same base name but different variants can collide when normalized:
- `"CAJA POTE 120_1000PCS"` → normalizes to `"CAJA POTE"`
- `"CAJA POTE 180_450PCS"` → also normalizes to `"CAJA POTE"`

These are **different items** (different itemCodes). When a mismatch is detected, verify by comparing the full normalized name AND itemCode before flagging as a real desfasado.

## Verification history

| Date | Result |
|------|--------|
| Jun 24 2026 | 121 portal, 121 sheet rows, 0 mismatches. Stale row cleared. |
| Jun 25 2026 | 121 portal, 121 sheet rows, 0 mismatches. Empty row 14 cleared. Normalize false positive on CAJA POTE identified. |

## Script status

NOT on disk — rebuild via execute_code each time or save to `scripts/lumos.py`.