# Plant Photo Naming & Spreadsheet Matching

## LUMOS Spell — Portal to Sheet Sync

`lumos` is the Harry Potter spell trigger that syncs EZY Portal inventory to Google Sheets.

**Current sheet structure (Sheet1):**
| Column | Header | Notes |
|--------|--------|-------|
| A | PLANTA | Item name (matching key) |
| B | FOTO | Photo URL or filename |
| C | STOCK | `itemStockTotal` from portal |
| D | PRECIO | Price — NOT readable via API (prices masked); enter manually |

**What `lumos` syncs:**
1. Fetch active items: `GET /api/items/items?expand=prices&isActive=true&perPage=100` (paginate)
2. Match to sheet rows by normalized name
3. Batch-update column C (STOCK) where empty

**Price limitation:** `X-Api-Key: ten_...` masks all prices — `prices: []` always returned. Column D must be updated manually or requires a key with price read permissions.

## LUMOS Execution Workflow

```
1. curl items from EZY Portal (terminal, not execute_code sandbox)
   curl -s -H "X-Api-Key: ten_..." "https://vivero.ezyts.com/api/items/items?expand=prices&isActive=true&perPage=100&page=1" > /tmp/page1.json
   (page 2 if hasMore=true)

2. python3 parse + match → /tmp/lumos_stock.json  (row_num, stock pairs)

3. python3 batchUpdate to Sheet1!C{row} via google_api.py
   body = {"valueInputOption": "USER_ENTERED", "data": [{"range": "Sheet1!C{row}", "values": [[stock]]}, ...]}
   sheetssvc.spreadsheets().values().batchUpdate(spreadsheetId=SHEET_ID, body=body)
```

**Why curl first, not python urllib:** The execute_code sandbox blocks outbound HTTPS or has SSL issues with Python 3.14 system Python. Always use `curl` in terminal to fetch, then python3 to parse.

**Google Sheets auth:** Use Hermes venv python (`/Users/abrahamkortovich/.hermes/hermes-agent/venv/bin/python3`) not system python — has correct SSL certs and google-api-python-client installed.

## Source Filename Pattern

Photos from the vivero portal export follow this pattern:

```
<PLANT_NAME>_<yyyyMMddHHmmss>_<8char_hex_hash>.jpeg
```

Example:
```
TRADESCANTIA_GOLD_EN_BOLSA_20260618132701_1bbbbfda.jpeg
ALOCASIA_GIGANTE_VARIEGADA_EN_PDB40_20260618132701_e2faf501.jpeg
```

Regex to strip timestamp+hash:
```python
import re
cleaned = re.sub(r'_\d{14}_[a-f0-9]{8}(?=\.|$)', '', filename)
```

## Common OCR Typos in Source Filenames

| Typo | Correct |
|------|---------|
| duranra | DURANTA |
| triandular | TRIANGULAR |
| philondendro | PHILODENDRON |
| ficus triandular | FICUS TRIANGULAR |

Always verify matches against the spreadsheet — automated string matching will misroute these.

## Google Sheets → CSV Export URL

For a published sheet:
```
https://docs.google.com/spreadsheets/d/<DOC_ID>/export?format=csv&gid=<sheet_gid>
```

Alternative published URL format:
```
https://docs.google.com/spreadsheets/d/e/<PUBLISHED_TOKEN>/pub?output=csv
```

## Matching Strategy

1. Strip timestamp+hash from source filename
2. Normalize both source and spreadsheet names: uppercase, remove `"'()[]`, collapse spaces
3. Use word-overlap scoring: more common words = higher confidence
4. For exact prefix match (source starts with spreadsheet name OR vice versa): boost score
5. Always review ambiguous matches manually (see OCR typos above)

## Duplicate Target Handling

When two source files map to the same plant name (e.g., two photos for one plant), the second is renamed with `_1` suffix:

```
FICUS TRIANGULAR EN MCL29.jpeg      # first
FICUS TRIANGULAR EN MCL29_1.jpeg    # second
```

## Spreadsheet Column

The sheet used in vivero has plant names in the `PLANTA` column, with `FOTO` as the photo indicator column.

## Rename Execution Pattern

```python
import os, re

foto_dir = "/path/to/plantas_para_subir_portal"

# Mapping of source → correct target (manually curated for tricky names)
correcciones = {
    "duranra en bolsa.jpeg":    "DURANTA EN BOLSA.jpeg",
    "ficus triandular.jpeg":    "FICUS TRIANGULAR EN MCL29.jpeg",
    "philondendron cobra.jpeg": "PHILODENDRON COBRA EN CANASTA.jpeg",
    "Guayacan enano.jpeg":      "GUAYACAN ENANO (TECOMA) EN POTE 6.jpeg",
}

for foto in os.listdir(foto_dir):
    if foto.endswith(('.jpeg', '.jpg', '.png')):
        if foto in correcciones:
            nuevo = correcciones[foto]
        else:
            # ... matching logic
        os.rename(os.path.join(foto_dir, foto),
                  os.path.join(foto_dir, nuevo))
```

## File Count

vivero folder: ~50 files — manageable to list and review manually before renaming.