#!/usr/bin/env python3
"""
Bulk create items from CSV for EZY Portal (vivero tenant)
Handles: itemCode normalization, duplicate detection, tagging, price list reference, rate limiting
"""

import csv
import re
import json
import time
import hashlib
import subprocess
import sys
from pathlib import Path

# ============== CONFIG ==============
API_KEY = "ten_iiXLA5AvHe-qjYgbrEjbdaWATDVjsxKxLmq8bSETi3Q"
BASE_URL = "https://vivero.ezyts.com/api/items/items"

TENANT_DEFAULTS = {
    "itemGroupId": "b38e9a2d-4951-4d40-9fa3-1357ef0dc631",  # PLANTS
    "itemClassId": "b65da4ee-1f20-45f7-b329-d2b884c7c10d",  # LIVE_PLANT
    "baseUom": "EA",
    "itemType": "stock",
    "isStock": True,
    "isPurchasable": True,
    "isSellable": True,
    "isActive": True,
    "currencyCode": "PAB",
}

CATEGORY_MAP = {
    "870c230c-8db6-4017-8cbf-a850d187a160": ("flowers", ["flower","petunin","clavel","coronet","cielito","crisontemo","poinsettia","novio","ixora","rosa","rosita","jazmin","anthurio","chavelita","torenia","celosia"]),
    "bfc5b004-b8f0-4457-8125-6286974d3d31": ("foliage", ["aglonaema","fitonia","molleja","aralia","diefenbachia","crot","cobrava","philodendron","singonio","monstera","pothos","photos","philomendro","pata de elefante","silver skill","bordeador","hypoestes","calathea","chaflera","china doll","chinita","cinta mala","lengua de suegra","lengua","tradescantia","purple lady","mini ericka","mini arbusto","oreja de elefante","alocasia","anthuri","sangrillo","dracena","dracaena","croto","mamy"]),
    "15f31814-9afc-4779-a4dd-28f9aa16addd": ("herbs", ["hierba","romero","menta","ruda","albahaca","oregano","tomillo","apio","culantro","hierba buena","hierba de limon"]),
    "33a9125f-de55-4b56-a94d-e85b8012545e": ("succulents", ["jade","aloe","sabila","zamioculca","peperonia","echeveria","sedum","crassula","suculentas","cactus"]),
    "ad132e26-1e28-4404-a305-ee6b5ca2b8e9": ("palms_trees", ["palma","bambu","pino","palo de brasil","bismarckia","madagascar","phoenix","roebelenii","real enana","majestica","cipre","thuja","araucaria","conifer","lorito","yuca","guayacan","tecoma","papo","copey","bijao","pino de oro","pino hindu","pino bonsai","pino rastrero","agave","texas nevado"]),
    "4196bac4-daae-4280-99a8-b098e96c68a4": ("foliage", ["helecho","helechos"]),
}

def normalize_item_code(name: str) -> str:
    """Convert plant name to PL-ITEM-CODE format"""
    code = name.upper()
    code = re.sub(r'[^\w\s-]', '', code)  # Remove special chars
    code = re.sub(r'\s+', '-', code.strip())  # Spaces to hyphens
    code = re.sub(r'-+', '-', code)  # Collapse multiple hyphens
    return f"PL-{code}"

def categorize(name: str, tags: list) -> str:
    """Return category ID based on name/tags"""
    text = (name + " " + " ".join(tags)).lower()
    for cat_id, (tag, keywords) in CATEGORY_MAP.items():
        if tag in [t.lower() for t in tags]:
            return cat_id
        for kw in keywords:
            if kw.lower() in text:
                return cat_id
    return None

def enrich_tags(name: str, description: str, price_list: str, base_tags: list) -> list:
    """Add standard tags based on content"""
    tags = set(base_tags)
    tags.add("vivero_import")
    
    if price_list == "COST_SARA":
        tags.add("cost_sara")
    
    desc_upper = (description or "").upper()
    name_upper = (name or "").upper()
    
    if "POCAS UNIDADES" in desc_upper:
        tags.add("low_stock")
    if "EN BOTONES" in desc_upper:
        tags.add("en_botones")
    if "PEQUEÑO" in desc_upper:
        tags.add("pequeno")
    if "NO MUY GRANDE" in desc_upper:
        tags.add("no_muy_grande")
    if "PROMOCION" in name_upper:
        tags.add("promocion")
    
    return list(tags)

def build_item(row: dict, price_list: str = "COST_SARA") -> dict:
    """Build item payload from CSV row"""
    name = row.get("VARIEDAD", "").strip()
    obs = row.get("OBSERVACIONES", "").strip()
    otros = row.get("OTROS", "").strip()
    precio_str = row.get("PRECIO Costo", "").strip()
    
    # Extract price
    price_match = re.search(r'B\/\.\s*([\d.]+)', precio_str)
    price = float(price_match.group(1)) if price_match else 0.0
    
    # Generate itemCode
    item_code = normalize_item_code(name)
    
    # Build description
    desc_parts = [p for p in [obs, otros] if p]
    description = " | ".join(desc_parts) if desc_parts else name
    
    # Tags
    tags = enrich_tags(name, description, price_list, [])
    
    # Category
    category_id = categorize(name, tags)
    if category_id:
        cat_tag = CATEGORY_MAP[category_id][0]
        if cat_tag not in tags:
            tags.append(cat_tag)
    
    # Payload
    payload = {
        **TENANT_DEFAULTS,
        "itemCode": item_code,
        "name": name,
        "description": description,
        "priceListCode": price_list,
        "tags": tags,
        "prices": [{
            "priceListCode": price_list,
            "uom": "EA",
            "price": price,
            "currencyCode": "PAB"
        }]
    }
    
    if category_id:
        payload["itemCategory"] = category_id
    
    return payload

def api_call(method: str, endpoint: str, payload: dict = None) -> tuple:
    """Make API call via curl"""
    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        "-H", f"X-Api-Key: {API_KEY}",
        "-H", "Accept: application/json",
        "-X", method,
        f"{BASE_URL}{endpoint}"
    ]
    if payload:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(payload)])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    output = result.stdout.strip()
    lines = output.split('\n')
    http_code = lines[-1] if lines else "000"
    body = '\n'.join(lines[:-1]) if len(lines) > 1 else output
    
    return http_code, body

def check_existing(item_code: str) -> dict:
    """Check if item already exists"""
    code, body = api_call("GET", f"/by-code/{item_code}?expand=prices")
    if code == "200":
        return json.loads(body)
    return None

def create_item(payload: dict) -> tuple:
    """Create new item"""
    return api_call("POST", "", payload)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bulk-create-items.py <csv_file> [price_list]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    price_list = sys.argv[2] if len(sys.argv) > 2 else "COST_SARA"
    
    # Load CSV
    items = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(build_item(row, price_list))
    
    print(f"Loaded {len(items)} items from CSV")
    
    # Check for duplicates
    to skip/update
    to_create = []
    for item in items:
        existing = check_existing(item["itemCode"])
        if existing:
            print(f"⚠️  EXISTS: {item['itemCode']} - {item['name']} (ID: {existing['id']})")
            # Could add update logic here
        else:
            to_create.append(item)
    
    print(f"Creating {len(to_create)} new items...")
    
    # Create items
    success = 0
    failed = 0
    for i, item in enumerate(to_create, 1):
        code, body = create_item(item)
        if code in ["200", "201"]:
            print(f"[{i}/{len(to_create)}] ✅ {item['itemCode']} - {item['name']}")
            success += 1
        else:
            print(f"[{i}/{len(to_create)}] ❌ {item['itemCode']} - HTTP {code}: {body[:200]}")
            failed += 1
        time.sleep(0.2)  # Rate limit
    
    print(f"\n=== SUMMARY ===")
    print(f"Created: {success}")
    print(f"Failed:  {failed}")

if __name__ == "__main__":
    main()