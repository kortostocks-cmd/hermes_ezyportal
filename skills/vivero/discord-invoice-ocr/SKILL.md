---
name: discord-invoice-ocr
description: "Autoprocesa imágenes de facturas enviadas al bot de Discord: descarga, OCR (Swift+Vision) y creación de SOs en EZY Portal."
version: 1.0.0
author: Agent
---

# Discord Invoice OCR

Usa este skill cuando alguien envíe una imagen de factura en Discord.

El bot ya tiene instrucciones permanentes en memoria. Este skill es respaldo.

## Scripts instalados (profile ezy_portal_expert)
- `~/scripts/ocr_swift.swift` — Core OCR con Apple Vision Framework
- `~/scripts/ocr_swift.sh` — OCR desde ruta local
- `~/scripts/download_ocr.sh` — Download URL + OCR + limpia

## Flujo en Discord
1. Usuario envía imagen con @HERMES_EZY
2. El mensaje tiene attachment URLs (chat.de Discordapp.com/...)
3. Terminal: `~/scripts/download_ocr.sh <URL>`
4. Procesar texto (Entrada de Mercancía, items, precios)
5. Mostrar resumen compacto al usuario, esperar confirmación ("dle")
6. Crear SO en draft via API

Records no requieren API keys — Vision nativo de macOS.