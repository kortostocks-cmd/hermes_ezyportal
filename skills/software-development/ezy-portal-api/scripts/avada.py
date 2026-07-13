#!/usr/bin/env python3
"""
Avada Kedavra — Full sheet update for vivero.ezyts.com

Updates all 3 tabs of the Google Sheet:
  INVENTARIO   — stock sync from portal
  REPORTS      — cost ranges, sale prices, margin %
  SOLD_AMOUNT  — units sold, total cost, total sale, margin

Requires:
  - EZY API key (ten_...) for items, POs, and SOs
  - Google OAuth token at ~/.hermes/profiles/ezy_portal_expert/google_token.json
  - Hermes venv Python with google-api-python-client installed
"""

import json, ssl, urllib.request, os, re, unicodedata
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

KEY = os.environ.get("EZY_KEY", "ten_YdKacbOqmKiaU96UBQWxjZ6cMZW6Y4uFpcvfx8cVrxE")
SHEET_ID = os.environ.get("SHEET_ID", "1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE")
BASE = "https://vivero.ezyts.com"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get(url):
    req = urllib.request.Request(url)
    req.add_header("X-Api-Key", KEY)
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        return json.loads(resp.read())

def nfkd(s):
    n = unicodedata.normalize("NFD", s.upper())
    n = re.sub(r"[\u0300-\u036f]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n

def pagin(u):
    r, p = [], 1
    while True:
        d = get(u.format(page=p))
        r.extend(d.get("data", []))
        if not d.get("hasMore"): break
        p += 1
    return r

def read_sheet(rng, svc):
    return svc.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=rng).execute().get("values", [])

def write_sheet(rng, data, svc):
    svc.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=rng,
        valueInputOption="USER_ENTERED", body={"values": data}).execute()

def main():
    print("=== AVADA KEDAVRA ===")

    # Fetch portal items (stock + name mapping)
    items = pagin(f"{BASE}/api/items/items?isActive=true&perPage=100&page={{page}}")
    item_stock = {}
    code_to_name = {}
    for d in items:
        item_stock[d["name"]] = d.get("itemStockTotal", 0)
        code_to_name[d.get("itemCode")] = d["name"]
    print(f"Items: {len(item_stock)}")

    # Fetch purchase orders (cost data)
    all_po = pagin(f"{BASE}/api/commerce/purchase-orders?perPage=50&page={{page}}")
    item_costs = {}
    latest_cost = {}
    for po in all_po:
        det = get(f"{BASE}/api/commerce/purchase-orders/{po['id']}?expand=lines")
        for line in det.get("lines", []):
            c = line.get("itemCode")
            p = line.get("unitPrice")
            dt = po.get("documentDate", "")[:10]
            if c and p is not None:
                if c not in item_costs: item_costs[c] = []
                if p not in item_costs[c]: item_costs[c].append(p)
                if c not in latest_cost or dt > latest_cost.get(c+"_d",""):
                    latest_cost[c] = p
                    latest_cost[c+"_d"] = dt
    print(f"POs: {len(all_po)}")

    # Fetch sales orders (sale data)
    all_so = pagin(f"{BASE}/api/commerce/sales-orders?perPage=50&page={{page}}")
    sold_qty, sold_amount, sold_cost, latest_sale = {}, {}, {}, {}
    for so in all_so:
        sd = so.get("documentDate", "")[:10]
        det = get(f"{BASE}/api/commerce/sales-orders/{so['id']}?expand=lines")
        for line in det.get("lines", []):
            nm, cd = line.get("itemName"), line.get("itemCode")
            q, pr = line.get("quantity") or 0, line.get("unitPrice") or 0
            if not nm: continue
            k = nfkd(nm)
            sold_qty[k] = sold_qty.get(k,0) + q
            sold_amount[k] = sold_amount.get(k,0) + (q*pr)
            if cd and cd in latest_cost: sold_cost[k] = sold_cost.get(k,0) + (q*latest_cost[cd])
            if k not in latest_sale or sd > latest_sale.get(k+"_d",""):
                latest_sale[k] = pr
                latest_sale[k+"_d"] = sd
    print(f"SOs: {len(all_so)}, sold items: {len(sold_qty)}")

    # Google Sheets auth
    TS = os.path.expanduser("~/.hermes/profiles/ezy_portal_expert/google_token.json")
    creds = Credentials.from_authorized_user_file(TS, ["https://www.googleapis.com/auth/spreadsheets"])
    if creds.expired and creds.refresh_token: creds.refresh(Request())
    svc = build("sheets", "v4", credentials=creds)

    # === INVENTARIO ===
    print("\n--- INVENTARIO ---")
    sd = read_sheet("INVENTARIO!A1:I500", svc)
    rows = sd[1:]
    u = 0
    for row in rows:
        nm = str(row[0]).strip() if row and len(row) > 0 and row[0] else ""
        if not nm: continue
        k = nfkd(nm)
        sk = 0
        for pn, pv in item_stock.items():
            if nfkd(pn) == k: sk = pv; break
        while len(row) < 3: row.append("")
        if str(sk) != str(row[2]).strip():
            row[2] = str(sk)
            u += 1
    write_sheet("INVENTARIO!A1:I"+str(len(sd)), [sd[0]] + rows, svc)
    print(f"  Stock updates: {u}")

    # === REPORTS ===
    print("--- REPORTS ---")
    sd = read_sheet("REPORTS!A1:D200", svc)
    rows = sd[1:]
    u = 0
    for row in rows:
        nm = str(row[0]).strip() if row and len(row) > 0 and row[0] else ""
        if not nm: continue
        k = nfkd(nm)
        ic = None
        for c, n in code_to_name.items():
            if nfkd(n) == k: ic = c; break
        cs = item_costs.get(ic, [])
        while len(row) < 4: row.append("")
        if cs:
            css = sorted(set(cs))
            row[1] = f"${css[0]}" if len(css) == 1 else f"${css[0]}-${css[-1]}"
        else: row[1] = ""
        sal = latest_sale.get(k)
        row[2] = f"${sal}" if sal else ""
        if cs and sal:
            mn, mx = min(cs), max(cs)
            ml = ((sal - mx) / sal) * 100
            mh = ((sal - mn) / sal) * 100
            row[3] = f"{ml:.0f}%" if abs(ml-mh) < 0.5 else f"{ml:.0f}-{mh:.0f}%"
        else: row[3] = ""
        u += 1
    write_sheet("REPORTS!A1:D"+str(len(sd)), [sd[0]] + rows, svc)
    print(f"  Rows: {u}")

    # === SOLD_AMOUNT ===
    print("--- SOLD_AMOUNT ---")
    sd = read_sheet("'SOLD_AMOUNT '!A1:E200", svc)
    rows = sd[1:]
    tq, tc, ts = 0, 0, 0
    for row in rows:
        nm = str(row[0]).strip() if row and len(row) > 0 and row[0] else ""
        if nm == "TOTAL":
            while len(row) < 5: row.append("")
            row[1], row[2], row[3], row[4] = str(int(tq)), f"${tc:.2f}", f"${ts:.2f}", f"${ts-tc:.2f}"
            continue
        if not nm: continue
        k = nfkd(nm)
        q, co, sa = sold_qty.get(k,0), sold_cost.get(k,0), sold_amount.get(k,0)
        while len(row) < 5: row.append("")
        row[1] = str(int(q)) if q else ""
        row[2] = f"${co:.2f}" if co else ""
        row[3] = f"${sa:.2f}" if sa else ""
        row[4] = f"${sa-co:.2f}" if (sa or co) else ""
        tq += q; tc += co; ts += sa
    write_sheet("'SOLD_AMOUNT '!A1:E"+str(len(sd)), [sd[0]] + rows, svc)

    print(f"\n{'='*40}")
    print(f"✅ AVADA KEDAVRA")
    print(f"INVENTARIO: stock sync")
    print(f"REPORTS: {u} rows")
    print(f"SOLD_AMOUNT: {int(tq)}un | ${tc:.2f} | ${ts:.2f} | ${ts-tc:.2f}")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()