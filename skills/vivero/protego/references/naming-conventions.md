# Naming Conventions: 3-Source Plant Name Matching

## Sources and their naming patterns

### 1. Supplier Invoices (raw)
- Short names, sometimes misspelled: "chocolate", "bombero", "mini uvas"
- No size suffix unless explicitly written ("POTE GRANDE", "POTE 180")
- Local names: "Chavelitas" (not just "Marigold"), "Novios"/"Novias"
- Singluar/plural inconsistent: "TORENIAS" (factura) vs "TORENIA" (sheet)

### 2. Google Sheet INVENTARIO
- Full descriptive names: "LENGUA DE SUEGRA MINI" (not "LENGUA MINI")
- Size as part of name: "CACTUS MEDIANO", "SUCULENTAS GRANDE", "PALO DE BRASIL DE ESCRITORIO"
- Singular form: "TORENIA", "CORONITA" (not "TORENIAS", "CORONITAS")
- Some with extra descriptors: "ALBAHACA VERDE" / "ALBAHACA ROJA"

### 3. Airtable (backup)
- Names carry suffix ` VR` on most plants: "HIERBA BUENA VR", "JADE VR", "ROMERO VR"
- Some exceptions: "SUCULENTAS POTE GRANDE" (no VR), "FLETE" (no VR)
- Airtable names are otherwise identical to Sheet INVENTARIO names

## Known mappings (invoice → sheet/portal)

| Invoice name | Sheet/Portal name | Reason |
|-------------|-------------------|--------|
| HIERBA BUENA | HIERBA BUENA | Direct match |
| MENTA | MENTA | Direct match |
| ROMERO | ROMERO | Direct match |
| BOMBERO | ROMERO | Local synonym |
| ALBAHACA | ALBAHACA VERDE | User specifies which variant |
| CACTUS | CACTUS MEDIANO | User specifies size |
| CACTUS HUESO DE DRAGÓN | CACTUS HUESO DE DRAGON | Direct (accent removed) |
| CHAVELITAS | CHAVELITAS | Direct match |
| CHOCOLATE | CHAVELITAS | Local synonym |
| CHAVELITAS (96+24+96) | CHAVELITAS | Sum of all sources |
| CINTAS | CINTA MALA MADRE | Full name in sheet |
| CLAVELES | CLAVELITO | Sheet uses diminutive |
| CORONITAS | CORONITA | Sheet uses singular |
| TORENIAS | TORENIA | Sheet uses singular |
| JADE | JADE | Direct match |
| MINI JADE | MINI JADE | Direct match |
| MINI UVAS | MINI JADE | Local synonym |
| NOVIOS / NOVIAS | NOVIO CHINO | Both map to same |
| LENGUA MINI | LENGUA DE SUEGRA MINI | Full name in sheet |
| LENGUA ENANA | LENGUA DE SUEGRA ENANA | Full name in sheet |
| SUCULENTAS POTE GRANDE | SUCULENTAS GRANDE | Sheet drops "POTE" |
| SUCULENTAS MEDIANA | SUCULENTAS MEDIANAS | Sheet uses plural |
| ZAMIOCULCA | MILLONARIA ZAMIOCULCA | Sheet uses prefix |
| ZAMIOCULCA NEGRA | MILLONARIA ZAMIOCULCA NEGRA | Sheet uses prefix |
| CAÑA DEL BRASIL | PALO DE BRASIL | Different common name |
| ALOCASIA LAVA | ALOCASIA LAVA ROJA | User specifies variant |
| FICUS TRIANGULAR | FICUS TRIANGULAR GRANDE | User specifies size |
| HELECHO | HELECHOS | Sheet uses plural |
| SÁBILA ALOE | SABILA ALOE PEQUEÑA / MEDIANA | User specifies size |
| ROSITA MINIATURA | ROSITA MINIATURA | Direct match |
| PALMA ROJA | PALMA ROJA | Direct match |
| MOLLEJA | MOLLEJA | Direct match |
| MILLONARIA ZAMIOCULCA | MILLONARIA ZAMIOCULCA | Direct match |
| MILLONARIA ZAMIOCULCA NEGRA | MILLONARIA ZAMIOCULCA NEGRA | Direct match |

## Normalization function (Python)

```python
import unicodedata, re

def normalize(name):
    """Normalize plant name for cross-source matching."""
    nfkd = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Z0-9]', '', nfkd.upper())

def normalize_airtable(name):
    """Normalize Airtable name (strip VR suffix, then normalize)."""
    n = name.upper().strip()
    # Strip common Airtable suffixes
    for suffix in [' VR', ' VR ', ' VR.']:
        if n.endswith(suffix):
            n = n[:-len(suffix)]
    return normalize(n)
```

## Products to EXCLUDE from plant purchase lists
- FLETE / FLETE INTERNO / FLETE POR CAJA (freight)
- CAJA POTE 180 / CAJA POTE 180_450PCS / CAJA POTE 120_1000PCS (pots boxes)
- Any item marked N/C (not charged) on invoice
- Any non-plant item (tierra negra, cascarilla de arroz)