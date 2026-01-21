# Work Order Creation API - Required Fields

## Endpoint
```
POST /api/v1/work-orders
```

## Required Headers
```
Authorization: Bearer <farmer_access_token>
Content-Type: application/json
```

## Request Body Schema

### Required Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `farming_organization_id` | UUID (string) | ✅ Yes | The farmer's organization ID | `"79286b56-dea9-41dc-9ff2-46ca890fd67d"` |
| `fsp_organization_id` | UUID (string) | ✅ Yes | The FSP organization ID from marketplace | `"3353a42a-15e9-4d01-816e-bc4d0b1f8f48"` |
| `title` | string | ✅ Yes | Work order title (1-200 chars) | `"Soil Testing Service Request"` |

### Optional Fields

| Field | Type | Required | Description | Default | Example |
|-------|------|----------|-------------|---------|---------|
| `service_listing_id` | UUID (string) | ❌ No | The specific service listing ID | `null` | `"70d2587a-a571-477a-b898-82c75e8c7fd9"` |
| `description` | string | ❌ No | Detailed description | `null` | `"Need soil testing for 5 acres"` |
| `terms_and_conditions` | string | ❌ No | T&C text | `null` | `"Payment on completion"` |
| `start_date` | date (YYYY-MM-DD) | ❌ No | Preferred start date | `null` | `"2026-01-25"` |
| `end_date` | date (YYYY-MM-DD) | ❌ No | Preferred end date | `null` | `"2026-01-30"` |
| `total_amount` | number | ❌ No | Total amount (≥ 0) | `null` | `500` |
| `currency` | string | ❌ No | Currency code | `"INR"` | `"INR"` |
| `scope_items` | array | ❌ No | Resources to grant access | `[]` | See below |

### Scope Items (Optional)

If you want to grant FSP access to specific farms/plots/crops:

```json
"scope_items": [
  {
    "scope": "FARM",
    "scope_id": "farm-uuid-here",
    "access_permissions": {
      "read": true,
      "write": false,
      "track": false
    },
    "sort_order": 0
  }
]
```

**Scope Types:**
- `"ORGANIZATION"` - Grant access to entire organization
- `"FARM"` - Grant access to specific farm
- `"PLOT"` - Grant access to specific plot
- `"CROP"` - Grant access to specific crop

**Access Permissions:**
- `read`: Can view data (default: `true`)
- `write`: Can modify data (default: `false`)
- `track`: Can track activities (default: `false`)

## Valid Currency Codes
- `"INR"` (Indian Rupee) - Default
- `"USD"` (US Dollar)
- `"EUR"` (Euro)
- `"GBP"` (British Pound)

## Validation Rules

1. ✅ **Title**: Cannot be empty, max 200 characters
2. ✅ **Dates**: `end_date` must be after `start_date` (if both provided)
3. ✅ **Amount**: Must be ≥ 0 if provided
4. ✅ **Currency**: Must be one of: INR, USD, EUR, GBP
5. ✅ **Scope Permissions**: Must include all three keys: `read`, `write`, `track` (all boolean)

## Example Requests

### Minimal Request (Only Required Fields)
```json
{
  "farming_organization_id": "79286b56-dea9-41dc-9ff2-46ca890fd67d",
  "fsp_organization_id": "3353a42a-15e9-4d01-816e-bc4d0b1f8f48",
  "title": "Soil Testing Service"
}
```

### Complete Request (All Fields)
```json
{
  "farming_organization_id": "79286b56-dea9-41dc-9ff2-46ca890fd67d",
  "fsp_organization_id": "3353a42a-15e9-4d01-816e-bc4d0b1f8f48",
  "service_listing_id": "70d2587a-a571-477a-b898-82c75e8c7fd9",
  "title": "Soil Testing for Main Farm",
  "description": "Comprehensive soil analysis needed for 5 acres before planting season",
  "terms_and_conditions": "Payment upon completion. Results required within 3 days.",
  "start_date": "2026-01-25",
  "end_date": "2026-01-28",
  "total_amount": 500,
  "currency": "INR",
  "scope_items": [
    {
      "scope": "FARM",
      "scope_id": "your-farm-uuid-here",
      "access_permissions": {
        "read": true,
        "write": false,
        "track": true
      },
      "sort_order": 0
    }
  ]
}
```

### Request from Marketplace (Recommended)
```json
{
  "farming_organization_id": "79286b56-dea9-41dc-9ff2-46ca890fd67d",
  "fsp_organization_id": "3353a42a-15e9-4d01-816e-bc4d0b1f8f48",
  "service_listing_id": "70d2587a-a571-477a-b898-82c75e8c7fd9",
  "title": "Soil Testing Service",
  "description": "Request from marketplace",
  "total_amount": 500,
  "currency": "INR"
}
```

## Success Response (201 Created)
```json
{
  "success": true,
  "message": "Work order created successfully",
  "data": {
    "id": "work-order-uuid",
    "work_order_number": "WO-20260121-0001",
    "status": "PENDING",
    "farming_organization_id": "79286b56-dea9-41dc-9ff2-46ca890fd67d",
    "fsp_organization_id": "3353a42a-15e9-4d01-816e-bc4d0b1f8f48",
    "title": "Soil Testing Service",
    "created_at": "2026-01-21T16:04:50.991216Z"
  }
}
```

## Error Response (422 Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "farming_organization_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `field required` | Missing required field | Add `farming_organization_id`, `fsp_organization_id`, or `title` |
| `Title cannot be empty` | Empty title string | Provide non-empty title |
| `End date must be after start date` | Invalid date range | Ensure `end_date` > `start_date` |
| `Currency must be one of: INR, USD, EUR, GBP` | Invalid currency | Use valid currency code |
| `Permissions must include: read, write, track` | Missing permission keys | Include all three permission keys |
| `All permission values must be boolean` | Non-boolean permission values | Use `true` or `false` for permissions |

## How to Get Required IDs

### 1. Farming Organization ID
Get from user's login response or organizations list:
```bash
GET /api/v1/organizations
```

### 2. FSP Organization ID
Get from marketplace service listing:
```bash
GET /api/v1/fsp-services/fsp-marketplace/services
```
Response includes `fsp_organization_id` for each service.

### 3. Service Listing ID
Also from marketplace response - the `id` field of the service.

### 4. Farm/Plot/Crop IDs (for scope)
```bash
GET /api/v1/farms/
GET /api/v1/farms/{farm_id}/plots
GET /api/v1/crops/
```

## Testing with cURL

```bash
# Get farmer token
TOKEN="your-farmer-token-here"

# Create work order
curl -X POST "http://localhost:8000/api/v1/work-orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "farming_organization_id": "79286b56-dea9-41dc-9ff2-46ca890fd67d",
    "fsp_organization_id": "3353a42a-15e9-4d01-816e-bc4d0b1f8f48",
    "service_listing_id": "70d2587a-a571-477a-b898-82c75e8c7fd9",
    "title": "Soil Testing Service",
    "total_amount": 500,
    "currency": "INR"
  }'
```

## Notes

> [!IMPORTANT]
> - The farmer must be logged in and have a valid access token
> - The farmer must be a member of the `farming_organization_id`
> - The work order starts with status `PENDING`
> - FSP must accept the work order before it becomes `ACCEPTED`
> - `scope_items` can be empty `[]` - FSP won't have access to any resources initially

> [!TIP]
> **Recommended approach for marketplace requests:**
> 1. User selects service from marketplace
> 2. Frontend extracts `fsp_organization_id` and service `id` (as `service_listing_id`)
> 3. Use service `title` or let user customize
> 4. Include `total_amount` from service `base_price`
> 5. Optionally let user select farms/plots to grant access
