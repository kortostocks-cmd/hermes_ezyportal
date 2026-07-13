# Ezy Portal Knowledge Sync — Session Example

**Date**: 2026-06-17
**Profile**: `ezy_portal_expert`
**Source**: `~/mi-cerebro/hermes/knowledge/ezy_portal/ezy_rules.md` (9,191 lines, ~283 KB)
**Target**: `~/.hermes/profiles/ezy_portal_expert/SOUL.md`

## What Was Done

1. **Discovered** the knowledge file via `find ~/mi-cerebro -name "*.md"`
2. **Read** the full file (Postman collection + OpenAPI definitions for Ezy Portal Items API)
3. **Extracted** ~15 actionable rules from 9k lines of verbose spec
4. **Appended** a marked section to SOUL.md with the distilled rules

## Source File Structure (Summary)

The source `ezy_rules.md` contains:
- **Lines 1-10**: Basic agent rules (auth, pagination, JSON, validation)
- **Lines 13-15**: Discord token (hardcoded — should be in env)
- **Lines 18-116**: Postman collection for "Portal Business — Items with Pricing"
  - Auth: `X-Api-Key` header with `ten_` prefix (Tenant API Key, Superuser only)
  - Base URL: `https://app.portal.net`
  - Endpoints: list items with pricing, filtered list, single item by code
  - Pagination: `page`, `perPage` params
  - Filters: `isActive`, `isSellable`, `query`, `sortBy`, `sortDescending`
  - Expand: `expand=prices` to include price arrays
- **Lines 123-9191**: OpenAPI/Swagger definitions (models: Item, ItemPrice, Barcode, Category, Group, Class, UOM, Tax, etc.)

## Distilled Rules Injected into SOUL.md

```markdown
# REGLAS EZY PORTAL (desde mi-cerebro/hermes/knowledge/ezy_portal/ezy_rules.md)
- **Autenticación API**: Todas las llamadas deben incluir el Bearer Token configurado en el entorno. Si un endpoint responde 401, intenta renovar el token o notifica al usuario inmediatamente.
- **Paginación**: Maneja siempre paginación al solicitar listas de usuarios o logs del portal.
- **Payloads**: Estructura los payloads de envío estrictamente en formato JSON válido.
- **Validación**: Muestra los cambios realizados y pregunta si es correcto antes de validar.
- **Documentación base**: https://docs.ezyts.com/en/portal/
- **Autenticación Tenant**: Usa header `X-Api-Key` prefijado con `ten_` (generado en Portal UI: Settings > API Keys, solo Superuser).
- **Endpoints clave**:
  - `GET {{BASE_URL}}/api/items/items?expand=prices` — Lista items con precios (paginado: page, perPage)
  - `GET {{BASE_URL}}/api/items/items/by-code/{code}?expand=prices` — Item individual por código
  - Filtros comunes: `isActive=true`, `isSellable=true`, `sortBy=name`, `query=` (búsqueda libre)
- **Respuesta de precios**: Cada price row tiene `masked: true/false` — si `masked=true`, `price=null` (sin autorización para ver ese precio). Key sin authorization group = acceso total tenant (nada enmascarado).
- **Discord**: Token disponible en reglas (preguntar si falla).
```

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Kept rules in Spanish | User's profile language; matches their mental model |
| Discarded full OpenAPI models | Too verbose for SOUL.md; agent can fetch schema on demand if needed |
| Kept endpoint templates with `{{BASE_URL}}` | Matches Postman collection pattern; user can substitute |
| Noted `masked` price behavior | Critical for correct UI rendering — agent must check before showing prices |
| Flagged Discord token in rules | Security risk — should move to env var; noted for user to fix |
| Referenced source path in header | Traceability for future re-sync |

## Re-sync Checklist

When the source file updates:
1. Re-read `~/mi-cerebro/hermes/knowledge/ezy_portal/ezy_rules.md`
2. Diff against current SOUL.md section
3. Update only changed rules (auth, endpoints, filters, price behavior)
4. Preserve the `(desde ...)` header for traceability