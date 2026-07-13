# vivero Sheet — plantas_nuevas Tab

## Sheet ID
`1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`

## Adding a new tab (NOT `sheets create`)

`google_api.py sheets create` makes a **new spreadsheet**, not a new tab. Use googleapiclient + batchUpdate:

```python
# write_file to /tmp/add_sheet.py, then run with hermes venv python
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from _hermes_home import get_hermes_home

HERMES_HOME = get_hermes_home()
TOKEN_FILE=*** / "google_token.json"
with open(TOKEN_FILE) as f:
    td = json.load(f)

creds = Credentials(token=td["token"], refresh_token=td.get("refresh_token"),
    token_uri=td.get("token_uri"), client_id=td.get("client_id"),
    client_secret=td.get("client_secret"),
    scopes=["https://www.googleapis.com/auth/spreadsheets"])
svc = build("sheets", "v4", credentials=creds)

result = svc.spreadsheets().batchUpdate(
    spreadsheetId="SHEET_ID",
    body={"requests": [{"addSheet": {"properties": {"title": "TAB_NAME", "index": 3}}}]}
).execute()
print(json.dumps(result, indent=2))
```

## Reading / Writing data in a tab

```python
# write_file to /tmp/read_write.py
svc.spreadsheets().values().get(spreadsheetId="SHEET_ID", range="TAB_NAME!A1:E5").execute()
svc.spreadsheets().values().update(
    spreadsheetId="SHEET_ID", range="TAB_NAME!A1",
    valueInputOption="RAW", body={"values": [["CODIGO","NOMBRE"],["PL-FOO","FOO"]]}
).execute()
```

**Runtime**: `/Users/abrahamkortovich/.hermes/hermes-agent/venv/bin/python3 /tmp/script.py`

## ⚠️ Pitfall: Append safely — read first, then write

**Problem**: `sheets update` with a fixed range (e.g., `plantas_nuevas!A65:E78`) **overwrites** existing rows. This happened Jun 29 2026 — wrote 29 new invoice plants at row 65, overwriting 4 existing plants (PALMA ROJA GRANDE, PALMA ABANICO, PALMA NEUIDAD, WASHMQTONIA). Had to reconstruct entire sheet (97 rows).

**Fix**: Always read first to find the actual last row:
```bash
# 1. Read column A to count rows
GAPI sheets get SHEET_ID "plantas_nuevas!A:A"

# 2. Find first empty row (len + 1 for header)
# 3. Write at that row
GAPI sheets update SHEET_ID "plantas_nuevas!A{next_row}:E{end_row}" --values '[[...]]'
```

Or use Python API `append` method directly (not exposed in `google_api.py` CLI).

## plantas_nuevas content (Jun 29 2026 — after invoice import)

| Row | CODIGO | NOMBRE | LISTA_PRECIO | PRECIO_USD | STOCK |
|-----|--------|--------|--------------|------------|-------|
| 1 | CODIGO | NOMBRE | LISTA_PRECIO | PRECIO_USD | STOCK |
| 2-64 | PL-ANTORCHA...PL-MICKY | 63 original plants | COST_HACIENDA/COST_SARA/COST_JARDIN | various | various |
| 65 | | PALMA ROJA GRANDE | COST_JARDIN | 20 | |
| 66 | | PALMA ABANICO | | 3 | |
| 67 | | PALMA NEUIDAD | | 7 | |
| 68 | | WASHMQTONIA | | 20 | |
| 69-82 | | 14 plants from factura #1590 (KALANCHOE R...POTO) | | 0.80-6.00 | |
| 83-97 | | 15 plants from factura Villero Ismael (BAMBÚ...CACTUS DE...) | | 1.50-30.00 | |

Total: 97 rows (1 header + 96 plants). Columns A, C, E empty for new rows — user completes manually.