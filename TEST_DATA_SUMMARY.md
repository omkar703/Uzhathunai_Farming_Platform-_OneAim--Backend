# Test Data Summary - What's Available Now

## ✅ Successfully Created

### 1. FSP User & Organization
- **Email**: `testfsp@aggroconnect.com`
- **Password**: `TestFSP@123`
- **Organization**: Test FSP Services
- **Org ID**: `3353a42a-15e9-4d01-816e-bc4d0b1f8f48`
- **Status**: ACTIVE

### 2. FSP Services (5 Services)
All services are **ACTIVE** and visible in marketplace:

| Service | ID | Price |
|---------|-----|-------|
| Soil Testing | `70d2587a-a571-477a-b898-82c75e8c7fd9` | ₹500 |
| Pest Control | `a8521481-ca79-49b4-9753-125f826f8a9b` | ₹2,000 |
| Crop Advisory | `4dab1549-5d9d-47f9-8241-3b12d1d434de` | ₹1,500 |
| Irrigation Setup | `b5c202d4-e39e-424e-992e-80f8ed9e684a` | ₹15,000 |
| Fertilizer Application | `e2633ebd-5ac9-4b9b-8ab9-197435b7a4ac` | ₹3,000 |

### 3. Work Order
- **ID**: `4cd672bd-dc23-48fb-bcb7-216f3b82679d`
- **Number**: `WO-2026-0001`
- **Status**: **ACCEPTED** ✅
- **Farmer Org**: `fd3f4e7a-b1a0-41f3-8ed3-aca6b6b87843`
- **FSP Org**: `3353a42a-15e9-4d01-816e-bc4d0b1f8f48`
- **Service**: Pest Control (₹2,000)
- **Created**: 2026-01-21
- **Accepted**: 2026-01-21 at 16:38

---

## 🎯 What You Can Test Now

### Farmer Frontend

1. **Marketplace** ✅
   ```
   GET /api/v1/fsp-services/fsp-marketplace/services
   ```
   - Should show all 5 FSP services
   - Can filter by district (Coimbatore, Erode, etc.)

2. **Work Orders List** ✅
   ```
   GET /api/v1/work-orders
   ```
   - Should show WO-2026-0001
   - Status: ACCEPTED
   - FSP details visible

3. **Work Order Details** ✅
   ```
   GET /api/v1/work-orders/4cd672bd-dc23-48fb-bcb7-216f3b82679d
   ```
   - Full work order info
   - Acceptance timestamp
   - FSP organization details

4. **Work Order Scope** ✅
   ```
   GET /api/v1/work-orders/4cd672bd-dc23-48fb-bcb7-216f3b82679d/scope
   ```
   - Currently empty `[]`
   - Farmer can add farms/plots here

---

## ⚠️ Schedules & Audits - Requires Additional Setup

### Why They're Not Created Yet

**Schedules** in this system are tied to **crops**, not work orders directly:
- Schedules require: `crop_id` + `template_id` or manual creation
- Work orders don't automatically create schedules
- FSP would create schedules for specific crops they're working on

**Audits** require:
- Farm access granted via work order scope
- Audit templates
- Specific farm/plot/crop IDs

### How to Enable Schedules & Audits

#### Option 1: Farmer Grants Access (Recommended)
```bash
# Farmer grants FSP access to a farm
POST /api/v1/work-orders/{work_order_id}/scope
{
  "scope_items": [
    {
      "scope": "FARM",
      "scope_id": "<farmer's-farm-id>",
      "access_permissions": {
        "read": true,
        "write": false,
        "track": true
      }
    }
  ]
}
```

#### Option 2: Create Schedules for Crops
```bash
# FSP creates schedule for a crop
POST /api/v1/schedules/from-scratch
{
  "crop_id": "<crop-id>",
  "name": "Pest Control Schedule",
  "description": "Schedule for WO-2026-0001"
}
```

---

## 📊 Current Test Coverage

| Feature | Status | Can Test |
|---------|--------|----------|
| FSP Marketplace | ✅ Working | Yes |
| Service Listings | ✅ Working | Yes |
| Work Order Creation | ✅ Working | Yes |
| Work Order Acceptance | ✅ Working | Yes |
| Work Order Details | ✅ Working | Yes |
| Work Order Scope | ✅ Working | Yes (empty) |
| Schedules | ⚠️ Requires crops | Needs setup |
| Audits | ⚠️ Requires farm access | Needs setup |

---

## 🚀 Quick Test Commands

### View Marketplace (Any User)
```bash
curl -X GET "http://localhost:8000/api/v1/fsp-services/fsp-marketplace/services" \
  -H "Authorization: Bearer <token>"
```

### View Work Orders (Farmer)
```bash
curl -X GET "http://localhost:8000/api/v1/work-orders" \
  -H "Authorization: Bearer <farmer_token>"
```

### View Work Order Details
```bash
curl -X GET "http://localhost:8000/api/v1/work-orders/4cd672bd-dc23-48fb-bcb7-216f3b82679d" \
  -H "Authorization: Bearer <token>"
```

### Complete Work Order (Either Party)
```bash
curl -X POST "http://localhost:8000/api/v1/work-orders/4cd672bd-dc23-48fb-bcb7-216f3b82679d/complete" \
  -H "Authorization: Bearer <token>"
```

---

## 💡 Recommendations

### For Frontend Testing:

1. **Start with Marketplace** ✅
   - All 5 services are visible
   - Test filtering, sorting, search

2. **Test Work Order Flow** ✅
   - Create work order from marketplace
   - View pending work orders
   - See acceptance status change
   - View work order details

3. **Test Scope Management** (Next Step)
   - Farmer grants FSP access to farm
   - FSP views granted resources
   - Test permission levels

4. **Schedules & Audits** (Advanced)
   - Requires crop data
   - Requires farm access
   - More complex setup needed

---

## 📝 Summary

**What's Working:**
- ✅ FSP organization with 5 services
- ✅ Services visible in marketplace
- ✅ Work order created and accepted
- ✅ Audit trail (status changes logged)

**What Needs Setup:**
- ⚠️ Schedules (require crops)
- ⚠️ Audits (require farm access via scope)

**Recommendation:**
Focus on testing the **marketplace → work order → acceptance** flow first. This is fully functional and ready to test!
