# Work Order Workflow - Complete Process

## Overview
This document outlines the complete work order lifecycle from both Farmer and FSP perspectives.

---

## 📋 Work Order Lifecycle States

```
PENDING → ACCEPTED → IN_PROGRESS → COMPLETED
                  ↓
              CANCELLED (can happen at any stage)
```

---

## 🌾 FARMER PERSPECTIVE

### Phase 1: Service Request (PENDING)
**What Farmer Does:**
1. Browse FSP marketplace
2. Select a service (e.g., "Pest Control - ₹2000/acre")
3. Fill work order form:
   - Service details
   - Farm/plot to service
   - Preferred dates
   - Special instructions
4. Submit work order

**API Call:**
```bash
POST /api/v1/work-orders
```

**What Happens:**
- Work order created with status: `PENDING`
- FSP receives notification
- Farmer waits for FSP acceptance

**Farmer Can:**
- ✅ View work order details
- ✅ Cancel work order
- ✅ Edit work order (before acceptance)
- ❌ Cannot mark as complete yet

---

### Phase 2: FSP Accepted (ACCEPTED)
**What Farmer Sees:**
- Work order status changes to `ACCEPTED`
- Acceptance timestamp displayed
- FSP contact information available

**Farmer Can:**
- ✅ View work order details
- ✅ Grant FSP access to farms/plots/crops (scope)
- ✅ Communicate with FSP
- ✅ Cancel work order (with reason)
- ❌ Cannot edit core details anymore

**API Calls:**
```bash
# Grant FSP access to resources
POST /api/v1/work-orders/{id}/scope
{
  "scope_items": [
    {
      "scope": "FARM",
      "scope_id": "farm-uuid",
      "access_permissions": {
        "read": true,
        "write": false,
        "track": true
      }
    }
  ]
}

# View work order
GET /api/v1/work-orders/{id}
```

---

### Phase 3: Work In Progress (IN_PROGRESS)
**What Farmer Sees:**
- FSP is actively working
- Can track FSP activities (if tracking enabled)
- Can see schedule updates
- Can view audit logs

**Farmer Can:**
- ✅ View real-time updates
- ✅ Monitor FSP access to resources
- ✅ Communicate with FSP
- ✅ View audit trail
- ✅ Cancel if needed (with penalties)

**API Calls:**
```bash
# View audit trail
GET /api/v1/farm-audit/audits?work_order_id={id}

# View schedules
GET /api/v1/schedules?work_order_id={id}
```

---

### Phase 4: Completion (COMPLETED)
**What Farmer Does:**
1. Review work done
2. Verify service quality
3. Confirm completion
4. Make payment
5. Rate FSP service

**API Calls:**
```bash
# Complete work order (can be done by either party)
POST /api/v1/work-orders/{id}/complete

# Rate FSP (future feature)
POST /api/v1/work-orders/{id}/rating
{
  "rating": 5,
  "review": "Excellent service!"
}
```

**What Happens:**
- Work order marked as `COMPLETED`
- FSP access to resources revoked
- Payment processed
- Service appears in history

---

## 🏢 FSP PERSPECTIVE

### Phase 1: New Request (PENDING)
**What FSP Sees:**
- New work order notification
- Farmer details
- Service requested
- Proposed dates and amount

**FSP Can:**
- ✅ View work order details
- ✅ Accept work order
- ✅ Reject/decline work order
- ✅ Request more information

**API Calls:**
```bash
# View pending work orders
GET /api/v1/work-orders?status=PENDING

# Accept work order
POST /api/v1/work-orders/{id}/accept

# Decline (by cancelling)
POST /api/v1/work-orders/{id}/cancel
```

---

### Phase 2: Accepted (ACCEPTED)
**What FSP Does:**
1. Review work order details
2. Plan service execution
3. Create schedule
4. Request access to farmer's resources (if needed)

**FSP Can:**
- ✅ View farmer's granted resources
- ✅ Create schedules
- ✅ Update work order details
- ✅ Communicate with farmer
- ✅ Start work

**API Calls:**
```bash
# Create schedule
POST /api/v1/schedules
{
  "organization_id": "fsp-org-id",
  "work_order_id": "work-order-id",
  "title": "Pest Control - Farm A",
  "start_date": "2026-01-22",
  "end_date": "2026-01-25"
}

# View granted scope
GET /api/v1/work-orders/{id}/scope

# Update work order
PUT /api/v1/work-orders/{id}
{
  "description": "Updated plan: Will use organic pest control"
}
```

---

### Phase 3: Work In Progress (IN_PROGRESS)
**What FSP Does:**
1. Execute service as scheduled
2. Record activities/observations
3. Update progress
4. Log any issues
5. Track resources used

**FSP Can:**
- ✅ Access granted farms/plots/crops
- ✅ Record audit entries
- ✅ Update schedules
- ✅ Add task actuals
- ✅ Upload photos/documents
- ✅ Communicate with farmer

**API Calls:**
```bash
# Record audit entry
POST /api/v1/farm-audit/audits
{
  "farm_id": "farm-id",
  "audit_template_id": "template-id",
  "work_order_id": "work-order-id",
  "audit_date": "2026-01-22",
  "observations": "Pest infestation level: moderate"
}

# Add task actual
POST /api/v1/task-actuals
{
  "schedule_id": "schedule-id",
  "task_id": "task-id",
  "actual_date": "2026-01-22",
  "quantity": 5,
  "notes": "Applied organic pesticide to 5 acres"
}

# Upload photos
POST /api/v1/crop-photos
{
  "crop_id": "crop-id",
  "photo_url": "s3://...",
  "description": "Before treatment"
}
```

---

### Phase 4: Completion (COMPLETED)
**What FSP Does:**
1. Finalize all records
2. Submit completion report
3. Mark work order as complete
4. Request payment

**API Calls:**
```bash
# Complete work order
POST /api/v1/work-orders/{id}/complete

# Submit final report (optional)
PUT /api/v1/work-orders/{id}
{
  "description": "Service completed. Applied organic pest control to 5 acres. Pest levels reduced by 80%. Recommend follow-up in 2 weeks."
}
```

**What Happens:**
- Work order marked as `COMPLETED`
- FSP loses access to farmer's resources
- Payment released
- Service added to FSP portfolio

---

## 🔄 Cancellation Flow

### Farmer Cancels
```bash
POST /api/v1/work-orders/{id}/cancel
```
- Can cancel anytime before completion
- May incur penalties if work already started
- FSP access immediately revoked

### FSP Cancels
```bash
POST /api/v1/work-orders/{id}/cancel
```
- Can decline before acceptance
- Can cancel after acceptance (with reason)
- Affects FSP rating

---

## 📊 Key API Endpoints Summary

### Work Orders
| Action | Method | Endpoint | Who Can Use |
|--------|--------|----------|-------------|
| Create | POST | `/api/v1/work-orders` | Farmer |
| List | GET | `/api/v1/work-orders` | Both |
| View | GET | `/api/v1/work-orders/{id}` | Both |
| Update | PUT | `/api/v1/work-orders/{id}` | Both |
| Accept | POST | `/api/v1/work-orders/{id}/accept` | FSP |
| Complete | POST | `/api/v1/work-orders/{id}/complete` | Both |
| Cancel | POST | `/api/v1/work-orders/{id}/cancel` | Both |

### Scope Management
| Action | Method | Endpoint | Who Can Use |
|--------|--------|----------|-------------|
| View Scope | GET | `/api/v1/work-orders/{id}/scope` | Both |
| Add Scope | POST | `/api/v1/work-orders/{id}/scope` | Farmer |
| Update Permissions | PUT | `/api/v1/work-orders/{id}/scope/{scope_id}` | Farmer |

### Schedules
| Action | Method | Endpoint | Who Can Use |
|--------|--------|----------|-------------|
| Create | POST | `/api/v1/schedules` | FSP |
| List | GET | `/api/v1/schedules?work_order_id={id}` | Both |
| Update | PUT | `/api/v1/schedules/{id}` | FSP |

### Audits
| Action | Method | Endpoint | Who Can Use |
|--------|--------|----------|-------------|
| Create | POST | `/api/v1/farm-audit/audits` | FSP (with access) |
| List | GET | `/api/v1/farm-audit/audits?work_order_id={id}` | Both |
| View | GET | `/api/v1/farm-audit/audits/{id}` | Both |

---

## 🎯 Current Test Status

### ✅ Completed
- Farmer created work order: `WO-2026-0001`
- FSP accepted work order
- Status: `ACCEPTED`
- Audit trail created

### 🔄 Next Steps to Test

#### As FSP:
1. Create a schedule for the work order
2. Record audit entries
3. Add task actuals
4. Complete the work order

#### As Farmer:
1. View accepted work order
2. Grant FSP access to farm/plot
3. Monitor FSP activities
4. View audit trail
5. Complete work order (confirm)

---

## 💡 Testing Commands

### View Work Order (Farmer)
```bash
curl -X GET "http://localhost:8000/api/v1/work-orders/4cd672bd-dc23-48fb-bcb7-216f3b82679d" \
  -H "Authorization: Bearer <farmer_token>"
```

### View Work Order (FSP)
```bash
curl -X GET "http://localhost:8000/api/v1/work-orders/4cd672bd-dc23-48fb-bcb7-216f3b82679d" \
  -H "Authorization: Bearer <fsp_token>"
```

### Complete Work Order (Either Party)
```bash
curl -X POST "http://localhost:8000/api/v1/work-orders/4cd672bd-dc23-48fb-bcb7-216f3b82679d/complete" \
  -H "Authorization: Bearer <token>"
```

---

## 📱 Frontend Display Recommendations

### Farmer Dashboard
- **Pending Requests**: Count of work orders awaiting FSP acceptance
- **Active Work Orders**: Accepted/In-Progress work orders
- **Completed**: Historical work orders
- **Notifications**: FSP acceptance, updates, completion

### FSP Dashboard
- **New Requests**: Pending work orders to accept/decline
- **Active Jobs**: Accepted/In-Progress work orders
- **Schedule**: Calendar view of all work orders
- **Completed**: Service history and ratings

---

## 🔐 Access Control

### Farmer Controls
- Grant/revoke FSP access to specific resources
- Set permission levels (read/write/track)
- View FSP activity logs

### FSP Access
- Only to explicitly granted resources
- Access automatically revoked on completion/cancellation
- All actions logged in audit trail
































































































































Audit Report Implementation Walkthrough
Changes
1. Photo Uploads (FSP App)
File: 
app/fsp/audits/components/AuditFormRenderer.tsx

Added expo-image-picker integration.
Implemented 
handlePickImage
 to select photos from the device library.
Uploads photo immediately to auditService.uploadEvidence and displays a preview.
2. Audit Curation (FSP App)
File: 
app/fsp/audits/[id]/curation.tsx

Standalone Recommendations: Added UI and logic to create recommendations that are not tied to specific issues.
Photo Flagging: Added logic to toggle specific evidence photos for inclusion in the final report.
Issue Recommendations: Added "Recommendation" field to the "Add Issue" modal.
3. Farmer Report View (Farmer App)
File: 
app/farmer/audits/[id]/report.tsx

Implemented the "Finalized Report" view.
Displays:
Executive Summary: Audit details and status.
Issues: Critical and Warning issues with their linked recommendations.
Action Plan: List of standalone recommendations.
Field Observations: Flagged parameter responses and selected evidence photos.
Verification
Automated Checks
Ran tsc to verify type safety (waiting for results).
Manual Verification Steps
FSP: Open an audit, upload a photo for a "PHOTO" parameter. Verify preview appears.
FSP: Go to "Review & Curate". Flag a parameter. Toggle a photo. Add a standalone recommendation.
FSP: Finalize the report.
Farmer: Open the audit in "Audit Center". Verify the new Report View is shown and contains the curated data.

Comment
Ctrl+Alt+M





















