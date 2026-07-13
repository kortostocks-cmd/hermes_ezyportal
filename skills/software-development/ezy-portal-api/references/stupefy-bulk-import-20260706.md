# Stupefy Bulk Import — Jul 6 2026

## Context
Fresh EZY Portal tenant (183 items created from scratch, no existing data).
Source: Google Sheet INVENTARIO tab (184 plants, 2 cajas).
Token: `ten_HoiNERJauY87azH92hGwD_3IIAK_XxsQIen9JNj0A-g`

## Workflow

1. **Read sheet**: `INVENTARIO!A1:B1000` (PLANTA + STOCK columns only)
2. **Build item list** with code generation, conflict resolution, and name overrides
3. **Show preview** to user for confirmation
4. **POST items** via curl subprocess (urllib gives 401 with newer keys)
5. **PATCH to activate**: All items created with `isActive=false`, `version=1`. PATCH each with `{"isActive": True, "version": 1}`.

## Name Overrides Applied

| Sheet Name | Portal Name | Portal Code |
|---|---|---|
| FICUS LYRATA (HASTA 200CM) | FICUS LYRATA GRANDE | PL-FICUS-LYRATA-GRANDE |
| FICUS LYRATA 3 RAMAS (HASTA 175CM) | FICUS LYRATA 3 RAMAS (HASTA 175CM) | PL-FICUS-LYRATA-3-RAMAS |
| CAJA POTE 120_1000PCS | CAJA POTE 120_1000PCS | CAJA-POTE-1201000PCS (sin PL-) |
| CAJA POTE 180_450PCS | CAJA POTE 180_450PCS | CAJA-POTE-180450PCS (sin PL-) |

## Dedup Rules
- MONSTERA ADANSONII: 2 rows in sheet (106, 107, identical) → include exactly 1
- FICUS LYRATA variants with parenthetical notes: include, strip parentheses from code only
- CAJA POTE items: include as stock items, no PL- prefix

## Results
- 183 items created and activated
- 181 plants (PL- prefix)
- 2 cajas (no prefix)
- 0 failures
- No prices set on any item

## API Quirks Found
- `itemType: "nonstock"` → 400 validation error. Use `"stock"` for all physical items including cajas.
- Items POSTed with `isSellable: True` receive default `isActive: False`. Must PATCH after creation.
- Fresh tenants have empty item groups + item classes endpoints. POST works without groupId/classId.
- curl subprocess works reliably with `ten_HoiNERJ...` key. Python urllib fails with 401.