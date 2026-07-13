---
name: protego
description: "Recibir fotos de facturas por Discord, identificar plantas por nombre, y sumar cantidades a STOCK_NECESARIO en la hoja STOCK_PENDIENTE del Google Sheet del vivero."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Protego — Stock Necesario desde Facturas

## Fase extendida: Reconciliación de facturas de proveedores

Cuando el usuario envía **múltiples facturas de proveedores** (5+), ejecutar este flujo completo:

### Fase 1: Extraer todas las cantidades
1. Usar visión para extraer cada factura: producto + cantidad
2. **NO** extraer precios ni totales (a menos que el usuario los necesite)
3. Sumar cantidades **por producto** a través de todas las facturas
4. Ignorar: FLETE, CAJA POTE 180, y cualquier otro item no-planta que el usuario confirme excluir

### Fase 2: Mapear nombres contra INVENTARIO (Google Sheet)
1. Leer columna A del sheet `INVENTARIO` (ID: `1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`)
2. Para cada producto de factura, normalizar: UPPERCASE, NFKD (quitar acentos), regex `[^A-Z0-9]`→vacío
3. Buscar match exacto normalizado en sheet
4. Si NO hay match → buscar parcial (palabras compartidas con 3+ caracteres)
5. Presentar los posibles matches al usuario y preguntar cuál es correcto
6. **Regla de convención**: "Bombero" = Romero, "Chocolate" = Chavelitas, "Mini Uvas" = Mini Jade, "Novias" = Novio Chino

### Fase 3: Verificar contra Airtable (stock actual)
1. Leer todos los registros de Airtable tabla Items (`tblTXfSmRyVPV6Tv1`)
2. Construir índice normalizado de nombre → stock
3. **CRÍTICO**: Airtable guarda nombres con sufijo ` VR` (ej: "HIERBA BUENA VR"). El normalizador debe ignorar el sufijo ` VR` y cualquier variante de tamaño (MEDIANA/MEDIANAS, GRANDE/PEQUEÑA)
4. Reportar: stock Airtable vs cantidad necesaria → diferencia = lo que realmente hay que comprar
5. Productos con diferencia = 0 no se compran

### Fase 4: Presentar resumen y confirmar
1. Siempre mostrar preview de **qué se va a crear/insertar** antes de ejecutar cualquier acción
2. Lista ordenada alfabéticamente
3. Preguntar: "¿Está correcto?" antes de proceder
4. Si el usuario dice "protegió" o "no lo pongas" → frenar inmediatamente, no hacer nada

## Pitfalls específicos de reconciliación

- **Sheet INVENTARIO usa nombres diferentes al portal**: ej. "LENGUA DE SUEGRA MINI" (sheet) ≠ "LENGUA MINI" (factura)
- **Airtable names carry "VR" suffix**: siempre normalizar quitando VR antes de comparar
- **Plural/singular mismatches**: "SUCULENTAS MEDIANA" (factura) = "SUCULENTAS MEDIANAS" (sheet)
- **"De" removal**: "LENGUA DE SUEGRA MINI" normaliza igual que "LENGUA SUEGRA MINI"
- **"MILLONARIA" prefix**: "ZAMIOCULCA" = "MILLONARIA ZAMIOCULCA" en sheet/portal
- **Nunca crear items nuevos sin confirmar con el usuario**

## Trigger
Cuando el usuario envía fotos de facturas por Discord.

## Flujo

1. El usuario envía imagen(s) de factura(s) por Discord
2. Usar visión para extraer:
   - **Nombre de planta** (buscar match en columna PLANTS de STOCK_PENDIENTE)
   - **Cantidad** (de la factura)
3. Buscar el nombre en la hoja **STOCK_PENDIENTE** del sheet `1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`
4. Si el nombre existe:
   - Sumar la cantidad al valor actual de **STOCK_NECESARIO**
   - Actualizar la celda correspondiente
5. Si el nombre **NO** existe o no se puede identificar claramente:
   - Preguntar al usuario **por Discord** dónde va esa planta
6. Ignorar precios, totales, impuestos, datos del proveedor — solo importa **nombre de planta + cantidad**

## Columnas de STOCK_PENDIENTE

| Columna | Descripción |
|---------|-------------|
| PLANTS (A) | Nombre de la planta |
| STOCK_NECESARIO (B) | Cantidad necesaria (se suma cada vez que llega una factura) |
| STOCK_ACTIVO (C) | Stock actual en el portal (se actualiza con otro spell) |

## Lógica de matching

- Normalizar ambos lados: UPPERCASE, quitar acentos (NFKD), espacios extras
- Si hay match exacto después de normalizar → usarlo
- Si hay múltiples matches → mostrar opciones al usuario
- Si no hay match → preguntar

## Script de actualización

```python
# Actualizar celda específica en STOCK_PENDIENTE
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

SID = '1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE'
creds = Credentials.from_authorized_user_file(
    '~/.hermes/profiles/ezy_portal_expert/google_token.json',
    ['https://www.googleapis.com/auth/spreadsheets']
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
service = build('sheets', 'v4', credentials=creds)

# Leer columna A para encontrar fila
result = service.spreadsheets().values().get(
    spreadsheetId=SID, range='STOCK_PENDIENTE!A:A'
).execute()
names = [r[0].strip().upper() if r else '' for r in result.get('values', [])]

# Encontrar índice por nombre
target = 'AGAVE AMARILLO'
row_idx = next(i for i, n in enumerate(names) if target in n or n in target)
# row_idx+1 porque sheets es 1-indexed, +1 por header

# Leer valor actual
current = service.spreadsheets().values().get(
    spreadsheetId=SID, range=f'STOCK_PENDIENTE!B{row_idx+1}'
).execute()
val = current.get('values', [[0]])[0][0]
nuevo = int(val) + cantidad if val else cantidad

# Actualizar
service.spreadsheets().values().update(
    spreadsheetId=SID, range=f'STOCK_PENDIENTE!B{row_idx+1}',
    valueInputOption='USER_ENTERED',
    body={'values': [[str(nuevo)]]}
).execute()
```