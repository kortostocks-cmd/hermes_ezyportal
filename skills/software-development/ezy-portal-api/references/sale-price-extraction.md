# Sale Price Extraction from Sales Orders — Jul 10 2026

## Problem
The portal has multiple API keys with different permission scopes. The "items" key
(`ten_YdKacbOqmKiaU96UBQWxjZ6cMZW6Y4uFpcvfx8cVrxE`) does NOT grant access to the
`prices` array on items — list and `by-code` endpoints return `prices: null`
even with `?expand=prices`.

This means we **cannot extract SALE_EXTRA sale prices directly from the items API.**

## Workaround — Pull from Sales Orders

The items key (`ten_YdKacbOqmKiaU96UBQWxjZ6cMZW6Y4uFpcvfx8cVrxE`) returns items WITHOUT prices but DOES return sales orders with `line[].unitPrice` — this IS the SALE_EXTRA price (SOs always use SALE_EXTRA price list).

**⚠️ As of Jul 10 2026**: The previously-working PO-access key (`ten_PRQ2XeyfLOvi_8Vf1528LoJgV7IlTqTqcQi5LLO4owg`) has expired. The `ten_YdKacb...` key now serves for items + POs + SOs.
with `line[].unitPrice` — this IS the SALE_EXTRA price (SOs always use SALE_EXTRA price list).

### Pattern (verified Jul 10 2026)

```python
def get(url):
    req = urllib.request.Request(url)
    req.add_header("X-Api-Key", KEY); req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        return json.loads(resp.read())

# 1. List SOs (sorted desc by date)
sos = []
page = 1
while True:
    data = get(f"{BASE}/api/commerce/sales-orders?perPage=50&page={page}"
               f"&sortBy=documentDate&sortDirection=desc")
    sos.extend(data.get("data", []))
    if not data.get("hasMore"): break
    page += 1

# 2. Fetch each SO individually to get lines (expand=lines on LIST returns empty)
latest_price = {}
latest_date = {}
for so in sorted(sos, key=lambda x: x.get("documentDate") or "", reverse=True):
    so_id = so["id"]
    so_date = so.get("documentDate", "")[:10]
    detail = get(f"{BASE}/api/commerce/sales-orders/{so_id}?expand=lines")
    for line in detail.get("lines", []):
        code = line.get("itemCode")
        name = line.get("itemName")
        price = line.get("unitPrice", 0)
        if not code or not price: continue
        for key in [name, code]:
            if key not in latest_price or so_date > latest_date.get(key, ""):
                latest_price[key] = price
                latest_date[key] = so_date
```

### IMPORTANT Quirk
- `expand=lines` on the LIST endpoint returns SOs/POs with EMPTY / null `lines` array.
- You MUST fetch each document individually: `GET /api/commerce/sales-orders/{id}?expand=lines` or `GET /api/commerce/purchase-orders/{id}?expand=lines`
- This makes it N+1: ~50 SOs × ~1 sec each = ~50 seconds minimum. Needs 300s+ timeout.
### Loop timing — need 300s timeout when iterating 50+ SOs.

## What This Is and Is NOT
- This IS the SALE price (venta) used at sale time — comes from SALE_EXTRA price list.
- This is NOT a cost/compra price — don't put in COST_MIJARDIN/COST_HACIENDA columns.
- For INVENTARIO sheet: use for sale price column (B) if user asks for SALE_EXTRA.

## Alternative — New API Key
Create a new API key in Portal UI (Settings > API Keys) with read access to prices.
Cleaner but requires user action in portal UI.
