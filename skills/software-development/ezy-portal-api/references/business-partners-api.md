# Business Partners API (EZY Portal)

**Module:** `business-partners` — Customers, Vendors, Leads
**Base URL:** `https://<tenant>.ezyts.com/api/business-partners`
**Auth:** `X-Api-Key: ten_...` (tenant API key, Superuser-generated)

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/bp` | List all business partners (paginated) |
| `POST` | `/bp` | Create business partner — **requires `Idempotency-Key` header** |
| `GET` | `/bp/{code}` | Get by code (code = `code` field, not UUID) |
| `GET` | `/contacts` | List contacts linked to business partners |

---

## Query Parameters (List)

- `page` (default: 1)
- `perPage` (default: 30)
- Filter by `roles`, `status`, `isCustomer`, `isVendor`, `isLead` — *untested, may work*

---

## Business Partner Object

```json
{
  "id": "uuid",
  "tenantId": "uuid",
  "code": "CL-001",           // unique code, used for GET by code
  "name": "ARRAIJAN",
  "legalName": "Vivero Mi Jardin",  // optional
  "status": "active",         // active | inactive
  "roles": ["customer"],      // customer | vendor | lead
  "isCustomer": true,
  "isVendor": false,
  "isLead": false,
  "taxExempt": false,
  "taxId": "8-779-196",       // optional
  "fiscalData": {             // optional
    "checkDigit": "59",
    "customerType": "taxpayer",
    "taxIdType": "juridical"
  },
  "currencyCode": "USD",
  "priceListCode": "SALE_PUBLIC",
  "creditLimit": 0,
  "onHold": false,
  "ownerUserId": "uuid",
  "ownerName": "RUBEN ROSE",
  "phone": "6201-0162",
  "email": "viverosian16@gmail.com",
  "languageCode": "es",
  "industry": "Venta de hierbas y flores",
  "defaultContactId": "uuid",
  "tags": ["provedor", "ruta_ruben"],
  "notes": "Nuestro Provedor de plantas",
  "syncState": "in_sync",
  "createdAt": "2026-06-10T14:58:44.867751Z",
  "createdBy": "uuid",
  "createdByName": "abraham kortovich",
  "updatedAt": "2026-06-10T15:38:22.541939Z",
  "updatedBy": "uuid",
  "updatedByName": "abraham kortovich",
  "version": 1
}
```

---

## Create Payload (Minimal Customer)

```json
{
  "code": "CL-0002",
  "name": "chorrera",
  "status": "active",
  "roles": ["customer"],
  "isCustomer": true,
  "isVendor": false,
  "isLead": false,
  "taxExempt": false,
  "currencyCode": "USD",
  "priceListCode": "SALE_PUBLIC",
  "creditLimit": 0,
  "onHold": false,
  "languageCode": "es",
  "tags": ["ruta_ruben"]
}
```

**Required header for POST:** `Idempotency-Key: <uuid>`

---

## Known Price Lists (from tenant)

| Code | Name | Used By |
|------|------|---------|
| `SALE_PUBLIC` | Public Sale | Customers (CL-*) |
| `COST_JARDIN` | Cost Jardin | Vendor PR-0001 |
| `COST_IAN` | Cost Ian | Vendor PR-0002 |
| `SALE_SUPER` | Sale Super | Items (PL-*) |
| `COST_SARA` | Cost Sara | Items (new imports) |

---

## Pagination

Response format:
```json
{
  "data": [...],
  "total": 43,
  "page": 1,
  "perPage": 30,
  "totalPages": 2,
  "hasMore": true
}
```

---

## cURL Examples

```bash
# List all
curl -H "X-Api-Key: ten_..." -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/business-partners/bp"

# Get by code
curl -H "X-Api-Key: ten_..." -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/business-partners/bp/CL-001"

# Create (requires Idempotency-Key)
curl -X POST -H "X-Api-Key: ten_..." -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"code":"CL-0002","name":"chorrera",...}' \
  "https://vivero.ezyts.com/api/business-partners/bp"

# Contacts
curl -H "X-Api-Key: ten_..." -H "Accept: application/json" \
  "https://vivero.ezyts.com/api/business-partners/contacts"
```

---

## Pitfalls

1. **GET by code uses `code` field, not UUID** — `/bp/CL-001` works, `/bp/<uuid>` returns 400 INVALID_UUID
2. **POST requires `Idempotency-Key` header** — without it returns `IDEMPOTENCY_KEY_REQUIRED` error
3. **No `expand=prices` equivalent** — prices are on items, not business partners
4. **Filter params untested** — may support `roles`, `status`, `isCustomer` query params
5. **`legalName`, `fiscalData`, `taxId` only on vendors** — customers don't typically have these
6. **`defaultContactId` links to contact** — must exist in `/contacts` first

---

## Discovered in Session

- Tenant: `vivero` (https://vivero.ezyts.com)
- API Key: `ten_88BZCwvI9-JjvwBoKF_KB-w69QHDtlsCH5G5uQIwQec`
- 38 clients created from image OCR (codes CL-0001 through CL-0216)
- Pattern: `CL-XXXX` for customers, `PR-XXXX` for vendors
- Tag `ruta_ruben` used for route identification

## Bulk Creation Example (2026-06-22) — 38 Clients from Image OCR

**Source:** Photo of printed route list (38 locations with numbers 1-216)

** plus 202-216)

**Code pattern:** `CL-XXXX` (4-digit zero-padded from image number)
- CL-0001 through CL-0041 (numbers 1-41, skipping gaps)
- CL-0202 through CL-0216 (numbers 202-216, skipping gaps)

**Payload per client:**
```json
{
  "code": "CL-0001",
  "name": "arraijan",
  "status": "active",
  "roles": ["customer"],
  "isCustomer": true,
  "isVendor": false,
  "isLead": false,
  "taxExempt": false,
  "currencyCode": "USD",
  "priceListCode": "SALE_PUBLIC",
  "creditLimit": 0,
  "onHold": false,
  "languageCode": "es",
  "tags": ["ruta_ruben"]
}
```

**Required header for POST:** `Idempotency-Key: <uuid>` (generate fresh UUID per request)

**Result:** All 38 created successfully. Total clients with `CL-*` codes: 39 (including pre-existing CL-001 ARRAIJAN).

**cURL batch pattern:**
```bash
for code in CL-0001 CL-0002 CL-0004 ...; do
  name=$(lookup_name "$code")
  uuid=$(uuidgen)
  curl -X POST -H "X-Api-Key: ten_..." -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "Idempotency-Key: $uuid" \
    -d "{\"code\":\"$code\",\"name\":\"$name\",...}" \
    "https://vivero.ezyts.com/api/business-partners/bp"
done
```