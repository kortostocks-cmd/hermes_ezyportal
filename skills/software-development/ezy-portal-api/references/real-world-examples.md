# Real-World API Examples (from vivero.ezyts.com session)

**Tenant:** vivero (https://vivero.ezyts.com)
**Auth:** Tenant API Key `ten_iiXLA5AvHe-qjYgbrEjbdaWATDVjsxKxLmq8bSETi3Q`
**Date:** 2026-06-17 / 2026-06-18

---

## List Items Response (page 1 of 2)

```bash
GET /api/items/items?expand=prices&page=1&perPage=50
```

```json
{
  "data": [
    {
      "id": "3c419eb5-7a42-425e-9622-b65cbc64484b",
      "tenantId": "fdf144d1-7d70-4b3e-ae20-a133b10c61d0",
      "itemCode": "PL-ROMERO",
      "name": "ROMERO VR",
      "description": "Imported from skus del vivero.xlsx row 5",
      "itemType": "stock",
      "isStock": true,
      "isPurchasable": true,
      "isSellable": true,
      "isActive": true,
      "isVariantParent": false,
      "baseUom": "EA",
      "itemGroupId": "b38e9a2d-4951-4d40-9fa3-1357ef0dc631",
      "itemClassId": "b65da4ee-1f20-45f7-b329-d2b884c7c10d",
      "sku": "7452106390029",
      "priceListCode": "SALE_SUPER",
      "itemStockTotal": 192,
      "itemReservedTotal": 0,
      "itemAvailableTotal": 192,
      "itemOnOrderTotal": 0,
      "itemAvgCost": 0.75,
      "itemLastCost": 0.75,
      "tags": ["has_barcode", "herbs", "live_plant", "vivero_import"],
      "syncState": "in_sync",
      "createdAt": "2026-06-08T18:38:35.353059Z",
      "createdBy": "0b3c7e11-1d14-4f6f-9a9d-57b8cabbbc94",
      "createdByName": "Import",
      "updatedAt": "2026-06-11T15:57:09.67383Z",
      "updatedBy": "019ea8af-508f-793b-864c-42b85ff9875c",
      "updatedByName": "abraham kortovich",
      "version": 4
    }
  ],
  "total": 56,
  "page": 1,
  "perPage": 50,
  "totalPages": 2,
  "hasMore": true
}
```

**Key observations:**
- `prices: []` — empty array because API key lacks price view permissions (masked)
- All 56 items are `isActive: true`, `itemType: "stock"` (except 1 `non_stock` = FLETE)
- Common `itemGroupId`: `b38e9a2d-4951-4d40-9fa3-1357ef0dc631` ("Plantas")
- Common `itemClassId`: `b65da4ee-1f20-45f7-b329-d2b884c7c10d` ("Planta viva")
- Tags include import metadata: `vivero_import`, `has_barcode`/`missing_barcode`, category tags (`herbs`, `flowers`, `foliage`, `succulents`, `palms_trees`, `ornamental`)

---

## Get Item by Code (Detail) Response

```bash
GET /api/items/items/by-code/PL-ROMERO?expand=prices
```

```json
{
  "id": "3c419eb5-7a42-425e-9622-b65cbc64484b",
  "tenantId": "fdf144d1-7d70-4b3e-ae20-a133b10c61d0",
  "itemCode": "PL-ROMERO",
  "name": "ROMERO VR",
  "description": "Imported from skus del vivero.xlsx row 5",
  "itemType": "stock",
  "isStock": true,
  "isPurchasable": true,
  "isSellable": true,
  "isActive": true,
  "isVariantParent": false,
  "baseUom": "EA",
  "itemGroupId": "b38e9a2d-4951-4d40-9fa3-1357ef0dc631",
  "itemGroup": {
    "id": "b38e9a2d-4951-4d40-9fa3-1357ef0dc631",
    "tenant_id": "fdf144d1-7d70-4b3e-ae20-a133b10c61d0",
    "code": "PLANTS",
    "name": "Plantas",
    "is_active": true,
    "created_at": "2026-06-08T18:32:56.489571Z",
    "created_by": "0b3c7e11-1d14-4f6f-9a9d-57b8cabbbc94",
    "created_by_name": "Import",
    "updated_at": "2026-06-08T18:32:56.489572Z",
    "updated_by": "0b3c7e11-1d14-4f6f-9a9d-57b8cabbbc94",
    "updated_by_name": "Import"
  },
  "itemClassId": "b65da4ee-1f20-45f7-b329-d2b884c7c10d",
  "itemClass": {
    "id": "b65da4ee-1f20-45f7-b329-d2b884c7c10d",
    "tenantId": "fdf144d1-7d70-4b3e-ae20-a133b10c61d0",
    "code": "LIVE_PLANT",
    "name": "Planta viva",
    "isActive": true,
    "createdAt": "2026-06-08T18:33:03.748462Z",
    "createdBy": "0b3c7e11-1d14-4f6f-9a9d-57b8cabbbc94",
    "createdByName": "Import",
    "updatedAt": "2026-06-08T18:33:03.748462Z",
    "updatedBy": "0b3c7e11-1d14-4f6f-9a9d-57b8cabbbc94",
    "updatedByName": "Import"
  },
  "sku": "7452106390029",
  "priceListCode": "SALE_SUPER",
  "itemStockTotal": 192,
  "itemReservedTotal": 0,
  "itemAvailableTotal": 192,
  "itemOnOrderTotal": 0,
  "itemAvgCost": 0.75,
  "itemLastCost": 0.75,
  "tags": ["has_barcode", "herbs", "live_plant", "vivero_import"],
  "syncState": "in_sync",
  "createdAt": "2026-06-08T18:38:35.353059Z",
  "createdBy": "0b3c7e11-1d14-4f6f-9a9d-57b8cabbbc94",
  "createdByName": "Import",
  "updatedAt": "2026-06-11T15:57:09.67383Z",
  "updatedBy": "019ea8af-508f-793b-864c-42b85ff9875c",
  "updatedByName": "abraham kortovich",
  "version": 4
}
```

**Key differences from list view:**
- `itemGroup` and `itemClass` are **fully expanded objects** (not just IDs)
- Includes `version` (optimistic lock) — critical for updates
- `syncState` shows replication status
- Audit fields include both creator and last updater with names

---

## Pagination Limit Confirmed

- **Max `perPage`: 100** (not 200)
- Request with `perPage=200` returns 400: `Field validation for 'PerPage' failed on the 'max' tag`

---

## Data Quality Dashboard Fix (2026-06-22)

**Endpoints (work with Tenant API Key):**
- `GET /api/items/stats` — Dashboard summary
- `GET /api/items/stats/quality` — Quality metrics

**Before (121 items):**
```json
{
  "itemsWithoutDescription": 6,
  "itemsWithoutGroup": 63,
  "itemsWithoutClass": 1,
  "itemsWithoutCategory": 121,
  "stockItemsWithoutUOM": 0,
  "totalItems": 121
}
```

**Fix workflow (63 PATCH requests):**
1. Fetch all items with `expand=prices` (2 pages)
2. Filter for `itemGroupId: null`, `itemClassId: null`, `description: ""`
3. For each: GET detail to get current `version`
4. PATCH with `{"itemGroup": "<group-id>", "version": <v>}` — **field is `itemGroup`, NOT `itemGroupId`**
5. PATCH `itemClassId` where needed
6. PATCH `description` where empty
7. Service items (FLETE): assign `FLETES DE CARGA` group + `flete de carga` class

**After:**
```json
{
  "itemsWithoutDescription": 0,
  "itemsWithoutGroup": 0,
  "itemsWithoutClass": 0,
  "itemsWithoutCategory": 121,
  "stockItemsWithoutUOM": 0,
  "totalItems": 121
}
```

**Distribution:**
| Group | Count |
|-------|-------|
| Plantas | 117 |
| Potes_Plantas | 2 |
| FLETES DE CARGA | 2 |

| Class | Count |
|-------|-------|
| Planta viva | 117 |
| Potes_plant | 2 |
| flete de carga | 2 |

---

## Image Clearing via API (2026-06-22)

**To clear image reference from item:**
```bash
PATCH /api/items/items/{item-id}
{
  "primaryImageStorageKey": "",
  "version": <current-version>
}
```

**Result:** `primaryImageStorageKey: ""`, `imageCount: null`

**Batch cleared:** 116/121 items in ~15 seconds.

**cURL example:**
```bash
# Get current version first
curl -H "X-Api-Key: ten_..." -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/items/items/{item-id}"

# Clear image
curl -X PATCH -H "X-Api-Key: ten_..." -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"primaryImageStorageKey":"","version":<v>}' \
  "https://vivero.ezyts.com/api/items/items/{item-id}"
```

---

## Business Partners Bulk Creation (2026-06-22)

**Source:** Photo of route list (38 locations)

**Created:** 38 clients with codes `CL-XXXX` (zero-padded 4-digit from image numbers)

**Payload per client:**
```json
{
  "code": "CL-0001",
  "name": "arraijan",
  "status": "active",
  "roles": ["customer"],
  "isCustomer": true,
  "isVendor": false,
  "isLead": false,
  "taxExempt": false,
  "currencyCode": "USD",
  "priceListCode": "SALE_PUBLIC",
  "creditLimit": 0,
  "onHold": false,
  "languageCode": "es",
  "tags": ["ruta_ruben"]
}
```

**Required:** `Idempotency-Key: <uuid>` header on POST

**Result:** 38/38 created. Total `CL-*` clients: 39.
| 1 | 50 | 50 | true |
| 2 | 50 | 6 | false |

Total: 56 items, 2 pages.

---

## Price Masking Behavior

With this tenant API key (no price authorization group):
- `expand=prices` → `"prices": []` (empty array)
- Without `expand=prices` → `"prices": null`

To see prices, the API key needs an authorization group with `items.viewCost` / `prices.view` permissions.

---

## Item Catalog Summary (vivero tenant)

| Category | Count | Example Items |
|----------|-------|---------------|
| Herbs (with barcode) | 6 | ROMERO, HIERBA BUENA, RUDA, MENTA, OREGANO, TOMILLO |
| Herbs (missing barcode) | 2 | ALBAHACA, APIO |
| Flowers (with barcode) | 6 | CHAVELITAS, CLAVELITO, PETUNIN, POINSETAS, NOVIO CHINO, TORENIA |
| Flowers (missing barcode) | 5 | CIELITO AZUL, CORONETA, CRISONTEMOS, ROSITA MINIATURA, POINSETAS PEQUEÑA |
| Succulents (with barcode) | 5 | JADE, MINI JADE, PEPERONIA SANDIA, SABILA ALOE PEQUENA, SABILA ALOE MEDIANA |
| Succulents (missing barcode) | 3 | ZAMICULCA, ZAMICULCA NEGRA, SUCULENTAS MEDIANAS |
| Foliage (with barcode) | 6 | AGLONEMAS, CINTA MALA MADRE, LENGUA DE SUEGRA, LENGUA DE SUEGRA ENANA, HELECHO ESPARRAGO, TRADESCANTIA ZEBRINA |
| Foliage (missing barcode) | 4 | FITTONIA ROJA, HELECHOS, MOLLEJA, SICDAXUS |
| Palms/Trees (with barcode) | 7 | BAMBU, PALMA CUBANA, PALMA ROJA, PALO DE BRASIL (3 variants), PINO BONSAI, PINO RASTRERO |
| Ornamental (with barcode) | 2 | CHILE MEDUSSA, CHILE POP |
| Ornamental (missing barcode) | 1 | MINI ARBUSTO |
| Other | 3 | AGAVE EN POTE, FLETE (non_stock), SUCULENTAS POTE GRANDE |

**Stock stats:**
- Items with stock > 0: ~30/56
- Total stock units: ~1,400+
- Highest stock: ROMERO (192), HIERBA BUENA (138), TORENIA (96), CHAVELITAS (120), RUDA (96)
- Zero stock: ~26 items (mostly imported, not yet received)

---

## Common Filter Patterns (tested)

```bash
# Active sellable stock items with prices
GET /api/items/items?expand=prices&isActive=true&isSellable=true&isStock=true

# Items with stock available
GET /api/items/items?stockQtyMoreThan=0&isActive=true

# Search by code/name
GET /api/items/items?query=ROMERO

# Filter by tags (AND logic)
GET /api/items/items?tags=herbs,has_barcode

# Exclude tags
GET /api/items/items?excludeTags=missing_barcode

# Lightweight select for dropdowns
GET /api/items/items/select?active=true&variantRole=parents&docType=purchase-order
```

---

## cURL Commands That Worked

```bash
# List with prices (tenant API key)
curl -H "X-Api-Key: ten_iiXLA5AvHe-qjYgbrEjbdaWATDVjsxKxLmq8bSETi3Q" \
  -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/items/items?expand=prices&page=1&perPage=50"

# Get by code with prices
curl -H "X-Api-Key: ten_iiXLA5AvHe-qjYgbrEjbdaWATDVjsxKxLmq8bSETi3Q" \
  -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/items/items/by-code/PL-ROMERO?expand=prices"

# Search by barcode
curl -H "X-Api-Key: ten_iiXLA5AvHe-qjYgbrEjbdaWATDVjsxKxLmq8bSETi3Q" \
  -H "Accept: application/json" \
  "https://vivero.ezyts.com/barcodes?barcode=7452106390029"
```

---

## Errors Encountered

| Error | Cause | Resolution |
|-------|-------|------------|
| `Could not resolve host: app.portal.net` | Generic base URL doesn't resolve | Use tenant-specific URL: `https://<tenant>.ezyts.com` |
| SSL cert verify failed (Python) | Self-signed or internal CA | Use `curl -k` or configure cert bundle |

---

## Lessons Learned

1. **Always use tenant-specific subdomain** (`vivero.ezyts.com`) — generic `app.portal.net` may not resolve
2. **Tenant API Key works perfectly** for read operations — `X-Api-Key: ten_...` header
3. **Price masking returns empty array** not null — handle `prices: []` in code
4. **Detail endpoint expands relations** — `itemGroup` and `itemClass` come as full objects
5. **Tags are rich metadata** — import source, barcode status, plant category all in tags
6. **Version field is present** — must include on updates for optimistic locking
7. **Pagination works as documented** — `totalPages`, `hasMore` reliable
8. **HTTP 207 on item creation with non-existent priceListCode** — item is created but price row is NOT linked. The `priceListCode` field is set on item but `prices` array remains empty. Fix: create price list in Portal UI first (Settings → Price Lists → New), then items will link automatically on next create or PATCH.
9. **Price Lists are NOT manageable via API** — must create in Portal UI: Settings → Price Lists → New. Endpoints like `/api/price-lists` return 404.
10. **Image handling**: Items store only `primaryImageStorageKey` reference. No upload endpoint in API. Storage key pattern: `images/{NAME}_{timestamp}_{hash}.{ext}`. Upload via Portal UI or direct storage API.
11. **ItemCode convention**: `PL-` + UPPERCASE_WITH_DASHES. Spaces→hyphens, special chars removed. Verify against existing before bulk create.
12. **Tagging convention**: `vivero_import`, `has_barcode`/`missing_barcode`, category tags (`herbs`, `flowers`, `foliage`, `succulents`, `palms_trees`, `ornamental`, `live_plant`), custom tags (`low_stock`, `promocion`, `en_botones`, `pequeno`, `no_muy_grande`, `cost_sara`).
13. **Duplicate detection**: Before bulk creation, fetch existing items and normalize names for comparison. Decide per case: skip, create variant (different size/pot), or update existing.

---

## Bulk Creation Example (2026-06-18) — 59 Items from CSV

**Source:** `lista_plantas_vivero.csv` — 59 plant varieties with cost prices

**Payload structure per item:**
```json
{
  "itemCode": "PL-AGAVE-EN-POTE-5",
  "name": "AGAVE EN POTE 5",
  "description": "POCAS UNIDADES",
  "itemType": "stock",
  "isStock": true,
  "isPurchasable": true,
  "isSellable": true,
  "isActive": true,
  "baseUom": "EA",
  "itemGroupId": "b38e9a2d-4951-4d40-9fa3-1357ef0dc631",
  "itemClassId": "b65da4ee-1f20-45f7-b329-d2b884c7c10d",
  "priceListCode": "COST_SARA",
  "prices": [{
    "priceListCode": "COST_SARA",
    "uom": "EA",
    "price": 2.50,
    "currencyCode": "PAB"
  }],
  "tags": ["vivero_import", "cost_sara", "low_stock"]
}
```

**Result:** All 59 items created successfully (HTTP 207 each). Items exist with correct `itemCode`, `name`, `description`, `tags`, `priceListCode="COST_SARA"`. Prices NOT linked because `COST_SARA` price list doesn't exist in Portal UI yet.

**Next step:** Create `COST_SARA` price list in Portal UI (Code: `COST_SARA`, Name: `Costo Sara`, Currency: `PAB`), then prices will link automatically.

---

## Image Audit (2026-06-18)

**Items with images (28):** PL-AGLONEMAS, PL-ALBAHACA, PL-APIO, PL-BAMBU, PL-CHAVELITAS, PL-CHILE-MEDUSSA, PL-CHILE-POP, PL-CIELITO AZUL, PL-CINTA-MALA-MADRE, PL-CLAVELITO, PL-CORONETA, PL-CRISONTEMOS, PL-FITONIA-ROJA, PL-HELECHO-ESPARRAGO-MEY, PL-HELECHOS, PL-HIERBA-BUENA, PL-HIERBA-DE-LIMON, PL-HYPOESTES, PL-IXORA, PL-JADE, PL-LENGUA-DE-SUEGRA, PL-LENGUA-DE-SUEGRA-2, PL-MENTA, PL-MINI-JADE, PL-MOLLEJA, PL-ROMERO, PL-RUDA, PL-ZAMIOCULCA, PL-ZAMIOCULCA-NEGRA

**Items without images (~89):** All 59 new items + ~30 existing items

**Storage key pattern:** `images/{NAME}_{YYYYMMDDHHMMSS}_{hash}.{ext}`
- Example: `images/AGLONEMAS_20260609164636_8343a097.jpg`
- Example: `images/bambu_20260611170200_625eeb72.png`

**No API upload endpoint** — must use Portal UI or direct storage.

---\n\n## UOM & Pricing Demo (2026-06-19)\n\n**Created item:** `PL-DEMO-CAJA-1000` — \"DEMO CAJA 1000 UNIDADES\"\n\n**UOM Structure:**\n```json\n\"initialUOMs\": [\n  { \"factor\": 1, \"uomCode\": \"EA\", \"isDefaultSales\": true },\n  { \"factor\": 1000, \"uomCode\": \"CAJA\", \"isDefaultPurchase\": true }\n]\n```\n- Base UOM: EA (each)\n- Purchase UOM: CAJA (factor 1000 = 1 CAJA = 1000 EA)\n- Price: 90 PAB on CAUM (SALE_SUPER price list)\n\n**Result:** HTTP 207 — item created, price NOT linked (SALE_SUPER price list doesn't exist in Portal UI yet).\n\n---\n\n## Image Audit & Analysis (2026-06-19)\n\n**Portal State (121 items):**\n| Status | Count | Details |\n|--------|-------|---------|\n| Items WITH images | 74 | 28 original + 34 AI-generated + 12 pre-existing |\n| Items WITHOUT images | 47 | Failed upload: \"Item was saved but some files could not be processed\" |\n| Local files available | 52 | In `~/Downloads/plantas_para_subir_portal/` (original photos) |\n| AI images in storage | 34 | Referenced by storage key, not downloadable via portal URL |\n\n**Storage Key Patterns Confirmed:**\n- Original: `images/{NAME}_{YYYYMMDDHHMMSS}_{hash}.{ext}`\n  - Example: `images/AGAVE_EN_POTE_5_20260618132701_76b78b8a.jpeg`\n- AI-generated: `images/{NAME}_{YYYYMMDD}_AI_{hash}.{ext}`\n  - Example: `images/PALMA_CUBANA_20260618_AI_9066f6c6.jpeg`\n\n**Critical Finding:** AI-generated images exist in external storage (S3/Azure/GCS) and are correctly referenced in `primaryImageStorageKey`, but **cannot be downloaded via `https://vivero.ezyts.com/images/...`** — returns 404. The portal only stores the reference key; actual files are in separate storage.\n\n**Items with MISMATCHED images (3):**\n| ItemCode | Portal Has | Local File |\n|----------|------------|------------|\n| PL-PINO-HINDU-EN-POTE-PREMIUM-5 | AI version | Original |\n| PL-PINO-DE-ORO-EN-POTE-21 | AI version | Original |\n| PL-APIO | `apio_20260611145928...` | Promo version |\n\n**47 Items MISSING images (need manual upload):**\nPL-CACTUS, PL-CELOSIA, PL-CIPRE-AZUL-EN-POTE-160-PROMOCION-HASTA-14-DE-JUNIO, PL-CIPRE-BOLA-EN-POTE-VCG17, PL-CIPRE-DORADO-EN-POTE-5, PL-CIPRE-THUJA-EN-GEOTEXTIL-35X28, PL-COBRA-VERDE-EN-POTE-8-19Z, PL-GUAYACAN-ENANO-TECOMA-EN-POTE-6, PL-JAZMIN-BLANCO-ENANO-EN-POTE-5, PL-MINI-ARBUSTO, PL-NOVIO-CHINO, PL-OREGANO, PL-PALMA-CUBANA, PL-PALMA-ROJA, PL-PALO-DE-BRASIL, PL-PALO-DE-BRASIL-2, PL-PALO-DE-BRAZIL, PL-PATA-DE-ELEFANTE-EN-POTE-6-160, PL-PEPERONIA-SANDIA, PL-PETUNIN, PL-PHILODENDRON-COBRA-EN-CANASTA, PL-PHILODENDRON-CONGO-EN-POTE-19, PL-PHILOMENDRO-XINADU, PL-PHOTUS, PL-PINO-BONSAI, PL-PINO-DE-ORO-EN-POTE-21, PL-PINO-HINDU-EN-POTE-PREMIUM-5, PL-PINO-RASTRERO, PL-POINSETAS-PEQUENA, PL-POINSETAS, PL-PURPLE-LADY-EN-BOLSA, PL-REINA-ISABEL-EN-POTE-8, PL-ROSA-FLOR-GRANDE-EN-POTE-8, PL-ROSA, PL-ROSITA-MINIATURA, PL-SABILA-ALOE-MEDIANA, PL-SABILA-ALOE-PEQUENA, PL-SANGRILLO-EN-BOLSA, PL-SICDAXUS, PL-SILVER-SKILL-EN-POTE-4, PL-SINGONIO-BLANCO-VARIEGADO-EN-BOLSA, PL-SUCULENTAS-MEDIANAS, PL-SUCULENTAS-POTE-GRAND, PL-TEXAS-NEVADO-EN-POTE-PDB-26K, PL-TORENIA, PL-TRADESCANTIA-GOLD-EN-BOLSA, PL-TRADESCANTIA-MINI-BOLSA, PL-TRADESCANTIA-REO-EN-BOLSA, PL-TRADESCANTIA-ZEBRINA, PL-Tomillo\n\n**Action Taken:** Created `~/Downloads/plantas_TODAS_para_portal/` with 52 original images for manual Portal UI upload.\n\n**Workflow for Missing Images:**\n1. Open each item in Portal UI\n2. Drag & drop corresponding file from `plantas_TODAS_para_portal/`\n3. Portal uploads to storage and updates `primaryImageStorageKey` automatically\n\n---\n\n## Price Lists Still Needed (Portal UI)\n\n| Code | Name | Currency | Status |\n|------|------|----------|--------|\n| SALE_SUPER | Sale Super | PAB | Missing — items reference it but prices not linked |\n| COST_SARA | Costo Sara | PAB | Missing — 59 items reference it |\n\n**Create in:** Settings → Price Lists → New\nAfter creation, existing items will auto-link on next PATCH or re-create.\n\n---\n\n## Internal Stock Endpoint (2026-06-19)\n\n**Endpoint:** `PUT/POST /internal/items/{id}/stock`\n\n**Behavior:** Serves the frontend React app (HTML), **not a JSON API**.\n- `GET` → Returns HTML page (200)\n- `PUT/POST` → Returns **405 Not Allowed** (nginx)\n\n**Cannot use for programmatic stock adjustments.** Must use Portal UI → Inventory → Stock Adjustment.\n\n---\n\n## UOM & Stock Interpretation Critical Findings (2026-06-19)\n\n### List vs Detail baseUom Mismatch\n- **List endpoint** (`/api/items/items`) returns `baseUom` but **`uoms: null`**\n- **Detail endpoint** (`/api/items/items/by-code/{code}`) returns full `uoms` array\n- **Discrepancy found:** List showed `baseUom: "BOX"` but Detail showed `baseUom: "EA"` for same item (CJ-CAJA-POTE-120)\n- **Always use detail endpoint for UOM/stock calculations**\n\n### CJ-CAJA-POTE Items - UOM Structure Changed\nOriginal design (created via API with `initialUOMs`):\n- `CJ-CAJA-POTE-120`: baseUom=BOX, UOMs: EA(×1), BOX(×1000)\n- `CJ-CAJA-POTE-180`: baseUom=BOX, UOMs: EA(×1), BOX(×405)\n\n**Current state (after unknown modification):**\n- `CJ-CAJA-POTE-120`: baseUom=EA, **only EA UOM exists** (BOX removed)\n- `CJ-CAJA-POTE-180`: baseUom=EA, UOMs: EA(×1), BOX(×450) — factor changed from 405→450\n\n**Impact:** Stock value "2" now means **2 EA (units)** not 2 BOX (2000/810 EA). Stock appears drastically lower.\n\n**To restore original structure:** PATCH item with `uoms` array including BOX UOM, or recreate with correct `initialUOMs`.\n\n---\n\n## onOrder Behavior (2026-06-19)\n\n**`itemOnOrderTotal` does NOT auto-clear** when goods are received via purchase order receipt.\n\n- Field tracks "quantity on open purchase orders"\n- **Must manually close/complete POs** in Portal UI: Purchases → Purchase Orders → Receive/Finalize\n- 22 items found with `stock > 0` AND `onOrder > 0` (received but PO still open)\n- Includes both plant items and CJ-CAJA-POTE items\n\n**Workflow to clear:**\n1. Portal UI → Purchases → Purchase Orders\n2. Find open POs for affected items\n3. Mark as "Received" / "Completed" or cancel remaining quantity\n\n---\n\n## Pagination Limit Confirmed\n\n- **Max `perPage`: 100** (not 200)\n- Request with `perPage=200` returns 400: `Field validation for 'PerPage' failed on the 'max' tag`