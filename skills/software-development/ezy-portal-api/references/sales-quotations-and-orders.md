# Sales Quotations & Sales Orders (vivero tenant)

## Endpoint Comparison

| Feature | Sales Quotations | Sales Orders |
|---------|-----------------|--------------|
| Endpoint | `POST /api/commerce/sales-quotations` | `POST /api/commerce/sales-orders` |
| Doc Prefix | `SQ-2026-000XXX` | `SO-2026-000XXX` |
| Status | DRAFT | DRAFT |
| Same payload? | Yes | Yes |

Both accept the same payload structure. Use Sales Orders for actual sales (Venta), Sales Quotations for quotes (Cotizaciones).

## Required Line Fields
```python
{
    "lineNumber": 1,                    # Sequential from 1 (NOT 0 — "duplicate lineNumber values: [0]" error)
    "itemId": "uuid-of-item",
    "itemCode": "PL-SOMETHING",
    "itemName": "Name for display",
    "description": "Line description",
    "quantity": 10.0,                   # field is "quantity" NOT "qty"
    "unitPrice": 1.75,
    "warehouseId": "uuid-warehouse",    # REQUIRED per line — never hardcode, fetch fresh each session
    "warehouseCode": "PRINCIPAL",       # NOT "PRIN" on new portal (Jul 2026+); code=PRINCIPAL, name=ALMACEN PRINCIPAL
    "warehouseName": "ALMACEN PRINCIPAL",
    "taxCategoryId": "097722df-e70c-4380-9372-a863c67c2bca",  # EXCENTO
    "taxCategoryCode": "EXCENTO",
    "taxCategoryName": "Excento",
    "uomCode": "EA"
}
```

## Date Format (ISO 8601)
Both `documentDate` and `validUntil` require ISO 8601 with T:
```python
"documentDate": "2026-06-04T00:00:00Z",
"validUntil": "2026-06-04T00:00:00Z"
```
Plain `"2026-06-04"` fails with: `cannot parse "" as "T"`.

## Reference Field
Use top-level `reference` field to link the SO to its source document:
```python
"reference": "Factura No.741"
```

## Warehouse Discovery
- **Endpoint**: `GET /api/inventory/warehouses` returns a **flat LIST** (not a paginated dict with `data` key). `/api/warehouses` and `/api/warehouses/warehouses` return 404 on the vivero tenant.
- **Confirmed (Aug 2026)**: code=`PRINCIPAL` (NOT `PRIN`), name=`ALMACEN PRINCIPAL`, description=`METRO PARK`, id=`95c298a9-54d8-4c51-ae78-5c3b76cac657`
- **Always fetch fresh**: warehouse IDs may change between tenants/sessions
- Example: `curl -s ... https://vivero.ezyts.com/api/warehouses` → `[{"id":"...","code":"PRINCIPAL","name":"ALMACEN PRINCIPAL",...}]`

## Payment Terms Discovery
- **Endpoint**: `GET /api/business-partners/payment-terms` returns a **flat LIST**
- **vivero tenant (Jul 2026)**: COD (Contra Reembolso), DUE_RECEIPT (Pagadero a la Recepción), NET15/30/45/60/90, PREPAY (Pago Anticipado)
- **Use for invoice with cash payment**: COD or DUE_RECEIPT
- Example: `curl -s ... https://vivero.ezyts.com/api/business-partners/payment-terms`

## Important: `expand=lines` may return empty
Even when lines are saved successfully (grandTotal is correct), `GET` with `?expand=lines` may return `lines: []`. Trust `grandTotal` as ground truth for whether data was saved.

## Sales Orders: Stricter Validation
Sales Orders validate `isActive=true` on each line item. If any item is inactive, the entire request fails with:
```
"code": "BAD_REQUEST",
"message": "Line N: Item: item is not active"
```
Fix: PATCH the item to reactivate before creating the order. Use `PATCH /api/items/items/{id}` with `{"isActive": True, "version": version}`.

## Price Lists for SUPER EXTRA (Updated Aug 2026)
- **SALE_PUBLIC and SALE_SUPER no longer exist** in the tenant. Only SALE_EXTRA is active.
- **SUPER EXTRA client** → Use `SALE_EXTRA` (id=`13ce22b6-0b29-4029-be65-42e8c23cb239`) for ALL branches.
- Always verify fresh: `GET /api/pricing-tax/price-lists?perPage=50`

## SUPER EXTRA Branches (vivero tenant, Jul 2026)
1. via israel (CL-0035, id=32249c40-4c89-4fdf-a381-73969dba188d)
2. los pueblos (CL-0005, id=a8cea960-d200-4222-8654-6cda0093d6b9)
3. albrook (CL-0017, id=db64ad3e-a54c-4f15-b15b-d60dba3917a4)
4. monterico (CL-0006, id=083fb553-ca57-4678-ba12-9ae1cf4b90ed)
5. el Lago (CL-0019, id=78532e5e-caa7-4863-aa80-7090e8e22257)
6. las acacias (CL-0004, id=6bf480fd-4f62-41da-a4a6-353541fce16f)

## Workflow: Vivero Rose Invoice → Sales Order
1. Parse invoice photo: items, quantities, unit prices, totals
2. Map items to portal codes via `GET /api/items/items/by-code/{code}`
3. Check `isActive` — reactivate inactive items via PATCH
4. Exclude items marked "N/C" and non-plant items (unless user says include)
5. **Show pre-creation summary to user and wait for confirmation**
6. POST to `/api/commerce/sales-orders` (or `/api/commerce/sales-quotations`)
7. On error, check which line/item caused it