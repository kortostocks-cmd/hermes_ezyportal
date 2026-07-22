# hermes_ezyportal

Hermes Agent profile for **vivero.ezyts.com** — EZY Portal automation for **SUPER EXTRA Panamá**.

## Skills
- **ezy-portal-api** — REST API integration (Items, Sales Orders, Purchase Orders, Pricing)
- **vivero-google-sheets** — INVENTARIO / REPORTS / SOLD_AMOUNT sync
- **discord-invoice-ocr** — Receipt → Sales Order pipeline from Discord images

## Scripts
- `lumos.py` — Portal stock+price → Google Sheet (INVENTARIO tab)
- `alohomora.py` — Portal items+BPs → Airtable backup
- `avada.py` — Full sheet refresh (INVENTARIO + REPORTS + SOLD_AMOUNT)
- `check_sheet_gaps.py` — Find portal items missing from sheet
- `monthly_export.sh` — Monthly close export (VENTAS_{MES} + SOLD_AMOUNT)
- `export_sold_amount_csv.py` — CSV per-month export
- `ocr_swift.swift` / `download_ocr.sh` — OCR pipeline for Discord invoice images

## Spells
- **lumos** — stock sync
- **alohomora** — Airtable backup
- **protego** — Receipt OCR → Sales Order draft
- **avada kedavra** — full 3-tab refresh

## Config & Keys
- API auth: `X-Api-Key` with `ten_` prefix (Superuser only)
- JWT Bearer also supported for some endpoints
- Current API key: `ten_IXGGXhQIxbDtPtQjsZQD1QvBDizJglI1TkMf-e1mpP0` (expires Jul 2026)
- Discount lists: `SALE_EXTRA` = `13ce22b6`

## Rules
- Prefer **DRAFT** Sales Orders unless confirmed otherwise
- Keep **negative stock** as-is
- Items with cost MUST have stock; otherwise exclude
- “Mc” on invoice = **Nota de Crédito** (exclude from SO)
- Soil/fertilizer/cascarilla → no cost, no stock, placed at bottom of sheet
