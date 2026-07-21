EZY Portal API: /api/categories and /api/categories/mappings require Bearer Token (JWT), not X-Api-Key (ten_...). Returns 404/401 with API Key. Image upload NOT available via API - only via Portal UI drag&drop or direct storage API (S3/Azure/GCS). API only accepts primaryImageStorageKey reference. Clearing primaryImageStorageKey via PATCH removes image association but files remain in external storage.
§
Lumos=stock, alohomora=backup Airtable. Zamioculca=MILLONARIA, Cactus mediano=PL-CACTUS, Chocolate=CHAVELITAS, Bombero=ROMERO, Novias=NovioChino. Compact terminal. Sinónimos dict en skill ezy-portal-api.
§
Discord Bot Token: (redacted - stored in env) (ezy bot) - Updated Jul 2026
§
SALE_EXTRA=13ce22b6 única lista precio. INVENTARIO cols Jul: D=MIJARDIN, G=A&G.
§
Facturas: no mezclar, procesar 1 por vez. Si No.Factura cortado, usar "Factura {sucursal} {fecha}" como reference.
§
API key ten_BvfgJJOvXHbkjuQKMpscKmFo92HMwl3-2UNsbVWYq4g (Jul 2026 activo). SO payload: BPID/BPCode/BPName, paymentTermsId=9025dae9, priceListCode, per-line: itemId/code/name, qty, unitPrice, warehouse+taxCategory info. Tax: EXCENTO (tierras), ITMBS 7% (plants).
§
Mes venta: TOTAL amarillo + NOTA_CREDITO rosa = exportar CSV a ~/Documents/vivero_ventas/. Jun 2026: 55 SOs, TOTAL=$6,856.30, NC=$25.44 (6 SOs).
§
Regla: si stock>0 debe tener costo. SALE_PUBLIC→COST_SARACELY, COST_JARDIN→COST_MIJARDIN. COST_IAN col J (jul 2026, Viveros ian). Si user dice "no compro mas de X"→quitar TODOS los costos de ese supplier. SUCULENTAS GRANDE: solo MIJARDIN $2.25 + IAN $0.80 (SARACELY $3.25 eliminado jul 2026). CAJAS POTE 120/180 cross-matchear.
§
Discord bot OCR: scripts Swift+Vision en ~/scripts/ocr_*.swift y skill discord-invoice-ocr creado para autoprocesar facturas desde imágenes en Discord.
§
Discord bot OCR: cuando envíen imagen factura en Discord, descargar con curl y extraer texto con ~/scripts/download_ocr.sh <url_attachment>. Skill: discord-invoice-ocr. Procesar datos y crear SOs en draft.