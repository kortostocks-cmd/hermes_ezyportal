# Excel Image Extraction for EZY Portal Import

## Problem
Excel files (.xlsx) with embedded images sent via WhatsApp/email need images extracted and mapped to items for bulk import.

## Solution: Unzip + XML Parsing

### Structure
```
.xlsx (ZIP archive)
├── xl/
│   ├── media/
│   │   ├── image1.jpeg, image2.jpeg, ...  # Raw images in order
│   ├── worksheets/
│   │   ├── sheet1.xml                     # Cell data (sharedStrings refs)
│   ├── sharedStrings.xml                  # All text values
│   ├── richData/
│   │   ├── rdrichvalue.xml                # Rich value entries (count = images)
│   │   ├── richValueRel.xml               # Relationship IDs per image
│   │   ├── _rels/richValueRel.xml.rels    # rId -> ../media/imageN.jpeg mapping
```

### Extraction Steps

```bash
# 1. Unzip
unzip -o "file.xlsx" -d /tmp/extract

# 2. Images are in xl/media/image{N}.jpeg (1-indexed, matches row order typically)
# 3. Map using sharedStrings + richData relationship
```

### Python Mapping Logic

```python
import openpyxl
import os
import shutil

# The sharedStrings.xml contains all cell text in order
# richData/rdrichvalue.xml has <rv> entries with <v> indices
# richValueRel.xml.rels maps rId -> ../media/image{N}.jpeg

# For vivero tenant: 52 plants in Excel, 52 images in xl/media/
# Row 2 (index 1) = image1.jpeg, Row 3 = image2.jpeg, etc.
# Column A = VARIEDAD name

# Matching strategy:
plants = [...]  # 52 plant names from sharedStrings (indices 1-52)
for i, plant_name in enumerate(plants, 1):
    src = f"/tmp/extract/xl/media/image{i}.jpeg"
    # Clean filename for portal
    safe_name = plant_name.replace('/', '-').replace('"', '').replace("'", "").replace('¨', '')
    dst = f"{item_code}_{timestamp}_{hash}.jpeg"
```

### Key Findings (vivero tenant)

| Excel Row | ItemCode | Image File |
|-----------|----------|------------|
| 2 | PL-AGAVE-EN-POTE-5 | image1.jpeg |
| 3 | PL-AJUGA-EN-BOLSA | image2.jpeg |
| ... | ... | ... |
| 53 | PL-YUCA-EN-POTE-129 | image52.jpeg |

**Note**: 3 extra CIPRE short names (CIPRE AZUL, CIPRE BOLA, CIPRE DORADO) at end of sharedStrings but no corresponding images (only 52 images for 55 strings).

### Portal Storage Key Format
```
images/{ITEMCODE_WITHOUT_PL_UNDERSCORES}_{YYYYMMDDHHMMSS}_{MD5_HASH_8}.jpeg
Example: images/AGAVE_EN_POTE_5_20260618132701_76b78b8a.jpeg
```

### Batch Upload
Since no API upload endpoint exists:
1. Upload extracted images to storage (S3/Azure Blob) maintaining `images/` prefix
2. PATCH items with `primaryImageStorageKey` pointing to uploaded objects
3. Or: manual drag-drop in Portal UI per item