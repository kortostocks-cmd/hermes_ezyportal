# UOM Box/Units Pattern (vivero tenant)

## Pattern: Box of N Units

**Use case:** Products sold by box (CAJA) containing N individual units (EA).

### Item Creation Payload

```json
{
  "itemCode": "PL-MI-PRODUCTO",
  "name": "Mi Producto Caja 1000",
  "itemType": "stock",
  "baseUom": "EA",
  "itemGroupId": "b38e9a2d-4951-4d40-9fa3-1357ef0dc631",
  "itemClassId": "b65da4ee-1f20-45f7-b329-d2b884c7c10d",
  "initialUOMs": [
    { "factor": 1, "uomCode": "EA", "isDefaultSales": true },
    { "factor": 1000, "uomCode": "CAJA", "isDefaultPurchase": true }
  ],
  "prices": [
    { "priceListCode": "SALE_SUPER", "uom": "CAJA", "price": 90, "currencyCode": "PAB" }
  ],
  "priceListCode": "SALE_SUPER
}
```

### Key Points

| Field | Value | Meaning |
|-------|-------|---------|
| `baseUom` | `EA` | Base unit = each individual unit |
| `factor: 1` (EA) | 1 | 1 EA = 1 base unit |
| `factor: 1000` (CAJA) | 1000 | 1 CAJA = 1000 EA |
| `isDefaultSales: true` (EA) | — | Sell by individual unit |
| `isDefaultPurchase: true` (CAJA) | — | Purchase by box |
| `price.uom: "CAJA"` | — | Price is PER BOX |

### Conversion Logic

- **Stock tracking:** Always in **base UOM** (not necessarily EA!)
  - If `baseUom=EA`: stock=1000 means 1000 EA
  - If `baseUom=BOX`: stock=2 means 2 BOX = 2000 EA (factor 1000)
  - If `baseUom=BOX`: stock=2 means 2 BOX = 810 EA (factor 405)
- **Purchase order:** 1 CAJA received → +1000 EA in stock (if baseUom=EA) OR +1 BOX in stock (if baseUom=BOX)
- **Sales order:** 1 EA sold → -1 EA from stock
- **Price display:** $90/CAJA = $0.09/EA (auto-calculated if needed)
- **OnOrder tracking:** Also in baseUom units (`itemOnOrderTotal`)

### Critical: baseUom Inconsistency (List vs Detail)

**Observed bug (2026-06-19):** `CJ-CAJA-POTE-120` shows different `baseUom` in list vs detail:
- List (`/api/items/items?expand=prices`): `baseUom=EA`, `uoms=None`
- Detail (`/api/items/items/by-code/...`): `baseUom=BOX`, `uoms=[EA:1, BOX:1000]`

**Rule:** Always use **detail endpoint** (`by-code` or `/{id}`) for accurate `baseUom` and UOM factors. List view may have stale/incorrect `baseUom`.

### Stock Adjustment — Portal UI Only

**`/internal/items/{id}/stock` endpoint is NOT an API** — serves React frontend HTML:
- `GET` → 200 with HTML (React app)
- `PUT`/`POST` → 405 Not Allowed

**To adjust stock:** Portal UI → Inventory → Stock Adjustment (Ajuste de Stock)
- Type: Entrada/Salida
- Quantity in **baseUom units** (e.g., 1 BOX for `CJ-CAJA-POTE-120`)
- Reason: "Corrección recepción", "Ajuste inventario", etc.

### Real Example (2026-06-19)

Created: `PL-DEMO-CAJA-1000` — "DEMO CAJA 1000 UNIDADES"
- UOMs created: EA (factor 1), CAJA (factor 1000)
- Price: 90 PAB on CAJA (SALE_SUPER)
- Result: HTTP 207 (price not linked — SALE_SUPER price list missing in Portal UI)

### Requirements

1. UOM codes (EA, CAJA) must exist in a UOM Group or be creatable
2. Price list (SALE_SUPER) must exist in Portal UI before price links
3. `initialUOMs` array in create request handles both UOMs at once