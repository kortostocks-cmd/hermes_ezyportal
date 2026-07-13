# Pricing-Tax Endpoint (vivero tenant)

## Endpoint

```
GET https://vivero.ezyts.com/api/pricing-tax/price-lists
```

Requires `X-Api-Key: ten_...` (same tenant API key as Items).

**Pitfall**: New API keys may return **401 from Python urllib** but work fine with curl
for this endpoint. Use curl via subprocess if Python urllib fails.

## vivero Price Lists (Jun 30 2026 — all 9 lists active)

| code | id | name | currency |
|------|----|------|----------|
| COST_A&G | 629c947f-5edf-441d-9a70-e8d571e5b1d8 | AGRO & GARDENS | USD |
| COST_IAN | 31000d32-75f2-467a-b2f8-e5f991aff36c | Costo - Viveros Ian | USD |
| COST_JARDIN | ccf36882-505b-420f-89f3-07273f024124 | Costo - Jardin | USD |
| COST_SARA | 607aa5ef-e4a9-4d0b-94dd-6eb04dea83bc | Costo - Sara | USD |
| COST_EDWIN | 02037417-1ac1-45bb-b3b4-df022ff6085d | Costo - Edwin | USD |
| COST_HACIENDA | 1be181ec-69d9-4661-bebd-e0a09f8ee851 | Costo - Hacienda | USD |
| COST_ISMAEL | 96c2a3fb-380b-41fd-861b-87076ac02bc6 | Costo - Ismael | USD |
| SALE_PUBLIC | 0455a655-460f-4a75-b4f7-e1d41b5e6886 | Venta Publico | USD |
| SALE_SUPER | e4d473ef-e97e-4258-8391-594b9d0eb9f0 | Venta Super | USD |

## Adding a Price via PATCH

```python
import urllib.request, json, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

item_id = "665396e4-db47-415d-b870-fcfea75120f8"
url = f"https://vivero.ezyts.com/api/items/items/{item_id}"

payload = json.dumps({
    "version": 1,  # current version from GET
    "prices": [{
        "priceListId": "1be181ec-69d9-4661-bebd-e0a09f8ee851",
        "priceListCode": "COST_HACIENDA",
        "price": 20.00,
        "currencyCode": "USD"
    }]
})

req = urllib.request.Request(url, data=payload.encode(), method="PATCH")
req.add_header("X-Api-Key", "ten_...")
req.add_header("User-Agent", "Mozilla/5.0")
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
    result = json.loads(resp.read())
    print("version after PATCH:", result["version"])  # 2 = success
```

**Note**: `prices` in response will be `[]` (masked) — check `version` incremented instead.