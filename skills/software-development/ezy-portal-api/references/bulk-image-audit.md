# Bulk Image Audit & Sync Workflow (vivero tenant)

## Problem

Bulk item creation from Excel/CSV creates items but **does not upload embedded images**. Portal UI shows: *"Item was saved but some files could not be processed."*

Images must be handled separately:
1. Extract from Excel → local files
2. Upload to storage (Portal UI or direct storage API)
3. PATCH items with `primaryImageStorageKey`

## Audit Workflow (2026-06-19)

### 1. Inventory Local Files

```bash
# Folder with images
~/Downloads/plantas_para_subir_portal/   # 52 original photos
~/Downloads/plantas_TODAS_para_portal/   # Copy for manual upload
```

### 2. Fetch Portal Items with Images

```bash
curl -H "X-Api-Key: ten_..." \
  "https://vivero.ezyts.com/api/items/items?expand=prices&page=1&perPage=200"
```

Extract: `itemCode`, `primaryImageStorageKey`, `imageCount`

### 3. Match Local Files to Items

**Naming convention:**
- Portal: `images/{NAME}_{timestamp}_{hash}.ext`
- Local: `{NAME}_{timestamp}_{hash}.ext` (same name, no `images/` prefix)

**Matching algorithm:**
```python
def itemcode_to_prefix(itemcode):
    # PL-AGAVE-EN-POTE-5 → AGAVE_EN_POTE_5
    return itemcode[3:].replace('-', '_')

# Match: local_name.startswith(prefix) OR prefix in local_name
```

### 4. Categorize Results (2026-06-19 actual)

| Category | Count | Action |
|----------|-------|--------|
| Match, portal has same image | ~28 | Nothing |
| Match, portal has AI version | 3 | Decide which to keep |
| Match, portal has NO image | 47 | **Upload via Portal UI** |
| Local file, no portal match | 0 | N/A |
| Portal item, no local file | ~44 | May need AI generation |

### 5. Fix Missing Images (47 items)

**Manual (recommended for one-time):**
1. Open item in Portal UI
2. Drag & drop from `plantas_TODAS_para_portal/`
3. Portal uploads to storage, updates `primaryImageStorageKey`

**Automated (if storage credentials available):**
1. Upload files to S3/Azure/GCS bucket
2. PATCH each item:
```json
PATCH /api/items/items/{id}
{ "primaryImageStorageKey": "images/AGAVE_EN_POTE_5_20260618132701_76b78b8a.jpeg" }
```

### 6. Storage Key Patterns

| Source | Pattern | Example |
|--------|---------|---------|
| Original photo | `images/{NAME}_{YYYYMMDDHHMMSS}_{hash}.ext` | `images/AGAVE_EN_POTE_5_20260618132701_76b78b8a.jpeg` |
| AI-generated | `images/{NAME}_{YYYYMMDD}_AI_{hash}.ext` | `images/PALMA_CUBANA_20260618_AI_9066f6c6.jpeg` |

**Critical:** AI images are in external storage (S3/Azure/GCS). `https://vivero.ezyts.com/images/...` returns 404. Only Portal UI or direct storage API can access them.

## Script: match_images.py

```python
#!/usr/bin/env python3
"""Match local image files to portal items, identify missing/mismatched."""

import json, os, subprocess

# 1. Load portal items
result = subprocess.run([
    "curl", "-s", "-H", "X-Api-Key: ten_...",
    "https://vivero.ezyts.com/api/items/items?expand=prices&perPage=200"
], capture_output=True, text=True)
data = json.loads(result.stdout)
items = {i['itemCode']: i for i in data['data']}

# 2. Load local files
folder = "/Users/abrahamkortovich/Downloads/plantas_para_subir_portal"
local = {f.rsplit('.',1)[0]: f for f in os.listdir(folder) if f.endswith(('.jpeg','.jpg','.png','.webp'))}

# 3. Match
def prefix(code):
    return code[3:].replace('-', '_') if code.startswith('PL-') else code.replace('-', '_')

matches, missing, mismatched = [], [], []

for code, item in items.items():
    p = prefix(code)
    found = [k for k in local if k.startswith(p) or p in k]
    if found:
        local_name = found[0]
        portal_key = item.get('primaryImageStorageKey', '')
        expected = f"images/{local_name}.{local[local_name].split('.')[-1]}"
        if not portal_key or item.get('imageCount', 0) == 0:
            missing.append({'code': code, 'local': local_name, 'expected': expected})
        elif portal_key != expected:
            mismatched.append({'code': code, 'local': local_name, 'portal': portal_key, 'expected': expected})
        else:
            matches.append(code)
    else:
        print(f"NO LOCAL FILE: {code}")

print(f"Matches: {len(matches)}")
print(f"Missing in portal: {len(missing)}")
print(f"Mismatched: {len(mismatched)}")
for m in missing: print(f"  UPLOAD: {m['code']} <- {m['local']}")
for m in mismatched: print(f"  CONFLICT: {m['code']} portal={m['portal']} local={m['expected']}")
```

## Related Files

- `scripts/extract_excel_images.py` — Extract embedded images from Excel
- `references/ai-image-generation.md` — Generate placeholder images via FAL
- `references/real-world-examples.md` — Full audit results (2026-06-19)