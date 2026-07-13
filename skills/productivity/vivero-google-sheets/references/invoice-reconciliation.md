# Invoice-to-Inventory Reconciliation (protego workflow)

This document captures the workflow for reconciling supplier invoices against the vivero inventory.

## Workflow

1. **Receive invoices** (photos)
2. **Extract data** manually or via vision
3. **Normalize names** using the synonym map (see naming-conventions.md)
4. **Sum quantities** across all invoices by normalized product name
5. **Exclude non-products**: fletes, caja pote, etc.
6. **Cross-reference** with inventory sheet (INVENTARIO tab) — check if each product exists
7. **Show preview** to user for confirmation BEFORE writing or creating anything
8. **Apply approved changes**

## Pitfalls (from session corrections)

- Do NOT include: fletes, caja pote 180, chocolate (unless confirmed)
- "Bombero" on invoices maps to ROMERO in inventory, not a separate product
- "Mini Uvas" maps to MINI JADE or is excluded if user says so
- "Chocolate" maps to CHAVELITAS
- "Novias" maps to NOVIO CHINO or CINTA MALA MADRE
- User will correct quantities — always show the math
- When in doubt, ASK before including/excluding an item

## Template: Invoice Item Table

| Factura | Proveedor | Producto | Cant | Precio |
|---------|-----------|----------|------|--------|
| No.XXX | Nombre | NOMBRE | # | $X.XX |

After all invoices processed: sum by product, alpha sort, present for confirmation.
