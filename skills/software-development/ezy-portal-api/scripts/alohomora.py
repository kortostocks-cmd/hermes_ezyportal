#!/usr/bin/env python3
"""
alohomora — EZY Portal backup to Airtable

Usage:
    python3 alohomora.py <portal_api_key>
"""
import sys, json, ssl, urllib.request, time, subprocess
from datetime import date

# ── Config ───────────────────────────────────────────────────────────────────
TENANT_URL   = "https://vivero.ezyts.com"
BASE_ID      = "appIQ4f4j6c2bMPlb"
TBL_ITEMS    = "tblTXfSmRyVPV6Tv1"
TBL_BP       = "tblXKTjY4kjgnPdTb"
AIRTABLE_KEY = "patozWFMZn8GCrcQZ.8a5a54ace302fe272c9905e94c93889ba864a514a562d5613f15a799d78c815bb"
TODAY_ISO    = date.today().isoformat()   # 2025-06-24

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# ── Portal fetch (curl subprocess — urllib gets 401 with some keys) ───────────
def portal_get(path):
    url = f"{TENANT_URL}{path}"
    result = subprocess.run([
        "curl", "-s",
        "-H", f"X-Api-Key: {sys.argv[1]}",
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        url
    ], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")
    return json.loads(result.stdout)

def fetch_all_items():
    items, page = [], 1
    while True:
        d = portal_get(f"/api/items/items?perPage=100&page={page}&isActive=true&expand=prices")
        items.extend(d.get("data", []))
        if not d.get("hasMore"):
            break
        page += 1
    return items

def fetch_all_bp():
    bps, page = [], 1
    while True:
        d = portal_get(f"/api/business-partners/bp?page={page}&perPage=100")
        bps.extend(d.get("data", []))
        if not d.get("hasMore"):
            break
        page += 1
    return bps

# ── Airtable upsert (PATCH existing or create new) ─────────────────────────────
def at_upsert(table_id, records, key_field):
    """
    For each record: find by key_field, then PATCH or POST.
    Airtable PATCH /records/{id} updates fields on existing record.
    We first GET all records to build id map, then PATCH each.
    """
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table_id}"

    # Get existing records to map key -> record_id
    headers = {"Authorization": f"Bearer {AIRTABLE_KEY}", "Content-Type": "application/json"}

    existing = {}
    offset = None
    while True:
        get_url = url + f"?pageSize=100" + (f"&offset={offset}" if offset else "")
        req = urllib.request.Request(get_url, headers=headers)
        with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as r:
            d = json.loads(r.read())
        for rec in d.get("records", []):
            key_val = rec["fields"].get(key_field, "")
            if key_val:
                existing[key_val] = rec["id"]
        offset = d.get("offset")
        if not offset:
            break

    print(f"  [{table_id}] {len(existing)} registros existentes")

    patched = 0
    created = 0
    for record in records:
        key_val = record.get(key_field, "")
        fields = {k: v for k, v in record.items() if v is not None and v != ""}
        if key_val and key_val in existing:
            # PATCH existing
            patch_url = f"{url}/{existing[key_val]}"
            body = json.dumps({"fields": fields}).encode()
            patch_req = urllib.request.Request(patch_url, data=body, headers=headers, method="PATCH")
            with urllib.request.urlopen(patch_req, timeout=30, context=SSL_CTX) as r:
                json.loads(r.read())
            patched += 1
        else:
            # POST new
            body = json.dumps({"fields": fields}).encode()
            post_req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(post_req, timeout=30, context=SSL_CTX) as r:
                json.loads(r.read())
            created += 1
        time.sleep(0.26)  # rate limit 5/sec

    return patched, created

# ── Main ──────────────────────────────────────────────────────────────────────
print(f"[alohomora] {TODAY_ISO} — Backup EZY Portal → Airtable")
print(f"[alohomora] Portal: {TENANT_URL}")

items = fetch_all_items()
print(f"[alohomora] {len(items)} items obtenidos")

bps = fetch_all_bp()
print(f"[alohomora] {len(bps)} business partners obtenidos")

# Build item records (ONLY fields that exist in Airtable Items table)
# Airtable Items fields: Name, itemCode, stock, precio, categoria, Notes, ...
item_records = []
for it in items:
    price_val = None
    prices = it.get("prices") or []
    price_row = next((p for p in prices if p.get("priceListCode") == "SALE_SUPER"), None)
    if price_row and isinstance(price_row.get("price"), (int, float)):
        price_val = price_row["price"]

    fields = {
        "itemCode":   it.get("itemCode", ""),
        "Name":       it.get("name", ""),
        "stock":      it.get("itemStockTotal", 0) or 0,
        "categoria":  it.get("priceListCode", "") or "",
        "precio":     price_val,
        "Notes":      f"backup {TODAY_ISO}",
    }
    # Remove None/empty
    fields = {k: v for k, v in fields.items() if v is not None and v != ""}
    item_records.append(fields)

# Build BP records (only existing BPs fields: Name, code, roles, Status)
bp_records = []
for bp in bps:
    fields = {
        "code": bp.get("code", ""),
        "Name": bp.get("name", ""),
        "Status": f"backup {TODAY_ISO}",
    }
    fields = {k: v for k, v in fields.items() if v is not None and v != ""}
    bp_records.append(fields)

print()
print(f"[alohomora] Subiendo items...")
p, c = at_upsert(TBL_ITEMS, item_records, "itemCode")
print(f"[alohomora]   → {p} actualizados, {c} creados")

print(f"[alohomora] Subiendo business partners...")
p2, c2 = at_upsert(TBL_BP, bp_records, "code")
print(f"[alohomora]   → {p2} actualizados, {c2} creados")

print(f"\n✅ alohomora {TODAY_ISO} — Items: {len(items)} | BPs: {len(bps)}")