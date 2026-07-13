# INVENTARIO Sheet Sync Workflow — Jul 10 2026

## Final Sheet Layout (Jul 10 2026)

The user established this column layout for the INVENTARIO tab
(sheet ID `1jYZn3Kd8nIMlRxcQ1nC3K6C3pIzpGPemsO8bc4qG3NE`):

| Col | Header | Source |
|-----|--------|--------|
| A | PLANTA | Sheet (manual input) |
| B | SALE_EXTRA (price) | Extracted from latest SO per item |
| C | STOCK | Portal `itemStockTotal` |
| D | COST_MIJARDIN | From `/api/commerce/purchase-orders?priceListCode=COST_MIJARDIN` |
| E | COST_SARACELY | From PO endpoint |
| F | COST_HACIENDA | From PO endpoint |
| G | COST_EDWIN | From PO endpoint |
| H | COST_SUGEY | From PO endpoint |
| I | COST_A&G | From PO endpoint |

Earlier columns (per existing skill): STOCK in C, COST_MIJARDIN in D, etc. The user
explicitly formatted this layout at session start — preserve it on every update.

## User Preference (verified Jul 10 2026)

- **User populates column headers manually** before asking Hermes to fill data.
  Don't try to add columns programmatically; just use what's there.
- Order: alphabetically by PLANTA name (UPPERCASE comparison).
- TIERRAS rows (TIERRA NEGRA, ABONO ORGANICO, CASCARILLA DE ARROZ) stay at the END
  of the sheet, not in alphabetical position.

## TIERRA-Rose Pricing Rule

The TIERRAS items (TIERRA NEGRA, ABONO ORGANICO, CASCARILLA DE ARROZ) do NOT have
purchase orders — they were created directly in the portal. Their source-of-truth
costs come from the **Vivero Rose** sales orders (BCVAL invoices seen in WhatsApp
photos: $0.95, $0.55, $0.55).

The user explicitly said **NO** to putting Vivero Rose sale prices in the cost
columns — those are venta (sale) prices, not compra (purchase) prices.

**Result**: Columns D-I for TIERRAS items stay EMPTY. If the user wants them
populated, add a separate column (e.g. "COST_ROSE" in column J) explicitly.

## Sync Order Pattern (verified working July 10 2026)

1. Read items from portal (paginated)
2. Read items + columns from sheet
3. Normalize names with `nfkd()` (NFKD + ASCII + UPPERCASE + strip parenthetical + strip "VR")
4. Walk every sheet row:
   a. Update STOCK in C from portal `itemStockTotal`
   b. Update each COST column (D-I) by searching PO via by-code lookup
   c. If item is TIERRAS, leave D-I empty
5. For SALE_EXTRA prices in column B, harvest from sales orders:
   - List all SOs sorted by documentDate desc
   - Fetch each SO individually with `?expand=lines`
   - Take the most recent `unitPrice` per item name (or itemCode)
   - Write to column B
6. Re-sort sheet alphabetically by column A (preserving TIERRAS at end)
7. Single batchUpdate to write all sorted rows back
8. Clear trailing empty rows (use values().clear() on everything below)

## Critical: Preserve-Sheet-Format Rule

Sheet has currency formatting set by the user manually. When writing prices, use
`valueInputOption: "USER_ENTERED"` to preserve formatting. If cells are blank,
write empty string `""` (not None) to avoid breaking the row layout.

## Script Behavior

When user says "lumos":
1. Sync stock from portal → sheet column C
2. Sync supplier costs from POs → sheet columns D-I
3. Sync SALE_EXTRA price from latest SOs → sheet column B
4. Sort alphabetically
5. Move TIERRAS to end
6. Report counts: "Updated X stock, Y costs, Z prices"

# Sheet Cleanup Recipes (verified Jul 10 2026)

## Clear trailing empty rows
After a sort that compacts rows, leftover rows below the last data row can confuse
later merge logic. Clear them with `values().clear()`:

```python
svc.spreadsheets().values().clear(
    spreadsheetId=SHEET_ID,
    range=f"INVENTARIO!A{last_data_row + 1}:Z500",
    body={}
).execute()
```

## Add missing items
When CHECK_GAPS finds items in portal but not in sheet (`~/tmp/check_gaps.py`):

```python
addback_rows = [["ITEM_NAME", "", "", "", "", "", "", "", ""]]
svc.spreadsheets().values().append(
    spreadsheetId=SHEET_ID,
    range=f"INVENTARIO!A{append_row}:I{append_row}",
    valueInputOption="USER_ENTERED",
    insertDataOption="INSERT_ROWS",
    body={"values": addback_rows}
).execute()
```

Note: appends at the bottom — need to re-sort after adding.

## Auth — token expires weekly (verified Jul 10 2026)

When `setup.py --check` returns `TOKEN_REVOKED: ('invalid_grant: Token has been expired...')`:
1. Run `--auth-url` to get OAuth URL
2. User opens URL in browser
3. User pastes the redirect URL (which starts with `http://localhost/?code=...`)
4. Pass that FULL URL (the entire thing) to `--auth-code`

DO NOT try to refresh a revoked token; you cannot. Re-auth with the user.
