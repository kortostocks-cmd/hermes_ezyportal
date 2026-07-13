# Business Partners Module API Discovery (2026-06-22)

## Summary
The EZY Portal UI has a **Business Partners** module accessible at `/business-partners/{id}#overview` (example: `https://vivero.ezyts.com/business-partners/ca064699-d848-4dc1-932e-1bb45f060a32#overview`). The corresponding REST API exists under `/api/business-partners/` and **data endpoints WORK with tenant `X-Api-Key`** (same auth as Items module) on specific sub-paths: `/bp` and `/contacts`.

## Tested Endpoints

| Endpoint | Method | Auth Tested | Result |
|---|---|---|---|
| `/api/business-partners` | GET | `X-Api-Key: ten_...` | 301 redirect to `/api/business-partners/` |
| `/api/business-partners/` | GET | `X-Api-Key: ten_...` | `{"service":"business-partners","status":"ok"}` (health check) |
| **`/api/business-partners/bp`** | GET | `X-Api-Key: ten_...` | **200 — List all Business Partners (paginated)** |
| **`/api/business-partners/bp/{code}`** | GET | `X-Api-Key: ten_...` | **200 — Single BP by code (e.g., CL-001)** |
| **`/api/business-partners/contacts`** | GET | `X-Api-Key: ten_...` | **200 — List all Contacts (paginated)** |
| `/api/business-partners/partners` | GET | `X-Api-Key: ten_...` | 404 Not Found |
| `/api/business-partners/list` | GET | `X-Api-Key: ten_...` | 404 Not Found |
| `/api/business-partners/search` | GET | `X-Api-Key: ten_...` | 404 Not Found |
| `/api/business-partners/{uuid}` | GET | `X-Api-Key: ten_...` | 404 Not Found |

## Key Findings

1. **Health check works with X-Api-Key**: `/api/business-partners/` returns status JSON
2. **Data endpoints ARE accessible with X-Api-Key** on `/bp` and `/contacts` — NOT on `/partners`, `/list`, `/search`
3. **GET by code uses `code` field (e.g., `CL-001`), NOT UUID** — `/bp/CL-001` works, `/bp/<uuid>` returns 400 `INVALID_UUID format`
4. **POST requires `Idempotency-Key` header** — without it returns `IDEMPOTENCY_KEY_REQUIRED` error
5. **Auth is same as Items API**: `X-Api-Key: ten_...` (tenant API key), NOT Bearer JWT
6. **UI URL uses UUID** but API uses `code` field for lookups

## cURL Commands Tested (Working)

```bash
# Health check - works with X-Api-Key
curl -H "X-Api-Key: ten_88BZCwvI9-JjvwBoKF_KB-w69QHDtlsCH5G5uQIwQec" \
  -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/business-partners/"

# List all business partners - WORKS with X-Api-Key
curl -H "X-Api-Key: ten_88BZCwvI9-JjvwBoKF_KB-w69QHDtlsCH5G5uQIwQec" \
  -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/business-partners/bp"

# Get by code - WORKS with X-Api-Key
curl -H "X-Api-Key: ten_88BZCwvI9-JjvwBoKF_KB-w69QHDtlsCH5G5uQIwQec" \
  -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/business-partners/bp/CL-001"

# Create - requires Idempotency-Key header
curl -X POST -H "X-Api-Key: ten_88BZCwvI9-JjvwBoKF_KB-w69QHDtlsCH5G5uQIwQec" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"code":"CL-0002","name":"chorrera","status":"active","roles":["customer"],"isCustomer":true,"isVendor":false,"isLead":false,"taxExempt":false,"currencyCode":"USD","priceListCode":"SALE_PUBLIC","creditLimit":0,"onHold":false,"languageCode":"es","tags":["ruta_ruben"]}' \
  "https://vivero.ezyts.com/api/business-partners/bp"

# List contacts - WORKS with X-Api-Key
curl -H "X-Api-Key: ten_88BZCwvI9-JjvwBoKF_KB-w69QHDtlsCH5G5uQIwQec" \
  -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/business-partners/contacts"
```

## Next Steps for User

To list/create business partners (clients) via API:
1. Use tenant API Key (`X-Api-Key: ten_...`) — same as Items API
2. Use `/bp` for business partners list/detail, `/contacts` for contacts
3. Use `code` field (e.g., `CL-001`) for GET by code, not UUID
4. Include `Idempotency-Key: <uuid>` header on POST

**No Bearer token needed** — works with the same tenant API key as Items.

## Related

- See `references/business-partners-api.md` for full model definitions, create payloads, and pagination
- See `references/accounts-endpoint-discovery.md` for the `/api/accounts` endpoint which DOES require Bearer JWT (different pattern)
- Business Partners and Accounts are different modules with different auth requirements