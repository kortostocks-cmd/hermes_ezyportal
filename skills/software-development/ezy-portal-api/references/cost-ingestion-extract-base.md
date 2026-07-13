# Cost Ingestion from Supplier Price Lists (updated Jul 10 2026)

## The `extract_base()` function

When processing physical price lists (photos/scans) from suppliers:

```python
def extract_base(name):
    """Strip container/size/promo details from supplier catalog names."""
    name = name.upper()
    # Remove "EN POTE 5", "EN BOLSA", "PROMOCION HASTA 14 DE JUNIO", etc.
    name = re.sub(r"\s*(EN\s+(POTE|BOLSA|MACETA|POT|GEOTEXTIL|PDB|VCG).*|PROMOCION.*)", "", name).strip()
    # Remove trailing inch marks
    name = re.sub(r'\s*".*', "", name).strip()
    # Remove bracketed codes [19Z]
    name = re.sub(r"\s*\[.*\]", "", name).strip()
    return nfkd(name)
```

## ⚠️ False Substring Match Trap (CRITICAL)

Never use Python's `in` operator to match supplier catalog names against portal names:

```python
# WRONG — produces false matches:
"BAMBU" in "BAMBU ENTRENZAS"   # True (wrong!)
"ROSA"  in "ROSADA"            # True (wrong!, ROSADA from CALATHEA MAGESTICA ROSADA)
"BIJAO" in "BIJAO TRICOLOR"    # True (wrong!)
"AGAVE" in "AGAVE AMARILLO"    # True (both are valid matches, ambiguous)
```

**Always use exact match (`norm == base`):**

```python
# RIGHT — no false positives:
for base, price in catalog_prices.items():
    if norm == base:   # exact character-for-character match
        found_price = price
        break
```

When the catalog has generic names (e.g., "AGAVE EN POTE 5" → base="AGAVE") and the portal has specific variants (AGAVE AMARILLO, AGAVE VERDE), **ask the user** which variant to assign the cost to. Do not auto-assign to all matching variants.

## Real Example (Jul 10 2026 — Sara Cely catalog)

Catalog items with pot sizes → matched to portal items:

| Catalog Name | extract_base() | Portal Match | Cost |
|---|---|---|---|
| AGAVE EN POTE 5 | AGAVE | (ambiguous) | $2.50 |
| AJUGA EN BOLSA | AJUGA | AJUGA ✅ | $0.85 |
| ALCANCEL EN BOLSA | ALCANCEL | ALCANCEL ✅ | $0.85 |
| ALOCASIA GIGANTE VARIEGADA EN PDB40 | ALOCASIA GIGANTE VARIEGADA | ✅ | $50.00 |
| ALOCASIA VERDE EN PDB 40 | ALOCASIA VERDE | ✅ | $20.00 |
| ANTHURIUM FLOR GRANDE EN POTE DE CERAMICA | ANTHURIUM FLOR GRANDE | ANTHURIO FLOR ✅ | $14.00 |
| APIO POTE 140 PROMOCION HASTA 14 DE JUNIO | APIO | APIO ✅ | $1.50 |
| ARALIA BLANCA EN POTE 5 | ARALIA BLANCA | ✅ | $1.75 |
| BAMBU EN POTE PDB 40 | BAMBU | BAMBU ✅ ($90) | $90.00 |
| BORDEADOR MATIZADO EN BOLSA | BORDEADOR MATIZADO | ✅ | $0.85 |
| CALATHEA MAGESTICA ROSADA EN POTE 140 | CALATHEA MAGESTICA ROSADA | ✅ | $5.00 |
| CINQUITO EN BOLSA | CINQUITO | ✅ | $1.25 |
| CIPRE AZUL EN POTE 160 PROMOCION HASTA 14 DE JUNIO | CIPRE AZUL | ✅ | $9.00 |
| COPEY EN POTE 140 | COPEY | ✅ | $3.00 |