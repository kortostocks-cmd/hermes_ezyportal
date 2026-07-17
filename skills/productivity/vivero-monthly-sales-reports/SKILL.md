---
name: vivero-monthly-sales-reports
description: "Monthly close workflow for VENTAS_{MES} and SOLD_AMOUNT tabs — yellow TOTAL row, pink NOTA_CREDITO column, proportional-discount NC computation, and CSV export to ventas_{YYYY-MM}.csv under ~/Documents/vivero_ventas/."
category: productivity
tags: [vivero, sheets, monthly, sales, csv, discount, NOTA_CREDITO, yellow, pink]
---

# vivero-monthly-sales-reports

Pattern for closing out a month's sales in EZY Portal + Google Sheets, with the visual + structural conventions the user requires.

## When to use

- The user says "ya puedes exportar", "csv", "fin de mes", or simply asks to close the month.
- The user asks "¿cuánto vendí en {mes}?".
- After running Avada Kedavra and detecting that a month just ended.

## Workflow

1. **Run Avada Kedavra** — refreshes INVENTARIO, REPORTS, SOLD_AMOUNT from portal.
2. **Check discount situation** — see "Portal discount behavior" below. If SOs have discounts, **warn user before proceeding**.
3. **Sort VENTAS_{MES} by REFERENCIA numeric** — columns A-C + F (NOTA_CREDITO).
4. **Add NOTA_CREDITO column** to SOLD_AMOUNT (col H) using proportional distribution.
5. **Apply yellow TOTAL row + pink NC column** formatting (recipe below).
6. **Confirm totals** — sum of grandTotals from SOs = sum of TOTAL_C in VENTAS_{MES} = sum of TOTAL_SALE in SOLD_AMOUNT.

## Color codes (RGB)

```python
YELLOW = {"red": 1.0, "green": 0.95, "blue": 0.4}   # TOTAL row, end-of-month visual
PINK   = {"red": 1.0, "green": 0.85, "blue": 0.85}  # NOTA_CREDITO col, "line with credit" visual
```

Apply via `spreadsheets.batchUpdate()` → `repeatCell` request with `sheetId` from `spreadsheets().get()`.

## Portal discount behavior (CRITICAL)

**The portal auto-applies `discountPercent=5` to new SOs** even when the POST payload contains no discount field. Triggered by `paymentTermsId: 9025dae9`. Silent — only visible in GET response.

**Detection (after every SO creation or sync)**:
```python
so = api_get(f"/api/commerce/sales-orders/{id}").json()
if (so.get('discountPercent') or 0) > 0 or (so.get('discountAmount') or 0) > 0:
    STOP — notify user with list of affected SOs before processing.
```

**If user accepts discounts**, compute per-item NC proportionally:
```python
ratio = grand / sub                                # ~0.95 for 5% discount
line_after = line_total * ratio                    # what each line "becomes"
nc_per_line = line_total - line_after              # portion attributed to NC
# Sum across all lines of all discounted SOs → per-item NC.
```

**Or simpler**: take grandTotal from top-level response. Sum of grandTotals across all SOs = the actual amount billed. Use that for the TOTAL row.

## Verified baseline (Jun 2026)

- 55 SOs total
- 6 with discount: SO-000068, 072, 075, 079, 081, 090
- Total discount: $25.44
- Total billed (grandTotal): $6,856.30
- Total sub (pre-discount): $6,881.74

## CSV export

`scripts/export_sold_amount_csv.py` writes `~/Documents/vivero_ventas/ventas_{YYYY-MM}.csv` from the SOLD_AMOUNT tab. Auto-named with current month. Run when user asks to export.

Columns: PLANTA, AMOUNT_SOLD, TOTAL_COST, TOTAL_SALE, TOTAL.

## Pitfalls

- `values().update()` with empty strings doesn't overwrite — use raw format then user-entered, or clear first then update.
- Yellow on TOTAL row requires `sheetId` from `spreadsheets().get()`, NOT sheet name.
- Forgetting to refresh SOLD_AMOUNT after a new SO batch → stale AMOUNT_SOLD.
- Sum of rounded per-row sale prices ≠ grandTotal (floating-point noise). Write the canonical grandTotal to TOTAL row directly.

## Related

- `ezy-portal-api` skill — endpoint details, SO creation pitfall (auto-discount warning embedded there).
- `vivero-google-sheets` skill — INVENTARIO / REPORTS sync workflow.
- Script: `scripts/export_sold_amount_csv.py`.
</content>
</invoke>