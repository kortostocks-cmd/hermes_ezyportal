#!/usr/bin/env python3
"""
check_sheet_gaps — after lumos, find portal items NOT in the INVENTARIO sheet.

Usage:
  ~/.hermes/hermes-agent/venv/bin/python3 \
    skills/software-development/ezy-portal-api/scripts/check_sheet_gaps.py

Output: list of (code, name, stock) for all portal items whose normalized name
doesn't match any row in the INVENTARIO sheet.
"""

import json, os, sys, ssl, subprocess, re, unicodedata, urllib.request

KEY = os.environ.get("EZY_KEY", "ten_3HW_frAuoKDYRyuzUfzUEDzva-ypPuzL9G3sljmBTWc")
SHEET_ID = "1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE"
PORTAL_URL = "https://vivero.ezyts.com"
SHEET_API = [
    os.path.expanduser("~/.hermes/hermes-agent/venv/bin/python3"),
    os.path.expanduser("~/.hermes/profiles/ezy_portal_expert/skills/productivity/vivero-google-sheets/scripts/sheets_api.py"),
]

def fetch_json(url):
    """Fetch via curl subprocess (urllib 401 workaround for ten_3HW_ keys)."""
    result = subprocess.run(
        ["curl", "-s", "-H", f"X-Api-Key: {KEY}", "-H", "User-Agent: Mozilla/5.0", url],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(result.stdout)

def norm(name):
    if not name: return ""
    nfkd = unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode("ASCII")
    return re.sub(r"[^A-Z0-9]", "", nfkd.upper())

def main():
    # 1. Fetch ALL portal items (paginated, perPage=25)
    portal_items = []
    page = 1
    while True:
        url = f"{PORTAL_URL}/api/items/items?isActive=true&perPage=25&page={page}"
        data = fetch_json(url)
        items = data.get("data", [])
        for it in items:
            portal_items.append({
                "code": it.get("itemCode", ""),
                "name": it.get("name", ""),
                "stock": it.get("itemStockTotal", 0),
            })
        if not data.get("hasMore"):
            break
        page += 1

    # 2. Fetch sheet
    r = subprocess.run(SHEET_API + ["read", "INVENTARIO", "A1:A"],
        capture_output=True, text=True, timeout=30)
    sheet_rows = json.loads(r.stdout)
    sheet_names = [row[0].strip().upper() if row and row[0] else "" for row in sheet_rows[1:]]
    sheet_norm = set(norm(n) for n in sheet_names)

    # 3. Find gaps
    missing = [it for it in portal_items if norm(it["name"]) and norm(it["name"]) not in sheet_norm]
    missing.sort(key=lambda x: x["name"])

    # 4. Report
    print(f"Portal: {len(portal_items)} items  Sheet: {len(sheet_names)} plants  Missing: {len(missing)}")
    if missing:
        print()
        for it in missing:
            print(f"  {it['code']:30s} {it['name']:30s} stock={it['stock']:3d}")

    return len(missing)

if __name__ == "__main__":
    sys.exit(main())