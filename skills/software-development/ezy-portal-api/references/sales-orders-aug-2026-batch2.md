# Sales Orders Batch — Aug 2026 (Second Batch)

8 sales orders created from Vivero Rose invoices for Super Xtra branches using SALE_EXTRA price list (13ce22b6-0b29-4029-be65-42e8c23cb239).

| SO | Branch | Factura | Date | Lines | Total B/. | Status |
|:--:|--------|:-------:|:----:|:-----:|:---------:|:------:|
| 25 | el Lago | 745 | 05/06 | 22 | 197.14 | DRAFT |
| 28 | las tablas | 780 | 23/06 | 30 | 285.90 | DRAFT |
| 29 | las tablas | (05/06) | 05/06 | 20 | 177.54 | DRAFT |
| 32 | chorrera | 783 | 25/06 | 29 | 263.05 | DRAFT |
| 33 | albrook | 742 | 05/06 | 21 | 119.56 | DRAFT |
| 35 | via israel | 781 | 24/06 | 29 | 287.95 | DRAFT |
| 37 | via israel | 767 | 15/06 | 13 | 96.25 | DRAFT |
| 40 | via israel | 740 | 03/06 | 13 | 83.85 | DRAFT |
| 52 | marqueza | 755 | 08/06 | 17 | 115.19 | DRAFT |
| 53 | albrook | 791 | 30/06 | 21 | 203.00 | DRAFT |
| 54 | chanis | 776 | 22/06 | 27 | 218.99 | DRAFT |
| 55 | condado | 790 | 30/06 | 21 | 194.40 | DRAFT |
| 57 | brisas del golf | 793 | 30/06 | 21 | 166.80 | DRAFT |

## Key Learnings

### Item Corrections
- **MC** (manuscrito) = Nota de Crédito = **excluir**, igual que N/C. No "incluir".

### New Items Added to Portal
- PL-MARIGOLD-VR (created via minimal POST payload)

### API Key Notes
- `ten_Zk271QDTbmEUkcXD4pu4LKvMSgv0n8-b6oyz6SCBjxU` works with Python urllib for all operations (BPs GET, SO POST, items by-code).
- `ten_3HW_...` gets 401 from urllib — use curl via subprocess.

### Client IDs Verified
- Chanis: CL-0040 (d73abea9-fac1-43ac-9c1b-236c3c06b358)
- Brisas Golf: CL-0031 (2c66161e-5906-4d59-afb7-5b3f815665d9)