#!/usr/bin/env python3
"""
Avada Kedavra — Full EZY → Sheet sync

READ → DIFF → APPLY

Fase 1: READ  — fetch portal items, POs, SOs
Fase 2: DIFF  — compare vs Google Sheets, print gaps
Fase 3: APPLY — sync changes (requires --apply flag)

Usage:
    python3 avada.py              # READ + DIFF only (dry-run)
    python3 avada.py --apply      # READ + DIFF + APPLY
"""

import json, ssl, urllib.request, os, re, unicodedata, sys
sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent/venv/lib/python3.11/site-packages"))
from collections import defaultdict
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

KEY = os.environ.get("EZY_KEY", "ten_BvfgJJOvXHbkjuQKMpscKmFo92HMwl3-2UNsbVWYq4g")
SHEET_ID = os.environ.get("SHEET_ID", "1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE")
BASE = "https://vivero.ezyts.com"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SUPPLIER_ORDER = ["COST_MIJARDIN", "COST_EDWIN", "COST_HACIENDA", "COST_A&G", "COST_SARACELY", "COST_SUGEY", "COST_IAN"]
COL_INDEX = {s: i for i, s in enumerate(SUPPLIER_ORDER, 3)}  # col D-J
SUPPLIER_TO_COL = {
    "COST_MIJARDIN": "COST_MIJARDIN", "COST_EDWIN": "COST_EDWIN",
    "COST_HACIENDA": "COST_HACIENDA", "COST_A&G": "COST_A&G",
    "COST_SARACELY": "COST_SARACELY", "COST_SUGEY": "COST_SUGEY",
    "COST_IAN": "COST_IAN",
    "SALE_PUBLIC": "COST_SARACELY", "COST_JARDIN": "COST_MIJARDIN",
}

def get(url):
    req = urllib.request.Request(url)
    req.add_header("X-Api-Key", KEY)
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        return json.loads(resp.read())

def nfkd(s):
    n = unicodedata.normalize("NFD", (s or '').upper())
    n = re.sub(r"[\u0300-\u036f]", "", n)
    return re.sub(r"\s+", " ", n).strip()

def name_key(n):
    n = (n or '').upper()
    if n in ("POTHOS", "PHOTUS"):
        return "PHOTUS"
    return nfkd(n)

def pagin(u):
    r, p = [], 1
    while True:
        d = get(u.format(page=p))
        r.extend(d.get("data", []))
        if not d.get("hasMore"):
            break
        p += 1
    return r

def parse_price_str(s):
    if not s or not s.strip():
        return set()
    s = s.strip()
    if '-' in s:
        m = re.match(r'\$?(\d+(?:\.\d+)?)-\$?(\d+(?:\.\d+)?)', s)
        if m:
            return {round(float(m.group(1)), 2), round(float(m.group(2)), 2)}
    m = re.match(r'\$?(\d+(?:\.\d+)?)', s)
    if m:
        return {round(float(m.group(1)), 2)}
    return set()

def fmt_price(p):
    if not p:
        return ""
    ps = sorted(set(p))
    if len(ps) == 1:
        return f"${ps[0]:.2f}"
    return f"${ps[0]:.2f}-${ps[-1]:.2f}"

def read_sheet(rng, svc):
    return svc.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=rng).execute().get("values", [])

def write_sheet(rng, data, svc):
    svc.spreadsheets().values().update(spreadsheetId=SHEET_ID, range=rng,
        valueInputOption="USER_ENTERED", body={"values": data}).execute()

def clear_range(rng, svc):
    svc.spreadsheets().values().clear(spreadsheetId=SHEET_ID, range=rng, body={}).execute()

# ===== FASE 1: READ =====

def read_phase():
    print("=== FASE 1: READ ===\n")

    items = pagin(f"{BASE}/api/items/items?isActive=true&perPage=100&page={{page}}")
    print(f"  Items: {len(items)}")

    pos = pagin(f"{BASE}/api/commerce/purchase-orders?perPage=50&page={{page}}")
    po_details = []
    for po in pos:
        try:
            det = get(f"{BASE}/api/commerce/purchase-orders/{po['id']}?expand=lines")
            po_details.append(det)
        except:
            pass
    print(f"  POs: {len(pos)}, con detalle: {len(po_details)}")

    sos = pagin(f"{BASE}/api/commerce/sales-orders?perPage=50&page={{page}}")
    so_details = []
    for so in sos:
        try:
            det = get(f"{BASE}/api/commerce/sales-orders/{so['id']}?expand=lines")
            so_details.append(det)
        except:
            pass
    print(f"  SOs: {len(sos)}, con detalle: {len(so_details)}")

    return items, po_details, so_details

# ===== FASE 2: DIFF =====

def diff_phase(items, po_details, so_details, svc):
    print("\n=== FASE 2: DIFF ===\n")

    # Build portal cost map (from POs)
    portal_cost = defaultdict(lambda: defaultdict(list))
    for po in po_details:
        col = SUPPLIER_TO_COL.get(po.get('priceListCode', ''))
        if not col:
            continue
        for line in po.get('lines', []):
            nk_raw = (line.get('itemDescription') or line.get('itemName') or '').upper()
            if nk_raw in ("AGAVE AMARILLO", "AGAVE VERDE"):
                nk = name_key("AGAVE GIGANTE")
            else:
                nk = name_key(nk_raw)
            up = float(line.get('unitPrice', 0) or 0)
            if up > 0:
                portal_cost[nk][col].append(up)

    # Portal stock + sale price
    portal_stock = {}
    portal_sale = {}
    portal_display = {}
    for it in items:
        nk = name_key(it['name'])
        portal_stock[nk] = it.get('itemStockTotal', 0) or 0
        portal_display[nk] = it['name'].upper()
        for p in it.get('prices', []):
            if p.get('priceListCode') == 'SALE_EXTRA':
                portal_sale[nk] = p.get('price', 0)
                break

    # SO sale data
    so_sale = defaultdict(lambda: {"qty": 0.0, "sale": 0.0})
    for so in so_details:
        sub = float(so.get('subTotal', 0) or 0)
        grand = float(so.get('grandTotal', 0) or 0)
        for line in so.get('lines', []):
            nk = name_key(line.get('itemDescription') or line.get('itemName'))
            if not nk:
                continue
            qty = float(line.get('quantity', 0))
            up = float(line.get('unitPrice', 0))
            lt = qty * up
            if sub > 0 and grand < sub:
                lt_after = lt * (grand / sub)
            else:
                lt_after = lt
            so_sale[nk]["qty"] += qty
            so_sale[nk]["sale"] += lt_after

    # Read INVENTARIO
    INV = read_sheet("INVENTARIO!A1:J500", svc)
    inv_set = set()
    inv_stock = {}
    inv_costs = defaultdict(dict)
    for r in INV[1:]:
        if not r or not r[0]:
            continue
        nk = name_key(r[0])
        inv_set.add(nk)
        try:
            inv_stock[nk] = int(float(r[2])) if r[2].strip() else 0
        except:
            inv_stock[nk] = 0
        for i, col in enumerate(SUPPLIER_ORDER):
            v = r[3+i].strip() if len(r) > 3+i else ""
            inv_costs[nk][col] = parse_price_str(v)

    # Read REPORTS
    REP = read_sheet("REPORTS!A1:D500", svc)
    rep_set = set()
    rep_cost = defaultdict(set)
    for r in REP[1:]:
        if not r or not r[0]:
            continue
        nk = name_key(r[0])
        rep_set.add(nk)
        rep_cost[nk] = parse_price_str(r[1] if len(r) > 1 else "")

    # Read SOLD_AMOUNT
    SA = read_sheet("'SOLD_AMOUNT '!A1:E200", svc)
    sa_set = set()
    for r in SA[1:]:
        if r and r[0] and r[0].upper() != "TOTAL":
            sa_set.add(name_key(r[0]))

    # DIFF 1: Portal items vs INVENTARIO
    portal_nk_set = set(portal_stock.keys())
    missing_in_inv = portal_nk_set - inv_set
    extra_in_inv = inv_set - portal_nk_set

    print(f"Portal items: {len(portal_nk_set)}")
    print(f"INVENTARIO items: {len(inv_set)}")
    if missing_in_inv:
        print(f"\n  ⚠ FALTAN en INVENTARIO ({len(missing_in_inv)}):")
        for nk in sorted(missing_in_inv):
            print(f"     + {portal_display.get(nk, nk)} (stock={portal_stock[nk]})")
    if extra_in_inv:
        print(f"\n  ⚠ EXTRA en INVENTARIO (no están en portal) ({len(extra_in_inv)}):")
        for nk in sorted(extra_in_inv):
            print(f"     - {nk}")

    # DIFF 2: Stock mismatch
    stock_diff = []
    for nk in portal_nk_set & inv_set:
        pstk = portal_stock[nk]
        isk = inv_stock.get(nk, 0)
        if pstk != isk:
            stock_diff.append((nk, portal_display.get(nk, nk), pstk, isk))

    print(f"\n  Stock mismatches: {len(stock_diff)}")
    for nk, nm, p, s in stock_diff[:20]:
        print(f"     {nm:<35} portal={p:>5} sheet={s:>5}")

    # DIFF 3: Items with stock but no cost
    items_stock_but_no_cost = []
    for nk in portal_nk_set:
        if portal_stock[nk] > 0:
            has_cost = any(cost for cost in portal_cost.get(nk, {}).values())
            has_inv_cost = any(cost for cost in inv_costs.get(nk, {}).values())
            if not has_cost and not has_inv_cost:
                items_stock_but_no_cost.append((nk, portal_display.get(nk, nk), portal_stock[nk]))

    if items_stock_but_no_cost:
        print(f"\n  ⚠ Items con stock pero SIN COSTO ({len(items_stock_but_no_cost)}):")
        for nk, nm, stk in sorted(items_stock_but_no_cost):
            print(f"     {nm:<35} stock={stk}")
    else:
        print(f"\n  ✓ Todos los items con stock tienen costo")

    # DIFF 4: REPORTS vs INVENTARIO cost union
    print(f"\n  REPORTS items: {len(rep_set)}")
    print(f"  SOLD_AMOUNT items: {len(sa_set)}")

    rep_diff = []
    for nk in inv_costs:
        expected = set()
        for col in SUPPLIER_ORDER:
            expected.update(inv_costs[nk].get(col, set()))
        got = rep_cost.get(nk, set())
        if expected != got:
            rep_diff.append((nk, expected, got))

    if rep_diff:
        print(f"\n  ⚠ REPORTS costo vs INVENTARIO union ({len(rep_diff)} diferencias):")
        for nk, exp, got in rep_diff[:10]:
            nm = portal_display.get(nk, nk)
            print(f"     {nm:<30} INV_union={fmt_price(exp):<10} REP={fmt_price(got):<10}")

    # DIFF 5: GrandTotal from SOs vs SOLD_AMOUNT
    actual_grand = 0.0
    for so in so_details:
        actual_grand += float(so.get('grandTotal', 0) or 0)

    sa_last = SA[-1] if SA and len(SA) > 1 else None
    sa_total = float(sa_last[4].replace('$','').replace(',','')) if sa_last and len(sa_last) > 4 and sa_last[4] else 0

    if abs(actual_grand - sa_total) > 0.01:
        print(f"\n  ⚠ SOLD_AMOUNT TOTAL != grandTotal de SOs:")
        print(f"     SOLD_AMOUNT: ${sa_total:.2f}")
        print(f"     SOs portal: ${actual_grand:.2f}")

    return {
        "items": items,
        "po_details": po_details,
        "so_details": so_details,
        "portal_cost": dict(portal_cost),
        "portal_stock": portal_stock,
        "portal_sale": portal_sale,
        "portal_display": portal_display,
        "so_sale": dict(so_sale),
        "sold_qty": {nk: d["qty"] for nk, d in so_sale.items()},
        "sold_amount": {nk: d["sale"] for nk, d in so_sale.items()},
        "inv_set": inv_set,
        "inv_stock": inv_stock,
        "inv_costs": dict(inv_costs),
    }

# ===== FASE 3: APPLY =====

def apply_phase(ctx_data, svc):
    print("\n=== FASE 3: APPLY ===\n")

    items = ctx_data["items"]
    portal_stock = ctx_data["portal_stock"]
    portal_sale = ctx_data["portal_sale"]
    portal_display = ctx_data["portal_display"]
    portal_cost = ctx_data["portal_cost"]
    so_sale = ctx_data["so_sale"]
    so_details = ctx_data["so_details"]

    # --- INVENTARIO ---
    print("Actualizando INVENTARIO...")
    portal_nks = sorted([nk for nk in portal_stock.keys() if nfkd(nk) not in {nfkd(k) for k in ['TIERRA NEGRA', 'ABONO ORGANICO', 'CASCARILLA DE ARROZ']}])
    tierra_nks = [nk for nk in portal_stock if nfkd(nk) in {nfkd(k) for k in ['TIERRA NEGRA', 'ABONO ORGANICO', 'CASCARILLA DE ARROZ']}]

    TIERRA_COST_ITEMS = set()  # no cost for tierras

    inv_header = ["PLANTA", "SALE_EXTRA", "STOCK"] + list(SUPPLIER_ORDER)
    new_inv = [inv_header]

    for nk in sorted(portal_nks + tierra_nks):
        nm = portal_display.get(nk, nk).upper()
        sale = portal_sale.get(nk, 0) or 0
        stock = portal_stock.get(nk, 0) or 0
        row = [nm, sale if sale else "", stock if stock else ""]
        for col in SUPPLIER_ORDER:
            prices = portal_cost.get(nk, {}).get(col, [])
            row.append(fmt_price(prices))
        new_inv.append(row)

    # Tierras al final
    tierra_nms = sorted([portal_display.get(nk, nk).upper() for nk in tierra_nks])
    non_tierra = [r for r in new_inv[1:] if r[0] not in tierra_nms]
    tierra = [r for r in new_inv[1:] if r[0] in tierra_nms]
    sorted_inv = [inv_header] + sorted(non_tierra, key=lambda r: r[0]) + tierra

    clear_range("INVENTARIO!A1:J500", svc)
    write_sheet("INVENTARIO!A1", sorted_inv, svc)
    print(f"  {len(sorted_inv)-1} rows esci tas")

    # --- REPORTS ---
    print("Actualizando REPORTS...")
    rep_rows = [["PLANTA", "COSTO", "SALE", "MARGIN %"]]
    for r in sorted_inv[1:]:
        nk = name_key(r[0])
        union = set()
        for i, col in enumerate(SUPPLIER_ORDER):
            union.update(parse_price_str(r[3+i].strip() if len(r) > 3+i else ""))
        cost_str = fmt_price(union)
        sd = so_sale.get(nk, {"qty": 0.0, "sale": 0.0})
        if sd["qty"] > 0:
            sale_val = sd["sale"] / sd["qty"]
        else:
            sale_val = portal_sale.get(nk, 0)
        sale_str = f"${sale_val:.2f}" if sale_val else ""
        margin_str = ""
        if sale_val and union:
            cs = sorted(union)
            min_c, max_c = cs[0], cs[-1]
            high = ((sale_val - min_c) / sale_val) * 100
            low = ((sale_val - max_c) / sale_val) * 100
            margin_str = f"{int(high)}%" if abs(high - low) < 1 else f"{int(low)}%-{int(high)}%"
        rep_rows.append([r[0], cost_str, sale_str, margin_str])

    clear_range("REPORTS!A1:D500", svc)
    write_sheet("REPORTS!A1", rep_rows, svc)
    print(f"  {len(rep_rows)-1} rows")

    # --- SOLD_AMOUNT ---
    print("Actualizando SOLD_AMOUNT...")
    sa_total_qty = 0.0
    sa_total_cost = 0.0
    sa_total_sale = 0.0

    so_grand_totals = []
    for so in so_details:
        so_grand_totals.append(float(so.get('grandTotal', 0) or 0))

    sa_rows = [["PLANTA", "AMOUNT_SOLD", "TOTAL_COST", "TOTAL_SALE", "TOTAL"]]
    for nk in sorted(so_sale.keys()):
        nm = portal_display.get(nk, nk).upper()
        qty = so_sale[nk]["qty"]
        sale_total = so_sale[nk]["sale"]
        cost_total = 0.0
        for col in SUPPLIER_ORDER:
            prices = portal_cost.get(nk, {}).get(col, [])
            if prices:
                avg_c = sum(prices) / len(prices)
                cost_total += avg_c * qty
                break
        profit = sale_total - cost_total
        sa_rows.append([
            nm,
            str(int(qty)) if qty else "",
            f"${cost_total:.2f}" if cost_total else "",
            f"${sale_total:.2f}",
            f"${profit:.2f}",
        ])
        sa_total_qty += qty
        sa_total_cost += cost_total
        sa_total_sale += sale_total

    total_grand = sum(so_grand_totals)
    sa_rows.append(["TOTAL", str(int(sa_total_qty)), f"${sa_total_cost:.2f}",
                     f"${total_grand:.2f}", f"${total_grand-sa_total_cost:.2f}"])

    clear_range("'SOLD_AMOUNT '!A1:E500", svc)
    write_sheet("'SOLD_AMOUNT '!A1", sa_rows, svc)
    print(f"  {len(sa_rows)} rows, TOTAL={total_grand:.2f}")

def main():
    apply = "--apply" in sys.argv
    if not apply:
        print("=== AVADA KEDAVRA (DRY RUN) ===")
        print("Modo: solo READ + DIFF. Usa --apply para escribir en el sheet.\n")
    else:
        print("=== AVADA KEDAVRA (APPLY MODE) ===")

    items, po_details, so_details = read_phase()

    TS = os.path.expanduser("~/.hermes/profiles/ezy_portal_expert/google_token.json")
    creds = Credentials.from_authorized_user_file(TS, ["https://www.googleapis.com/auth/spreadsheets"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    svc = build("sheets", "v4", credentials=creds)

    ctx = diff_phase(items, po_details, so_details, svc)

    if apply:
        apply_phase(ctx, svc)
        print(f"\n{'='*50}")
        print("✅ AVADA KEDAVRA completado (APPLY)")
        print(f"{'='*50}")
    else:
        print(f"\n{'='*50}")
        print("🏁 DRY RUN completo — sin cambios en el sheet.")
        print("Ejecuta con --apply para sincronizar.")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()