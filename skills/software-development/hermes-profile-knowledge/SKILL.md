---
name: hermes-profile-knowledge
description: "Manage Hermes profile knowledge: sync external knowledge sources into SOUL.md, maintain profile-specific rules, and integrate domain expertise into the agent's system prompt."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, profile, soul, knowledge, configuration, sync]
    related_skills: [hermes-agent, plan]
---

# Hermes Profile Knowledge Management

Manage the **SOUL.md** file (the profile's system prompt) and integrate external knowledge sources (markdown files, docs, API specs) into the agent's persistent instructions.

## When to Use This Skill

- User has domain knowledge in external files (e.g., `~/mi-cerebro/...`, `~/docs/...`, Notion, Obsidian) that should be reflected in SOUL.md
- Profile needs domain-specific rules (API auth patterns, pagination, validation flows, endpoints)
- You need to extract, summarize, and inject structured rules from verbose source docs into SOUL.md
- SOUL.md has grown stale and needs a refresh from source-of-truth files

## Core Workflow

### 1. Discover Knowledge Sources
```bash
# Common locations users keep domain knowledge
~/mi-cerebro/hermes/knowledge/<domain>/
~/docs/<domain>/
~/projects/<project>/docs/
~/.hermes/profiles/<profile>/references/
```

Use `search_files` or `terminal` to find `.md`, `.yaml`, `.json` files with rules, specs, or configs.

### 2. Extract & Distill
Read the source file(s) and pull out **actionable rules** the agent should follow:
- Authentication patterns (headers, token refresh, prefixes)
- Pagination / filtering conventions
- Payload formats (JSON, form-data, multipart)
- Validation gates (confirm before write, dry-run flags)
- Key endpoints with param templates
- Error-handling flows (401 → refresh, 429 → backoff)
- Environment variable names for secrets

**Discard**: verbose examples, full schemas, tutorial prose, outdated versions.

### 3. Update SOUL.md
Append a clearly marked section (e.g., `# DOMAIN RULES (from <source>)`) with bullet-point rules. Keep it **scannable** — the agent reads this every turn.

```markdown
# DOMAIN RULES (from ~/mi-cerebro/hermes/knowledge/ezy_portal/ezy_rules.md)
- **Auth**: Bearer Token in env; on 401 → refresh or alert user
- **Pagination**: Always use `page` + `perPage` on list endpoints
- **Payloads**: Strict JSON only
- **Validation**: Show changes, ask before executing
- **Base URL**: https://docs.ezyts.com/en/portal/
- **Tenant Auth**: Header `X-Api-Key: ten_...` (Superuser only)
- **Endpoints**:
  - `GET /api/items/items?expand=prices&page=1&perPage=20`
  - `GET /api/items/items/by-code/{code}?expand=prices`
  - Filters: `isActive`, `isSellable`, `sortBy=name`, `query=`
- **Prices**: `masked=true` → `price=null` (no auth group = full access)
- **Discord**: Token in rules (ask if fails)
```

### 4. Verify
- Read back `SOUL.md` to confirm the section is present and concise
- Ask user: "Does this capture what you need, or should I adjust?"

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| Copying entire 9k-line OpenAPI spec into SOUL.md | Extract only the 5-10 rules the agent actually needs at inference time |
| Forgetting to mark the source path | Always include `(from <path>)` in the section header for traceability |
| Overwriting the base HERMES identity block | Prepend/append; never replace lines 1-3 of SOUL.md |
| Syncing secrets (tokens, keys) into SOUL.md | **Never** — reference env var names only (e.g., `BEARER_TOKEN` in env) |
| Creating duplicate sections on re-sync | Search for existing section header first; replace in place |

## Commands Reference

| Action | Command |
|--------|---------|
| View current SOUL.md | `read_file(path="~/.hermes/profiles/<profile>/SOUL.md")` |
| Edit SOUL.md | `patch(path="~/.hermes/profiles/<profile>/SOUL.md", old_string="...", new_string="...")` |
| List profile dir | `terminal(command="ls -la ~/.hermes/profiles/<profile>/")` |
| Find knowledge files | `search_files(pattern="ezy_rules|api.*spec|config", target="files", path="~/mi-cerebro")` |

## Related Files

- `~/.hermes/profiles/<profile>/SOUL.md` — the system prompt (edit this)
- `~/.hermes/profiles/<profile>/references/` — place for synced reference copies
- `~/mi-cerebro/` — user's external knowledge base (common pattern)

## Example: Ezy Portal Sync (This Session)

**Source**: `~/mi-cerebro/hermes/knowledge/ezy_portal/ezy_rules.md` (9k lines, Postman collection + OpenAPI)

**Extracted into SOUL.md**:
```markdown
# REGLAS EZY PORTAL (desde mi-cerebro/hermes/knowledge/ezy_portal/ezy_rules.md)
- **Autenticación API**: Bearer Token en entorno; 401 → renovar o avisar
- **Paginación**: Obligatoria en listas de usuarios/logs
- **Payloads**: JSON válido estricto
- **Validación**: Mostrar cambios y confirmar antes de ejecutar
- **Docs base**: https://docs.ezyts.com/en/portal/
- **Auth Tenant**: Header `X-Api-Key: ten_...` (solo Superuser)
- **Endpoints clave**: `/api/items/items?expand=prices`, `/api/items/items/by-code/{code}?expand=prices`
- **Filtros**: `isActive`, `isSellable`, `sortBy=name`, `query=`
- **Precios**: `masked=true` → `price=null`; sin auth group = acceso total
- **Discord**: Token en reglas (preguntar si falla)
```

**Result**: ~15 lines of actionable rules replacing 9k lines of raw spec.