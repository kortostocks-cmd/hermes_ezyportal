# Embedding Photos from Local Files into Google Sheets

A proven workflow: match local image files to sheet rows by name, upload each image
to Google Drive (world-readable), then write the `drive.google.com/uc?export=view&id=...`
URL into the corresponding sheet cell.

Used successfully for: plant photo catalogs, inventory images, product sheets.

## Step-by-Step

### 1. Read the sheet to map plant names → row numbers

```python
from google_api import get_credentials, build_service

creds = get_credentials()
sheets_svc = build_service("sheets", "v4")

result = sheets_svc.spreadsheets().values().get(
    spreadsheetId=SHEET_ID, range="Sheet1!A:B"
).execute()
rows = result.get("values", [])

# planta_to_row: clean name → 1-indexed row (skip header at row 0)
planta_to_row = {}
for i, row in enumerate(rows):
    if row and i > 0:
        planta_to_row[normalize(row[0])] = i + 1
```

### 2. Normalize names for matching

Sheet plant names often contain trailing quotes, brackets, and dashes that break
exact string matching. Always normalize both sides:

```python
import re

def normalize(s):
    s = s.upper()
    s = re.sub(r'["\'\(\)\[\]]', '', s)   # strip quotes, parens, brackets
    s = re.sub(r'\s+', ' ', s)              # collapse whitespace
    s = re.sub(r'\s*[-–]\s*', ' ', s)        # treat dash as space
    return s.strip()
```

**Common pitfall**: Sheet names like `ALOCASIA VERDE EN PDB 40"` (trailing `"`)
or `COBRA VERDE EN POTE 8" [19Z]` (trailing `" [19Z]`) will NOT match the
same string without normalization.

### 3. Upload photos to Drive

```python
from googleapiclient.http import MediaFileUpload

drive_svc = build_service("drive", "v3")

for foto in fotos:
    clean_foto = normalize(foto.rsplit('.', 1)[0])
    path = os.path.join(FOTO_DIR, foto)

    file_metadata = {"name": foto, "mimeType": "image/jpeg"}
    media = MediaFileUpload(path, mimetype="image/jpeg")
    uploaded = drive_svc.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()

    file_id = uploaded["id"]

    # Make world-readable so the URL works without authentication
    drive_svc.permissions().create(
        fileId=file_id, body={"type": "anyone", "role": "reader"}
    ).execute()

    url = f"https://drive.google.com/uc?export=view&id={file_id}"
    row_num = planta_to_row.get(clean_foto)

    if row_num:
        # store (row_num, url) for batch update
    else:
        # no match — log and handle manually

    time.sleep(0.4)  # rate limit between uploads
```

### 4. Batch-update the sheet

```python
data = [{"range": f"Sheet1!B{row}", "values": [[url]]} for row, url in updates]

body = {
    "valueInputOption": "USER_ENTERED",
    "data": data
}

result = sheets_svc.spreadsheets().values().batchUpdate(
    spreadsheetId=SHEET_ID, body=body
).execute()
```

## Prerequisites (Google Cloud Console)

Both APIs must be enabled **independently** in the project:

| API | Enable URL |
|-----|-----------|
| Google Sheets API | `https://console.cloud.google.com/apis/library/sheets.googleapis.com` |
| Google Drive API | `https://console.cloud.google.com/apis/library/drive.googleapis.com` |

Enabling Sheets API does **not** automatically enable Drive API.

## Python Runtime

On macOS with PEP 668-managed Python, use the hermes venv:
```python
PYTHON = "/Users/abrahamkortovich/.hermes/hermes-agent/venv/bin/python3"
```

```python
sys.path.insert(0, "/path/to/skills/productivity/google-workspace/scripts")
from google_api import get_credentials, build_service
```

## File Naming Hazards

- **Don't delete ambiguous files** during rename/matching. If two source files
  map to the same normalized name (e.g. `ficus triandular` and `ficus triangular`
  both becoming `FICUS TRIANGULAR`), verify actual image content before deleting.
  An ambiguous file deleted is data lost.
- **Always inspect filenames** in the source folder before bulk rename operations.
- When a sheet has 117 plants and you have 51 photos, many plants simply won't
  have photos — that is expected, not an error.