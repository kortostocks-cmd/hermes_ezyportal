# Purchase Order Cost Extraction (Jul 10 2026)

## Endpoint Discovery

The purchase order API lives at `/api/commerce/purchase-orders` — NOT `/api/purchases/` (404).

**Different API key required**: The main vivero tenant key (`ten_YdKacb...`) does NOT have access. A dedicated key `ten_PRQ2XeyfLOvi_8Vf1528LoJgV7IlTqTqcQi5LLO4owg` is required.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/commerce/purchase-orders?perPage=50&page=1&sortBy=createdAt&sortDirection=desc` | List POs |
| `GET /api/commerce/purchase-orders/{id}?expand=lines` | Single PO with line items |

**⚠️ List-quirk**: `expand=lines` on the LIST endpoint returns POs with empty `lines`. Only fetching a single PO by UUID returns actual line items. To extract all costs:
1. List POs (no expand needed)
2. Fetch each PO individually with `expand=lines`
3. Extract `unitPrice` from each line

## Line Item Fields (from single PO fetch)

```
lineNumber, itemId, itemCode, itemName, description, quantity, unitOfMeasure,
unitPrice, discountPercent, priceAfterDiscount, taxRate, taxAmount, lineTotal,
taxCategoryId/Code/Name, orderedQty, fulfilledQty, fulfillmentStatus,
warehouseId/Code/Name, uomCode, conversionFactor, baseQuantity
```

Cost is in `unitPrice` — NOT `unitCost` or `cost`.

## Top-Level PO Fields

`documentNumber`, `bpName`, `bpCode`, `bpId`, `priceListCode`, `priceListId`,
`paymentTermsId/Code/Name`, `subTotal`, `grandTotal`, `status`, `documentDate`,
`deliveryDate`, `vendorRefNumber`

## Verified Suppliers & Cost Price Lists

| Supplier | Price List Code | Price List ID | Items Count |
|----------|----------------|---------------|-------------|
| Viveros Mi Jardin | COST_MIJARDIN | fbd1e2fc-9386-4e7b-8ee-b4ec501eead1a | 33 |
| HACIENDA CAFETALERA | COST_HACIENDA | 0dbfdd7b-db25-4040-a90b-5f452378de86 | 27 |
| DISTRIBUIDORA CHIRIQUI | COST_EDWIN | d1eeecb8-e5a8-4f89-90d8-fc4a6480f902 | 12 |
| Agro&Gardens | COST_A&G | 3957783e-b384-4bf9-a6a5-7982f7ad8d2f | 8 |
| Vivero Sara Cely | COST_SARACELY | 65399687-8f36-46af-8145-01b5d50198f0 | 8 |
| Vivero Sugey | COST_SUGEY | e38bab32-70c5-4b66-b16c-dc5cdb2dbaa4 | 5 |
| Viveros ian | COST_MIJARDIN (same PL as Mi Jardin) | — | 5 |

## Not Covered by POs (no purchase orders exist)

- Vivero Rose (TIERRA NEGRA $0.95, ABONO ORGANICO $0.55, CASCARILLA DE ARROZ $0.55)
- These items were created directly in the portal, not purchased through the PO system.
- No cost column exists for them in the current sheet layout.

## Cost-Fill Script Pattern

```python
# 1. Build cost lookup from POs
supplier_costs = {}  # itemCode -> {priceListCode: unitPrice}
data = get(f"{BASE}/api/commerce/purchase-orders?perPage=50&page=1")
for po in data.get("data", []):
    detail = get(f"{BASE}/api/commerce/purchase-orders/{po['id']}?expand=lines")
    for line in detail.get("lines", []):
        code = line["itemCode"]
        pl = detail["priceListCode"]
        price = line["unitPrice"]
        if code not in supplier_costs:
            supplier_costs[code] = {}
        if pl not in supplier_costs[code]:
            supplier_costs[code][pl] = price

# 2. Column mapping (price list code → sheet column index)
code_to_col = {
    "COST_MIJARDIN": 3, "COST_SARACELY": 4, "COST_HACIENDA": 5,
    "COST_EDWIN": 6, "COST_SUGEY": 7, "COST_A&G": 8
}

# 3. Fill costs in sheet
for row in rows:
    name = str(row[0]).strip().upper()
    # Find matching item code for this plant name
    # Then for each PL code, if cost exists, fill column
```