# AI Image Generation for Missing Product Photos

## Problem
Some items in the catalog lack product photos. The Excel import had 52 images for 55 plants (3 CIPRE short names had no images). 34 additional items from the original import had no images at all.

## Solution: Generate via FAL (AI Image Generation)

Using the `image_generate` tool (FAL.ai backend via Nous subscription) to create professional nursery-style product photos.

## Generation Process

### 1. Prepare Prompts
For each missing item, create a specific prompt describing the plant in a nursery context:

```python
prompts = [
    ("PL-CIPRE-AZUL-EN-POTE-160", 
     "Professional nursery photo of Blue Cypress in large 160mm pot, silvery-blue foliage, conical shape, clean white background"),
    ("PL-PINO-BONSAI",
     "Professional nursery photo of Pine Bonsai, miniature trained pine with needles, artistic form in shallow bonsai pot, clean white background"),
    # ... etc
]
```

### 2. Generate via image_generate tool
```python
# Each call returns a FAL media URL
result = image_generate(
    prompt="Professional nursery photo of ...",
    aspect_ratio="square"  # Square works best for product catalogs
)
# Returns: {"success": true, "image": "https://v3b.fal.media/files/b/..."}
```

### 3. Download & Upload to Storage
Since EZY Portal API doesn't have image upload:
1. Download generated images from FAL URLs
2. Upload to portal storage (S3/Azure Blob) maintaining `images/` prefix
3. PATCH items with `primaryImageStorageKey`

### 4. Portal Storage Key Format
```
images/{ITEMCODE_WITHOUT_PL_UNDERSCORES}_{YYYYMMDD}_AI_{MD5_HASH_8}.jpeg
Example: images/CIPRE_AZUL_EN_POTE_160_20260618_AI_47e81445.jpeg
```

## Prompt Engineering Tips

### Do:
- "Professional nursery photo of [Plant Name] in [pot size], [key visual features], clean white background, well-lit commercial photography"
- Specify pot size when known (e.g., "in 160mm pot", "in pot 5")
- Include distinguishing features: "silvery-blue foliage", "golden-yellow needles", "bright red crownshaft"

### Don't:
- Use artistic/abstract styles
- Include hands, people, or lifestyle context
- Use colored backgrounds (stick to clean white)

## Batch Generation Script

```python
#!/usr/bin/env python3
"""Generate AI images for missing plant photos"""
import json
import time
from hermes_tools import image_generate

missing_items = [
    ("PL-CIPRE-AZ-AZUL-160", "Blue Cypress in 160mm pot, silvery-blue conical foliage"),
    # ... 34 items total
]

results = {}
for code, desc in missing_items:
    prompt = f"Professional nursery photo of {desc}, clean white background, commercial plant photography"
    result = image_generate(prompt=prompt, aspect_ratio="square")
    if result.get("success"):
        results[code] = result["image"]
        print(f"✅ {code}")
    else:
        print(f"❌ {code}: {result}")
    time.sleep(1)  # Rate limit

with open("generated_images.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Results (vivero tenant, 2026-06-18)
- **Generated**: 34 images for previously missing items
- **Success rate**: 100% (all prompts generated valid images)
- **Cost**: Included in Nous subscription (FAL backend)
- **Time**: ~1 minute for 34 images (sequential with 1s delay)

## Integration with Bulk Update
After generation, items are PATCHed with the new `primaryImageStorageKey`:

```python
payload = {
    "itemCode": code,
    "name": name,
    "version": version,  # Critical for optimistic locking
    "primaryImageStorageKey": f"images/{name_part}_{date}_AI_{hash_part}.jpeg",
    # ... all other required fields
}
PATCH /api/items/items/{id}
```

## Limitations
- AI images are placeholders — not real photos of actual inventory
- Should be replaced with real photos when available
- FAL URLs are temporary; must download and re-host on portal storage
- Aspect ratio: square (1:1) works best for catalog thumbnails