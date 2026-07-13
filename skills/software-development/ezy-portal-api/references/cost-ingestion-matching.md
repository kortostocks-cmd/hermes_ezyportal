# Cost Ingestion from Supplier Price Lists — Matching Pitfalls

## Goal
When the user provides a physical price list (photo/scan) from a supplier, extract item names and prices, match them to portal items, and write to the correct COST_ column.

## Matching Algorithm

### Step 1: Extract Base Name
Strip pot sizes, PROMOCION, container types, and measurement suffixes:

```python
def extract_base(name):
    name = name.upper()
    name = re.sub(r"\s*(EN\s+(POTE|BOLSA|MACETA|POT|GEOTEXTIL|PDB|VCG).*|PROMOCION.*)", "", name).strip()
    name = re.sub(r'\s*".*', "", name).strip()
    name = re.sub(r"\s*\d+"'"', "", name).strip()
    name = re.sub(r"\s*\[.*\]", "", name).strip()
    return nfkd(name)
```

### Step 2: Normalize (NFKD)
```python
def nfkd(s):
    n = unicodedata.normalize("NFD", s.upper())
    n = re.sub(r"[\u0300-\u036f]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n
```

### Step 3: Match
For each extracted base name, find portal items by checking:
- `base in portal_name or portal_name in base` (loose match)
- ⚠️ This has false substring matches (see below)

## False Substring Match Pitfall (CRITICAL)

Simple substring matching produces false positives:

| Price List Item | Portal Match? | Why |
|---|---|---|
| BAMBU ($90.00) | BAMBU ENTRENZAS ✅ FALSE | "BAMBU" in "BAMBU ENTRENZAS" |
| BIJAO ($10.00) | BIJAO TRICOLOR ✅ FALSE | "BIJAO" in "BIJAO TRICOLOR" |
| ROSA → from "ROSADA" in CALATHEA MAGESTICA ROSADA | ROSA ✅ FALSE | "ROSA" in "CALATHEA MAGESTICA ROSADA" |
| AGAVE ($2.50) | AGAVE AMARILLO + VERDE | Ambiguous |

### Mitigation
After loose matching, always clear known false matches explicitly:
```python
bad_matches = ["BAMBU ENTRENZAS", "BIJAO TRICOLOR", "ROSA", "AGAVE AMARILLO", "AGAVE VERDE"]
for name in bad_matches:
    clear_cell(name, target_col)
```

For ambiguous matches (e.g., "AGAVE" matching multiple portal items), clear ALL and let the user decide.

### Exact Match Priority
When both `base in norm` AND `norm in base` could match, prefer the LONGER match. If neither contains the other, use word-overlap and confirm with user.

## Verified Matches from COST_SARACELY (Jul 10 2026)

Full verified mapping table in the session. Key corrections:
- POTHOS → does not exist. User confirmed: only PHOTOS MULTI RAMA and PHOTUS
- TIERRAS items (TIERRA NEGRA, ABONO ORGANICO, CASCARILLA) have NO cost from any supplier COST_ column — user confirmed "las tierras no tienen costo"