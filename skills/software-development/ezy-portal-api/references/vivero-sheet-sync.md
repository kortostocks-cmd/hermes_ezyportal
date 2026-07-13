# Google Sheets Sync (vivero tenant)

Sheet ID: `1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`

## Tabs

| Tab | Content | Columns | Rows (Jun 2026) |
|-----|---------|---------|-----------------|
| `INVENTARIO` | Main stock sheet (lumos target) | A=PLANTA, B=FOTO, C=STOCK, D=PRECIO | 122 rows (120 plant types + CG/CJ + header) |
| `plantas_nuevas` | New plants pending portal creation | A=CODIGO, B=NOMBRE, C=LISTA_PRECIO, D=PRECIO_USD, E=STOCK, F=DESCRIPCION | 58 plants |

**INVENTARIO stats** (excluyendo CG/CJ cajas):
- Total tipos de plantas: 120
- Con stock disponible (>0): 43
- SIN stock (=0): 77
- Cantidad total en stock: 4,479 unidades

## Google API Tool Usage

The `google_api.py` CLI is at:
```
/Users/abrahamkortovich/.hermes/hermes-agent/venv/bin/python3 \
  /Users/abrahamkortovich/.hermes/skills/productivity/google-workspace/scripts/google_api.py
```

### Common commands

```bash
# Read range
python3 google_api.py sheets get <sheet_id> "Sheet1!A1:D10"

# Clear range (before rebuilding)
python3 google_api.py sheets clear <sheet_id> "Sheet1!A1:D200"

# Update range — --values is a JSON 2D array (array of row arrays)
python3 google_api.py sheets update <sheet_id> "Sheet1!B1:B123" \
  --values '[["FOTO"],["Aglonema.jpeg"],[""]]'

# Append rows
python3 google_api.py sheets append <sheet_id> "Sheet1" --values '[["NAME", "", 0, ""]]'
```

**Critical**: `--values` accepts a **JSON 2D array** (array of row arrays), NOT a flat array.  
Correct: `'[["header"],["val1"],["val2"]]'`  
Wrong: `'["header","val1","val2"]'`  
Wrong: `'[[["header"]]]'`  (nested too deep)

## Image Filename → Sheet Matching Recipe

When syncing local image filenames (e.g. `~/Downloads/pics/`) to sheet rows:

```python
import unicodedata, re, os

def remove_accents(s):
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))

def normalize(s):
    """Normalize sheet filename for matching."""
    s = s.upper() if s else ""
    s = remove_accents(s)
    s = re.sub(r'[\"\'\(\)\[\]]', '', s)
    s = re.sub(r'\s*[-–]\s*', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*VR\s*$', '', s)  # strip portal suffix
    return s.strip()

# Build sheet index
sheet_index = {normalize(row[0].strip()): i + 1
               for i, row in enumerate(sheet_rows) if row and row[0].strip()}

# Manual overrides for known misspellings
manual_overrides = {
    'Crisantemo.jpeg': 43,       # -> CRISONTEMOS
    'Sicdaus.jpeg': 109,         # -> SICDAXUS VR
    'Toreina.jpeg': 115,         # -> TORENIA VR
    'zamioculca negra.jpeg': 123 # -> ZAMIACULCA NEGRA
}

# Match with partial fallback
matches = {}
for fname in sorted(os.listdir(pics_dir)):
    if fname in manual_overrides:
        matches[manual_overrides[fname]] = fname
        continue
    clean = normalize(os.path.splitext(fname)[0])
    if clean in sheet_index:
        matches[sheet_index[clean]] = fname
    else:
        for sheet_name, row_num in sheet_index.items():
            if row_num in matches:
                continue
            if (len(clean) >= 5 and len(sheet_name) >= 5 and
                (clean in sheet_name or sheet_name in clean or
                 clean[:6] == sheet_name[:6])):
                matches[row_num] = fname
                break
```

**Partial match heuristic**: compare first 6 characters. Requires both strings to be ≥5 chars. VR suffix stripped before comparison. Manual overrides handle irreconcilable spelling differences (e.g. `Crisantemo` → `CRISONTEMOS`).

## Spells

- **lumos** — sync portal stock → sheet `STOCK` column (column C). Matches items by normalized name. Overwrites all matched rows (not just empty ones).
- **alohomora** — TBD