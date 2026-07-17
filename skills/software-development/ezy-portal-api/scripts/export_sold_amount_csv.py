"""
Export SOLD_AMOUNT to CSV for monthly reporting.

Run:
    ~/.hermes/hermes-agent/venv/bin/python3 scripts/export_sold_amount_csv.py

Output: ~/Documents/vivero_ventas/ventas_YYYY-MM.csv

Behavior (Jul 13 2026):
- Reads the SOLD_AMOUNT tab (note trailing space in the tab name).
- Strips "$" and thousand separators; uses integer qty and 2-decimal currency.
- Sums TOTAL row from unrounded raw values to avoid drift.
- Recommended trigger: run after the SOLD_AMOUNT TOTAL row has been highlighted
  yellow (end-of-month cue) or when the user asks to export the month.
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
TAB = "'SOLD_AMOUNT '"  # trailing space is intentional
TOKEN = os.path.expanduser("~/.hermes/profiles/ezy_portal_expert/google_token.json")


def get_sold_amount():
    creds = Credentials.from_authorized_user_file(TOKEN, ["https://www.googleapis.com/auth/spreadsheets"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN, "w") as f:
            json.dump(json.loads(creds.to_json()), f)
    svc = build("sheets", "v4", credentials=creds)
    return svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=f"{TAB}!A1:E200"
    ).execute().get("values", [])


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

    # Skip header (row 0). Aggregate totals with raw floats to avoid rounding drift.
    raw_total = {"qty": 0, "cost": 0.0, "sale": 0.0, "profit": 0.0}
    body_rows = []

    for r in rows[1:]:
        if not r or not r[0]:
            continue
        if r[0].upper() == "TOTAL":
            continue
        padded = (r + [""] * 5)[:5]
        try:
            qty = int(float(padded[1])) if padded[1] else 0
        except ValueError:
            qty = 0
        try:
            cost = float(padded[2].replace("$", "").replace(",", "")) if padded[2] else 0.0
        except ValueError:
            cost = 0.0
        try:
            sale = float(padded[3].replace("$", "").replace(",", "")) if padded[3] else 0.0
        except ValueError:
            sale = 0.0
        profit = sale - cost
        body_rows.append([padded[0], qty, round(cost, 2), round(sale, 2), round(profit, 2)])
        raw_total["qty"] += qty
        raw_total["cost"] += cost
        raw_total["sale"] += sale
        raw_total["profit"] += profit

    csv_rows = [["PLANTA", "AMOUNT_SOLD", "TOTAL_COST", "TOTAL_SALE", "TOTAL"]]
    csv_rows.extend(body_rows)
    csv_rows.append([
        "TOTAL",
        raw_total["qty"],
        round(raw_total["cost"], 2),
        round(raw_total["sale"], 2),
        round(raw_total["profit"], 2),
    ])

    out_dir = os.path.expanduser("~/Documents/vivero_ventas")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"ventas_{datetime.now():%Y-%m}.csv"
    out_path = to_csv(csv_rows, os.path.join(out_dir, filename))

    print(f"OK -> {out_path}")
    print(f"   items: {len(body_rows)}")
    print(f"   TOTAL sale:  ${raw_total['sale']:.2f}")
    print(f"   TOTAL cost:  ${raw_total['cost']:.2f}")
    print(f"   TOTAL profit: ${raw_total['profit']:.2f}")


if __name__ == "__main__":
    main()
