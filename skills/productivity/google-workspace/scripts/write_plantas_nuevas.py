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
SID = "1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE"

# Todas las filas con codigo, nombre, lista_precio, precio, stock, descripcion
values = [
    ["CODIGO",       "NOMBRE",              "LISTA_PRECIO",  "PRECIO_USD", "STOCK", "DESCRIPCION"],
    ["PL-ANTORCHA",  "ANTORCHA",            "COST_HACIENDA",  20,           0,       "Aloe aristata (Aristaloe aristata). Suculenta."],
    ["PL-LIRIO",     "LIRIO",               "COST_HACIENDA",  30,           "",      ""],
    ["PL-CALATEA-CELORINA", "CALATEA CELORINA", "COST_HACIENDA", 10,       "",      ""],
    ["PL-DRACAENA-REFLEXA", "Dracaena reflexa",  "COST_HACIENDA", 35,       "",      ""],
]

result = svc.spreadsheets().values().update(
    spreadsheetId=SID,
    range="plantas_nuevas!A1",
    valueInputOption="RAW",
    body={"values": values},
).execute()
print("OK — filas escritas:", result.get("updatedRows"))