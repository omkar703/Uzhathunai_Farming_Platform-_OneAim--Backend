# Project Changelog - Uzhathunai Backend Enhancements

This document summarizes all technical changes, new features, and bug fixes implemented in the repository since the cloning process.

## Summary of New Endpoints

Below is a list of the new API endpoints added to the system:

1.  **`PUT /api/v1/work-orders/{work_order_id}/access`**: Toggles the "Give Access" setting for a work order.
2.  **`POST /api/v1/farm-audit/audits/{audit_id}/evidence`**: Independent upload for audit photos.
3.  **`GET /api/v1/farming-services/providers`**: Retrieves a list of Farm Service Providers a farmer is working with.
4.  **`GET /api/v1/farm-audit/audits/{audit_id}/report`**: (Existing, but heavily updated with standardization and issuing issues/recommendations).

---

## 1. Work Order Access Control ("Give Access" Feature)

### Overview
Implemented a "Master Key" toggle for Work Orders that allows Farmers to explicitly grant or revoke access to their data for specific FSP contracts, overriding granular scope permissions.

### Implementation Details:
- **Database**: Added `access_granted` column (Boolean, default `true`) to the `work_orders` table.
- **Endpoints**: 
    - `PUT /api/v1/work-orders/{work_order_id}/access`: Toggles the access state.
- **Access Control Logic**:
    - Updated `WorkOrderScopeService` to validate `access_granted` before allowing any FSP operations.
    - Modified permission hierarchy to allow FSPs to deploy schedules even with limited scope if `access_granted=True`.
- **Bug Fixes**: 
    - Fixed `start_work_order` permission error reporting.

---

## 2. Schedule Management Enhancements

### Features:
- **Restricted Template Access**: Blocked Farming Organizations from using system/FSP templates (FSP Only feature).
- **Manual Schedule Creation**: 
    - Enhanced `ScheduleFromScratchCreate` schema to support `start_date` and `template_parameters`.
    - Persisted manual configuration into the `Schedule` model.
- **Status Computation**: Implemented logic to correctly set initial statuses (e.g., `NOT_STARTED`) and computed `ACTIVE` states.

### Technical Fixes:
- **Serialization Fix**: Resolved a `PydanticSerializationError` on `GET /api/v1/schedules` by:
    - Creating a new `PaginatedScheduleResponse` schema.
    - Updating the API to use the new schema instead of raw `dict`.
- **Status Enum Compatibility**: Updated `ScheduleResponse` to allow string statuses like "ACTIVE" which are computed at runtime.

---

## 3. Farm Audit & Evidence Upload

### Features:
- **Independent Evidence Upload**: 
    - Added `POST /api/v1/farm-audit/audits/{audit_id}/evidence`.
    - Allows users to upload photos *before* submitting an audit response.
- **Intelligent Linking**: 
    - Updated `ResponseService` to detect pre-uploaded photos via `evidence_urls` array.
    - Automatically links photos to the correct `AuditResponse` upon submission to avoid data duplication.

### Database & Stability Fixes:
- **Schema Alignment**: Altered `audit_response_photos` table to allow `audit_response_id` to be NULL (initially unlinked state).
- **ENUM Synchronization**: Fixed `sqlalchemy.exc.DataError` by adding missing values (`COMPLETED`, `SUBMITTED_TO_FARMER`) to the database `audit_status` ENUM.
- **Response Validation**: Updated `PhotoUploadResponse` schema to make `audit_response_id` optional.
- **Syntax Correction**: Fixed manual syntax errors in `audits.py` and consolidated FSP ID query parameters (`fsp_id` vs `fsp_organization_id`).

---

## 4. Other Improvements

### API Stability:
- **Consolidated Filters**: Added `work_order_id` and normalized `fsp_id` aliases to audit listing endpoints.
- **Progress Tracking**: Added `progress` float field to the `AuditResponse` schema for front-end consumption.
- **Immutability Rules**: Updated `ResponseService` to block modifications to audits in terminal states (SUBMITTED, COMPLETED, etc.).

---

## 5. Summary of Modified Files

- `app/api/v1/farm_audit/audits.py` (Multiple endpoints and filters)
- `app/api/v1/work_orders.py` (Access toggle endpoint)
- `app/api/v1/schedules.py` (Serialization fix)
- `app/services/audit_service.py` (Progress and filters)
- `app/services/photo_service.py` (Evidence upload logic)
- `app/services/response_service.py` (Linking logic and immutability)
- `app/services/work_order_scope_service.py` (Access control enforcement)
- `app/schemas/audit.py` (Progress, evidence, and response schemas)
- `app/schemas/schedule.py` (Pagination and status fixes)
- `app/models/audit.py` (Relationship mapping)
- `app/models/enums.py` (Enum synchronization)



*Documentation compiled on 2026-01-28*