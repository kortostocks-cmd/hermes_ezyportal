"""
Cross-reference INVENTARIO sheet cost columns vs Purchase Order data.

Run:
    ~/.hermes/hermes-agent/venv/bin/python3 scripts/inventory_audit_po_costs.py

Use this to verify the user's sheets match the portal reality:
1. Reads INVENTARIO from sheet (PLANTA + cost cols D-I).
2. Fetches all POs (paginated) and details each with expand=lines.
3. Builds canonical cost map (name_key -> {supplier: sorted unique prices}).
4. Prints any row where the sheet's per-supplier price set differs from the PO's.

Tail of report shows items-with-cost-only-in-sheet (orphans) and items-with-cost-only-in-PO (missing
in sheet). Useful to detect:
- Cost not migrated (e.g. AGAVE GIGANTE should be $5 in COST_A&G but PO line was AGAVE AMARILLO/VERDE).
- Items where the user manual-overrode a value.
- Supplier priceListCode drift (e.g. PO-2026-000028 uses COST_IAN which is not in the active set).
"""
import json
import os
import re
import ssl
import subprocess
import sys
import unicodedata
from collections import defaultdict

sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent/venv/lib/python3.11/site-packages"))
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE = "https://vivero.ezyts.com"
SHEET_ID = "1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE"
TOKEN = os.path.expanduser("~/.hermes/profiles/ezy_portal_expert/google_token.json")
SUPPLIER_ORDER = ["COST_MIJARDIN", "COST_EDWIN", "COST_HACIENDA", "COST_A&G", "COST_SARACELY", "COST_SUGEY"]


def _curl_json(path):
    cmd = [
        "curl", "-s", "-S",
        "-H", "X-Api-Key: ten_BvfgJJOvXHbkjuQKMpscKmFo92HMwl3-2UNsbVWYq4g",
        "-H", "User-Agent: Mozilla/5.0",
        f"{BASE}{path}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0 or not r.stdout.strip():
        return {}
    return json.loads(r.stdout)


def nfkd(s):
    n = unicodedata.normalize("NFD", (s or "").upper())
    n = re.sub(r"[\u0300-\u036f]", "", n)
    return re.sub(r"\s+", " ", n).strip()


def name_key(n):
    n = (n or "").upper()
    if n in ("POTHOS",):
        return "PHOTUS"
    return nfkd(n)


def fetch_paged(path):
    items = []
    page = 1
    while True:
        d = _curl_json(f"{path}perPage=100&page={page}")
        items.extend(d.get("data", []))
        if not d.get("hasMore"):
            break
        page += 1
    return items


def main():
    # Fetch PO list + each detail
    pos = fetch_paged("/api/commerce/purchase-orders?")
    po_details = []
    for po in pos:
        d = _curl_json(f"/api/commerce/purchase-orders/{po['id']}?expand=lines")
        if d:
            po_details.append(d)
    print(f"POs: {len(pos)}, with details: {len(po_details)}")

    # Canonical cost map: name -> {supplier: set of prices}
    canonical = defaultdict(lambda: defaultdict(set))
    for po in po_details:
        supplier = po.get("priceListCode", "")
        if supplier not in set(SUPPLIER_ORDER):
            continue
        for line in po.get("lines", []):
            nk = name_key(line.get("itemDescription") or line.get("itemName"))
            up = float(line.get("unitPrice", 0) or 0)
            if up > 0:
                canonical[nk][supplier].add(round(up, 2))

    # Sheet cost map
    creds = Credentials.from_authorized_user_file(TOKEN, ["https://www.googleapis.com/auth/spreadsheets"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN, "w") as f:
            json.dump(json.loads(creds.to_json()), f)
    svc = build("sheets", "v4", credentials=creds)
    inv = svc.spreadsheets().values().get(spreadsheetId=SHEET_ID, range="INVENTARIO!A1:I300").execute().get("values", [])

    sheet = defaultdict(lambda: defaultdict(set))
    sheet_display = {}
    for r in inv[1:]:
        if not r or not r[0]:
            continue
        nm = r[0].upper().strip()
        nk = name_key(nm)
        sheet_display[nk] = nm
        for i, col in enumerate(SUPPLIER_ORDER, start=3):
            v = r[i].strip() if i < len(r) else ""
            if not v:
                continue
            m = re.match(r"\$?(\d+(?:\.\d+)?)(?:-\$(\d+(?:\.\d+)))?", v)
            if not m:
                continue
            lo = float(m.group(1))
            hi = float(m.group(2)) if m.group(2) else lo
            sheet[nk][col].update([lo, hi] if hi != lo else [lo])

    # Compare
    diffs, correct = [], 0
    all_keys = set(canonical) | set(sheet)
    for nk in sorted(all_keys):
        issues = []
        for col in SUPPLIER_ORDER:
            canon = sorted(canonical[nk].get(col, set()))
            sh = sorted(sheet[nk].get(col, set()))
            if canon != sh:
                issues.append((col, canon, sh))
        if not issues:
            correct += 1
        else:
            diffs.append((sheet_display.get(nk, nk.upper()), issues))

    print(f"\nItems compared: {len(all_keys)}")
    print(f"Correct: {correct}")
    print(f"Mismatches: {len(diffs)}")

    if diffs:
        print(f"\n{'Item':<35} {'Supplier':<14} {'In PO':<12} {'In Sheet':<12}")
        print("-" * 80)
        seen = set()
        for nm, issues in diffs:
            for col, c, s in issues:
                key = (nm, col)
                if key in seen:
                    continue
                seen.add(key)
                c_str = f"${c[0]:.2f}" + (f"-${c[-1]:.2f}" if len(c) > 1 else "") if c else "-"
                s_str = f"${s[0]:.2f}" + (f"-${s[-1]:.2f}" if len(s) > 1 else "") if s else "-"
                print(f"{nm[:34]:<35} {col:<14} {c_str:<12} {s_str:<12}")

    print(f"\nItems with cost in PO but NOT in sheet: {sorted(set(canonical) - set(sheet))[:10]}")
    print(f"Items with cost in sheet but NOT in any PO: {sorted(set(sheet) - set(canonical))[:10]}")


if __name__ == "__main__":
    main()
