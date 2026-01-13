# Audit Module Database Scripts

This directory contains the database schema changes and seed data for the Farm Audit Management System.

## Files

### 003_audit_module_changes.sql
**Purpose:** Schema modifications for the audit module

**Changes:**
1. **New ENUM Types:**
   - `issue_severity`: LOW, MEDIUM, HIGH, CRITICAL
   - `sync_status`: pending_sync, synced, sync_failed

2. **Table Modifications:**
   - Modified `audit_issues.severity` to use `issue_severity` ENUM
   - Added `sync_status` column to `audits` table (default: 'synced')
   - Made `audits.work_order_id` nullable for independent audit creation

3. **Performance Indexes:**
   - Comprehensive indexes for audit operations
   - Indexes for template management
   - Indexes for option sets and parameters
   - Indexes for schedule change log (audit recommendations)

4. **Documentation:**
   - Updated `parameter_metadata` documentation to include photo requirements (min_photos, max_photos)

**Requirements Covered:** 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7

### a02_audit_RBAC_Seed_Data.sql
**Purpose:** Permissions and role mappings for audit operations

**Permissions Created:**
1. **Audit Template Management** (18.1)
   - AUDIT_TEMPLATE_MANAGE, CREATE, READ, UPDATE, DELETE, COPY

2. **Audit Creation** (18.2)
   - AUDIT_CREATE

3. **Audit Response** (18.3)
   - AUDIT_RESPONSE, RESPONSE_CREATE, RESPONSE_UPDATE, PHOTO_UPLOAD

4. **Audit Review** (18.4)
   - AUDIT_REVIEW, REVIEW_CREATE, REVIEW_UPDATE, ISSUE_CREATE, RECOMMENDATION_CREATE

5. **Audit Finalization** (18.5)
   - AUDIT_FINALIZE

6. **Audit Sharing** (18.6)
   - AUDIT_SHARE

7. **Recommendation Approval** (18.7)
   - AUDIT_RECOMMENDATION_APPROVE

**Role Mappings:**

| Role | Permissions |
|------|-------------|
| SUPER_ADMIN | Full access to all audit operations |
| FSP_OWNER | Full FSP audit operations including template management |
| FSP_ADMIN | Full FSP audit operations including template management |
| FSP_MANAGER | Audit operations without template management |
| SENIOR_CONSULTANT | Full audit operations with template copy |
| CONSULTANT | Audit operations without finalization |
| TECHNICAL_ANALYST | Audit response and basic operations |
| FSP_SUPERVISOR | Field audit operations (create, respond, photo upload) |
| OWNER (Farming) | Recommendation approval and read access |
| ADMIN (Farming) | Recommendation approval and read access |
| MANAGER (Farming) | Read access and report generation |
| SUPERVISOR (Farming) | Read access only |
| WORKER (Farming) | Read access only |

**Requirements Covered:** 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7

## Execution Order

1. **First:** Run `003_audit_module_changes.sql` to modify the schema
2. **Second:** Run `a02_audit_RBAC_Seed_Data.sql` to add permissions and role mappings

## Rollback

If you need to rollback these changes:

```sql
-- Rollback 003_audit_module_changes.sql
DROP INDEX IF EXISTS idx_audits_sync_status;
DROP INDEX IF EXISTS idx_audits_farming_org_status;
DROP INDEX IF EXISTS idx_audits_fsp_org_status;
DROP INDEX IF EXISTS idx_audits_crop_status;
DROP INDEX IF EXISTS idx_audits_finalized_at;
DROP INDEX IF EXISTS idx_audits_shared_at;
DROP INDEX IF EXISTS idx_audit_responses_created_by;
DROP INDEX IF EXISTS idx_audit_responses_created_at;
DROP INDEX IF EXISTS idx_audit_reviews_reviewed_at;
DROP INDEX IF EXISTS idx_audit_reviews_flagged;
DROP INDEX IF EXISTS idx_audit_issues_severity;
DROP INDEX IF EXISTS idx_audit_issues_created_at;
DROP INDEX IF EXISTS idx_template_sections_template;
DROP INDEX IF EXISTS idx_template_sections_sort;
DROP INDEX IF EXISTS idx_template_parameters_section;
DROP INDEX IF EXISTS idx_template_parameters_sort;
DROP INDEX IF EXISTS idx_parameter_option_set_map_param;
DROP INDEX IF EXISTS idx_parameter_option_set_map_option_set;
DROP INDEX IF EXISTS idx_options_option_set;
DROP INDEX IF EXISTS idx_options_sort;
DROP INDEX IF EXISTS idx_option_sets_owner;
DROP INDEX IF EXISTS idx_option_sets_system;
DROP INDEX IF EXISTS idx_parameters_owner;
DROP INDEX IF EXISTS idx_parameters_system;
DROP INDEX IF EXISTS idx_parameters_type;
DROP INDEX IF EXISTS idx_sections_owner;
DROP INDEX IF EXISTS idx_sections_system;
DROP INDEX IF EXISTS idx_templates_owner;
DROP INDEX IF EXISTS idx_templates_system;
DROP INDEX IF EXISTS idx_templates_crop_type;
DROP INDEX IF EXISTS idx_schedule_change_log_trigger_audit;
DROP INDEX IF EXISTS idx_schedule_change_log_is_applied;

ALTER TABLE audits DROP CONSTRAINT IF EXISTS chk_audits_sync_status_valid;
ALTER TABLE audit_issues DROP CONSTRAINT IF EXISTS chk_audit_issues_severity_valid;

ALTER TABLE audits DROP COLUMN IF EXISTS sync_status;
ALTER TABLE audits ALTER COLUMN work_order_id SET NOT NULL;
ALTER TABLE audit_issues ALTER COLUMN severity TYPE VARCHAR(20);

DROP TYPE IF EXISTS sync_status;
DROP TYPE IF EXISTS issue_severity;

-- Rollback a02_audit_RBAC_Seed_Data.sql
DELETE FROM role_permissions WHERE permission_id IN (
    SELECT id FROM permissions WHERE code LIKE 'AUDIT_%'
);

DELETE FROM permissions WHERE code LIKE 'AUDIT_%';
```

## Validation

After running the scripts, validate the changes:

```sql
-- Check ENUM types
SELECT typname, enumlabel 
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid 
WHERE typname IN ('issue_severity', 'sync_status')
ORDER BY typname, enumsortorder;

-- Check audits table modifications
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'audits' 
AND column_name IN ('sync_status', 'work_order_id');

-- Check audit_issues severity column
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'audit_issues' 
AND column_name = 'severity';

-- Check indexes
SELECT indexname, tablename
FROM pg_indexes
WHERE tablename IN ('audits', 'audit_responses', 'audit_reviews', 'audit_issues', 
                    'templates', 'template_sections', 'template_parameters',
                    'parameters', 'sections', 'option_sets', 'options')
ORDER BY tablename, indexname;

-- Check permissions
SELECT code, name, resource, action
FROM permissions
WHERE code LIKE 'AUDIT_%'
ORDER BY code;

-- Check role permissions
SELECT r.code as role_code, p.code as permission_code, rp.effect
FROM role_permissions rp
JOIN roles r ON rp.role_id = r.id
JOIN permissions p ON rp.permission_id = p.id
WHERE p.code LIKE 'AUDIT_%'
ORDER BY r.code, p.code;
```

## Notes

- All changes are backward compatible with existing data
- The `sync_status` column defaults to 'synced' for existing audits
- The `work_order_id` can now be NULL, allowing audits to be created independently
- Performance indexes are optimized for common query patterns
- RBAC permissions follow the principle of least privilege
- System admins have full access, FSP roles have operational access, Farming org roles have read/approval access
