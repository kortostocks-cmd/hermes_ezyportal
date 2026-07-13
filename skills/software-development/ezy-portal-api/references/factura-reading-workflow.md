# Factura Reading Workflow (protego)

Workflow for reading Vivero Rose supplier invoices and converting them to EZY Portal sales orders.

## When to Use

User sends a photo of a printed invoice (factura) from a supplier (Vivero Cely, Vivero Mi Jardín, Vivero Ian, etc.) and asks to create a sales order for a specific SUPER EXTRA branch.

## Critical Rules

1. **NO MEZCLAR FACTURAS** — Each invoice is processed independently. Never combine line items from multiple invoices unless the user explicitly says "juntame todas" or "suma todo".
2. **NO SUMAR STOCK** — When processing a single invoice, do NOT add quantities to existing inventory. Just report the items and quantities AS THEY APPEAR on the invoice.
3. **SOLO LO QUE SE PIDE** — Only process what the user asked. If they say "no hagas nada aun", stop. If they say "solo esta imagen", don't reference previous images. Reset state per invoice.
4. **PREGUNTAR ANTES DE CREAR** — Always show a summary table before creating the order. User must confirm with "si" before creating.
5. **NO ASUMIR ITEMS** — If text is blurry or illegible, ask the user to confirm rather than guessing. The user will tell you what it says.

## Annotation Handling (Red Handwriting on Invoices)

Vivero Rose invoices often have handwritten red annotations next to items:

| Annotation | Meaning | Action |
|------------|---------|--------|
| **N/C** | Nota de Crédito — item was returned/credited | **EXCLUDE** from SO. Ask user if unclear. |
| **MC** | NOT like N/C — confirmed by user as "no traquilo" (include them). Likely "Mercancía Cancelada" from supplier perspective but NOT a credit to exclude. | **INCLUDE** in SO normally. Do NOT skip or ask. |

## Workflow workflow

### Step 1: Read the invoice image
Use the vision description of the image directly. Do NOT skip or summarize — include ALL items, even partially visible ones.

### Step 2: Present summary table
Show the user a clean table: | # | Producto | Cant | Precio | Total |

### Step 3: User correction loop
The user may correct specific items ("no es petunin, es petunia", "no sumes esto"). Apply corrections immediately and present the updated table.

### Step 4: Confirm before creating
Ask "¿está correcto para crear la orden de venta?" and wait for explicit confirmation.

### Step 5: Create Sales Order (SO)
Use `POST /api/commerce/sales-orders` with:
- `bpId` / `bpCode` for the SUPER EXTRA branch
- `documentDate` / `validUntil` = invoice date
- `lines[]` with exact items from the confirmed table
- `priceListId` / `priceListCode` = SALE_EXTRA (SALE_SUPER no longer exists)
- `currency` = "USD" or "B/." (whichever is on the invoice)
- `reference` = "Factura No.{number}"
- `status` = "DRAFT" (user preference, confirmed Jul 2026)

### Step 6: Report result
After creation, report: SO number, total, how many lines.

## Branch Mapping (SUPER EXTRA)

| Branch | BP Code | BP ID |
|--------|---------|-------|
| via israel | CL-0035 | 32249c40-... |
| los pueblos | CL-0005 | a8cea960-... |
| albrook | CL-0017 | db64ad3e-... |
| monterico | CL-0006 | 083fb553-... |
| el Lago | CL-0019 | 78532e5e-... |
| las acacias | CL-0004 | 6bf480fd-... |
| sabanitas | (none yet) | e1df2e36-... |

## Common Corrections & Typo Mappings

User often corrects:
- "muelleja es molleja" (MOLLEJITAS corrected to MOLLEJA)
- "bombero es romero" (BOMBERO corrected to ROMERO)
- "b chocolate es chavelitas" (CHOCOLATE corrected and added to CHAVELITAS count)
- "albahaca" & "albaga" → ALBAHACA VERDE (ALBAGA is a known typo for ALBAHACA)
- "photus" → POTHOS (both PL-PHOTUS and PL-POTHOS exist as separate portal items; use PL-POTHOS as canonical and note original name in description)
- "palo de brazil" (with Z) → PALO DE BRASIL (with S)
- Price/unit format (the user says "$0.75" but means B/. 0.75)
- "albahaca" vs "albahaca verde" (sheet naming)

When user says "X es Y" (e.g., "bombero es romero") — this means: item X from the invoice should be treated as item Y in the order. It does NOT mean add X to Y's total. It means X's quantity replaces (or maps to) Y's.

## Pitfall: Invoice Image Legibility

Invoice photos are often blurry, angled, or partially obscured. Items 6, 7, 8 in a 9-item invoice may be unreadable. Do NOT guess.

Approach:
1. Read clearly visible items with high confidence
2. For borderline items, present what you think it says with a question mark
3. Ask user for the items you cannot read
4. Wait for user to type them out or send a clearer photo

## Pitfall: "Tajos / mini Tajos" naming

The user uses Spanish nursery shorthand:
- "Jade / mini jade" on an invoice may mean both Jade and Mini Jade are present
- "Tajos / mini Tajos" may mean items are bundled together
- The user decides whether to split or combine. Ask: "¿Jade y mini jade son líneas separadas o la misma?"
