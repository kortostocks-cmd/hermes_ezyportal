# Accounts/Clients Endpoint Discovery (2026-06-22)

## Summary
The EZY Portal API has an `/api/accounts` endpoint for managing clients/accounts, but it uses **Bearer JWT authentication** — NOT the tenant `X-Api-Key` used by the Items API.

## Tested Endpoints

| Endpoint | Method | Auth Tested | Result |
|----------|--------|-------------|--------|
| `/api/accounts` | GET | `X-Api-Key: ten_...` | **401 Unauthorized** |
| `/api/accounts` | GET | (Bearer needed) | Not tested — requires user login JWT |
| `/api/customers` | GET | `X-Api-Key: ten_...` | 404 Not Found |
| `/api/clients` | GET | `X-Api-Key: ten_...` | 404 Not Found |
| `/api/contacts` | GET | `X-Api-Key: ten_...` | 404 Not Found |
| `/api/partners` | GET | `X-Api-Key: ten_...` | 404 Not Found |
| `/api/parties` | GET | `X-Api-Key: ten_...` | 404 Not Found |

## cURL Commands That Worked

```bash
# Items API — works with X-Api-Key
curl -H "X-Api-Key: ten_iiXLA5AvHe-qjYgbrEjbdaWATDVjsxKxLmq8bSETi3Q" \
  -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/items/items?expand=prices&page=1&perPage=50"

# Accounts API — requires Bearer token (NOT X-Api-Key)
curl -H "Authorization: Bearer <USER_JWT_TOKEN>" \
  -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/accounts"
```

## Key Finding
The same tenant domain (`vivero.ezyts.com`) hosts multiple API services with **different authentication schemes**:
- **Items/Catalog API** (`/api/items/...`) → `X-Api-Key: ten_...`
- **Accounts/Clients API** (`/api/accounts`) → `Authorization: Bearer <jwt>`
- **Integrations API** (separate domain) → `Authorization: ApiKey <key>`

This is not documented in the main EZY Portal docs — discovered empirically.

## Next Steps for User
To list/create clients via API:
1. Obtain a Bearer JWT token by logging into the Portal UI as a user
2. Use that token with `Authorization: Bearer <token>` header
3. Call `GET /api/accounts` to list, `POST /api/accounts` to create

Without a Bearer token, client management must be done via the Portal UI.