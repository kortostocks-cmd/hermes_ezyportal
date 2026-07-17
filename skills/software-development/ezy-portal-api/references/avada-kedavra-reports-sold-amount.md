# avada kedavra — REPORTS + SOLD_AMOUNT full recalc (Jul 2026 verified recipe)

This is the **full pipeline** for the REPORTS and SOLD_AMOUNT tabs beyond what `lumos.py` covers for INVENTARIO. Worked end-to-end on Jul 16 2026, validated to $0 drift against portal `grandTotal` sum.

**User confirmation rule**: ALWAYS confirm with "¿Corro Avada Kedavra completo o solo INVENTARIO?" before applying. Common user response: "no metas los costos todavía" (= update INVENTARIO only, skip REPORTS/SOLD_AMOUNT/cost writes). Common alternative: "solo arreglalo" (= minimal fix only, no full sync).

## Read phase inputs

All cached locally first to avoid hitting portal twice:
```
/tmp/items.json, /tmp/items_p2.json     portal items paginated
/tmp/po_data/po_*.json                  19 POs with `expand=lines`
/tmp/so_data/so_*.json                  55 SOs with `expand=lines`
```

Caching pattern (avoids repeated urllib heredoc blocks that get blocked):
```
python3 -c "import json; [print(p['id']) for p in json.load(open('/tmp/po_data/list.json'))['data']]" > /tmp/po_ids.txt
while read pid; do
  short=${pid:0:8}
  [ -f "/tmp/po_data/po_${short}.json" ] || curl -s -m 20 \
    -H "X-Api-Key: $KEY" -H "User-Agent: Mozilla/5.0" \
    "$BASE/api/commerce/purchase-orders/${pid}?expand=lines" \
    > "/tmp/po_data/po_${short}.json"
done < /tmp/po_ids.txt
```

Same pattern for `/tmp/so_data/so_*.json`.

## Phase A — REPORTS tab (PLANTA | COSTO | SALE | MARGIN %)

**COSTO** column logic:
1. Walk each PO. Group lines by `name_key(itemName)` → bucket of `unitPrice` per `priceListCode`.
2. Map `priceListCode` → sheet column letter:
   ```
   COST_MIJARDIN=D, COST_EDWIN=E, COST_HACIENDA=F, COST_A&G=G,
   COST_SARACELY=H, COST_SUGEY=I, COST_IAN=J
   COST_JARDIN→D (alias MIJARDIN), SALE_PUBLIC→H (alias SARACELY,
     same bpName=Vivero Sara Cely), COST_IAN→J,
     COST_ISMAEL→E, COST_EDUARDO→E (best-effort only)
   ```
3. For each item, dedupe prices in each column to cents, sort → if 1 unique value use `$X.XX`, otherwise `$min-$max`.
4. Join non-empty columns with ` / ` separator. Example: `JADE` → `$0.95-$1.00`.
5. **manual_aliases** must be applied at PO-ingest time (before bucketing):
   ```
   AGAVE AMARILLO → AGAVE GIGANTE
   AGAVE VERDE    → AGAVE GIGANTE
   ```
   Pattern in code: `if nk in MANUAL_ALIASES: nk = name_key(MANUAL_ALIASES[nk])`

**SALE** column logic:
1. Walk all SOs. For each line, take `qty * unitPrice` weighted by per-SO ratio `grandTotal/subTotal`
   (1.0 unless the portal auto-applied discount — see Phase B).
2. **Take the MOST RECENT** sold price per `(itemId | name)` by `documentDate` (NOT qty-weighted; the most-recent observation wins).
3. Additionally apply alias rules at sale-ingest time: BOMBERO→ROMERO, CHOCOLATE/CHOCOLATITO→CHAVELITAS, NOVIAS→NOVIO CHINO, POTHOS→PHOTUS, plus the manual_aliases for AGAVE.

**MARGIN %** formula:
```
If COSTO is single:  ((sale - cost) / sale) * 100 → "X.X%"
If COSTO is range:   ((sale - avgCost) / sale) * 100  (avg of min/max per column)
If COSTO is "$low-$hi / $foo" (multiple columns): average each column's mid-point, then average across columns
```

## Phase B — SOLD_AMOUNT tab (plan has trailing space: `'SOLD_AMOUNT '`)

Columns: `PLANTA | AMOUNT_SOLD | TOTAL_COST | TOTAL_SALE | TOTAL`.

**Per-item aggregation across all SOs**:
- `AMOUNT_SOLD` = Σ (`line.quantity`)
- `TOTAL_SALE`  = Σ (`line.quantity` × `line.unitPrice` × `so_ratio`) — where `so_ratio = grandTotal/subTotal` if discount, else 1.0. This is what makes TOTAL_SALE match portal `grandTotal` sum to $0.00.
- `TOTAL_COST`  = Σ (`line.quantity` × min_cost[item]) — `min_cost[item]` = lowest supplier price for that item across all PO lines (incl. suppliers like SALE_PUBLIC, COST_JARDIN, COST_IAN that don't have sheet columns). If no PO price exists, leave blank.
- `TOTAL`       = TOTAL_SALE − TOTAL_COST.

**TOTAL row (last row)**:
- Bold, yellow background `#FFEE66` (RGB 1.0/0.95/0.4).
- Sum of all columns above.
- Use UNROUNDED floats during accumulation; only round at display (drift pollution if you round early).

**NOTA_CREDITO column H (pink)** — optional, only when portals applied auto-discount:
- Add per-row discount share: `nc_share = (line_total / subTotal) * (subTotal - grandTotal)` for the ~6 SOs that auto-applied discount; 0 for the rest.
- Pink background: `#FFD9D9` (RGB 1.0/0.85/0.85).
- Apply formatting via `batchUpdate` with `repeatCell` requests.

## Phase C — validation / audit (REQUIRED before claiming done)

After writing:
```
SHEET_TOTAL_SALE  = sheet SOLD_AMOUNT last row col D  (TOTAL_SALE)
PORTAL_SUM_GRAND  = Σ grandTotal across all SOs
assert abs(SHEET_TOTAL_SALE - PORTAL_SUM_GRAND) < 0.01   # $0 drift
SHEET_NC          = Σ col H across SOLD_AMOUNT data rows (or compute total discount = PORTAL_SUM_SUB - PORTAL_SUM_GRAND)
assert abs(SHEET_NC - (PORTAL_SUM_SUB - PORTAL_SUM_GRAND)) < 0.01
```

Verified values on Jul 16 2026:
- SOs: 55 (all CLOSED)
- Portal `subTotal` sum:   $6,881.74
- Portal `grandTotal` sum: $6,856.30
- Discount:                $25.44 (across 6 SOs)
- NC SOs: SO-2026-000068 ($6.07), -000072 ($6.07), -000075 ($5.41), -000079 ($2.14), -000081 ($3.04), -000090 ($2.71)

## Sheet write pattern (clear+write, NEVER just update)

```
def write_tab(svc, sheet_id, tab, data):
    h = len(data); w = max(len(r) for r in data)
    last = col_letter(w)
    rng = f"'{tab}'!A1:{last}{h}"
    svc.spreadsheets().values().clear(spreadsheetId=sheet_id, range=rng, body={}).execute()
    svc.spreadsheets().values().update(spreadsheetId=sheet_id, range=rng,
        valueInputOption="USER_ENTERED", body={"values": data}).execute()
    svc.spreadsheets().values().clear(spreadsheetId=sheet_id,
        range=f"'{tab}'!A{h+1}:{last}999", body={}).execute()
```

For SOLD_AMOUNT the trailing-space tab name `'SOLD_AMOUNT '` is REQUIRED; using `'SOLD_AMOUNT'` returns the "sheet not found" error. Match the sheet ID via `/spreadsheets.get` and grep by title-stripped.

## Inline Google token refresh (avoids user re-auth)

```
import json, urllib.parse, urllib.request, datetime, os
t = json.load(open(os.path.expanduser("~/.hermes/profiles/ezy_portal_expert/google_token.json")))
data = urllib.parse.urlencode({
    'client_id': t['client_id'], 'client_secret': t['client_secret'],
    'refresh_token': t['refresh_token'], 'grant_type': 'refresh_token',
}).encode()
r = urllib.request.urlopen(urllib.request.Request(
    t['token_uri'], data=data,
    headers={'Content-Type':'application/x-www-form-urlencoded'}), timeout=15)
new = json.loads(r.read())
t['token'] = new['access_token']
t['expiry'] = (datetime.datetime.utcnow() + datetime.timedelta(seconds=new['expires_in'])).isoformat() + 'Z'
json.dump(t, open(<TOKEN_PATH>,'w'))
```

This works even when the token was stamped before expiry check ran. Saves the user a `--auth-url` roundtrip.

## "Solo arreglalo" / "no metas los costos todavía" pattern

- User saying "solo X" or "no Y todavía" → apply ONLY X. Don't run full sync.
- Default to the **minimum scope that satisfies the message**, not the maximum scope you have scripts for.
- When in doubt, ask before writing: "¿Solo INVENTARIO, o full avada?"
- Confirms against `udto` shape: present diff first, scope-snap, then apply when user says "dle".
