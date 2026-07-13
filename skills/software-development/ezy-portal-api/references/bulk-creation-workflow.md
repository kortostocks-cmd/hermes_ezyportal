# Bulk Item Creation from Google Sheets (Jun 30 2026 update)

## Context
Adding plants from the `plantas_nuevas` sheet tab to the vivero EZY Portal.
Sheet ID: `1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`
Tab: `plantas_nuevas`
Columns: CODIGO, NOMBRE, LISTA_PRECIO, PRECIO_USD, STOCK, DESCRIPCION

## Pre-creation duplicate check (MANDATORY)

Always run this before POSTing items. ~50% of sheet items may already exist in the portal.

```python
# 1. Fetch ALL active portal items (paginate, perPage=100)
# 2. Build lookup dicts:
#    - portal_by_name: {name.upper().strip(): item}
#    - portal_by_norm: {normalize(name): item}  (strip accents, remove non-alphanum)
# 3. For each sheet row, check:
#    a. Exact name match → SKIP (already in portal)
#    b. Normalized name match → SKIP
#    c. Code already in portal → SKIP
# 4. Only CREATE what remains
```

Known vivero duplicate names (Jun 2026):
- ANTORCHA, LIRIO, DRACAENA REFLEXA, CORDILINIA, PALMA ZICA, etc. — all existed
- CALATHEA CEBRINA = existing PL-CALATEA-CELORINA (typo in portal)
- BANDEJA DE HAWORTHIA / (with slash) matched via normalize to PL-BANDEJA-HAWORTHIA

## Price lists in plantas_nuevas (all exist in portal as of Jun 30 2026)

| Sheet list   | Portal list ID                            | Qty |
|--------------|-------------------------------------------|-----|
| COST_HACIENDA| 1be181ec-69d9-4661-bebd-e0a09f8ee851     | 28  |
| COST_SARA    | 607aa5ef-e4a9-4d0b-94dd-6eb04dea83bc     | 26  |
| COST_EDWIN   | 02037417-1ac1-45bb-b3b4-df022ff6085d     | 14  |
| COST_ISMAEL  | 96c2a3fb-380b-41fd-861b-87076ac02bc6     | 11  |
| COST_A&G     | 629c947f-5edf-441d-9a70-e8d571e5b1d8     | 8   |
| COST_JARDIN  | ccf36882-505b-420f-89f3-07273f024124     | 5   |
| COST_EDUARDO | (does not exist — needs creation)         | 2   |

## ERROR: \"Item class not found\"
If itemGroupId or itemClassId UUIDs are hardcoded and stale, the API returns HTTP 400 with this error. **Always fetch fresh UUIDs before each bulk creation run:**
```python
import subprocess, json
result = subprocess.run(["curl", "-s", "-H", "X-Api-Key: ten_...",
    "https://vivero.ezyts.com/api/items/item-groups?perPage=50"],
    capture_output=True, text=True, timeout=15)
groups = json.loads(result.stdout)
# As of Jun 30 2026: PLANTS=b38e9a2d..., POTES=92335cf2..., FLETES=b2442d2e...

result = subprocess.run(["curl", "-s", "-H", "X-Api-Key: ten_...",
    "https://vivero.ezyts.com/api/items/item-classes?perPage=50"],
    capture_output=True, text=True, timeout=15)
classes = json.loads(result.stdout)
# As of Jun 30 2026: LIVE_PLANT=b65da4ee..., CARGA=4459719d..., POTES=128060d6...
```

Use `curl` via subprocess, NOT Python urllib — newer tenant keys get 401 from urllib even with correct headers.

## POST payload (omit initialUOMs)

```python
payload = {
    "itemCode": "PL-NEW-ITEM",
    "name": "NEW ITEM NAME",
    "description": "New Item.",
    "itemType": "stock",
    "isStock": True,
    "isPurchasable": True,
    "isSellable": True,
    "baseUom": "EA",
    # OMIT: "initialUOMs" — causes chk_uom_code SQL error
    "itemGroupId": GROUP_ID,
    "itemClassId": CLASS_ID,
    "itemCategory": CATEGORY,
    "defaultSalesTaxCategoryId": TAX_ID,
    "defaultPurchaseTaxCategoryId": TAX_ID,
    "prices": [{
        "priceListId": "uuid",
        "priceListCode": "COST_HACIENDA",
        "price": 20.0,
        "currencyCode": "USD"
    }],
}
```

## POST response may omit itemCode
Use `id` field from response, not `itemCode`.

## Google Sheets: write full corrected data, don't patch individual cells
Rewrite the entire range with a full data dump to clear stale formatting.

## Duplicate cleanup in source sheet
Before creating, check for duplicate *names* within the sheet itself. Remove them. In Jun 30 session: 3 duplicates removed (2x CACTUS DE..., 1x SANSEVIERIA R).

## Results from Jun 30 2026 run
- 94 total plants in sheet (after duplicate cleanup)
- 47 already existed in portal (SKIP)
- 47 new to create
- 2 without price list (CAJA BN 90/100 — COST_EDUARDO not in portal)
- 1 with malformed price (CACTUS MIX: "10/20/30")