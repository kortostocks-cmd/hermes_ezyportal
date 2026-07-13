# STUPEFY: Sheet → Portal (crear items nuevos)

Importa plantas desde el Google Sheet INVENTARIO al EZY Portal.

## Origen: INVENTARIO

La pestaña **INVENTARIO** tiene solo 2 columnas activas:
- A: PLANTA (nombre)
- B: STOCK (vacío u opcional)

No tiene columna de precio. No tiene columna de código.

## Reglas de código

### Plantas regulares → prefijo `PL-`

```
nombre: "AGAVE AMARILLO"
código: PL-AGAVE-AMARILLO
```

Slugify: UPPERCASE → Ñ→N, acentos quitados → `[^A-Z0-9\s]` eliminado → espacios a guiones.

### CAJAS → sin `PL-`

Todo item que contenga "CAJA POTE" en el nombre recibe código sin prefijo:
```
nombre: "CAJA POTE 120_1000PCS"
código: CAJA-POTE-1201000PCS  (guion bajo se elimina)
```

### Nombres con paréntesis

Regla del usuario: **el código NO debe incluir el contenido del paréntesis**, pero el **nombre SÍ** lo conserva.

```
nombre: "FICUS LYRATA (HASTA 200CM)"
código: PL-FICUS-LYRATA-HASTA-200CM  → paréntesis extraído como sufijo
            
nombre: "FICUS LYRATA 3 RAMAS (HASTA 175CM)"
código: PL-FICUS-LYRATA-3-RAMAS      → "3 RAMAS" está antes del paréntesis, no hay conflicto
```

**Algoritmo de código**:
1. Generar `code_base` = slugify(nombre con paréntesis removido)
2. `code = "PL-" + code_base`
3. Si `code` ya existe en `seen_codes`:
   - Extraer contenido del paréntesis: `re.search(r'\(([^)]*)\)', nombre)`
   - slugify_raw(contenido del paréntesis): normaliza el texto sin quitar paréntesis, luego remueve `()`
   - `code = "PL-" + code_base + "-" + extra`
4. Si aún así hay conflicto, añadir sufijo numérico `-2`, `-3`, etc.

**Nota**: `slugify_raw()` normaliza pero NO elimina contenido entre paréntesis — solo remueve los caracteres `(` y `)` al final.

### GUAYACAN ENANO (TECOMA)

El slugify quita `(TECOMA)` → `PL-GUAYACAN-ENANO`. No hay conflicto porque el nombre sin paréntesis es único.

## Exclusión de duplicados

Cuando un mismo nombre aparece 2+ veces en INVENTARIO:
- **MONSTERA ADANSONII** (filas 106 y 107): crear solo UNA instancia, la segunda se skip.

## Exclusiones por decisión del usuario

El usuario puede pedir excluir items específicos:
- Monstera Adansonii completo → excluir ambas filas
- Variantes de FICUS LYRATA con `(HASTA ...)` → inicialmente excluidas, luego el usuario pidió incluirlas pero con código limpio

Siempre preguntar al usuario qué hacer con items ambiguos.

## Precios

**No se asignan precios durante la importación**. Todos los items se crean sin precio. El usuario no ha definido precios en el INVENTARIO.

## Flujo de confirmación

Siempre:
1. Leer INVENTARIO completo
2. Generar lista con códigos + nombres
3. Mostrar al usuario: **"¿Está bien?"** con resumen (total plantas, total cajas, excluidos)
4. Esperar confirmación explícita antes de llamar a la API del portal

## Payload API

Usar endpoint `POST /api/items/items` con X-Api-Key:

```json
{
  "code": "PL-AGAVE-AMARILLO",
  "name": "AGAVE AMARILLO",
  "isActive": true,
  "isSellable": true,
  "uomCode": "U",
  "itemType": "Item"
}
```

Para CAJAS, mismo payload pero sin prefijo `PL-` en code.