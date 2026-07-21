# Receipt Reading with Vision Correction (Jul 2026)

## When to Use
RECIBOLM "Entrada de Mercancía" documents from Super Xtra are often photographed rotated due to landscape format. The initial user-provided image description/OCR may contain errors in quantities and prices.

## Workflow

1. **Identify rotation**: Check if the image is rotated 90 degrees clockwise (portrait photo of landscape document).

2. **Rotate with PIL**:
```python
from PIL import Image
img = Image.open("/path/to/original.jpg")
rotated = img.rotate(90, expand=True)
rotated.save("/tmp/factura_NNN_rotated.jpg", quality=95)
```

3. **Extract text from image** — use ONE of:

   **Method A (preferred): vision_analyze** — when available in the session:
   ```python
   vision_analyze(image_url="/tmp/factura_NNN_rotated.jpg",
       question="Lee CLARAMENTE los valores de esta factura...")
   ```

   **Method B (Swift/Vision fallback)**: When vision_analyze is unavailable (CLI-only session) and tesseract not installed, use macOS built-in Vision framework:
   ```bash
   swift /path/to/skills/software-development/ezy-portal-api/scripts/ocr_invoice.swift /tmp/factura.jpg 2>&1
   ```
   Uses `VNRecognizeTextRequest` with `.accurate` level. Output is raw OCR text line by line.
   **Pitfall**: Raw OCR garbles names — "SAMIAOCULA"=ZAMIOCULCA, "AMAOCUILA"=AJI BOLITA, "EQUENO"=PEQUENO, "MEGRA"=NEGRA, "SAMIAOCULA"=ZAMIOCULCA. Always map through the correction table.

4. **Compare quantities** against the invoice total to validate:
   - Line-level: `qty x unitPrice == subtotal` should match
   - Document total: sum of all subtotals equals IMPORTE TOTAL

5. **Map corrected item names** to portal codes using the name mapping table in the skill.

## Verified Corrections Made (Jul 9 2026)
- Factura 782 (XM Capira): OCR misread 9 lines; vision corrected quantities, prices, and even a product name (CLAVELITO AZUL → CIELITO AZUL)
- Factura 779 (Chitré): 23 lines all verified correct via vision

## Pitfalls
- The `vision_analyze` tool may fail with `--enable-multimodal` errors on the first attempt — retry on the rotated copy
- Some item names are OCR garbage (e.g. "SAMIAOCULA" = ZAMIOCULCA, "AMAOCUILA" = AJI BOLITA, "MEGRA" = NEGRA) — use the mapping table, not the raw OCR
- Always trust the visual output over the initial description when they conflict