#!/usr/bin/env python3
"""
Extract images from Excel (.xlsx) with embedded images for EZY Portal import
Maps images to plant names from sharedStrings and saves with portal-compatible names
"""

import zipfile
import xml.etree.ElementTree as ET
import os
import shutil
import hashlib
import re
from pathlib import Path

def extract_excel_images(xlsx_path: str, output_dir: str, tenant_prefix: str = "PL"):
    """
    Extract images from Excel and map to plant names.
    
    Args:
        xlsx_path: Path to .xlsx file
        output_dir: Directory to save mapped images
        tenant_prefix: Prefix for item codes (default: "PL")
    
    Returns:
        dict: {item_code: storage_key} mapping
    """
    
    extract_dir = Path(output_dir) / "extract"
    mapped_dir = Path(output_dir) / "mapped"
    extract_dir.mkdir(parents=True, exist_ok=True)
    mapped_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Unzip
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        z.extractall(extract_dir)
    
    # 2. Parse sharedStrings to get plant names (column A)
    shared_strings = []
    ss_path = extract_dir / "xl" / "sharedStrings.xml"
    if ss_path.exists():
        tree = ET.parse(ss_path)
        root = tree.getroot()
        ns = {'ss': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for si in root.findall('.//ss:si', ns):
            # Get text from <t> or <r><t>
            texts = []
            for t in si.findall('.//ss:t', ns):
                if t.text:
                    texts.append(t.text)
            shared_strings.append(''.join(texts))
    
    # 3. Parse richData relationships to get image order
    # richValueRel.xml.rels maps rId -> ../media/image{N}.jpeg
    rels_path = extract_dir / "xl" / "richData" / "_rels" / "richValueRel.xml.rels"
    image_map = {}  # rId -> image filename
    if rels_path.exists():
        tree = ET.parse(rels_path)
        root = tree.getroot()
        ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
        for rel in root.findall('.//r:Relationship', ns):
            r_id = rel.get('{http://schemas.openxmlformats.org/package/2006/relationships}id')
            target = rel.get('Target')
            if target and target.startswith('../media/'):
                image_map[r_id] = Path(target).name
    
    # 4. Parse rdrichvalue.xml to get count (usually matches row count)
    rv_path = extract_dir / "xl" / "richData" / "rdrichvalue.xml"
    image_count = 0
    if rv_path.exists():
        tree = ET.parse(rv_path)
        root = tree.getroot()
        ns = {'rv': 'http://schemas.microsoft.com/office/spreadsheetml/2017/richdata'}
        image_count = int(root.get('count', 0))
    
    # 5. Build plant name list from sharedStrings
    # For vivero format: row 0 = header "VARIEDAD", rows 1-52 = plant names
    plant_names = []
    for s in shared_strings:
        if s and s != "VARIEDAD" and not s.startswith("#VALUE"):
            plant_names.append(s)
    
    print(f"Found {len(plant_names)} plant names, {image_count} images")
    
    # 6. Match images to plant names (1:1 by order)
    media_dir = extract_dir / "xl" / "media"
    results = {}
    
    for i, plant_name in enumerate(plant_names):
        img_num = i + 1
        src_image = media_dir / f"image{img_num}.jpeg"
        
        if not src_image.exists():
            print(f"  ⚠️  Missing image{img_num}.jpeg for {plant_name}")
            continue
        
        # Generate itemCode
        item_code = f"{tenant_prefix}-{normalize_name(plant_name)}"
        
        # Generate portal storage key
        timestamp = "20260618132701"  # Use current or fixed
        hash_part = hashlib.md5(item_code.encode()).hexdigest()[:8]
        name_part = item_code.replace("PL-", "").replace("-", "_")
        storage_key = f"images/{name_part}_{timestamp}_{hash_part}.jpeg"
        
        # Copy to mapped dir with clean name
        safe_name = re.sub(r'[^\w\s-]', '', plant_name)
        safe_name = re.sub(r'\s+', '_', safe_name.strip())
        safe_name = safe_name[:100]
        dst = mapped_dir / f"{i+1:02d}_{safe_name}.jpeg"
        shutil.copy2(src_image, dst)
        
        results[item_code] = storage_key
        print(f"  ✅ {item_code} <- image{img_num}.jpeg -> {storage_key}")
    
    print(f"\nExtracted {len(results)} images to {mapped_dir}")
    return results

def normalize_name(name: str) -> str:
    """Normalize plant name to itemCode format"""
    code = name.upper()
    code = re.sub(r'[^\w\s-]', '', code)
    code = re.sub(r'\s+', '-', code.strip())
    code = re.sub(r'-+', '-', code)
    return code

def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 extract_excel_images.py <xlsx_file> <output_dir> [tenant_prefix]")
        sys.exit(1)
    
    xlsx_path = sys.argv[1]
    output_dir = sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else "PL"
    
    mapping = extract_excel_images(xlsx_path, output_dir, prefix)
    
    # Save mapping JSON
    import json
    mapping_file = Path(output_dir) / "image_mapping.json"
    with open(mapping_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"Mapping saved to {mapping_file}")

if __name__ == "__main__":
    main()