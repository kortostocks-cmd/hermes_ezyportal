# Normalización de plantas_nuevas (LUMOS)

Workflow para limpiar y normalizar la pestaña `plantas_nuevas` del sheet del vivero.

## Columnas

| # | Columna | Ejemplo | Notas |
|---|---------|---------|-------|
| A | CODIGO | PL-ANTORCHA | Prefijo `PL-` + nombre slugificado |
| B | NOMBRE | ANTORCHA | **Siempre UPPERCASE** |
| C | LISTA_PRECIO | COST_HACIENDA | Ver lista de precios válidos |
| D | PRECIO_USD | 20 | Precio en dólares |
| E | STOCK | (opcional) | Se llena manualmente |
| F | DESCRIPCION | (opcional) | Se llena manualmente |

## Slugificación de códigos PL-

Reglas:
1. Normalizar UTF-8: Ñ→N, ü→u, acentos quitados (NFKD + ASCII ignore)
2. UPPERCASE
3. Reemplazar todo lo no alfanumérico por guiones
4. Quitar guiones dobles y extremos
5. Prefijar `PL-`

```python
def slugify(nombre):
    import unicodedata, re
    n = unicodedata.normalize('NFKD', nombre)
    n = n.encode('ASCII', 'ignore').decode('ASCII')
    n = n.upper()
    n = re.sub(r'[^A-Z0-9]+', '-', n)
    n = n.strip('-')
    return 'PL-' + n
```

## Detección de duplicados vs INVENTARIO

La pestaña `INVENTARIO` tiene nombres más descriptivos (ej: "AGAVE EN POTE 5")
mientras que `plantas_nuevas` usa nombres comerciales cortos (ej: "AGAVE AMARILLO").
La comparación debe ser por **nombre normalizado** (NFKD + ASCII + UPPERCASE + sin espacios/guiones)
contra columna A del INVENTARIO.

Código de comparación:

```python
inv_nombres = set()
for r in inventario_rows:
    if r and r[0]:
        inv_nombres.add(normalize(r[0]))

def normalize(s):
    import unicodedata, re
    s = unicodedata.normalize('NFKD', s).encode('ASCII','ignore').decode('ASCII')
    return re.sub(r'[^A-Z0-9]', '', s.upper())

for r in nuevas_rows:
    nombre = r[1]
    if normalize(nombre) in inv_nombres:
        print(f'DUPLICADO: {nombre}')
    else:
        print(f'NUEVA: {nombre}')
```

## Correcciones de ortografía detectadas

| En plantas_nuevas | Corrección |
|---|---|
| ARBLOL CITRONELA | (así está en source) |
| PHOTOS MULTI RAMA | (así está en source) |
| WASHINTONIA | (así está en source) |
| PAPIRUS → PAPIRO | Corregido |
| JAZMINES → JAZMIN DEL CABO | Corregido |

## Eliminación de filas duplicadas (ejemplo real)

Sesión 2026-06-30: se identificaron y borraron 3 filas duplicadas:

| Nombre | Ocurrencias | Acción |
|---|---|---|
| CACTUS DE... | 3 (filas 85-87), sin precio, mismas características | Borrar filas 86 y 87, conservar fila 85 |
| SANSEVIERIA R | 2 (filas 75-76), ambas COST_EDWIN $2, idénticas | Borrar fila 76 |
| CORDILINIA | 2 (fila 7 COST_HACIENDA y fila 89 COST_ISMAEL) | **Conservar ambas** — diferentes listas de precio |

Los índices se pasan como `startIndex` (0-based, exclusive end) en `deleteDimension`. Siempre borrar **de abajo hacia arriba** para no afectar índices de filas superiores.