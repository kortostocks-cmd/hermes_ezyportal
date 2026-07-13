#!/usr/bin/env python3
"""Simple Sheets CLI for vivero sheet (ID: 1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE)."""

import argparse
import json
import os
import sys
from pathlib import Path

# Profile root = 4 levels up from scripts/ (scripts -> skill -> productivity -> profile_root)
HERMES_PROFILE_HOME = Path(__file__).resolve().parents[4]
os.environ["HERMES_HOME"] = str(HERMES_PROFILE_HOME)

TOKEN_PATH = HERMES_PROFILE_HOME / "google_token.json"
SHEET_ID = "1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE"

def get_creds():
    from google.oauth2.credentials import Credentials
    if not TOKEN_PATH.exists():
        print(f"ERROR: No token at {TOKEN_PATH}. Run setup first.", file=sys.stderr)
        sys.exit(1)
    return Credentials.from_authorized_user_file(str(TOKEN_PATH))

def get_service():
    from googleapiclient.discovery import build
    creds = get_creds()
    return build("sheets", "v4", credentials=creds)

def cmd_read(args):
    svc = get_service()
    range_name = f"{args.sheet}!{args.range}" if args.range else args.sheet
    result = svc.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=range_name).execute()
    values = result.get("values", [])
    print(json.dumps(values, ensure_ascii=False, indent=2))

def cmd_append(args):
    svc = get_service()
    values = json.loads(args.values)
    body = {"values": values}
    result = svc.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"{args.sheet}!A1",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    print(f"Appended {result.get('updates', {}).get('updatedRows', 0)} rows")

def cmd_write(args):
    svc = get_service()
    values = json.loads(args.values)
    body = {"values": values}
    result = svc.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"{args.sheet}!{args.range}",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    print(f"Updated {result.get('updatedRows', 0)} rows x {result.get('updatedColumns', 0)} cols")

def cmd_add_sheet(args):
    svc = get_service()
    body = {"requests": [{"addSheet": {"properties": {"title": args.title, "index": args.index}}}]}
    result = svc.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()
    sheet_id = result["replies"][0]["addSheet"]["properties"]["sheetId"]
    print(f"Created sheet '{args.title}' (sheetId: {sheet_id})")

def main():
    parser = argparse.ArgumentParser(description="Vivero Sheets CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_read = sub.add_parser("read", help="Read sheet/range")
    p_read.add_argument("sheet", help="Sheet name (e.g., plantas_nuevas)")
    p_read.add_argument("range", nargs="?", help="A1 notation range (e.g., A1:F50)")
    p_read.set_defaults(func=cmd_read)

    p_append = sub.add_parser("append", help="Append rows")
    p_append.add_argument("sheet", help="Sheet name")
    p_append.add_argument("values", help="JSON array of rows, e.g., '[[\",\",\"]]'")
    p_append.set_defaults(func=cmd_append)

    p_write = sub.add_parser("write", help="Write/overwrite range")
    p_write.add_argument("sheet", help="Sheet name")
    p_write.add_argument("range", help="A1 notation start cell (e.g., A2)")
    p_write.add_argument("values", help="JSON array of rows")
    p_write.set_defaults(func=cmd_write)

    p_add = sub.add_parser("add-sheet", help="Add new sheet tab")
    p_add.add_argument("title", help="New sheet title")
    p_add.add_argument("--index", type=int, default=0, help="Tab position index")
    p_add.set_defaults(func=cmd_add_sheet)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()