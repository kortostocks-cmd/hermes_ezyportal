---
name: vivero-google-sheets
description: "Google Sheets access for vivero.ezyts.com — automated OAuth + read/write 'plantas_nuevas' tab (ID: 1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE)"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
required_credential_files:
  - path: google_token.json
    description: "Google OAuth2 token (auto-managed by setup)"
  - path: google_client_secret.json
    description: "Google OAuth2 client credentials (Desktop app)"
metadata:
  hermes:
    tags: [Google, Sheets, vivero, plants, OAuth]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [google-workspace]
---

# Vivero Google Sheets

Skill dedicado al Google Sheet del vivero (`1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`).
Maneja OAuth automático (token en `~/.hermes/profiles/ezy_portal_expert/google_token.json`)
y expone CLI simple para leer/escribir la pestaña `plantas_nuevas`.

## Configuración (una sola vez)

```bash
# 1. Verificar si ya está autenticado
VSETUP --check

# 2. Si NO_AUTHENTICATED: guardar client_secret.json y correr
VSETUP --client-secret /ruta/a/client_secret.json

# 3. Obtener URL de autorización
VSETUP --auth-url

# 4. Abrir URL en navegador, autorizar TODOS los scopes, copiar URL final (http://localhost/?code=...)
# 5. Intercambiar código
VSETUP --auth-code "URL_COMPLETA_DEL_NAVEGADOR"

# 6. Verificar
VSETUP --check
# Debe salir: AUTHENTICATED: Token valid
```

Alias recomendados (agregar a `~/.zshrc` o `~/.bashrc`):
```bash
VSETUP="python ~/.hermes/profiles/ezy_portal_expert/skills/productivity/vivero-google-sheets/scripts/setup.py"
VAPI="python ~/.hermes/profiles/ezy_portal_expert/skills/productivity/vivero-google-sheets/scripts/sheets_api.py"
```

## Spells (Workflow Commands)

El usuario usa nomenclatura Harry Potter para comandos de workflow:

| Spell | Acción |
|-------|--------|
| **lumos** | Portal → INVENTARIO (sincronizar stock/precios) |
| **alohomora** | Backup → Airtable |
| **stupefy** | Sheet → Portal (crear items nuevos desde INVENTARIO) |
| **protego** | Reconciliar facturas de proveedores vs INVENTARIO y Airtable (nombre+stock) | Ver skill `vivero/protego` |

### STUPEFY — Importar INVENTARIO al Portal

Workflow para crear items en EZY Portal desde la pestaña **INVENTARIO** del Google Sheet.

**Pasos**:
1. Leer `INVENTARIO!A1:B1000` (columnas: PLANTA, STOCK)
2. Por cada fila (excepto header):
   - Generar código: `PL-` + slugify(nombre) para plantas
   - CAJAS (contienen "CAJA POTE") → código sin `PL-`
   - Nombres con paréntesis → nombre lo conserva, código lo remueve
   - Si hay conflicto de código (e.g. FICUS LYRATA vs FICUS LYRATA (HASTA 200CM)): añadir contenido del paréntesis como sufijo
   - No asignar precio
3. Excluir duplicados exactos (e.g. MONSTERA ADANSONII ×2 → solo 1)
4. Mostrar lista completa al usuario y esperar confirmación
5. POST a `/api/items/items` con X-Api-Key

Ver `references/stupefy-workflow.md` para:
- Algoritmo de slugify y conflictos
- Reglas de parentesis en códigos vs nombres
- Payload API exacto
- Exclusiones y casos borde

--
## Sheets en el documento

El sheet ID `1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE` tiene estas pestañas:

| Pestaña | ID | Filas | Propósito |
|---------|----|-------|-----------|
| **INVENTARIO** | 0 | ~191 items | Catálogo principal. Columnas: PLANTA (A), SALE_EXTRA (B), STOCK (C), COST_MIJARDIN (D), COST_SARACELY (E), COST_HACIENDA (F), COST_EDWIN (G), COST_SUGEY (H), COST_A&G (I). |
| **REPORTS** | ? | ~191 items (same as INVENTARIO) | Reportes de costos y márgenes. Columnas: PLANTA (A), COSTO (B), SALE (C), MARGIN % (D). COSTO muestra $X o $min-$max si hay varios proveedores. |
| **SOLD_AMOUNT** | 828083203 | ~191 items + TOTAL row | Unidades vendidas y márgenes reales. ⚠️ Tab name has trailing space: `'SOLD_AMOUNT '`. Columnas: PLANTA (A), AMOUNT_SOLD (B), TOTAL_COST (C), TOTAL_SALE (D), TOTAL (E). **User wants this tab "más fácil de ver"** — see "SOLD_AMOUNT visualization" below. |
| **PLANTAS_NUEVAS** | 1375933155 | 1000 | Plantas nuevas para importar al portal. **Nombre exacto en mayúsculas**. |

> **Regla**: Las pestañas en Google Sheets son **case-sensitive**. Siempre usar `INVENTARIO` y `PLANTAS_NUEVAS` en mayúsculas. `plantas_nuevas` en minúscula devuelve tabla vacía.

## Uso directo en Python (recomendado)

Los scripts `sheets_api.py` y `setup.py` pueden fallar con `ModuleNotFoundError` porque el venv del skill no tiene `googleapiclient`. Usar el **venv de Hermes** siempre:

```bash
VENV_PY="~/.hermes/hermes-agent/venv/bin/python3"
$VENV_PY - <<'PY'
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json, os

TOKEN = os.path.expanduser('~/.hermes/profiles/ezy_portal_expert/google_token.json')
creds = Credentials.from_authorized_user_file(TOKEN, ['https://www.googleapis.com/auth/spreadsheets'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN, 'w') as f:
        json.dump(json.loads(creds.to_json()), f)
        
svc = build('sheets', 'v4', credentials=creds)
SID = '1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE'

# Ejemplo: leer INVENTARIO completo
result = svc.spreadsheets().values().get(spreadsheetId=SID, range='INVENTARIO!A1:B1000').execute()
print(f"Filas: {len(result.get('values', []))}")
PY
```

## Uso vía CLI (VAPI alias) — si falla, usar Python directo arriba

```bash
# Leer PLANTAS_NUEVAS (tabla completa) — usar SIEMPRE mayúsculas
$VAPI read PLANTAS_NUEVAS

# Leer rango específico
$VAPI read PLANTAS_NUEVAS A1:F50

# Escribir/actualizar filas (append)
$VAPI append PLANTAS_NUEVAS '[[\"PL-NUEVO\",\"NUEVA PLANTA\",\"COST_HACIENDA\",\"15\",\"\",\"Desc\"]]'

# Sobrescribir rango
$VAPI write PLANTAS_NUEVAS A2 '[[\"PL-NUEVO\",\"NUEVA PLANTA\",\"COST_HACIENDA\",\"15\",\"\",\"Desc\"]]'

# Crear nueva pestaña (batchUpdate addSheet)
$VAPI add-sheet nombre_pestaña
```

## Estructura de `plantas_nuevas`

| Columna | Ejemplo | Notas |
|---------|---------|-------|
| CODIGO | PL-ANTORCHA | Prefijo `PL-` |
| NOMBRE | ANTORCHA | Nombre comercial |
| LISTA_PRECIO | COST_HACIENDA | COST_HACIENDA / COST_SARA |
| PRECIO_USD | 20 | Número (string en sheet) |
| STOCK | (vacío) | Opcional |
| DESCRIPCION | (vacío) | Opcional |

## Scripts

- `scripts/setup.py` — OAuth setup (wrapper del google-workspace setup.py apuntando a este profile)
- `scripts/sheets_api.py` — CLI simple read/append/write/add-sheet para este sheet ID

## Workflow LUMOS — Sincronizar portal → INVENTARIO

Cuando el usuario dice "LUMOS" (o "lumos"), ejecutar:

1. Correr el script directamente:
   ```bash
   ~/.hermes/hermes-agent/venv/bin/python3 \
     ~/.hermes/profiles/ezy_portal_expert/skills/software-development/ezy-portal-api/scripts/lumos.py
   ```
2. Reportar: total items portal, total filas sheet, cuántas actualizaciones se hicieron

**Importante**: lumos solo **actualiza** filas existentes en INVENTARIO. NO agrega items nuevos que existan en el portal pero no en el sheet. Si el usuario reporta que falta una planta (ej. MARIGOLD), hay que agregarla manualmente con `VAPI append INVENTARIO '[["NOMBRE","","stock","precio"]]'`.

## Workflow LUMOS (legacy) — Normalización de plantas_nuevas

Cuando el usuario dice "LUMOS" y se refiere específicamente a plantas_nuevas (sesiones anteriores):
3. Para cada fila:
   - Normalizar NOMBRE a UPPERCASE
   - Si CODIGO está vacío o incorrecto: generar `PL-` + slugify(nombre)
   - Slugify usa NFKD normalisation (Ñ→N, acentos quitados), UPPERCASE, regex `[^A-Z0-9]+`→`-`
4. Aplicar batchUpdate con `valueInputOption: USER_ENTERED`
5. Verificar duplicados vs pestaña INVENTARIO (comparar nombres normalizados)
6. Reportar resultado al usuario

Ver `references/plantas-nuevas-normalizacion.md` para detalles de slugificación y detección de duplicados.  
Ver `references/inventario-plantas-2026.md` para la lista completa de 184 plantas del INVENTARIO con sinónimos y ejemplos de códigos.

### Eliminación de filas duplicadas en plantas_nuevas

Cuando filas duplicadas tienen el mismo nombre y lista de precio (ej: "SANSEVIERIA R" ×2 ambas COST_EDWIN), borrar con `deleteDimension`. Las filas se borran **de abajo hacia arriba** para no alterar índices:

```python
requests = [
    {
        'deleteDimension': {
            'range': {
                'sheetId': 0,      # ID de la primera sheet (generalmente 0)
                'dimension': 'ROWS',
                'startIndex': row_index,    # 0-indexed, fila sheet a borrar
                'endIndex': row_index + 1
            }
        }
    }
]
body = {'requests': requests}
svc.spreadsheets().batchUpdate(spreadsheetId=SID, body=body).execute()
```

**Regla**: solo borrar duplicados idénticos (misma lista, mismo precio, sin diferenciación en nombre). Si tienen diferente lista de precio (ej: CORDILINIA COST_HACIENDA vs CORDILINIA COST_ISMAEL), conservar ambas.

### Verificación final

Después de limpiar y normalizar, verificar contra la pestaña INVENTARIO por nombre normalizado (NFKD + ASCII + UPPERCASE + `re.sub(r'[^A-Z0-9]', '', s)`) para asegurar que son plantas realmente nuevas, no existentes con nombre diferente.

## SOLD_AMOUNT visualization (Jul 13 2026, user preference)

User wants this tab **"más fácil de ver"** at a glance. Apply formatting after every write:

### Apply via batchUpdate (after each write)
```python
from googleapiclient.discovery import build

def beautify_sold_amount(svc, sheet_id, n_rows):
    sid = sheet_id
    requests = []

    # 1. Freeze header row
    requests.append({"updateSheetProperties": {
        "properties": {"sheetId": 828083203, "gridProperties": {"frozenRowCount": 1}},
        "fields": "gridProperties.frozenRowCount"
    }})

    # 2. Header row: bold + green fill + white text
    requests.append({"repeatCell": {
        "range": {"sheetId": 828083203, "startRowIndex": 0, "endRowIndex": 1},
        "cell": {"userEnteredFormat": {
            "backgroundColor": {"red": 0.20, "green": 0.60, "blue": 0.30},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
        }},
        "fields": "userEnteredFormat(backgroundColor,textFormat)"
    }})

    # 3. Bold the TOTAL row (last row)
    requests.append({"repeatCell": {
        "range": {"sheetId": 828083203, "startRowIndex": n_rows-1, "endRowIndex": n_rows},
        "cell": {"userEnteredFormat": {
            "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.85},
            "textFormat": {"bold": True}
        }},
        "fields": "userEnteredFormat(backgroundColor,textFormat)"
    }})

    # 4. Conditional format: highlight items with no sales (AMOUNT_SOLD = 0 or empty) in red text
    requests.append({"addConditionalFormatRule": {
        "rule": {
            "ranges": [{"sheetId": 828083203, "startRowIndex": 1, "endRowIndex": n_rows-1,
                        "startColumnIndex": 0, "endColumnIndex": 5}],
            "booleanRule": {
                "condition": {"type": "CUSTOM_FORMULA",
                              "values": [{"userEnteredValue": "=$B2=0"}]},
                "format": {"textFormat": {"foregroundColor": {"red": 0.85, "green": 0.30, "blue": 0.30}}}
            }
        },
        "index": 0
    }})

    # 5. Resize columns: PLANTA wide, others auto
    requests.append({"updateDimensionProperties": {
        "range": {"sheetId": 828083203, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
        "properties": {"pixelSize": 220},
        "fields": "pixelSize"
    }})

    svc.spreadsheets().batchUpdate(spreadsheetId=sid, body={"requests": requests}).execute()
```

### Quick "más fácil de ver" version (if batchUpdate flags sheet ID 828083203 unfound, fall back)
Just freeze + bold header + bold total — minimum acceptable formatting:
```python
def beautify_minimal(svc, sheet_id, n_rows):
    requests = [
        {"updateSheetProperties": {"properties": {"sheetId": 828083203,
            "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}},
        {"repeatCell": {"range": {"sheetId": 828083203, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
            "fields": "userEnteredFormat.textFormat"}}
    ]
    svc.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={"requests": requests}).execute()
```

### Sort rule already applied
Items are pre-sorted by AMOUNT_SOLD descending (top sellers at top). Use this in the write step:
```python
for name, data in sorted(sales_by_item.items(), key=lambda x: x[1]["qty"], reverse=True):
```
(The avada.py spell does this. Verify after writing.)

### Currency format on TOTAL_SALE / TOTAL_COST / TOTAL columns
Apply `numberFormat: {type: "CURRENCY", pattern: "$#,##0.00"}` for columns C, D, E if header parsing isn't enough.

## VENTAS_JUNIO tab (Jul 13 2026, sales reconciliation)

Per-factura breakdown sheet for monthly reporting. Created Jul 13 2026 from 54 sales orders.

### Structure
| Col | Field | Example |
|-----|-------|---------|
| A | FACTURA | `No.000068` |
| B | REFERENCIA | `Factura No.759` |
| C | TOTAL | $115.33 (grandTotal post-discount) |
| F | NOTA_CREDITO | $6.07 (per-row discount) |

### Sort order
**Sort by REFERENCIA number** (numeric), NOT documentNumber. User request: "llena ventas junio ordenado por numero de referencias" → ascending by the invoice number in `Factura No.X`:
```python
def ref_number(so):
    ref = so.get('reference', '') or ''
    m = re.search(r'(\d+)', ref)
    return int(m.group(0)) if m else 0

sos_sorted = sorted(sos, key=lambda so: (ref_number(so), so.get('documentNumber', '')))
```

### NOTA_CREDITO calculation
The portal may auto-apply 5% discount to some SOs. Use `discountAmount` from each SO:
```python
disc_amt = float(so.get('discountAmount', 0) or 0)
if disc_amt > 0:
    note = round(disc_amt, 2)
```

**Total NC ≠ 5% of all SOs.** As of Jul 13 2026: 6 SOs had discount (not 5) — always re-query live. Total NC accumulated = $25.44 (CHITRE, LAS ACACIAS, EL LAGO, SANTIAGO TERMINAL, CHORRERA, PENONOME).

### Formatting rules (must apply after every write)
- **TOTAL row**: yellow background `{red:1, green:0.95, blue:0.4}`, bold
- **NOTA_CREDITO col F**: pink background `{red:1, green:0.85, blue:0.85}`
- Empty columns D & E are visual padding (Sheet looks cleaner with gap between TOTAL and NC)

### Diagnostic: total mismatch between SOLD_AMOUNT and VENTAS_JUNIO
Both sheets MUST show the same TOTAL. If they don't:
1. Check if all SOs are pulled (`hasMore` pagination exhausted)
2. Verify discount distribution in SOLD_AMOUNT uses proportional formula: `lineAfter = lineTotal * (grand / sub)` for the 6 affected SOs only
3. Cross-check grandTotal sum vs subTotal sum — gap = total NC

As of Jul 13 2026: both sheets show **$6,856.30** with NC = **$25.44** ✅

## "Mira que todos los artículos estén" — sheet completeness ritual

When user says "mira que todos los articulos esten en inventario, reporte" or similar completeness-check, run this 3-step verification (don't skip steps):

**Step 1: Get all portal items (paginated)**
```python
items = []
page = 1
while True:
    d = get(f"{BASE}/api/items/items?perPage=100&page={page}&isActive=true&sortBy=name")
    items.extend(d.get('data', []))
    if not d.get('hasMore'): break
    page += 1
```

**Step 2: Read INVENTARIO, REPORTS, SOLD_AMOUNT**

**Step 3: Normalize names and diff**
```python
import unicodedata, re
def nfkd(s):
    n = unicodedata.normalize("NFD", s.upper())
    n = re.sub(r"[\u0300-\u036f]", "", n)
    return re.sub(r"\s+", " ", n).strip()

portal_norm = {nfkd(i['name']) for i in items}
inv_set = {nfkd(r[0]) for r in INV if r and r[0]}
missing = portal_norm - inv_set
```

Expected normal output: 0 missing items in INVENTARIO + 0 in REPORTS. (SOLD_AMOUNT can have many missing — that's normal, only sold items go there.)

If missing > 0, add them:
- Look up portal item by name with `?query=NAME`
- If found, append to sheet (alphabetical sort, plants before TIERRAS)
- Preserve trailing space `'SOLD_AMOUNT '` tab name

**Known Jul 13 2026 gap set**: DALIA, MICKY, PAPIRO were 3 missing — all stock=0 in portal but added to sheets for future purchases.

## CSV export workflow (Jul 13 2026)

User asked: "cada fin de mes se ponga amarillo todo asi yo se que tengo que exportarlo" → CSV export of SOLD_AMOUNT is part of monthly ritual.

### Script
`scripts/export_sold_amount_csv.py` exists for this purpose. Run with:
```bash
~/.hermes/hermes-agent/venv/bin/python3 \
  ~/.hermes/profiles/ezy_portal_expert/scripts/export_sold_amount_csv.py
```

Default output: `~/Documents/vivero_ventas/ventas_YYYY-MM.csv`

### CSV format
```
PLANTA,AMOUNT_SOLD,TOTAL_COST,TOTAL_SALE,TOTAL
TIERRA NEGRA,1007,0.0,937.88,937.88
...
TOTAL,3786,6.4,6804.91,6798.51
```

The TOTAL row at end sums all items; TOTAL_COST = PHOTUS unit_cost (0.80) × qty only (other plants have no tracked cost → 0).

### Signals that trigger CSV export reminder
- User says "ya puedes exportar a csv?" → run the export
- End of month (last day) → can be cron'd (not auto-set up yet)
- Yellow highlighting on SOLD_AMOUNT TOTAL = visual cue user mentioned

## Reglas

1. **Nunca** hacer write/append sin confirmar con el usuario (mostrar preview).
2. Token se renueva solo; si falla → `VSETUP --revoke` y repetir pasos 2-5.
3. Sheet ID fijo: `1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE` (no cambiar sin confirmar).
4. **Nombres en mayúsculas**: toda fila nueva debe tener NOMBRE en UPPERCASE. Si encuentras minúsculas, corregir antes de procesar.
5. **Códigos según nombre**: el código debe generarse con `PL-` + nombre normalizado (sin acentos, Ñ→N, espacios→guiones). No usar códigos arbitrarios.
6. **Duplicados en el sheet**: antes de crear items, verificar nombres repetidos dentro del mismo sheet y eliminarlos.

## Pitfalls

### PEP 668: pip bloqueado en macOS

macOS 12.7.6+ tiene PEP 668 activo — `pip install` falla incluso con `--user`. Los scripts `setup.py` y `sheets_api.py` fallan si intentan instalar dependencias.

**Fix**: usar el venv de Hermes directamente:

```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(
    '~/.hermes/profiles/ezy_portal_expert/google_token.json',
    ['https://www.googleapis.com/auth/spreadsheets']
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    import json
    with open('~/.hermes/profiles/ezy_portal_expert/google_token.json', 'w') as f:
        json.dump(json.loads(creds.to_json()), f)
    print('Token refreshed OK')
service = build('sheets', 'v4', credentials=creds)
result = service.spreadsheets().values().get(...)
```

### Token OAuth expirado con refresh_token disponible

El token Google expira cada hora. Si `setup.py --check` falla pero el token tiene `refresh_token`, se puede refrescar programáticamente sin re-autenticar. El truco es usar `Request()` de `google.auth.transport.requests` — no requiere browser.

### lumos no agrega items nuevos al INVENTARIO — usar check_sheet_gaps.py

El script lumos.py solo hace matching por nombre normalizado entre portal y sheet y actualiza stock/precio donde hay diferencias. No agrega filas nuevas.

Flujo correcto después de lumos:
1. Correr check_sheet_gaps.py para detectar items en portal que faltan en el sheet
2. Si hay gaps, agregarlos con VAPI append INVENTARIO
3. Dejar precio vacío — lumos lo llenará si el portal tiene precio configurado

Ejemplo Jul 2026: 224 portal items vs 210 en sheet = 38 gaps detectados.

### ModuleNotFoundError: googleapiclient

Los scripts `sheets_api.py` y `setup.py` del skill usan `from googleapiclient.discovery import build`, pero el venv del skill no tiene la dependencia instalada. **Fix**: usar siempre `~/.hermes/hermes-agent/venv/bin/python3` (que sí tiene google-auth + google-api-python-client). Ver sección "Uso directo en Python" arriba.

### Case-Sensitive pestañas: tabla vacía al leer

Google Sheets es case-sensitive en nombres de pestañas. La pestaña real en el sheet se llama `PLANTAS_NUEVAS` (mayúsculas), no `plantas_nuevas` (minúsculas). En sesiones anteriores la habíamos creado como minúscula, pero el sheet actual usa mayúsculas. Siempre usar `INVENTARIO` y `PLANTAS_NUEVAS` en mayúsculas en código y en la API.

El endpoint `GET /api/pricing-tax/price-lists` sí funciona con X-Api-Key (devuelve todos los price lists con sus IDs). Pero `expand=prices` en items devuelve array vacío porque la API key no tiene permiso de lectura de precios. El script lumos.py ya maneja esto internamente.