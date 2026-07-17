"""
Export SOLD_AMOUNT to CSV for monthly reporting.

Usage:
    python3 scripts/export_sold_amount_csv.py [--month YYYY-MM]

Default: current month. If no flag, exports all data.
The SOLD_AMOUNT tab name has a trailing space — handle it.
"""
import csv
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent/venv/lib/python3.11/site-packages"))
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SHEET_ID = "1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE"
TAB = "'SOLD_AMOUNT '"
TOKEN = os.path.expanduser("~/.hermes/profiles/ezy_portal_expert/google_token.json")


def get_sold_amount():
    creds = Credentials.from_authorized_user_file(TOKEN, ["https://www.googleapis.com/auth/spreadsheets"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN, "w") as f:
            json.dump(json.loads(creds.to_json()), f)
    svc = build("sheets", "v4", credentials=creds)
    result = svc.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=f"{TAB}!A1:E200").execute()
    return result.get("values", [])


def to_csv(rows, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for r in rows:
            writer.writerow(r)
    return out_path


def main():
    rows = get_sold_amount()
    if not rows:
        print("SOLD_AMOUNT empty")
        return

    now = datetime.now()
    month_str = now.strftime("%Y-%m")

    out_dir = os.path.expanduser(f"~/Documents/vivero_ventas")
    os.makedirs(out_dir, exist_ok=True)

    # Try to find CSV column F (MES_EXPORT) for marker
    filename = f"ventas_{month_str}.csv"
    out_path = os.path.join(out_dir, filename)

    # Build CSV
    header = ["PLANTA", "AMOUNT_SOLD", "TOTAL_COST", "TOTAL_SALE", "TOTAL"]
    csv_rows = [header]
    # Sum TOTAL row into a known position
    total = {"qty": 0, "cost": 0.0, "sale": 0.0, "profit": 0.0}

    for i, r in enumerate(rows[1:], start=1):  # skip header
        if r and r[0].upper() == "TOTAL":
            continue
        if not r or not r[0]:
            continue
        try:
            r_padded = (r + [""] * 5)[:5]
            name = r_padded[0]
            qty = int(float(r_padded[1])) if r_padded[1] else 0
            cost = float(r_padded[2].replace("$", "")) if r_padded[2] else 0.0
            sale = float(r_padded[3].replace("$", "")) if r_padded[3] else 0.0
            profit = sale - cost
            csv_rows.append([name, qty, round(cost, 2), round(sale, 2), round(profit, 2)])
            total["qty"] += qty
            total["cost"] += cost
            total["sale"] += sale
            total["profit"] += profit
        except (ValueError, IndexError):
            continue

    csv_rows.append([
        "TOTAL",
        total["qty"],
        round(total["cost"], 2),
        round(total["sale"], 2),
        round(total["profit"], 2),
    ])

    to_csv(csv_rows, out_path)
    print(f"✅ Exports to: {out_path}")
    print(f"   Items: {len(csv_rows) - 2}")
    print(f"   Total sale: ${total['sale']:.2f}")
    print(f"   Total cost: ${total['cost']:.2f}")
    print(f"   Total profit: ${total['profit']:.2f}")


if __name__ == "__main__":
    main()