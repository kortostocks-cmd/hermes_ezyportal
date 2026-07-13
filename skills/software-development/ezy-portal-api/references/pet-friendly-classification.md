# Plant Pet-Friendly Classification (Vivero Catalog)

Based on ASPCA Animal Poison Control (https://www.aspca.org/pet-care/animal-poison-control/dogs-plant-list), The Spruce, and ASPCA Pet-Safe Plants guides.

## Criteria
- Non-toxic to cats and dogs (no calcium oxalate crystals, no saponins, no philodendron-type toxins)
- Used for labeling/tagging in EZY Portal: add `pet_friendly` tag via PATCH

---

## ✅ PET-FRIENDLY — Safe for cats and dogs

### Herbs / Aromaticas
ALBAHACA, MENTA VR, OREGANO VR, ROMERO VR, Tomillo VR, HIERBA BUENA VR, HIERBA DE LIMON VR, APIO, RUDA VR

### Palms (all true palms — Palmae family)
PALMA CUBANA VR, PALMA ROJA VR, PALMA MAJESTIC EN POTE 140", PALMA PHOENIX ROEBELENII, PALMA REAL ENANA, PALMA BISMARCKIA, PALMA DE MADAGASCAR, BAMBU VR (Areca)

### Succulents
SUCULENTAS MEDIANAS, SUCULENTAS POTE GRANDE, JADE VR, MINI JADE VR, PEPERONIA SANDIA VR, AGAVE EN POTE 5

### Cacti
CACTUS HUESO DE DRAGON VR, CACTUS MEDIANO VR

### Ferns
HELECHOS, HELECHO ESPARRAGO MEYERI VR

### Calathea / Maranta family
CALATHEA MAGESTICA ROSADA EN POTE 140", CINTA MALA MADRE VR

### Flowers / Ornamentals
ANTHURIO FLOR GRANDE, ROSA VR, ROSA FLOR GRANDE, ROSITA MINIATURA, CLAVELITO VR, CELOCIA VR, PETUNIN VR, TORENIA VR, CHAVELITAS VR, CIELITO AZUL, IXORA VR, REINA ISABEL, CORONETA, NOVIO CHINO VR, PURPLE LADY, CRINUM ASIATICO

### Foliage / Shrubs
ARALIA BLANCA, GUAYACAN ENANO (TECOMA), DURANTA EN BOLSA, COPEY EN POTE 140", CHAFLERA TRINET, COBRA GIGANTE, COBRA VERDE, PAPO, BIJAO, SANGRILLO, MINI ARBUSTO VR, MINI ERICKA EN BOLSA, BORDEADOR MATIZADO, CINQUITO, AJUGA EN BOLSA

### Hoya / Trailing
PHOTUS VR (Hoya), TRADESCANTIA (Gold, Mini, REO, ZEBRINA)

### Pines / Cypres
PINO BONSAI VR, PINO DE ORO EN POTE 21, PINO HINDU EN POTE PREMIUM 5", PINO RASTRERO VR, CIPRE AZUL, CIPRE BOLA, CIPRE DORADO, CIPRE THUJA

### Trees / Special
PATA DE ELEFANTE (Beaucarnea/Nolina — safe), LORITO, YUCA EN POTE 129"

---

## ⚠️ TOXIC — Do NOT tag pet_friendly

| Planta | Razón tóxica |
|--------|-------------|
| **PHILODENDRON (TODOS — Cobra, Congo, Xinadu, generic)** | **Oxalatos de calcio (Araceae). Corregido Jun 25 2026 — eran marcados pet_friendly incorrectamente** |
| AGLONEMAS VR | Oxalatos |
| DIEFFENBACHIA DALILA | Muy tóxica — oxalatos |
| MONSTERA DELICIOSA, MONSTERA ADANSONII | Oxalatos |
| LENGUA DE SUEGRA / SANSEVIERA | Saponinas |
| SABILA ALOE (ambas) | Saponinas / Laxante |
| ZAMIOCULCA / ZAMIOCULCA NEGRA | Oxalatos |
| FICUS (Bambino, Elastica, Lyrata, Triangular) | Látex irritante |
| CROTO MAMY AMARILLO | Toxicidad desconocida |
| ALOCASIA (todas) | Oxalatos |
| SINGONIO BLANCO VARIEGADO | Oxalatos |
| POINSETAS | Látex irritante |
| CLUSIA | Posiblemente tóxica |
| LORITO | Verificar especie |
| JAZMIN BLANCO | Niveles bajos pero evitar |

---

## How to Tag in EZY Portal

Items have a `tags: string[]` field. Add `pet_friendly` via PATCH:

```python
import json, urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

key = "ten_YOUR_KEY"

# Get item with version
url = "https://vivero.ezyts.com/api/items/items?isActive=true&expand=prices,itemUoms&perPage=1"
# PATCH requires version for optimistic concurrency
payload = json.dumps({
    'tags': existing_tags + ['pet_friendly'],
    'version': item['version']  # REQUIRED
}).encode()

req = urllib.request.Request(f"/api/items/items/{item_id}", data=payload, method='PATCH')
req.add_header("X-Api-Key", key)
req.add_header("Content-Type", "application/json")
# ...urlopen with context
```

**Note**: Always fetch the item fresh before PATCH to get the current `version`. Stale version = 409 Conflict.

## Jun 25 2026 — Accuracy Fix

Cruce de 71 items pet_friendly con ASPCA reveló **2 falsos positivos** que fueron corregidos:
- PHILODENDRON COBRA EN CANASTA → tag `pet_friendly` removido (era tóxico)
- PHILODENDRON CONGO EN POTE 19 → tag `pet_friendly` removido (era tóxico)

Conteo pet_friendly: 71 → 69 tras corrección. Además se identificó que la referencia
tenía mal clasificado Philodendron como "algunos seguros" — la realidad ASPCA es que
**todos los Philodendron contienen oxalatos de calcio** y son tóxicos para mascotas.