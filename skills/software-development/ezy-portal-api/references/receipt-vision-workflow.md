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

3. **Use vision_analyze on rotated copy**:
```python
vision_analyze(image_url="/tmp/factura_NNN_rotated.jpg",
    question="Lee CLARAMENTE los valores de esta factura...")
```

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