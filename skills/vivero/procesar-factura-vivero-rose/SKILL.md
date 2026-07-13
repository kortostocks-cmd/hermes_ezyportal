---
name: procesar-factura-vivero-rose
description: "Procesar facturas (fotos) de Vivero Rose → Sales Orders en EZY Portal. Extraer items de la imagen, mapear a items del portal, crear SO con SALE_EXTRA. Maneja notas rojas (MC, N/C), sinónimos y sucursales de Super Xtra."
category: vivero
tags: [ezy, factura, vivero-rose, super-xtra, sales-order, protego]
---

# Procesar Factura de Vivero Rose → Sales Order

## Trigger
- Usuario envía una foto de factura de **Vivero Rose** (proveedor, logo rosa roja)
- Usuario dice "mira esta factura", "procesa esto", o envía imagen

## Requisitos previos
- Cargar skill `ezy-portal-api` (tiene auth, endpoints, price lists)
- API key activa: `ten_6lRpIW7SBXsZOHylXp80MTf-qFAdW-DjKWJITOdF6bk`
- Tenant: `vivero.ezyts.com`
- Usar `curl` via subprocess para todas las llamadas API (urllib da 401 con keys nuevas)
- Siempre verificar items activos antes de incluirlos en SO
- Precio de factura se pone manualmente como unitPrice, no se usa precio del portal

## Pasos

### 1. Extraer datos de la imagen
Usar `vision_analyze` para extraer:
- Número de factura ("Factura No.XXX")
- Fecha (documentDate)
- Cliente y sucursal (de la dirección: El Lago, Sabanitas, etc.)
- OC (número de orden de compra, suele estar en recuadro beige abajo)
- Items: descripción, cantidad, precio unitario, total
- Notas rojas: MC, N/C u otras anotaciones manuscritas
- Total

**⚠️ Factura No. no visible**: A veces el número de factura está cortado en la foto. Si no se ve, usar `"Factura {sucursal} {fecha}"` como reference (ej. "Factura Aguadulce 22/06/2026").

### 2. Identificar sucursal de Super Xtra
De la dirección en la factura determinar la sucursal:

| Dirección en factura | Sucursal | BP ID |
|---|---|---|
| "El LAGO" / "EL LAGO" | el Lago | 78532e5e-caa7-4863-aa80-7090e8e22257 |
| "SABANITAS" / "COLON" | Sabanitas | e1df2e36-4388-4630-86b5-d73c0e668f99 |
| "AGUADULCE" | Aguadulce | d9cd6c5e-9886-41df-a3a8-4d30ede82a7a |
| "VILLA LUCRE" / "VILLA LUCRE" | Villa Lucre | 8ca7ecc1-dfcf-4085-83cc-bd2166fee458 |
| "CHITRE" / "CHITRÉ" / "CHIRE" | Chitré | 796f2a9e-4ef6-4720-a61b-d965fc75a95c |
| "BRISAS DEL GOLF" / "BRISAS" | Brisas del Golf | 2c66161e-5906-4d59-afb7-5b3f815665d9 |
| "VILLA LOBOS" / "VILLALOBOS" | Villa Lobos | bf0fa375-e60e-482a-abad-0692bb732da7 |
| "TRANSISMICA" / "TRANSÍSMICA" | Transísmica | 78b4f197-790f-4665-b431-1b8c43ad9ef0 |
| "CATIVA" / "CATIVA" | Cativa | f4e05fff-d789-4899-81b9-aad1aab0546a |
| "CONDADO DEL REY" / "CONDADO" | Condado | 15ee6af1-c661-45a1-acd9-7e62a8cd3c3d |
| "PENONOME" / "PENONOMÉ" | Penonomé | b3b486a9-bb07-4670-841c-fe4c95eead1a |
| "VIA ISRAEL" | via israel | 32249c40-4c89-4fdf-a381-73969dba188d |
| "LOS PUEBLOS" | los pueblos | a8cea960-d200-4222-8654-6cda0093d6b9 |
| "ALBROOK" | albrook | db64ad3e-a54c-4f15-b15b-d60dba3917a4 |
| "MONTERICO" | monterico | 083fb553-ca57-4678-ba12-9ae1cf4b90ed |
| "LAS ACACIAS" | las acacias | 6bf480fd-4f62-41da-a4a6-353541fce16f |

Si no está en la lista, buscar el BP en el portal:
```
GET /api/business-partners/bp?query={nombre}&perPage=50
```

### 3. Mapear items de la factura a items del portal

| Nombre en factura | Item en portal | Código |
|---|---|---|
| HIERBA BUENA VR | HIERBA BUENA | PL-HIERBA-BUENA |
| ROMERO VR (sinónimo: Bombero) | ROMERO | PL-ROMERO |
| OREGANO VR | OREGANO | PL-OREGANO |
| MENTA VR | MENTA | PL-MENTA |
| RUDA VR | RUDA | PL-RUDA |
| CHAVELITAS VR (sinónimo: Chocolate) | CHAVELITAS | PL-CHAVELITAS |
| MINI JADE VR | MINI JADE | PL-MINI-JADE |
| JADE VR | JADE | PL-JADE |
| ALBACA VR / ALBAGA VR (=ALBAHACA) | ALBAHACA VERDE | PL-ALBAHACA-VERDE |
| EPISCIAS VR | EPISCIAS VR | PL-EPISCIAS-VR |
| MILLONARIA NEGRA VR | MILLONARIA ZAMIOCULCA NEGRA | PL-MILLONARIA-ZAMIOCULCA-NEGRA |
| SUCULENTAS VARIAS PEQUENAS | SUCULENTA PEQUENA | PL-SUCULENTA-PEQUENA |
| HYPOESTES VR | HYPOESTES | PL-HYPOESTES |
| AGLONEMAS VR | AGLONEMAS | PL-AGLONEMAS |
| CACTUS VARIADOS PEQUENO VR | CACTUS PEQUENO | PL-CACTUS-PEQUENO |
| CACTUS VARIADOS MEDIANO VR | CACTUS MEDIANO | PL-CACTUS-MEDIANO |
| SUCULENTAS VARIADAS PEQUEN | SUCULENTA PEQUENA | PL-SUCULENTA-PEQUENA |
| SUCULENTAS VARIADAS MEDIAN | SUCULENTAS MEDIANAS | PL-SUCULENTAS-MEDIANAS |
| SUCULENTAS VARIADAS GRAND | SUCULENTAS GRANDE | PL-SUCULENTAS-GRANDE |
| CORONITA DE CRISTO VR | CORONITA | PL-CORONITA |
| ROSAS VR | ROSA | PL-ROSA |
| MARIGOLD VR | MARIGOLD VR | PL-MARIGOLD-VR |
| COLEOS VR | COLEOS | PL-COLEOS |
| CRISANTEMOS EN POTE VR | CRISANTEMOS | PL-CRISANTEMOS |
| TORENIA VR | TORENIA | PL-TORENIA |
| NOVIO CHINO VR (sinónimo: Novias) | NOVIO CHINO | PL-NOVIO-CHINO |
| PHOTUS | POTHOS | PL-POTHOS |
| PALO DE BRAZIL | PALO DE BRASIL | PL-PALO-DE-BRASIL |
| PALO DE BRAZIL MEDIANO | PALO DE BRAZIL MEDIANO | PL-PALO-DE-BRAZIL-MEDIANO |
| PALMA ABANICO VR | PALMA ABANICO | PL-PALMA-ABANICO |
| MINI ARBUSTO VR | MINI ARBUSTO | PL-MINI-ARBUSTO |
| HIERBA DE LIMON VR | HIERBA DE LIMON | PL-HIERBA-DE-LIMON |
| LENGUA DE SUEGRA MINI VR | LENGUA DE SUEGRA MINI | PL-LENGUA-DE-SUEGRA-MINI |
| LENGUA DE SUEGRA ENANA VR | LENGUA DE SUEGRA ENANA | PL-LENGUA-DE-SUEGRA-ENANA |
| SABILA ALOE PEQUEÑA VR | SABILA ALOE PEQUENA | PL-SABILA-ALOE-PEQUENA |
| SABILA ALOE MEDIANA VR | SABILA ALOE MEDIANA | PL-SABILA-ALOE-MEDIANA |
| TOMILLO VR | TOMILLO | PL-TOMILLO |
| MOLLEJITAS VR (preferencia: Molleja) | MOLLEJA | PL-MOLLEJA |
| CINTA MALA MADRE VR | CINTA MALA MADRE | PL-CINTA-MALA-MADRE |
| AJI BOLITA DECORATIVO VR | AJI BOLITA | PL-AJI-BOLITA |
| FITONIA ROJA VR | FITONIA ROJA | PL-FITONIA-ROJA |
| CLAVELITO VR | CLAVELITO | PL-CLAVELITO |
| PETUNIN VR | PETUNIN | PL-PETUNIN |
| CELOZIA VR | CELOCIA | PL-CELOCIA |
| CIELITO AZUL VR | CIELITO AZUL | PL-CIELITO-AZUL |
| MILLONARIA ZAMIOCULCA VR (sinónimo: Zamioculca) | MILLONARIA ZAMIOCULCA | PL-MILLONARIA-ZAMIOCULCA |
| TOMILLO VR | TOMILLO | PL-TOMILLO |
| SABILA ALOE PEQUEÑA VR | SABILA ALOE PEQUENA | PL-SABILA-ALOE-PEQUENA |
| SABILA ALOE MEDIANA VR | SABILA ALOE MEDIANA | PL-SABILA-ALOE-MEDIANA |
| HELECHO VR | HELECHOS | PL-HELECHOS |

**Regla de nombres**: El portal tiene items con nombres específicos. Usar description en el SO para reflejar el nombre original de la factura. Ej: item=POTHOS pero description="PHOTUS".

**Si un item no existe en el portal**: Preguntar al usuario si crearlo. Si confirma, crearlo con payload mínimo:
```python
{
    "itemCode": "PL-NOMBRE",
    "name": "NOMBRE",
    "description": "NOMBRE",
    "itemType": "stock",
    "isStock": True,
    "isPurchasable": True,
    "isSellable": True,
    "isActive": True,
    "baseUom": "EA",
    "defaultSalesTaxCategoryId": "097722df-e70c-4380-9372-a863c67c2bca",
    "defaultPurchaseTaxCategoryId": "097722df-e70c-4380-9372-a863c67c2bca"
}
```

### 4. Manejar notas rojas en factura
- **N/C** (Nota de Crédito): Excluir esos items del SO por completo — no incluirlos en líneas ni en total. Si el subtotal impreso incluye el item N/C, el total del SO será menor que el de la factura.
- **N/C con número** ("-1 N/C", "-2 N/C", "NC-1", "NC-2"): Cancelación parcial. Reducir la cantidad, no excluir el item por completo.
  - "NC-1" o "-1 N/C" con qty 4 → incluir con quantity=3 (restar 1)
  - "NC-2" o "-2 N/C" con qty 4 → incluir con quantity=2 (restar 2)
  - Ejemplos reales: ROSAS VR "-1 N/C" 4→3, NOVIO CHINO "-1 N/C" 4→3 (Factura 746 Aguadulce), CORONITA "NC-2" 4→2 (Factura 788 Villa Lobos)
- **MC** (anotación en rojo): **SÍ es equivalente a N/C** (Nota de Crédito). MC = NC. Excluir esos items del SO — no incluirlos en líneas ni en total. Usuario corrigió explícitamente: "Mc significa nc nota de crédito esas no vienen quita lengua enana". Anteriormente se interpretó como "incluir", pero la interpretación correcta es "Nota de Crédito = excluir".
- **Tachado manual**: Preguntar al usuario si no está claro qué significa.

### 5. Presentar resumen pre-creación
Siempre mostrar tabla compacta ANTES de crear:

| Cliente | Factura | Fecha | Líneas | Total | OC |
|---|---|---|---|---|---|
| Sucursal | No.XXX | DD/MM/AAAA | N | $X.XX | Número |

Y tabla de items con: #, nombre factura → item portal, cant, P/U, total.

Preguntar: "¿Creo el SO?" Esperar confirmación.

### 6. Crear Sales Order
Endpoint: `POST /api/commerce/sales-orders`

Payload structure (ver skill ezy-portal-api para estructura completa):

**⚠️ BP sin código**: Los BPs nuevos que agrega el usuario desde el portal (Sabanitas, Condado, Penonomé) tienen `bpCode: null`. El endpoint valida bpCode como requerido. Workaround: pasar un string arbitrario como bpCode (ej. "SABANITAS", "CONDADO") junto con bpId y bpName. El API lo acepta.
```python
{
    "bpId": "{bp_id}",
    "bpCode": "{bp_code}",
    "bpName": "{bp_name}",
    "documentDate": "2026-06-08T00:00:00Z",
    "validUntil": "2026-07-08T00:00:00Z",  # 30 días después
    "priceListId": "13ce22b6-0b29-4029-be65-42e8c23cb239",
    "priceListCode": "SALE_EXTRA",
    "priceListName": "SALE_EXTRA",
    "paymentTermsId": "9025dae9-6d36-465b-a98f-733966ef8f37",
    "paymentTermsCode": "NET30",
    "paymentTermsName": "Neto 30 Días",
    "currency": "USD",
    "reference": "Factura No.{numero}",
    "lines": [
        {
            "lineNumber": 1,
            "itemId": "{item_id}",
            "itemCode": "{item_code}",
            "itemName": "{item_name}",
            "description": "{nombre_original_factura}",
            "quantity": {cantidad},
            "unitPrice": {precio_unitario},
            "warehouseId": "95c298a9-54d8-4c51-ae78-5c3b76cac657",
            "warehouseCode": "PRINCIPAL",
            "warehouseName": "ALMACEN PRINCIPAL",
            "taxCategoryId": "097722df-e70c-4380-9372-a863c67c2bca",
            "taxCategoryCode": "EXCENTO",
            "taxCategoryName": "EXCENTO",
            "uomCode": "EA"
        }
    ]
}
```

### 7. Confirmar resultado
Mostrar: Document Number, Status, Grand Total.

### 8. Múltiples facturas
- NO mezclar facturas — cada factura es su propio SO
- Procesar una a la vez, preguntar antes de pasar a la siguiente
- Si el usuario envía una nueva mientras hay una pendiente, preguntar cuál procesar primero
- El usuario a veces procesa facturas por su cuenta directamente en el portal. Si dice "no, ya la hice yo", seguir con la siguiente.

### 9. Atajo "mismo cliente"
Cuando el usuario dice **"mismo cliente"** (o "misma sucursal"), usar el mismo `bpId` y `bpCode` del SO anterior. No es necesario re-verificar el BP.

### 10. Precios de factura vs portal
Usar SIEMPRE el precio unitario que aparece en la factura como `unitPrice`, incluso si difiere del precio del portal. El portal no recalcula — usamos el precio de la factura original. Excepción: si el precio de factura está en blanco/ilegible, usar el precio del portal.

## Crear un nuevo BP (Business Partner)
Si el BP de la sucursal no existe en el portal, crearlo:

```python
POST /api/business-partners/bp
{
    "code": "CL-XXXX",  # <-- CAMPO "code", NO "bpCode"
    "name": "Super Extra {sucursal}",
    "bpType": "customer",
    "roles": ["customer"]
}
```

**Pitfall**: El campo se llama `code` no `bpCode`. Usar `bpCode` da error "Business partner code is required". Usar `Idempotency-Key` header con UUID para evitar duplicados.

Luego usar el `bpCode` y `bpName` del BP creado en el SO, y pasar `bpCode` como el valor de `code` del payload de creación.

## IDs fijos (vivero tenant, Jul 2026)
- SALE_EXTRA: 13ce22b6-0b29-4029-be65-42e8c23cb239
- Warehouse PRINCIPAL: 95c298a9-54d8-4c51-ae78-5c3b76cac657
- Tax EXCENTO: 097722df-e70c-4380-9372-a863c67c2bca
- PaymentTerms NET30: 9025dae9-6d36-465b-a98f-733966ef8f37

## TIERRA-NEGRA / ABONO-ORGANICO / CASCARILLA-DE-ARROZ (verified Jul 10 2026)

These three soil items exist from initial setup and have these fixed IDs:
| Code | ID |
|------|-----|
| TIERRA-NEGRA | fa5966d6-e11e-402b-bc0a-eba245eab0a2 |
| ABONO-ORGANICO | 96acf659-aae3-471d-b219-e16b35a2f44a |
| CASCARILLA-DE-ARROZ | 7c01f7e4-3fb4-4932-a835-5872f5caaa69 |

When a facturation omits timestamp/expiration checks: SO has 30-day validUntil and no N/C clauses.

For Vivero Rose tierra sales (factura fotos like #766, #759, #771, #750): use these prices:
- TIERRA NEGRA: $0.95
- ABONO ORGÁNICO: $0.55
- CASCARILLA DE ARROZ: $0.55

These come from sales order **factura data** (the invovation price, not from PO).
If user wants these in the wastee Inventory cost columns, do NOT put them — they are
VENTA not COMPRA. Column should be empty for tierras items, or new column COST_ROSE.

## Pre-created SUPER EXTRA branches (verified Aug 2026)

When user says a branch name that's in the table at the start of this skill, just
use the bpId/bpCode directly — no search needed.

**Branch ID drift warning**: bpIds may change between sessions (UI-driven renames).
Always re-fetch via `GET /api/business-partners/bp?query=<name>` if a known ID fails.