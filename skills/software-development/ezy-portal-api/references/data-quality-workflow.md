# Data Quality Workflow (EZY Portal Items API)

**Session:** 2026-06-22 — Fixed 121 items quality issues on vivero.ezyts.com

---

## Quality Endpoints (Work with Tenant API Key)

| Endpoint | Auth | Returns |
|---|---|---|
| `GET /api/items/stats` | `X-Api-Key: ten_...` | Dashboard summary (totals, by type/group/class) |
| `GET /api/items/stats/quality` | `X-Api-Key: ten_...` | Counts of items missing group, class, description, category, UOM |

**Note:** Documentation says these need CookieAuth, but **tenant API key works**.

---

## Quality Response Example (Before Fix)

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

---

## Fix Workflow (63 items missing group/class, 6 missing description)

### 1. Identify Items Missing Data

```bash
# Page 1 (100 items)
GET /api/items/items?expand=prices&page=1&perPage=100

# Page 2 (21 items)
GET /api/items/items?expand=prices&page=2&perPage=100
```

Filter locally for: `itemGroupId: null`, `itemClassId: null`, `description: "" or null`

### 2. For Each Item: Get Current Version

```bash
GET /api/items/items/{item-id}
# Extract "version" from response
```

### 3. PATCH with Correct Fields

**Critical: Use `itemGroup` (not `itemGroupId`)**

```json
// Assign group (Plantas: b38e9a2d-4951-4d40-9fa3-1357ef0dc631)
PATCH /api/items/items/{item-id}
{
  "itemGroup": "b38e9a2d-4951-4d40-9fa3-1357ef0dc631",
  "version": <current-version>
}

// Assign class (Planta viva: b65da4ee-1f20-45f7-b329-d2b884c7c10d)
PATCH /api/items/items/{item-id}
{
  "itemClassId": "b65da4ee-1f20-45f7-b329-d2b884c7c10d",
  "version": <current-version>
}

// Add description
PATCH /api/items/items/{item-id}
{
  "description": "PLANT NAME VARIANT",
  "version": <current-version>
}

// Fix service item (FLETE) — different group/class
PATCH /api/items/items/{flete-id}
{
  "itemGroup": "b2442d2e-5fc4-4a16-b68f-6e1c4093cd66",  // FLETES DE CARGA
  "itemClassId": "4459719d-1fc5-47d5-babc-03330a203b72", // flete de carga
  "version": <current-version>
}
```

### 4. Verify Fix

```bash
GET /api/items/stats/quality
# Should return all zeros except itemsWithoutCategory (needs Bearer JWT)
```

---

## Results After Fix

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

**Distribution by Group:**
- Plantas: 117
- Potes_Plantas: 2
- FLETES DE CARGA: 2

**Distribution by Class:**
- Planta viva: 117
- Potes_plant: 2
- flete de carga: 2

---

## Image Clearing via API

Items store only `primaryImageStorageKey` (string) and `imageCount` (integer, computed).

**To clear image (remove reference):**

```bash
PATCH /api/items/items/{item-id}
{
  "primaryImageStorageKey": "",
  "version": <current-version>
}
```

**Result:** `primaryImageStorageKey: ""`, `imageCount: null`

**Batch cleared:** 116 items in ~15 seconds (116 PATCH requests)

---

## Categories Still Need Bearer JWT

`/api/categories` and `/api/categories/mappings` return 404/401 with `X-Api-Key`. Require user Bearer token from browser session.

---

## Pitfalls Discovered

1. **`itemGroup` vs `itemGroupId`** — PATCH field is `itemGroup` (string UUID). Using `itemGroupId` is silently ignored.
2. **Stats endpoints accept tenant API key** — despite docs saying CookieAuth only.
3. **Categories need Bearer JWT** — tenant API key won't work for category mappings.
4. **Version increments on every PATCH** — must fetch fresh version for each update.
5. **Image clearing is instant** — no async job, just PATCH with empty string.