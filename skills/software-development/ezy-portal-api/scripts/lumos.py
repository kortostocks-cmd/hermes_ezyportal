#!/usr/bin/env python3
"""
lumos — sync EZY Portal stock + price → Google Sheet
Harry Potter spell: light to reveal truth

Usage:
  python3 scripts/lumos.py

Requires:
  - X-Api-Key: ten_...  (set in KEY below, or export EZY_KEY)
  - Google Sheets API credentials (~/.hermes/profiles/ezy_portal_expert/google_token.json)
  - Sheet ID: 1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE
  - Hermes venv python (needs google-api-python-client + google-auth)
"""

import json, os, ssl, re, unicodedata, urllib.request
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# === CONFIG ===
KEY = os.environ.get("EZY_KEY", "ten_YdKacbOqmKiaU96UBQWxjZ6cMZW6Y4uFpcvfx8cVrxE")
SHEET_ID = "1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE"
SHEET_RANGE = "INVENTARIO!A1:D500"
PRICE_LIST = "SALE_EXTRA"
PORTAL_URL = "https://vivero.ezyts.com"
TOKEN_FILE = os.path.expanduser("~/.hermes/profiles/ezy_portal_expert/google_token.json")
# ==============

# Items to move to end of sheet (tierras group)
TIERRAS_NAMES = {"TIERRA NEGRA", "TIERRA-NEGRA",
                 "ABONO ORGANICO", "ABONO-ORGANICO",
                 "CASCARILLA DE ARROZ", "CASCARILLA-DE-ARROZ"}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def get_sheets_service():
    creds = Credentials.from_authorized_user_file(
        TOKEN_FILE, ["https://www.googleapis.com/auth/spreadsheets"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as f:
            json.dump(json.loads(creds.to_json()), f)
    return build("sheets", "v4", credentials=creds)


def fetch_portal_items():
    items = {}
    page = 1
    while True:
        url = f"{PORTAL_URL}/api/items/items?isActive=true&expand=prices&perPage=100&page={page}"
        req = urllib.request.Request(url)
        req.add_header("X-Api-Key", KEY)
        req.add_header("User-Agent", "Mozilla/5.0")
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = json.loads(resp.read())
        for d in data["data"]:
            price = ""
            for p in d.get("prices", []):
                if p.get("priceListCode") == PRICE_LIST and not p.get("masked"):
                    price = str(p.get("price", ""))
                    break
            items[d["name"]] = {"stock": d.get("itemStockTotal", 0), "price": price}
        if not data.get("hasMore"):
            break
        page += 1
    return items


def normalize(name):
    n = unicodedata.normalize("NFD", name.upper())
    n = re.sub(r"[\u0300-\u036f]", "", n)
    n = re.sub(r"[\(\)\[\]].*", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    n = re.sub(r"\s*(VR|EN POTE.*|BOLSA.*|POTE.*|PDB.*|MCL.*|VCG.*|19Z.*|GEOTEXTIL.*)$", "", n)
    return n.strip()


def is_empty_row(row):
    return not row or all(str(c).strip() == "" for c in row)


def main():
    print("Fetching portal items...")
    portal_items = fetch_portal_items()
    print(f"  {len(portal_items)} items")
    portal_norm = {normalize(n): (n, d) for n, d in portal_items.items()}

    print("Fetching sheet...")
    svc = get_sheets_service()
    result = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=SHEET_RANGE).execute()
    sheet_data = result.get("values", [])
    print(f"  {len(sheet_data)} rows incl. header")

    header = sheet_data[0]
    rows = sheet_data[1:]

    # Compact empty rows
    before = len(rows)
    rows = [r for r in rows if not is_empty_row(r)]
    if len(rows) < before:
        print(f"  Removed {before - len(rows)} empty row(s)")

    # Process rows: update stock/price, separate tierras
    tierras = []
    normal_rows = []
    updates = 0

    for row in rows:
        name = str(row[0]).strip().upper() if row else ""
        if not name or name == "PLANTA":
            normal_rows.append(row)
            continue

        # Check if this is a tierras item
        name_upper = name.replace("-", " ").replace("  ", " ").strip()
        if name_upper in TIERRAS_NAMES or name in TIERRAS_NAMES:
            tierras.append(row)
        else:
            normal_rows.append(row)

        # Update stock/price from portal
        old_stock = str(row[2]).strip() if len(row) > 2 else ""
        norm = normalize(name)
        if norm not in portal_norm:
            continue
        _, pdata = portal_norm[norm]
        portal_stock = str(pdata["stock"])
        portal_price = pdata["price"] or ""

        changed = False
        while len(row) < 4:
            row.append("")
        if old_stock != portal_stock:
            row[2] = portal_stock
            changed = True
        if portal_price and row[3] != portal_price:
            row[3] = portal_price
            changed = True
        if changed:
            updates += 1

    # Reorder: normal rows first, tierras at end
    reordered = normal_rows + tierras
    sheet_data = [header] + reordered

    print(f"  Updates applied: {updates}")
    if tierras:
        print(f"  Tierras moved to end: {len(tierras)} rows")

    if updates == 0 and not tierras:
        print("No updates needed — sync OK")
        return

    print("Writing sheet...")
    result = svc.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"INVENTARIO!A1:D{len(sheet_data)}",
        valueInputOption="USER_ENTERED",
        body={"values": sheet_data}
    ).execute()
    print(f"  Written: {result.get('updatedCells')} cells")
    print("✅ LUMOS COMPLETE")


if __name__ == "__main__":
    main()