-- Uzhathunai Database Schema Changes - Audit Module V2.0
-- Version: 2.0
-- Description: Schema modifications for Farm Audit Management System
-- Requirements: 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7

-- ============================================
-- ENUM TYPE ADDITIONS
-- ============================================

-- Create issue_severity ENUM type (Requirement 22.1)
CREATE TYPE issue_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

COMMENT ON TYPE issue_severity IS 'Severity levels for audit issues: LOW, MEDIUM, HIGH, CRITICAL';

-- Create sync_status ENUM type (Requirement 22.2)
CREATE TYPE sync_status AS ENUM ('pending_sync', 'synced', 'sync_failed');

COMMENT ON TYPE sync_status IS 'Sync status for offline audit operations: pending_sync (queued), synced (completed), sync_failed (error)';

-- ============================================
-- TABLE MODIFICATIONS
-- ============================================

-- Modify audit_issues table to use issue_severity ENUM (Requirement 22.2)
ALTER TABLE audit_issues 
ALTER COLUMN severity TYPE issue_severity 
USING severity::issue_severity;

COMMENT ON COLUMN audit_issues.severity IS 'Issue severity level using issue_severity ENUM: LOW, MEDIUM, HIGH, CRITICAL';

-- Add sync_status column to audits table (Requirement 22.3)
ALTER TABLE audits 
ADD COLUMN sync_status sync_status DEFAULT 'synced';

COMMENT ON COLUMN audits.sync_status IS 'Sync status for offline operations: pending_sync (queued for sync), synced (successfully synced), sync_failed (sync error occurred)';

-- Make work_order_id nullable in audits table (Requirement 22.4)
ALTER TABLE audits 
ALTER COLUMN work_order_id DROP NOT NULL;

COMMENT ON COLUMN audits.work_order_id IS 'Optional work order association - audits can be created independently of work orders';

-- ============================================
-- PERFORMANCE INDEXES (Requirement 22.6)
-- ============================================

-- Audit module performance indexes
CREATE INDEX idx_audits_sync_status ON audits(sync_status);
CREATE INDEX idx_audits_farming_org_status ON audits(farming_organization_id, status);
CREATE INDEX idx_audits_fsp_org_status ON audits(fsp_organization_id, status);
CREATE INDEX idx_audits_crop_status ON audits(crop_id, status);
CREATE INDEX idx_audits_finalized_at ON audits(finalized_at) WHERE finalized_at IS NOT NULL;
CREATE INDEX idx_audits_shared_at ON audits(shared_at) WHERE shared_at IS NOT NULL;

-- Audit response indexes
CREATE INDEX idx_audit_responses_created_by ON audit_responses(created_by);
CREATE INDEX idx_audit_responses_created_at ON audit_responses(created_at);

-- Audit review indexes
CREATE INDEX idx_audit_reviews_reviewed_at ON audit_reviews(reviewed_at);
CREATE INDEX idx_audit_reviews_flagged ON audit_reviews(is_flagged_for_report) WHERE is_flagged_for_report = true;

-- Audit issue indexes
CREATE INDEX idx_audit_issues_severity ON audit_issues(severity);
CREATE INDEX idx_audit_issues_created_at ON audit_issues(created_at);

-- Template management indexes
-- CREATE INDEX idx_template_sections_template ON template_sections(template_id);
CREATE INDEX idx_template_sections_sort ON template_sections(template_id, sort_order);
CREATE INDEX idx_template_parameters_section ON template_parameters(template_section_id);
CREATE INDEX idx_template_parameters_sort ON template_parameters(template_section_id, sort_order);
CREATE INDEX idx_parameter_option_set_map_param ON parameter_option_set_map(parameter_id);
CREATE INDEX idx_parameter_option_set_map_option_set ON parameter_option_set_map(option_set_id);

-- Option set indexes
CREATE INDEX idx_options_option_set ON options(option_set_id);
CREATE INDEX idx_options_sort ON options(option_set_id, sort_order);
-- CREATE INDEX idx_option_sets_owner ON option_sets(owner_org_id) WHERE owner_org_id IS NOT NULL;
-- CREATE INDEX idx_option_sets_system ON option_sets(is_system_defined) WHERE is_system_defined = true;

-- Parameter indexes
-- CREATE INDEX idx_parameters_owner ON parameters(owner_org_id) WHERE owner_org_id IS NOT NULL;
-- CREATE INDEX idx_parameters_system ON parameters(is_system_defined) WHERE is_system_defined = true;
-- CREATE INDEX idx_parameters_type ON parameters(parameter_type);

-- Section indexes
-- CREATE INDEX idx_sections_owner ON sections(owner_org_id) WHERE owner_org_id IS NOT NULL;
-- CREATE INDEX idx_sections_system ON sections(is_system_defined) WHERE is_system_defined = true;

-- Template indexes
-- CREATE INDEX idx_templates_owner ON templates(owner_org_id) WHERE owner_org_id IS NOT NULL;
-- CREATE INDEX idx_templates_system ON templates(is_system_defined) WHERE is_system_defined = true;
-- CREATE INDEX idx_templates_crop_type ON templates(crop_type_id) WHERE crop_type_id IS NOT NULL;

-- Schedule change log indexes for audit recommendations
CREATE INDEX idx_schedule_change_log_trigger_audit ON schedule_change_log(trigger_type, trigger_reference_id) WHERE trigger_type = 'AUDIT';
CREATE INDEX idx_schedule_change_log_is_applied ON schedule_change_log(is_applied) WHERE is_applied = false;

-- ============================================
-- DOCUMENTATION UPDATES (Requirement 22.5)
-- ============================================

-- Update parameter_metadata documentation to include photo requirements
COMMENT ON COLUMN parameters.parameter_metadata IS 'JSONB: {"min_value": 0, "max_value": 100, "unit": "cm", "decimal_places": 2, "min_photos": 0, "max_photos": 3, "validation_rules": {"required": true, "range": [0, 100]}, "display_format": "0.00", "help_text": "Measure from soil level", "additional": {...}}';

-- ============================================
-- VALIDATION CONSTRAINTS
-- ============================================

-- Add check constraint for sync_status transitions
ALTER TABLE audits
ADD CONSTRAINT chk_audits_sync_status_valid 
CHECK (sync_status IN ('pending_sync', 'synced', 'sync_failed'));

-- Add check constraint for issue severity
ALTER TABLE audit_issues
ADD CONSTRAINT chk_audit_issues_severity_valid
CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'));

-- ============================================
-- SUMMARY
-- ============================================

-- This migration adds:
-- 1. issue_severity ENUM type with values: LOW, MEDIUM, HIGH, CRITICAL
-- 2. sync_status ENUM type with values: pending_sync, synced, sync_failed
-- 3. Modified audit_issues.severity to use issue_severity ENUM
-- 4. Added sync_status column to audits table (default: 'synced')
-- 5. Made audits.work_order_id nullable for independent audit creation
-- 6. Added comprehensive performance indexes for audit operations
-- 7. Updated documentation for parameter_metadata to include photo requirements
-- 8. Added validation constraints for data integrity

-- Requirements covered:
-- 22.1: issue_severity ENUM type created
-- 22.2: audit_issues.severity modified to use ENUM
-- 22.3: sync_status column added to audits table
-- 22.4: work_order_id made nullable in audits table
-- 22.5: min_photos and max_photos documented in parameter_metadata
-- 22.6: Performance indexes created for frequently queried columns
-- 22.7: All schema changes documented in this script
