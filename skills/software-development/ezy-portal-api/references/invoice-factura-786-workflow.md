# Factura 786 Sales Order Workflow — Los Pueblos (Jul 2026)

## Overview
Complete workflow for converting a Vivero Rose invoice (Factura No. 786) into an EZY Portal Sales Order for Super Extra los pueblos (CL-0005).

## Invoice Details
- **Client:** SUPER EXTRA los pueblos (CL-0005, bpId: `a8cea960-d200-4222-8654-6cda0093d6b9`)
- **Factura No.:** 786
- **Date:** 26/06/2026
- **Reference:** Factura No.786
- **Price List:** SALE_EXTRA (`13ce22b6-0b29-4029-be65-42e8c23cb239`)
- **Payment Terms:** COD (`382b5aac-6850-4838-b225-b23afa7594d1`)
- **Currency:** USD

## Items Mapped (26 lines, excluding N/C)

| Line | Description | Portal Code | Qty | Unit Price (B/.) |
|---|---|---|---|---|
| 1 | HIERBA BUENA VR | PL-HIERBA-BUENA | 4 | 1.75 |
| 2 | ROMERO VR | PL-ROMERO | 10 | 1.75 |
| 3 | MENTA VR | PL-MENTA | 4 | 1.75 |
| 4 | RUDA VR | PL-RUDA | 8 | 1.75 |
| 5 | LENGUA DE SUEG (1st) | PL-LENGUA-DE-SUEGRA-MINI | 3 | 3.80 |
| 6 | LENGUA DE SUEG (2nd) | PL-LENGUA-DE-SUEGRA-MINI | 3 | 3.80 |
| 7 | CHAVELITAS VR | PL-CHAVELITAS | 8 | 1.50 |
| 8 | SABILA ALOE PEQ | PL-SABILA-ALOE-PEQUENA | 2 | 2.20 |
| 9 | MINI JADE VR | PL-MINI-JADE | 3 | 2.00 |
| 10 | JADE VR | PL-JADE | 3 | 3.20 |
| 11 | TOMILLO VR | PL-TOMILLO | 3 | 1.75 |
| 12 | FITONIA ROJA | PL-FITONIA-ROJA | 3 | 2.25 |
| 13 | CINTA MALA MADRE | PL-CINTA-MALA-MADRE | 3 | 1.75 |
| 14 | MOLLEJITAS VR | **N/C — EXCLUDED** | — | — |
| 15 | CACTUS VARIADO | PL-CACTUS-MEDIANO | 3 | 1.95 |
| 16 | CACTUS VARIADOS | PL-CACTUS-MEDIANO | 3 | 2.85 |
| 17 | HELECHO VR | PL-HELECHOS | 2 | 4.00 |
| 18 | CORONITA DE CRISTO | PL-CORONITA | 2 | 2.25 |
| 19 | AJI BOLITA DECOR | PL-AJI-BOLITA | 3 | 4.25 |
| 20 | COLEOS VR | PL-COLEOS | 2 | 2.00 |
| 21 | ZAMIOCULCA NEGRA | PL-MILLONARIA-ZAMIOCULCA-NEGRA | 2 | 14.00 |
| 22 | PETUNIN VR | PL-PETUNIN | 3 | 2.50 |
| 23 | NOVIO CHINO VR | PL-NOVIO-CHINO | 4 | 2.25 |
| 24 | CRISANTEMOS EN | PL-CRISANTEMOS | 4 | 2.50 |
| 25 | CLAVELITO VR | PL-CLAVELITO | 4 | 2.00 |
| 26 | TORENIA VR | PL-TORENIA | 4 | 2.50 |
| 27 | CELOZIA VR | PL-CELOCIA | 4 | 1.95 |

**SO Total:** B/. 241.50 (excludes MOLLEJITAS N/C = B/. 4.50)  
**Factura Total:** B/. 246.00

## Key IDs (from existing SO d17d9a26-e027-4d77-bbeb-0a00849e9780)
- **warehouseId:** `95c298a9-54d8-4c51-ae78-5c3b76cac657` (PRINCIPAL / ALMACEN PRINCIPAL)
- **taxCategoryId:** `097722df-e70c-4380-9372-a863c67c2bca` (EXCENTO)
- **uomCode:** `EA`
