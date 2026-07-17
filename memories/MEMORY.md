EZY Portal API: /api/categories and /api/categories/mappings require Bearer Token (JWT), not X-Api-Key (ten_...). Returns 404/401 with API Key. Image upload NOT available via API - only via Portal UI drag&drop or direct storage API (S3/Azure/GCS). API only accepts primaryImageStorageKey reference. Clearing primaryImageStorageKey via PATCH removes image association but files remain in external storage.
§
Lumos=stock, alohomora=backup Airtable. Zamioculca=MILLONARIA, Cactus mediano=PL-CACTUS, Chocolate=CHAVELITAS, Bombero=ROMERO, Novias=NovioChino. Compact terminal. Sinónimos dict en skill ezy-portal-api.
§
Discord Bot Token: (redacted - stored in env) (ezy bot) - Updated Jul 2026
§
PHOTUS unit_cost=0.80 (abril). Crear SOs con item MILLONARIA ZAMIOCULCA, description=nombre factura.
§
SALE_EXTRA=13ce22b6 única lista venta. SUP/PUBLIC inactivas. INVENTARIO col order Jul 16: D=MIJARDIN, G=A&G (skill dice lo correcto, memoria vieja al revés).
§
Facturas: no mezclar, procesar 1 por vez. Si No.Factura cortado, usar "Factura {sucursal} {fecha}" como reference.
§
BP sin bpCode: Chanis,Chitre,Sabanitas,VillaLucre,BrisasGolf,SanIsidro,XMCapira,SantiagoTerminal(CL-0021),LaSiestas(CL-0202). Tierras IDs: TIERRA-NEGRA=fa5966d6, ABONO-ORGANICO=96acf659, CASCARILLA-DE-ARROZ=7c01f7e4. Item groups: SUCULENTAS, CACTUS, ARBOLES, MEDICINALES, ORNAMENTALES, TIERRA(06), TIERRAS. MCP endpoint /mcp req mcp_ token. lumos: tierras al final INVENTARIO.
§
API key ten_BvfgJJOvXHbkjuQKMpscKmFo92HMwl3-2UNsbVWYq4g funciona items+POs+SOs (Jul 13 2026 activo). Key anteriores expiraron (ten_Zk271..., ten_YdKacb..., ten_PRQ2Xey..., ten_6lRpIW...).
§
Mes venta: TOTAL amarillo + NOTA_CREDITO rosa = exportar CSV a ~/Documents/vivero_ventas/. Jun 2026: 55 SOs, TOTAL=$6,856.30, NC=$25.44 (6 SOs).
§
Regla: si stock>0 debe tener costo. SALE_PUBLIC→COST_SARACELY, COST_JARDIN→COST_MIJARDIN. COST_IAN col J (jul 2026, Viveros ian). Si user dice "no compro mas de X"→quitar TODOS los costos de ese supplier. SUCULENTAS GRANDE: solo MIJARDIN $2.25 + IAN $0.80 (SARACELY $3.25 eliminado jul 2026). CAJAS POTE 120/180 cross-matchear.