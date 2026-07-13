# Stupefy Bulk Create — Jun 30 2026

## Context
Bulk-created 44 new items from `plantas_nuevas` Google Sheet tab to EZY Portal.
Then assigned categories + tags to all 44 via PATCH.

## Correct Group & Class IDs (discovered fresh from API)
```
GET /api/items/item-groups?perPage=50
  → PLANTS    b38e9a2d-4951-4d40-9fa3-1357ef0dc631
  → POTES     92335cf2-948d-4962-acf7-d894382102b0
  → FLETES    b2442d2e-5fc4-4a16-b68f-6e1c4093cd66

GET /api/items/item-classes?perPage=50
  → LIVE_PLANT  b65da4ee-1f20-45f7-b329-d2b884c7c10d
  → CARGA       4459719d-1fc5-47d5-babc-03330a203b72
  → POTES       128060d6-2f28-4e9a-8d4a-f89ef91e36d2
```

**NEVER hardcode these IDs.** Fetch them each session via the API. The memory had stale/wrong IDs.

## Category Assignment via PATCH (works, no Bearer token needed)
Even though `GET /api/categories` requires Bearer JWT, assigning a category to an item via `PATCH /api/items/items/{id}` with `itemCategory` field works with the tenant API key:

```python
payload = {
    "version": current_version,
    "itemCategory": CATEGORY_UUID,
    "tags": list(set(current_tags + [tag_name]))
}
# → 200 OK
```

Tags are a `string[]` field on the item. PATCH merges by sending the full desired array.

## Price Lists (all 9 discovered)
As of Jun 30 2026, the vivero tenant has:
- COST_A&G, COST_IAN, COST_JARDIN, COST_SARA, COST_EDWIN, COST_HACIENDA, COST_ISMAEL, SALE_PUBLIC, SALE_SUPER
- COST_EDUARDO does NOT exist — items with this price list (CAJA BN) could not be created with a price

## Key Error: "Item class not found"
This error means `itemGroupId` or `itemClassId` in the POST payload is a UUID that doesn't exist.
Fix: always fetch from the live `/api/items/item-groups` and `/api/items/item-classes` endpoints at the start of a bulk-create session.

## Key Error: "Item code already exists" (DUPLICATE)
Caught one: PL-SANSEVIERIA-R was already created (duplicate row in sheet).
Fix: check by code AND name before creating.

## Barcodes Need UOMs
Items created via POST with `baseUom: "EA"` but WITHOUT `initialUOMs` have NO `itemUoms` array.
The `/api/items/items/{id}/barcodes` POST endpoint requires an `itemUomId` — without UOMs, barcodes can't be generated.
Fix: add UOMs via PATCH first, or accept that barcodes require a two-step process.

## Google Sheets Cleanup
After moving data out of `plantas_nuevas`, clear the data rows (keep header) and sort INVENTARIO A→Z.
Sorting is done server-side: read all rows, sort by name in Python, write back entire range.

## Python urllib 401 with newer API keys
Keys from `ten_3HW_...` onwards get 401 from Python urllib on ALL portal endpoints, even with Mozilla UA + SSL context. The hermes-agent venv Python (`~/.hermes/hermes-agent/venv/bin/python3`) seems to have a different TLS stack. Workaround: use `curl` via subprocess for ALL API calls with these keys.