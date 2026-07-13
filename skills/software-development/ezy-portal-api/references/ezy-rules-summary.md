# EZY Portal API — Condensed Reference

Source: `mi-cerebro/hermes/knowledge/ezy_portal/ezy_rules.md` (OpenAPI/Swagger 2.0, 9,191 lines)

---

## Authentication Quick Reference

```bash
# Bearer (JWT) — most endpoints
curl -H "Authorization: Bearer $TOKEN" ...

# Cookie — /stats, /stats/quality only
curl -b "session=..." ...

# Tenant API Key — X-Api-Key header
curl -H "X-Api-Key: ten_..." ...
```

---

## Items API — Most Common Operations

### List Items (with prices)
```bash
GET /api/items/items?expand=prices&page=1&perPage=50&isActive=true&isSellable=true&sortBy=name
```

**Filters:** `query`, `itemType`, `isActive`, `isStock`, `isPurchasable`, `isSellable`, `itemGroup`, `tags` (AND), `excludeTags`, `stockQtyMoreThan`, `stockQtyLessThan`, `includeDeleted`

### Get Item by Code (with prices)
```bash
GET /api/items/items/by-code/ITEM-001?expand=prices
```

### Create Item (with nested UOMs, barcodes, categories, prices)
```json
POST /api/items/items
{
  "itemCode": "NEW-001",
  "name": "New Item",
  "itemType": "stock",
  "baseUom": "EA",
  "itemGroup": "ELECTRONICS",
  "itemCategory": "cat-uuid",
  "initialUOMs": [{ "factor": 1, "uomCode": "EA", "uomGroupId": "ug-uuid", "isDefaultSales": true }],
  "initialBarcodes": [{ "barcode": "1234567890123", "barcodeType": "ean13", "itemUomId": "uom-uuid", "isPrimary": true }],
  "initialCategories": [{ "categoryId": "cat-uuid" }],
  "prices": [{ "priceListId": "pl-uuid", "itemUomId": "uom-uuid", "price": 19.99, "currencyCode": "USD" }]
}
```

### Update Item (with nested UOM management)
```json
PATCH /api/items/items/{id}
{
  "name": "Updated Name",
  "version": 5,
  "uoms": [
    { "factor": 12, "uomCode": "DZ", "uomGroupId": "ug-uuid", "isDefaultPurchase": true },
    { "id": "existing-uom-uuid", "factor": 1, "delete": false },
    { "id": "old-uom-uuid", "delete": true }
  ]
}
```

### Search by Barcode
```bash
GET /barcodes?barcode=1234567890123
```

---

## Price Masking — Critical

```json
{
  "prices": [
    { "id": "price-1", "priceListId": "pl-1", "itemUomId": "uom-1", "price": 19.99, "currencyCode": "USD", "masked": false, "priceList": {...}, "itemUom": {...} },
    { "id": "price-2", "priceListId": "pl-2", "itemUomId": "uom-1", "price": null, "currencyCode": null, "masked": true, "priceList": {...}, "itemUom": {...} }
  ]
}
```

**Rule:** Always check `masked` before rendering `price`. Key without auth group = nothing masked.

---

## Pagination Standard

```json
{
  "data": [...],
  "total": 150,
  "page": 1,
  "perPage": 20,
  "totalPages": 8,
  "hasMore": true
}
```

---

## Variant Matrix

```bash
GET /api/items/items/select?variantRole=all&docType=purchase-order
```

Response includes `variantMatrix: { parentItemId, group, children[] }` where each child has `onHand`, `combinationKey`, `values`, `isPurchasable`, `isSellable`.

---

## Models Cheatsheet

| Model | Required Fields | Key Optional |
|-------|----------------|--------------|
| ItemCreateRequest | `itemCode`, `itemType`, `name` | `baseUom`, `itemGroup`, `initialUOMs[]`, `initialBarcodes[]`, `prices[]`, `itemCategory`, `priceListCode`, `description`, `sku`, `tags[]` |
| ItemUpdateRequest | (none — all optional) | `uoms[]` (ItemUOMInput), `barcodes[]` (ItemBarcodeInput), `categories[]` (ItemCategoryInput), `version` |
| ItemUOMCreateRequest | `factor`, `itemId`, `uomCode`, `uomGroupId` | `tempId`, `isDefaultPurchase`, `isDefaultSales` |
| ItemBarcodeCreateRequest | `barcode`, `barcodeType`, `itemId`, `itemUomId` | `isPrimary` |
| BulkUpsertItem (price) | `priceListId`, `itemUomId`, `price`, `currencyCode` | `id` (for update), `validFrom`, `validTo`, `delete` |

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request / validation error |
| 401 | Unauthorized (token expired → refresh) |
| 404 | Not found |
| 409 | Conflict (version mismatch or duplicate code) |
| 500 | Server error |

---

## Business Partners API — Quick Reference (Discovered 2026-06-22)

**Auth:** `X-Api-Key: ten_...` (same as Items module)

| Operation | Endpoint | Auth |
|-----------|----------|------|
| List all | `GET /api/business-partners/bp` | X-Api-Key |
| Get by ID | `GET /api/business-partners/bp/{id}` | X-Api-Key |
| List contacts | `GET /api/business-partners/contacts` | X-Api-Key |

**BusinessPartner key fields:** `id`, `code` (CL-XXX/PR-XXX), `name`, `legalName`, `status`, `roles[]`, `isCustomer`, `isVendor`, `isLead`, `taxId`, `fiscalData`, `currencyCode`, `priceListCode`, `creditLimit`, `onHold`, `ownerUserId`, `tags[]`, `notes`, `version`

**Contact key fields:** `id`, `bpId`, `firstName`, `lastName`, `role`, `isPrimary`, `email`, `phone`, `languageCode`, `active`, `version`

**See:** `references/business-partners-api.md` for full models and examples.

---

## Base URLs

| Environment | Base URL |
|-------------|----------|
| Production (gateway) | `https://app.portal.net/api/items/items` |
| Direct backend | `https://app.portal.net/api/items` |