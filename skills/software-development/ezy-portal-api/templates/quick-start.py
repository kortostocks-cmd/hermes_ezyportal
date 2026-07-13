# EZY Portal API — Quick Start Templates

## Python Client Boilerplate

```python
"""Minimal EZY Portal API client."""
import os
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Use tenant-specific base URL: https://<tenant>.ezyts.com
# Example: https://vivero.ezyts.com, https://miempresa.ezyts.com
BASE_URL = os.getenv("EZY_PORTAL_BASE_URL", "https://vivero.ezyts.com")
BEARER_TOKEN = os.getenv("EZY_BEARER_TOKEN")
TENANT_API_KEY = os.getenv("EZY_TENANT_API_KEY")  # ten_...

class EzyPortalClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _auth_headers(self, use_tenant_key: bool = False) -> Dict[str, str]:
        if use_tenant_key and TENANT_API_KEY:
            return {"X-Api-Key": TENANT_API_KEY, "Accept": "application/json"}
        if BEARER_TOKEN:
            return {"Authorization": f"Bearer {BEARER_TOKEN}", "Accept": "application/json"}
        return {"Accept": "application/json"}

    def _get(self, path: str, params: Dict = None, use_tenant_key: bool = False) -> Dict:
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, headers=self._auth_headers(use_tenant_key), params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json: Dict, use_tenant_key: bool = False) -> Dict:
        url = f"{self.base_url}{path}"
        resp = self.session.post(url, headers=self._auth_headers(use_tenant_key), json=json)
        resp.raise_for_status()
        return resp.json()

    def _patch(self, path: str, json: Dict) -> Dict:
        url = f"{self.base_url}{path}"
        resp = self.session.patch(url, headers=self._auth_headers(), json=json)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> Dict:
        url = f"{self.base_url}{path}"
        resp = self.session.delete(url, headers=self._auth_headers())
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    # --- Items ---
    def list_items(self, **filters) -> Dict:
        """List items with pagination. Add expand=prices for prices."""
        params = {k: v for k, v in filters.items() if v is not None}
        return self._get("/api/items/items", params=params)

    def get_item_by_code(self, code: str, expand_prices: bool = True) -> Dict:
        params = {"expand": "prices"} if expand_prices else {}
        return self._get(f"/api/items/items/by-code/{code}", params=params)

    def create_item(self, payload: Dict) -> Dict:
        return self._post("/api/items/items", json=payload)

    def update_item(self, item_id: str, payload: Dict, version: int) -> Dict:
        payload["version"] = version
        return self._patch(f"/api/items/items/{item_id}", json=payload)

    def delete_item(self, item_id: str) -> Dict:
        return self._delete(f"/api/items/items/{item_id}")

    def search_by_barcode(self, barcode: str) -> Dict:
        return self._get("/barcodes", params={"barcode": barcode}, use_tenant_key=True)

    # --- Categories ---
    def list_categories(self, active: Optional[bool] = None) -> List[Dict]:
        params = {"active": str(active).lower()} if active is not None else {}
        return self._get("/api/categories", params=params)

    def create_category(self, code: str, name: str, parent_id: Optional[str] = None) -> Dict:
        payload = {"code": code, "name": name}
        if parent_id:
            payload["parentId"] = parent_id
        return self._post("/api/categories", json=payload)

    # --- Item Groups ---
    def list_item_groups(self, active: Optional[bool] = None, page: int = 1, per_page: int = 100) -> Dict:
        params = {"page": page, "perPage": per_page}
        if active is not None:
            params["active"] = str(active).lower()
        return self._get("/api/item-groups", params=params)

    # --- Stats ---
    def get_stats(self) -> Dict:
        return self._get("/api/items/stats")

    def get_quality_stats(self) -> Dict:
        return self._get("/api/items/stats/quality")


# Usage example
if __name__ == "__main__":
    client = EzyPortalClient()

    # List sellable active items with prices
    items = client.list_items(
        expand="prices",
        isActive=True,
        isSellable=True,
        page=1,
        perPage=50,
        sortBy="name"
    )
    print(f"Total: {items.get('total')}")

    # Get single item by code with prices
    item = client.get_item_by_code("ITEM-001")
    for price in item.get("prices", []):
        if price.get("masked"):
            print(f"  {price['priceList']['code']}: MASKED")
        else:
            print(f"  {price['priceList']['code']}: {price['price']} {price['currencyCode']}")
```

---

## Bash/curl Quick Commands

```bash
# Export these
export EZY_BASE="https://vivero.ezyts.com"
export EZY_TOKEN="your-bearer-token"
export EZY_TENANT_KEY="ten_your-key"
# List items with prices (Bearer)
curl -H "Authorization: Bearer $EZY_TOKEN" \
  "$EZY_BASE/api/items/items?expand=prices&isActive=true&isSellable=true&page=1&perPage=20"

# List items with prices (Tenant API Key)
curl -H "X-Api-Key: $EZY_TENANT_KEY" \
  "$EZY_BASE/api/items/items?expand=prices&isActive=true&isSellable=true"

# Get item by code
curl -H "Authorization: Bearer $EZY_TOKEN" \
  "$EZY_BASE/api/items/items/by-code/ITEM-001?expand=prices"

# Create item
curl -X POST -H "Authorization: Bearer $EZY_TOKEN" -H "Content-Type: application/json" \
  -d '{"itemCode":"NEW-001","name":"New Item","itemType":"stock","baseUom":"EA"}' \
  "$EZY_BASE/api/items/items"

# Search by barcode
curl -H "X-Api-Key: $EZY_TENANT_KEY" \
  "$EZY_BASE/barcodes?barcode=1234567890123"
```

---

## TypeScript Types (from OpenAPI)

```typescript
// Core types extracted from spec
type ItemType = "stock" | "non_stock" | "service" | "bundle" | "virtual" | "style";
type SyncState = "in_sync" | "pending_create" | "pending_update" | "pending_delete" | "error" | "ignored";
type BarcodeType = "ean13" | "upc" | "code128" | "qr" | "internal" | "other";
type VariantDimensionType = "SIZE" | "COLOR" | "MATERIAL" | "WIDTH" | "CUSTOM";
type VariantGroupType = "SIMPLE" | "MATRIX" | "BUNDLE";

interface LocalItemPriceResponse {
  id: string;
  priceListId: string;
  itemUomId: string;
  price: number | null;
  currencyCode: string | null;
  masked: boolean;
  validFrom: string;
  validTo: string;
  priceList?: LocalPriceList;
  itemUom?: ItemUOM;
}

interface ItemResponse {
  id: string;
  itemCode: string;
  name: string;
  itemType: ItemType;
  isActive: boolean;
  isStock: boolean;
  isPurchasable: boolean;
  isSellable: boolean;
  baseUom: string;
  itemGroupId: string;
  itemGroup?: ItemGroup;
  itemCategory: string;
  itemCategoryName: string;
  prices: LocalItemPriceResponse[] | null;
  uoms: ItemUOM[];
  barcodes: ItemBarcode[];
  categories: ItemCategoryResponse[];
  variantMatrix?: VariantMatrixResponse;
  variantParentItemCode?: string;
  variantValues: Record<string, string>;
  itemStockTotal: number;
  itemAvailableTotal: number;
  itemAvgCost: number;
  itemLastCost: number;
  itemOnOrderTotal: number;
  itemReservedTotal: number;
  itemCostMasked: boolean;
  version: number;
  syncState: SyncState;
}

interface ItemCreateRequest {
  itemCode: string;
  name: string;
  itemType: ItemType;
  baseUom?: string;
  itemGroup?: string;
  itemCategory?: string;
  itemClassId?: string;
  priceListCode?: string;
  description?: string;
  sku?: string;
  isActive?: boolean;
  isStock?: boolean;
  isPurchasable?: boolean;
  isSellable?: boolean;
  initialUOMs?: ItemUOMCreateRequest[];
  initialBarcodes?: InitialBarcodeInput[];
  initialCategories?: ItemCategoryInput[];
  prices?: BulkUpsertItem[];
  defaultSalesTaxCategoryId?: string;
  defaultPurchaseTaxCategoryId?: string;
  tags?: string[];
  ext?: Record<string, any>;
  syncState?: SyncState;
  lastSyncAt?: string;
}
```