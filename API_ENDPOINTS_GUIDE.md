# API Endpoints for Field/Plot and Crop Creation

## Correct Endpoints

### 1. Create Plot (Field)
**Endpoint:** `POST /api/v1/plots/farms/{farm_id}/plots`

**Path Parameters:**
- `farm_id`: UUID of the farm (e.g., `91551b9e-7a29-4878-8ccd-cdb49df59cc0`)

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Minimal Request Body:**
```json
{
  "name": "Test Field 1"
}
```

**Full Request Body Example:**
```json
{
  "name": "Test Field 1",
  "description": "Test field for schedule management",
  "area": 2.5,
  "area_unit_id": "unit-uuid-here",
  "boundary": {
    "type": "Polygon",
    "coordinates": [
      [
        [77.123456, 11.123456],
        [77.124456, 11.123456],
        [77.124456, 11.124456],
        [77.123456, 11.124456],
        [77.123456, 11.123456]
      ]
    ]
  },
  "plot_attributes": {
    "soil_ph": 6.5,
    "soil_ec": 0.8
  }
}
```

**Response (201 Created):**
```json
{
  "id": "plot-uuid-here",
  "farm_id": "91551b9e-7a29-4878-8ccd-cdb49df59cc0",
  "name": "Test Field 1",
  "description": "Test field for schedule management",
  "area": 2.5,
  "area_unit_id": "unit-uuid-here",
  "boundary": {...},
  "plot_attributes": {...},
  "is_active": true,
  "created_at": "2026-01-21T17:00:00Z",
  "updated_at": "2026-01-21T17:00:00Z",
  "created_by": "user-uuid",
  "updated_by": "user-uuid"
}
```

---

### 2. Create Crop
**Endpoint:** `POST /api/v1/crops/`

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Minimal Request Body:**
```json
{
  "plot_id": "plot-uuid-from-step-1",
  "name": "Test Tomato Crop"
}
```

**Full Request Body Example:**
```json
{
  "plot_id": "plot-uuid-from-step-1",
  "name": "Test Tomato Crop",
  "description": "Test crop for schedule testing",
  "crop_type_id": "crop-type-uuid",
  "crop_variety_id": "variety-uuid",
  "area": 1.5,
  "area_unit_id": "unit-uuid",
  "plant_count": 400,
  "planned_date": "2026-01-25"
}
```

**Alternative (using variety name instead of ID):**
```json
{
  "plot_id": "plot-uuid-from-step-1",
  "name": "Test Tomato Crop",
  "variety_name": "Cherry Tomato"
}
```

**Response (201 Created):**
```json
{
  "id": "crop-uuid-here",
  "plot_id": "plot-uuid-from-step-1",
  "name": "Test Tomato Crop",
  "description": "Test crop for schedule testing",
  "crop_type_id": "crop-type-uuid",
  "crop_variety_id": "variety-uuid",
  "area": 1.5,
  "area_unit_id": "unit-uuid",
  "plant_count": 400,
  "lifecycle": "PLANNED",
  "planned_date": "2026-01-25",
  "planted_date": null,
  "transplanted_date": null,
  "production_start_date": null,
  "completed_date": null,
  "terminated_date": null,
  "closed_date": null,
  "created_at": "2026-01-21T17:00:00Z",
  "updated_at": "2026-01-21T17:00:00Z",
  "created_by": "user-uuid",
  "updated_by": "user-uuid"
}
```

---

## What Was Wrong

❌ **Incorrect:** `POST /api/v1/farms/{farm_id}/fields`  
✅ **Correct:** `POST /api/v1/plots/farms/{farm_id}/plots`

The API uses "plots" not "fields" in the endpoint path.

---

## Usage in create_work_order.py

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
FARM_ID = "91551b9e-7a29-4878-8ccd-cdb49df59cc0"
ACCESS_TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Step 1: Create Plot
plot_response = requests.post(
    f"{BASE_URL}/plots/farms/{FARM_ID}/plots",
    headers=headers,
    json={"name": "Test Field 1"}
)
plot_id = plot_response.json()["id"]
print(f"Created plot: {plot_id}")

# Step 2: Create Crop
crop_response = requests.post(
    f"{BASE_URL}/crops/",
    headers=headers,
    json={
        "plot_id": plot_id,
        "name": "Test Tomato Crop"
    }
)
crop_id = crop_response.json()["id"]
print(f"Created crop: {crop_id}")

# Step 3: Create Schedule from Template
schedule_response = requests.post(
    f"{BASE_URL}/schedules/from-template",
    headers=headers,
    json={
        "crop_id": crop_id,
        "template_id": "template-uuid",
        "start_date": "2026-01-25",
        "area": 1.5,
        "area_unit_id": "unit-uuid",
        "plant_count": 400
    }
)
print(f"Created schedule: {schedule_response.json()['id']}")
```

---

## Notes

1. **Authentication Required:** All endpoints require a valid JWT token in the `Authorization` header.
2. **Organization Context:** The API automatically derives the organization from the JWT token.
3. **Minimal Payloads:** Only `name` is required for plots, and `plot_id` + `name` for crops.
4. **Boundary Optional:** The GeoJSON boundary for plots is optional but must follow strict validation rules if provided.
5. **Crop Lifecycle:** New crops start in `PLANNED` lifecycle state by default.
