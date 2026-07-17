# INVENTARIO sheet column order (Jul 16 2026 verified)

**TRUTH from re-read A1:J1**: actual order is **NOT** the memory snippet.

| Col | Header       | Notes                                       |
|-----|--------------|---------------------------------------------|
| A   | PLANTA       | item name                                   |
| B   | SALE_EXTRA   | SALE price (USD)                            |
| C   | STOCK        | itemStockTotal                             |
| D   | COST_MIJARDIN| NOT COST_A&G                                |
| E   | COST_EDWIN   |                                             |
| F   | COST_HACIENDA|                                             |
| G   | COST_A&G     |                                             |
| H   | COST_SARACELY|                                             |
| I   | COST_SUGEY   |                                             |
| J   | COST_IAN     |                                             |

**Pitfall**: if a script or memory says "col D = COST_A&G" it's WRONG for the current sheet. Always read A1:J1 once at session start and use letter-accurate column indices. The lumos.py and other existing scripts get this right because they read headers dynamically — only ad-hoc patches need to be careful.

## AGAVE alias rule (Jul 16 2026)

POs may list `AGAVE AMARILLO` and `AGAVE VERDE` (PO-2026-000021, COST_A&G, $5 each, 4 units each) but the **INVENTARIO sheet has only AGAVE GIGANTE — already merged**. Don't try to create new rows. Add the $5 to **AGAVE GIGANTE row, COST_A&G column G**.

When audit shows "AGAVE AMARILLO in PO, sheet has $5 in AGAVE GIGANTE" this is the correct outcome — it's a manual_aliases merge, not a missing row.

## SUCULENTAS GRANDE cost instructors

Three POs, three suppliers, all from Viveros Mi Jardin / Viveros ian:
- COST_MIJARDIN $2.25 (PO-2026-000015)
- COST_IAN $0.80 (PO-2026-000028)
- COST_HACIENDA $2.25 (PO-2026-000032 — note: bp="Viveros ian" but priceListCode="COST_HACIENDA", cost goes to HACIENDA col F anyway)
- COST_SARACELY $3.25 (PO-2026-000029) — **user explicitly cleared this in Jul 2026**

User memory rule: "SUCULENTAS GRANDE: solo MIJARDIN $2.25 + IAN $0.80 (SARACELY \$3.25 eliminado jul 2026)". If a PO shows SARACELY $3.25, skip it.

## ALCANCEL dual-supplier pattern

Two different POs for same item, two different suppliers:
- PO-2026-000030 (Viveros Mi Jardin, pl=COST_JARDIN) → $0.75 → COST_MIJARDIN col D
- PO-2026-000028 (Viveros ian, pl=COST_IAN) → $0.60 → COST_IAN col J

When sheet shows COST_MIJARDIN=$0.75 but the COST_IAN cell is empty, that's a half-filled row. Don't assume drift — fill the missing column.

## "Solo arreglalo" workflow signal

When user says "solo arreglalo" / "solo X" / "wtf" after a diff report:
- DO NOT run full avada kedavra cascade
- DO NOT touch REPORTS / SOLD_AMOUNT / other tabs unless asked
- Fix ONLY the named rows/columns
- Don't explain the broader system architecture
- Show before/after rows compactly

"aliases agave wtf" specifically: user did NOT want the manual_aliases system explained or expanded — just the AGAVE GIGANTE row updated and any orphan AGAVE AMARILLO/VERDE rows cleared.
