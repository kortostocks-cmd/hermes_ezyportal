import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _hermes_home import get_hermes_home
HERMES_HOME = get_hermes_home()
TOKEN_FILE = HERMES_HOME / "google_token.json"

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open(TOKEN_FILE) as f:
    td = json.load(f)

creds = Credentials(
    token=td["token"], refresh_token=td.get("refresh_token"),
    token_uri=td.get("token_uri"), client_id=td.get("client_id"),
    client_secret=td.get("client_secret"),
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
)
svc = build("sheets", "v4", credentials=creds)

r = svc.spreadsheets().values().get(
    spreadsheetId="1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE",
    range="plantas_nuevas!A1:E5"
).execute()
for row in r.get("values", []):
    print(row)