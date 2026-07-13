# Sales Order Creation via curl (discovered Aug 1 2026)

## Context
Python `urllib` returns 401 with all newer API keys (`ten_3HW_...` onwards), even with Cloudflare workaround. Only `curl` works for SO creation.

## Workflow

### 1. Fetch item IDs fresh
```bash
python3 /tmp/get_ids.py
```
Script content:
```python
import subprocess, json
KEY = "ten_Zk271QDTbmEUkcXD4pu4LKvMSgv0n8-b6oyz6SCBjxU"
BASE = "https://vivero.ezyts.com"
codes = ["PL-HIERBA-BUENA", "PL-ROMERO", ...]
for code in codes:
    r = subprocess.run(["curl","-s","-H",f"X-Api-Key: {KEY}",f"{BASE}/api/items/items/by-code/{code}"],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    print(f'{d["itemCode"]:35s} | {d["id"]}')
```

**CRITICAL**: Do NOT reuse item IDs from earlier `execute_code` calls in the same session — they are STALE. The by-code endpoint returns DIFFERENT IDs than the list endpoint. Run a dedicated `curl | python3` fetch at the START of the SO creation entry point.

**Also**: The by-code endpoint and the `/api/items/items` list endpoint return DIFFERENT UUIDs for the SAME itemCode. The list endpoint IDs are stale/divergent. Always use by-code IDs in SO line payloads. Using list-endpoint IDs gives `"Item: item not found"` on ALL lines except the ones whose IDs coincidentally match.

### 2. Build JSON payload
Write to `/tmp/so_<branch>.json`:
```json
{
  "bpId": "78532e5e-caa7-4863-aa80-7090e8e22257",
  "bpCode": "CL-0019",
  "bpName": "SUPER EXTRA el Lago",
  "documentDate": "2026-06-05T00:00:00Z",
  "validUntil": "2026-07-05T00:00:00Z",
  "paymentTermsId": "9025dae9-6d36-465b-a98f-733966ef8f37",
  "priceListId": "13ce22b6-0b29-4029-be65-42e8c23cb239",
  "priceListCode": "SALE_EXTRA",
  "currency": "USD",
  "reference": "Factura No.745",
  "lines": [
    {
      "lineNumber": 1,
      "itemId": "062d1a46-052c-4708-9133-07fe2a81233e",
      "itemCode": "PL-HIERBA-BUENA",
      "itemName": "HIERBA BUENA",
      "description": "HIERBA BUENA VR",
      "quantity": 6,
      "unitPrice": 1.75,
      "warehouseId": "95c298a9-54d8-4c51-ae78-5c3b76cac657",
      "warehouseCode": "PRINCIPAL",
      "warehouseName": "ALMACEN PRINCIPAL",
      "taxCategoryId": "097722df-e70c-4380-9372-a863c67c2bca",
      "taxCategoryCode": "EXCENTO",
      "taxCategoryName": "Excento",
      "uomCode": "EA"
    }
  ]
}
```

**REQUIRED fields per line** (all are mandatory — missing any gives "incomplete data"):
- `lineNumber` (1-indexed)
- `itemId` (UUID from by-code)
- `itemCode`
- `itemName`
- `description`
- `quantity` (NOT `qty`)
- `unitPrice`
- `warehouseId`
- `warehouseCode`
- `warehouseName`
- `taxCategoryId`
- `taxCategoryCode`
- `taxCategoryName`
- `uomCode`

### 3. Send via curl
```bash
curl -s -X POST "https://vivero.ezyts.com/api/commerce/sales-orders" \
  -H "X-Api-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/so_branch.json | python3 -c "
import sys,json
d=json.load(sys.stdin)
num = d.get('documentNumber') or d.get('orderNumber')
print(f'Order: {num}')
print(f'Lines: {len(d.get(\"lines\",[]))}')
print(f'Total: {d.get(\"totalAmount\")}')
print(f'Status: {d.get(\"status\")}')
"
```

### 4. Response parsing
- Response key is `documentNumber` (NOT `orderNumber`)
- `totalAmount` may be `null` for draft orders
- Status is always `DRAFT`
- Confirm line count matches expected

### Known Working IDs (Aug 1 2026 vivero tenant)
- Warehouse PRINCIPAL: `95c298a9-54d8-4c51-ae78-5c3b76cac657` (code: PRINCIPAL, name: ALMACEN PRINCIPAL)
- Tax cat EXCENTO: `097722df-e70c-4380-9372-a863c67c2bca` (code: EXCENTO)
- SALE_EXTRA: `13ce22b6-0b29-4029-be65-42e8c23cb239`
- Payment terms: `9025dae9-6d36-465b-a98f-733966ef8f37`
- Client EL LAGO: `78532e5e-caa7-4863-aa80-7090e8e22257` (CL-0019)
- Client LOS PUEBLOS: `a8cea960-d200-4222-8654-6cda0093d6b9` (CL-0005)
- Client LAS TABLAS: `cbb72b57-a924-408d-9772-ca7de21834ae` (CL-0024)
- Client CHORRERA: `3d7f8040-61ea-45dd-b42d-97721513f018` (CL-0002)
- Client ALBROOK: `db64ad3e-a54c-4f15-b15b-d60dba3917a4` (CL-0017)
- Client MARQUEZA: `36ebc81e-c06d-450a-88e9-ad722e3bcd73` (CL-0030)
- Client VIA ISRAEL: `32249c40-4c89-4fdf-a381-73969dba188d` (CL-0035)