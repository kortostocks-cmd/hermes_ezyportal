# INVENTARIO Sheet — Stock Count Pattern

## Sheet Reference
- **Sheet ID**: `1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`
- **Tab**: `INVENTARIO`
- **Columns**: A=NOMBRE, B=FOTO, C=STOCK, D=PRECIO

## Stock Count (excluding boxes/fletes)

```python
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

HERMES_HOME = Path("~/.hermes/profiles/ezy_portal_expert").expanduser()
with open(HERMES_HOME / "google_token.json") as f:
    td = json.load(f)

creds = Credentials(token=td["token"], refresh_token=td.get("refresh_token"),
    token_uri=td.get("token_uri"), client_id=td.get("client_id"),
    client_secret=td.get("client_secret"),
    scopes=["https://www.googleapis.com/auth/spreadsheets"])
svc = build("sheets", "v4", credentials=creds)

SID = "1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE"

r = svc.spreadsheets().values().get(
    spreadsheetId=SID, range="INVENTARIO!A1:E200"
).execute()
rows = r.get("values", [])

total_plantas = 0
con_stock = 0
sin_stock = 0
total_qty = 0

for row in rows[1:]:
    if not row or not row[0]:
        continue
    name = row[0]
    if name.startswith(("CG-", "CJ-")) or name.startswith("FLETE"):
        continue
    total_plantas += 1
    try:
        qty = int(row[2]) if len(row) >= 3 and row[2] else 0
    except:
        qty = 0
    if qty > 0:
        con_stock += 1
        total_qty += qty
    else:
        sin_stock += 1

print(f"Total tipos de plantas:      {total_plantas}")
print(f"Con stock (>0):               {con_stock}")
print(f"SIN stock (=0):                {sin_stock}")
print(f"Cantidad total en stock:      {total_qty:,}")
```

## Current values (Jun 29 2026)
- 120 plant types (excl. cajas/fletes)
- 43 con stock
- 77 sin stock
- 4,479 unidades totales