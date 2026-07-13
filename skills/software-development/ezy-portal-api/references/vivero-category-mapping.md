# Category Mapping Reference (vivero.ezyts.com tenant)

## Category IDs and Their Meanings

| Category ID | Name | Plant Types | Tag to Add |
|-------------|------|-------------|------------|
| `870c230c-8db6-4017-8cbf-a850d187a160` | **Flores** | Petunias, Clavelitos, Crisontemos, Poinsettias, Torenias, Novios chinos, Ixora, Rosas, Chavelitas, Cielitos, Celosias | `flowers` |
| `bfc5b004-b8f0-4457-8125-6286974d3d31` | **Follaje** | Aglaonemas, Alocasias, Ficus, Monsteras, Philodendrons, Tradescantias, Calatheas, Crotons, Dieffenbachias, Hypoestes, Lengua de suegra, Cinta mala, Silver Skill, Bordeador, Singonio, etc. | `foliage` |
| `15f31814-9afc-4779-a4dd-28f9aa16addd` | **Hierbas** | Albahaca, Menta, Romero, Ruda, Orégano, Tomillo, Apio, Hierba buena, Hierba de limón | `herbs` |
| `33a9125f-de55-4b56-a94d-e85b8012545e` | **Suculentas** | Jade, Aloe/Sabila, Zamioculcas, Peperonias, Echeverias, Sedums, Cactus | `succulents` |
| `ad132e26-1e28-4404-a305-ee6b5ca2b8e9` | **Palmeras/Árboles** | Palmas (Bismarckia, Madagascar, Phoenix, Real enana, Majestic, Roja, Cubana), Bambú, Pinos (Bonsai, Oro, Hindú, Rastrero), Cipreses, Tuya, Agave, Yuca, Lorito, Guayacán, Texas Nevado, Papo, Bijao | `palms_trees` |
| `4196bac4-daae-4280-99a8-b098e96c68a4` | **Helechos** | Helecho espárrago, Helechos | `foliage` |
| `8cd35fc9-5a6a-4f85-b6d7-63f0c21814ac` | **Logística** | Flete, Carga | `Logistica`, `Carga` |

## Keyword-Based Auto-Categorization Rules

### Flowers (CAT_FLOWERS)
Keywords: `flower`, `petunin`, `clavel`, `coronet`, `cielito`, `crisontemo`, `poinsettia`, `novio`, `ixora`, `rosa`, `rosita`, `jazmin`, `anthurio`, `chavelita`, `torenia`, `celosia`

### Herbs (CAT_HERBS)
Keywords: `hierba`, `romero`, `menta`, `ruda`, `albahaca`, `oregano`, `tomillo`, `apio`, `culantro`, `hierba buena`, `hierba de limon`

### Succulents (CAT_SUCCULENTS)
Keywords: `jade`, `aloe`, `sabila`, `zamioculca`, `peperonia`, `echeveria`, `sedum`, `crassula`, `suculentas`, `cactus`

### Palms/Trees (CAT_PALMS)
Keywords: `palma`, `bambu`, `pino`, `palo de brasil`, `bismarckia`, `madagascar`, `phoenix`, `roebelenii`, `real enana`, `majestica`, `cipre`, `thuja`, `araucaria`, `conifer`, `lorito`, `yuca`, `guayacan`, `tecoma`, `papo`, `copey`, `bijao`, `pino de oro`, `pino hindu`, `pino bonsai`, `pino rastrero`, `agave`, `texas nevado`

### Ferns (CAT_HELECHOS)
Keywords: `helecho`, `helechos`

### Foliage (CAT_FOLIAGE) — Default for foliage plants
Keywords: `aglonaema`, `fitonia`, `molleja`, `aralia`, `diefenbachia`, `crot`, `cobrava`, `philodendron`, `singonio`, `monstera`, `pothos`, `photos`, `philomendro`, `pata de elefante`, `silver skill`, `bordeador`, `hypoestes`, `calathea`, `chaflera`, `china doll`, `chinita`, `cinta mala`, `lengua de suegra`, `lengua`, `tradescantia`, `purple lady`, `mini ericka`, `mini arbusto`, `oreja de elefante`, `alocasia`, `anthuri`, `sangrillo`, `dracena`, `dracaena`, `crot`, `amarillys`, `croto`, `mamy`

## Tag Enrichment Rules

When assigning category, ALSO add the corresponding tag:

| Category | Tag |
|----------|-----|
| Flowers | `flowers` |
| Foliage | `foliage` |
| Herbs | `herbs` |
| Succulents | `succulents` |
| Palms/Trees | `palms_trees` |
| Ferns | `foliage` |

## Existing Category Assignments (as of 2026-06-18)

Items that ALREADY had categories (preserved during batch update):
- PL-AGLONEMAS → FOLIAGE
- PL-ALBAHACA → HERBS
- PL-APIO → FOLIAGE
- PL-CIELITO AZUL → FLOWERS
- PL-CLAVELITO → FLOWERS
- PL-CORONETA → FLOWERS
- PL-CRISONTEMOS → FLOWERS
- PL-FITONIA-ROJA → FOLIAGE
- PL-HELECHO-ESPARRAGO-MEY → FOLIAGE
- PL-HELECHOS → HELECHOS
- PL-IXORA → FLOWERS
- PL-JADE → SUCCULENTS
- PL-MENTA → HERBS
- PL-MINI-JADE → SUCCULENTS
- PL-MOLLEJA → FOLIAGE
- PL-NOVIO-CHINO → FLOWERS
- PL-PALMA-ROJA → PALMS_TREES
- PL-PALO-DE-BRASIL → PALMS_TREES
- PL-PALO-DE-BRASIL-2 → PALMS_TREES
- PL-PALO-DE-BRAZIL → PALMS_TREES
- PL-PETUNIN → FLOWERS
- PL-PINO-BONSAI → PALMS_TREES
- PL-POINSETAS → FLOWERS
- PL-POINSETAS-PEQUENA → FLOWERS
- PL-RUDA → HERBS
- PL-SABILA-ALOE-MEDIANA → SUCCULENTS
- PL-SABILA-ALOE-PEQUENA → SUCCULENTS
- PL-SICDAXUS → FOLIAGE
- PL-TORENIA → FLOWERS
- PL-TRADESCANTIA-ZEBRINA → FOLIAGE
- PL-Tomillo → HERBS
- PL-ZAMIOCULCA → SUCCULENTS
- PL-ZAMIOCULCA-NEGRA → SUCCULENTS