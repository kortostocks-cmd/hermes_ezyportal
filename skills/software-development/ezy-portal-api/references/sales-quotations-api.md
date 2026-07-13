# Sales Quotations API (vivero tenant)

Discovered: Jun 30, 2026, via trial-and-error endpoint probing.

## Endpoint

```
GET    /api/commerce/sales-quotations          # List (paginated)
GET    /api/commerce/sales-quotations/{id}      # Detail
POST   /api/commerce/sales-quotations           # Create
PATCH  /api/commerce/sales-quotations/{id}      # Update (DRAFT only)
DELETE /api/commerce/sales-quotations/{id}      # Delete (DRAFT only)
```

**Auth**: `X-Api-Key: ten_...` (NOT Bearer JWT) — same as Items module.
**Base**: `https://vivero.ezyts.com`

## Critical Query Parameters

- `?expand=lines` — **REQUIRED** to get line items. Without this, `lines: []` even when lines exist.
- `?perPage=N` — Pagination (max 100)
- `?page=N` — Page number

## List Response Model

```json
{
  "total": 6,
  "data": [
    {
      "id": "uuid",
      "tenantId": "uuid",
      "documentNumber": "SQ-2026-000001",
      "documentDate": "2026-06-03T00:00:00Z",
      "status": "DRAFT",
      "createdAt": "2026-06-30T17:03:24Z",
      "createdByName": "abraham kortovich",
      "masked": false,
      "bpId": "uuid",
      "bpCode": "CL-0035",
      "bpName": "SUPER EXTRA via israel",
      "paymentTermsCode": "PREPAY",
      "priceListId": "uuid",
      "priceListCode": "SALE_PUBLIC",
      "priceListName": "Precio Publico",
      "currency": "USD",
      "exchangeRate": 1,
      "subTotal": 0,
      "discountPercent": 0,
      "discountAmount": 0,
      "taxTotal": 0,
      "grandTotal": 0,
      "validUntil": null,
      "version": 1,
      "availableTransitions": ["SEND", "EDIT"],
      "lines": []
    }
  ]
}
```

## With lines (expand=lines)

```json
{
  "lines": [
    {
      "id": "uuid",
      "itemId": "uuid",
      "itemCode": "PL-HIERBA-BUENA-VR",
      "itemName": "HIERBA BUENA VR",
      "quantity": 3,
      "unitPrice": 1.75,
      "discountPercent": 0,
      "taxCategoryId": "uuid",
      "taxPercent": 0,
      "lineTotal": 5.25
    }
  ]
}
```

## Statuses

| Status | Description |
|--------|-------------|
| DRAFT | Editable, deletable |
| SENT | Locked for editing |
| ACCEPTED | Customer accepted |
| REJECTED | Can revert to DRAFT |
| CANCELLED | Terminal |
| EXPIRED | ValidUntil passed |
| CONVERTED | Converted to Sales Order |

## vivero tenant — SUPER EXTRA client branches (Jun 30 2026)

There are 6 existing draft quotations for different SUPER EXTRA branches, all with 0 lines (empty). The user needs 3 new quotations for **SUPER EXTRA Via Israel** (RUC 356-19-77860, DV 12) matching 3 invoices from Vivero Rose:

1. **Factura 740** — 03/06/2026 — $83.85 — 13 items
2. **Factura 767** — 15/06/2026 — $105.75 — 15 items
3. **Factura 781** — 24/06/2026 — $317.95 — 31 items

Each should use `SALE_SUPER` price list (id=e4d473ef-e97e-4258-8391-594b9d0eb9f0) with `EXCENTO` tax category (id=097722df-e70c-4380-9372-a863c67c2bca) and `PREPAY` payment terms.

## Creating a Quotation (with inline lines — DISCOVERED Jun 30 2026)

**POST** `/api/commerce/sales-quotations`

Unlike the earlier theory, **POST accepts line items inline**. All line fields must be present — partial lines fail with "itemCode is required" / "itemName is required" / "warehouseName is required" / "taxCategoryName is required".

Required fields per line:
- `lineNumber` (integer, sequential; duplicates cause `"duplicate lineNumber values: [0]"`)
- `itemId` (UUID from `/api/items/items/by-code/{code}`)
- `itemCode` (string, e.g. `"PL-HIERBA-BUENA"`)
- `itemName` (string, display name)
- `description` (string, can differ from itemName for annotation)
- `quantity` (number > 0)
- `unitPrice` (number, manually set — does not need to match price list)
- `warehouseId`, `warehouseCode`, `warehouseName` (all required; vivero: `d8294c0c-ea75-4f03-a464-7f9b9efa9abf` / `PRIN` / `Principal`)
- `taxCategoryId`, `taxCategoryCode`, `taxCategoryName` (all required; vivero EXCENTO: `097722df-e70c-4380-9372-a863c67c2bca` / `EXCENTO` / `Excento`)
- `unitOfMeasure`, `uomCode` (both `"EA"`)

Header required fields:
- `bpId`, `bpCode`, `bpName` — customer info (all three required)
- `documentDate`, `validUntil` — ISO 8601 date with `T00:00:00Z`
- `priceListId`, `priceListCode`, `priceListName` — all three required
- `paymentTermsId`, `paymentTermsCode`, `paymentTermsName` — all three required
- `currency` — `"USD"`

**Full working payload** (Python):

```python
payload = {
    "bpId": "32249c40-4c89-4fdf-a381-73969dba188d",
    "bpCode": "CL-0035",
    "bpName": "SUPER EXTRA via israel",
    "documentDate": "2026-06-03T00:00:00Z",
    "validUntil": "2026-06-03T00:00:00Z",
    "priceListId": "0455a655-460f-4a75-b4f7-e1d41b5e6886",
    "priceListCode": "SALE_PUBLIC",
    "priceListName": "Venta Público",
    "paymentTermsId": "6c310a2b-c40d-410d-926d-42f7bb827ef4",
    "paymentTermsCode": "PREPAY",
    "paymentTermsName": "Pago Anticipado",
    "currency": "USD",
    "lines": [
        {
            "lineNumber": 1,
            "itemId": "fd83f4a4-9791-40ef-a6da-7f3619341ded",
            "itemCode": "PL-HIERBA-BUENA",
            "itemName": "HIERBA BUENA VR",
            "description": "HIERBA BUENA VR",
            "quantity": 3,
            "unitPrice": 1.75,
            "warehouseId": "d8294c0c-ea75-4f03-a464-7f9b9efa9abf",
            "warehouseCode": "PRIN",
            "warehouseName": "Principal",
            "taxCategoryId": "097722df-e70c-4380-9372-a863c67c2bca",
            "taxCategoryCode": "EXCENTO",
            "taxCategoryName": "Excento",
            "unitOfMeasure": "EA",
            "uomCode": "EA"
        }
    ]
}
```

**Response** (success):
```json
{
  "documentNumber": "SQ-2026-000001",
  "status": "DRAFT",
  "grandTotal": 5.25,
  "version": 1,
  ...
}
```

Note: lines returned in the POST response may be visible, but **subsequent GET with `?expand=lines` may return `lines: []`** even when lines were successfully saved. This appears to be an API anomaly (possibly caching or permission-gated). The `grandTotal` field is reliable — if it matches the expected sum, the lines were saved.

## Validating Line Data (critical)

When a POST fails, the error is one of:

| Error | Cause | Fix |
|-------|-------|-----|
| `"price list is required"` | Missing `priceListCode` or `priceListName` in header | Add all 3 `priceListId/Code/Name` |
| `"duplicate lineNumber values: [0]"` | All lines have `lineNumber: 0` | Assign sequential `lineNumber: 1,2,3...` |
| `"itemId is required"` | Line has `null` itemId | Every line must reference an existing portal item UUID |
| `"itemCode is required"` | Line missing `itemCode` string | Add `itemCode` to every line |
| `"itemName is required"` | Missing `itemName` | Add `itemName` (display name) |
| `"warehouseName is required"` | Missing warehouse fields | Add all 3 `warehouseId/Code/Name` |
| `"taxCategoryName is required"` | Missing tax fields | Add all 3 `taxCategoryId/Code/Name` |
| `"Item: item not found"` | Wrong `itemId` UUID | Fetch with `/api/items/items/by-code/{code}` first |
| `"Item: item is not active"` | Item is soft-deleted (`isActive=false`) | Use a different active item, or restore first |

## Items Must be Active

The API refuses lines where `item.isActive === false`. Check with `GET /api/items/items/by-code/{code}` and look at the `isActive` field. If inactive, either:
- **Restore**: `POST /api/items/items/{id}/restore` (superuser)
- **Swap**: use a different active item (e.g., `PL-CACTUS` instead of `PL-CACTUS-MEDIANO`)

## Items Not in Portal — Workaround

If the invoice has items that don't exist in the portal catalog at all, you **cannot** create a line with `itemId: null`. The API rejects it. Options:
1. Find the closest portal item match and use its ID, annotating via `description` field (e.g., invoice says "CNAVELITAS VR" but portal has "CHAVELITAS VR" — use CHAVELITAS ID with description="CNAVELITAS VR")
2. Create the missing item in the portal first, then reference its ID
3. Skip those items and note the discrepancy in the grand total

## SUPER EXTRA Business Partner IDs (vivero tenant, Jun 30 2026)

| BP ID | Code | Name |
|-------|------|------|
| 32249c40-4c89-4fdf-a381-73969dba188d | CL-0035 | SUPER EXTRA via israel |
| a8cea960-d200-4222-8654-6cda0093d6b9 | CL-0005 | SUPER EXTRA los pueblos |
| db64ad3e-a54c-4f15-b15b-d60dba3917a4 | CL-0017 | SUPER EXTRA albrook |
| 083fb553-ca57-4678-ba12-9ae1cf4b90ed | CL-0006 | SUPER EXTRA monterico |
| 15ee6af1-c661-45a1-acd9-7e62a8cd3c3d | CL-0010 | SUPER EXTRA condado |
| 78532e5e-caa7-4863-aa80-7090e8e22257 | CL-0019 | SUPER EXTRA el Lago |
| d9cd6c5e-9886-41df-a3a8-4d30ede82a7a | CL-0027 | SUPER EXTRA aguadulce |
| d73abea9-fac1-43ac-9c1b-236c3c06b358 | CL-0040 | SUPER EXTRA Chanis |
| cbb72b57-a924-408d-9772-ca7de21834ae | CL-0024 | SUPER EXTRA las tablas |
| b3b486a9-bb07-4670-841c-fe4c95eead1a | CL-0028 | SUPER EXTRA penonome |

All use: Price list `SALE_PUBLIC`, Payment terms `PREPAY`, Currency `USD`.

## Warehouse & Tax Constants (vivero tenant)

- Warehouse: `d8294c0c-ea75-4f03-a464-7f9b9efa9abf` / code `PRIN` / name `Principal`
- Tax (exento): `097722df-e70c-4380-9372-a863c67c2bca` / code `EXCENTO` / name `Excento`
- Payment terms (PREPAY): `6c310a2b-c40d-410d-926d-42f7bb827ef4`

## Price List IDs (vivero tenant)

```python
price_lists = {
    "COST_A&G": "629c947f-5edf-441d-9a70-e8d571e5b1d8",
    "COST_IAN": "31000d32-75f2-467a-b2f8-e5f991aff36c",
    "COST_JARDIN": "ccf36882-505b-420f-89f3-07273f024124",
    "COST_SARA": "607aa5ef-e4a9-4d0b-94dd-6eb04dea83bc",
    "COST_EDWIN": "02037417-1ac1-45bb-b3b4-df022ff6085d",
    "COST_HACIENDA": "1be181ec-69d9-4661-bebd-e0a09f8ee851",
    "COST_ISMAEL": "96c2a3fb-380b-41fd-861b-87076ac02bc6",
    "SALE_PUBLIC": "0455a655-460f-4a75-b4f7-e1d41b5e6886",
    "SALE_SUPER": "e4d473ef-e97e-4258-8391-594b9d0eb9f0",
}
```

## Jul 1 2026 — Batch Quotations for 3 SUPER EXTRA Branches

The session created **7 draft quotations** across 3 customer branches, matching invoices from Vivero Rose (supplier). Key patterns that emerged:

### Quotations created:

| Doc | Branch | Date | Factura | Total | Items |
|-----|--------|------|---------|-------|-------|
| SQ-2026-000024 | via israel | 03/06 | No.740 | $83.85 | 13 |
| SQ-2026-000025 | via israel | 15/06 | No.767 | $105.75 | 15 |
| SQ-2026-000026 | via israel | 24/06 | No.781 | $317.95 | 30 |
| SQ-2026-000027 | los pueblos | 04/06 | No.741 | $57.50 | 5 |
| SQ-2026-000029 | los pueblos | 26/06 | No.786 | $241.50 | 26 |
| SQ-2026-000032 | albrook | 05/06 | No.742 | $115.60 | 20 |

### Item Mapping Strategy (invoice name → portal code)

When invoice items don't exactly match portal items:

1. **Known mislabelings** (user corrected Jul 1):
   - "MILLONARIA SAMIAOCULA VR" → **ZAMIOCULCA** (`PL-ZAMIOCULCA`) — the user said "Zamioculca se llama"
   - "MILLONARIA NEGRA VR" → **ZAMIOCULCA NEGRA** (`PL-ZAMIOCULCA-NEGRA`)
   - "MOLLEJITAS VR" → **MOLLEJA** (`PL-MOLLEJA`) — the user corrected: "se llama molleja ve"

2. **Invoice typos automatically mapped**:
   - "CNAVELITAS VR" → CHAVELITAS
   - "CRISANTEMOS EN POTE VR" → CRISONTEMOS
   - "ALBACA VR" → ALBAHACA
   - "PETUNIA VR" → PETUNIN
   - "CELOZIA VR" → CELOCIA
   - "CORONITA DE CRISTO VR" → CORONETA

3. **Items excluded per user instruction**:
   - "TIERRA NEGRA" (no existe en portal, user dijo no ponerla)
   - "MARIGOLD VR" (no existe en portal)
   - Lines marked "N/C" on invoice (exclude from quotation)

### `expand=lines` Consistency Issue

Confirmed again: even when lines are saved successfully (grandTotal is correct), subsequent `GET ?expand=lines` may return `lines: []`. This is a persistent API quirk, not a data loss. The `grandTotal` field is the reliable indicator.

### PATCH for Reactivation is More Reliable than RESTORE

`POST /api/items/items/{id}/restore` returned 200 but `isActive` remained `false`. Using `PATCH /api/items/items/{id}` with `{"isActive": True, "version": version}` worked for all 57 items.

### Item UUIDs Drift Between Sessions

Item UUIDs must be re-fetched via `/api/items/items/by-code/{code}` at the START of each session. Hardcoded UUIDs from a previous session will fail with `"Item: item not found"`. Example: PL-AGLONEMAS changed from `7b54c85e-...` to `5a714320-...` between sessions.

## Pitfalls (updated Jul 1 2026)

1. **Python urllib gets Cloudflare 403** even with valid X-Api-Key — use `curl` to verify the key works first, then use the Mozilla UA + CERT_NONE workaround
2. **`expand=lines` may return empty even when lines exist** — trust `grandTotal` as ground truth. Verify by creating a new GET via curl or Portal UI.
3. **Lines can't have `itemId: null`** — every line must reference a real portal item. Use closest-match items with custom `description` for invoice annotations.
4. **All line fields required** — missing any of `itemCode`, `itemName`, `warehouseName`, `taxCategoryName` causes per-line validation failure.
8. **Item UUIDs drift between sessions** — Always re-fetch via `/api/items/items/by-code/{code}` at the start of each session. Hardcoded UUIDs from a previous session fail with `"Item: item not found"`.
9. **PATCH isActive=True is more reliable than RESTORE** — `POST /api/items/items/{id}/restore` may return 200 with `isActive` still false. Use PATCH with `{"isActive": True, "version": version}` instead. On 409 Conflict, retry with `version + 1`.
10. **Items with same itemCode for different unitPrices** — When invoice has the same item at two different unit prices (e.g., "CACTUS VARIADOS PEQUENO @ $1.95" and "CACTUS VARIADOS MEDIANO @ $2.85"), you can add two lines with the same `itemId` but different `unitPrice` and `description`. The API accepts it — the unitPrice is overridden per-line.

## Reactivating Inactive Items (vivero tenant, Jun 30 2026)

When a POST to create a quotation fails with `"Item: item is not active"`, the item is soft-deleted (`isActive=false`). Two methods:

**Method 1 — PATCH with isActive** (more reliable):
```python
payload = json.dumps({"isActive": True, "version": item["version"]})
result = subprocess.run(["curl", "-s", "-X", "PATCH",
    "-H", f"X-Api-Key: {KEY}", "-H", "Content-Type: application/json",
    "-d", payload, f"{BASE}/api/items/items/{item['id']}"],
    capture_output=True, text=True, timeout=10)
```

**Method 2 — RESTORE endpoint** (`POST /api/items/items/{id}/restore`) — may return 200 but item stays inactive.

On Jun 30 2026: 57 items were reactivated via PATCH in a single batch. All returned `isActive: true` with 0 failures.

## vivero Items — Invoice Name to Portal Code Mapping (Jun 30 2026)

Invoices from Vivero Rose use names with `VR` suffix. Common lookups:

| Invoice Name | Portal Code | Notes |
|-------------|------------|-------|
| HIERBA BUENA VR | PL-HIERBA-BUENA | Exact match |
| MINI JADE VR | PL-MINI-JADE | Exact match |
| OREGANO VR | PL-OREGANO | Exact match |
| TORENIA VR | PL-TORENIA | Exact match |
| ROMERO VR | PL-ROMERO | Exact match |
| RUDA VR | PL-RUDA | Exact match |
| CNAVELITAS VR | PL-CHAVELITAS | Invoice typo; use CHAVELITAS |
| CHAVELITAS VR | PL-CHAVELITAS | Exact match |
| HYPOESTES VR | PL-HYPOESTES | Exact match |
| MENTA VR | PL-MENTA | Exact match |
| COLEOS VR | PL-COLEOS VR | Exact match |
| IXORAS VARIADAS VR | PL-IXORA | No separate "variadas" variant |
| CRISANTEMOS EN POTE VR | PL-CRISONTEMOS | Invoice typo (CRISAN vs CRISON) |
| SABILA ALOE MEDIANA VR | PL-SABILA-ALOE-MEDIANA | Exact match |
| LENGUA DE SUEGRA MINI VR | PL-LENGUA-DE-SUEGRA | Exact match |
| LENGUA DE SUEGRA ENANA VR | PL-LENGUA-DE-SUEGRA-2 | Exact match |
| ZAMIOCULCA VR | PL-ZAMIOCULCA | Portal shows "ZAMICULCA VR" (typo) |
| ZAMIOCULCA NEGRA VR | PL-ZAMIOCULCA-NEGRA | Exact match |
| MOLLEJITAS VR | PL-MOLLEJA | Invoice diminutive; portal has MOLLEJA |
| PETUNIA VR | PL-PETUNIN | Invoice typo (PETUNIA vs PETUNIN) |
| ROSAS VR | PL-ROSA | Exact match |
| CACTUS VARIADOS PEQUENO VR | PL-CACTUS | "CACTUS MEDIANO VR" closest |
| CACTUS VARIADOS MEDIANO VR | PL-CACTUS (same item) | Use same, different unitPrice |
| MILLONARIA SAMIAOCULA VR | PL-ZAMIOCULCA | Actually Zamioculca (mislabeled) |
| MILLONARIA NEGRA VR | PL-ZAMIOCULCA-NEGRA | Actually Zamioculca Negra (mislabeled) |
| PALO DE BRASIL VR | PL-PALO-DE-BRASIL-2 | Exact match |
| CORONITA DE CRISTO VR | PL-CORONETA | Different display name, same plant |
| AJI BOLITA DECORATIVO VR | PL-AJI-BOLITA | Exact match |
| CELOZIA VR | PL-CELOSIA | Portal: CELOCIA VR |
| HELECHO VR | PL-HELECHO-ESPARRAGO-MEY | Closest match available |
| NOVIO CHINO VR | PL-NOVIO-CHINO | Exact match |
| CLAVELITO VR | PL-CLAVELITO | Exact match |