# VIVERO.TS.COM — API Quirks & Session Findings

## SSL / Network Access

- **Python sandbox (execute_code) CANNOT reach vivero.ezyts.com** — SSL `CERTIFICATE_VERIFY_FAILED` in both system Python 3.14 and uv-managed 3.11.
  - **Workaround**: Use `terminal()` with `curl` — curl works fine.
  - Alternatively: run scripts via `/Users/abrahamkortovich/.hermes/hermes-agent/venv/bin/python3` from terminal (the venv has its own cert bundle).
  - Do NOT use `urllib.request.urlopen()` in sandboxed Python — it will fail with SSL errors.

## Authentication — Price Masking

- Tenant API key (`X-Api-Key: ten_...`) returns **masked prices** (`prices: []`) even with `expand=prices`.
- This is **not an API bug** — the key lacks authorization group for price data.
- **To read prices**: need **Bearer JWT** from user login session (not tenant key).
  - Could do user login flow to get Bearer token, but hasn't been tested yet.
  - Alternatively: create a different API key in Portal UI with price permissions.
- `itemStockTotal` and `itemAvailableTotal` are **NOT masked** — stock data works fine with tenant key.

## Missing API Modules on vivero.ezyts.com

The following return **404** — these modules don't exist on this tenant:

| Endpoint | Result |
|----------|--------|
| `/api/purchase-orders` | 404 |
| `/api/orders` | 404 |
| `/api/invoices` | 404 |
| `/api/expenses` | 404 |
| `/api/transactions` | 404 |
| `/api/purchases` | 404 |
| `/api/movements` | 404 |

Only **Items** and **Business Partners** are accessible via API on this tenant.

## Sheet Sync Pattern (lumos spell)

The established workflow for `lumos` (sync EZY → Google Sheets):

1. `curl` → fetch all items from `GET /api/items/items?expand=prices&isActive=true&perPage=100&page=N` (2 pages = 122 items)
2. Parse JSON with `python3 -c "import json..."` in terminal (avoids sandbox SSL)
3. Match items to sheet rows by normalized name (remove quotes, parens, extra spaces, dashes)
4. For each match: extract `itemStockTotal` or `itemAvailableTotal`
5. Write to `/tmp/lumos_stock.json`
6. Use `google_api.py` script (venv python) → `batchUpdate` on Sheet1 column C
7. 109 cells updated per run

**Key normalization regex** (in use):
```python
def normalize(s):
    s = s.upper() if s else ''
    s = re.sub(r'["\'\(\)\[\]]', '', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*[-–]\s*', ' ', s)
    return s.strip()
```

## Google Sheets Auth

- `google_api.py` script at: `/Users/abrahamkortovich/.hermes/skills/productivity/google-workspace/scripts/google_api.py`
- Use venv python: `/Users/abrahamkortovich/.hermes/hermes-agent/venv/bin/python3`
- Sheet ID: `1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`
- Sheet columns: A=PLANTA, B=FOTO, C=STOCK, D=PRECIO

## Spells Convention (Session Pattern)

User wants Harry Potter spell keywords to trigger automations:

| Spell | Function |
|-------|----------|
| `lumos` | Sync stock from EZY portal → Google Sheet column C |
| `alohomora` | Planned: track expenses per plant in separate sheet tab (NOT YET BUILT — expenses module doesn't exist in EZY) |

Spell scripts go in `/tmp/` and are invoked from terminal.