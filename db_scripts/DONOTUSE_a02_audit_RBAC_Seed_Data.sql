-- Uzhathunai Database Initial Data - Audit Module RBAC
-- Version: 2.0
-- Description: Permissions and role mappings for Farm Audit Management System
-- Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7

-- ============================================
-- AUDIT MODULE PERMISSIONS
-- ============================================

-- Insert audit-specific permissions
INSERT INTO permissions (code, name, resource, action, description) VALUES
-- Audit Template Management (Requirement 18.1)
('AUDIT_TEMPLATE_MANAGE', 'audit.template.manage', 'audit_template', 'manage', 'Manage audit templates, sections, parameters, and option sets'),
('AUDIT_TEMPLATE_CREATE', 'audit.template.create', 'audit_template', 'create', 'Create audit templates'),
('AUDIT_TEMPLATE_READ', 'audit.template.read', 'audit_template', 'read', 'View audit templates'),
('AUDIT_TEMPLATE_UPDATE', 'audit.template.update', 'audit_template', 'update', 'Update audit templates'),
('AUDIT_TEMPLATE_DELETE', 'audit.template.delete', 'audit_template', 'delete', 'Delete audit templates'),
('AUDIT_TEMPLATE_COPY', 'audit.template.copy', 'audit_template', 'copy', 'Copy audit templates'),

-- Audit Creation (Requirement 18.2)
('AUDIT_CREATE', 'audit.create', 'audit', 'create', 'Create new audits from templates'),

-- Audit Response Submission (Requirement 18.3)
('AUDIT_RESPONSE', 'audit.response', 'audit', 'response', 'Submit audit responses and upload photos'),
('AUDIT_RESPONSE_CREATE', 'audit.response.create', 'audit', 'response_create', 'Create audit responses'),
('AUDIT_RESPONSE_UPDATE', 'audit.response.update', 'audit', 'response_update', 'Update audit responses'),
('AUDIT_PHOTO_UPLOAD', 'audit.photo.upload', 'audit', 'photo_upload', 'Upload photos to audit responses'),

-- Audit Review Operations (Requirement 18.4)
('AUDIT_REVIEW', 'audit.review', 'audit', 'review', 'Review audits and modify responses'),
('AUDIT_REVIEW_CREATE', 'audit.review.create', 'audit', 'review_create', 'Create audit reviews'),
('AUDIT_REVIEW_UPDATE', 'audit.review.update', 'audit', 'review_update', 'Update audit reviews'),
('AUDIT_ISSUE_CREATE', 'audit.issue.create', 'audit', 'issue_create', 'Create audit issues'),
('AUDIT_RECOMMENDATION_CREATE', 'audit.recommendation.create', 'audit', 'recommendation_create', 'Create audit recommendations'),

-- Audit Finalization (Requirement 18.5)
('AUDIT_FINALIZE', 'audit.finalize', 'audit', 'finalize', 'Finalize audits and lock data'),

-- Audit Sharing (Requirement 18.6)
('AUDIT_SHARE', 'audit.share', 'audit', 'share', 'Share finalized audits with farming organizations'),

-- Audit Recommendation Approval (Requirement 18.7)
('AUDIT_RECOMMENDATION_APPROVE', 'audit.recommendation.approve', 'audit', 'recommendation_approve', 'Approve or reject audit recommendations'),

-- Audit Read Access
('AUDIT_READ', 'audit.read', 'audit', 'read', 'View audit details and reports'),
('AUDIT_REPORT_GENERATE', 'audit.report.generate', 'audit', 'report_generate', 'Generate audit reports');

-- ============================================
-- ROLE PERMISSION MAPPINGS
-- ============================================

-- System Admin (SUPER_ADMIN) - Full access to all audit operations
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'SUPER_ADMIN'
AND p.code IN (
    'AUDIT_TEMPLATE_MANAGE',
    'AUDIT_TEMPLATE_CREATE',
    'AUDIT_TEMPLATE_READ',
    'AUDIT_TEMPLATE_UPDATE',
    'AUDIT_TEMPLATE_DELETE',
    'AUDIT_TEMPLATE_COPY',
    'AUDIT_CREATE',
    'AUDIT_RESPONSE',
    'AUDIT_RESPONSE_CREATE',
    'AUDIT_RESPONSE_UPDATE',
    'AUDIT_PHOTO_UPLOAD',
    'AUDIT_REVIEW',
    'AUDIT_REVIEW_CREATE',
    'AUDIT_REVIEW_UPDATE',
    'AUDIT_ISSUE_CREATE',
    'AUDIT_RECOMMENDATION_CREATE',
    'AUDIT_FINALIZE',
    'AUDIT_SHARE',
    'AUDIT_RECOMMENDATION_APPROVE',
    'AUDIT_READ',
    'AUDIT_REPORT_GENERATE'
);

-- FSP Owner (FSP_OWNER) - Full FSP audit operations
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'FSP_OWNER'
AND p.code IN (
    'AUDIT_TEMPLATE_MANAGE',
    'AUDIT_TEMPLATE_CREATE',
    'AUDIT_TEMPLATE_READ',
    'AUDIT_TEMPLATE_UPDATE',
    'AUDIT_TEMPLATE_DELETE',
    'AUDIT_TEMPLATE_COPY',
    'AUDIT_CREATE',
    'AUDIT_RESPONSE',
    'AUDIT_RESPONSE_CREATE',
    'AUDIT_RESPONSE_UPDATE',
    'AUDIT_PHOTO_UPLOAD',
    'AUDIT_REVIEW',
    'AUDIT_REVIEW_CREATE',
    'AUDIT_REVIEW_UPDATE',
    'AUDIT_ISSUE_CREATE',
    'AUDIT_RECOMMENDATION_CREATE',
    'AUDIT_FINALIZE',
    'AUDIT_SHARE',
    'AUDIT_READ',
    'AUDIT_REPORT_GENERATE'
);

-- FSP Admin (FSP_ADMIN) - Full FSP audit operations
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'FSP_ADMIN'
AND p.code IN (
    'AUDIT_TEMPLATE_MANAGE',
    'AUDIT_TEMPLATE_CREATE',
    'AUDIT_TEMPLATE_READ',
    'AUDIT_TEMPLATE_UPDATE',
    'AUDIT_TEMPLATE_DELETE',
    'AUDIT_TEMPLATE_COPY',
    'AUDIT_CREATE',
    'AUDIT_RESPONSE',
    'AUDIT_RESPONSE_CREATE',
    'AUDIT_RESPONSE_UPDATE',
    'AUDIT_PHOTO_UPLOAD',
    'AUDIT_REVIEW',
    'AUDIT_REVIEW_CREATE',
    'AUDIT_REVIEW_UPDATE',
    'AUDIT_ISSUE_CREATE',
    'AUDIT_RECOMMENDATION_CREATE',
    'AUDIT_FINALIZE',
    'AUDIT_SHARE',
    'AUDIT_READ',
    'AUDIT_REPORT_GENERATE'
);

-- FSP Manager (FSP_MANAGER) - Audit operations without template management
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'FSP_MANAGER'
AND p.code IN (
    'AUDIT_TEMPLATE_READ',
    'AUDIT_CREATE',
    'AUDIT_RESPONSE',
    'AUDIT_RESPONSE_CREATE',
    'AUDIT_RESPONSE_UPDATE',
    'AUDIT_PHOTO_UPLOAD',
    'AUDIT_REVIEW',
    'AUDIT_REVIEW_CREATE',
    'AUDIT_REVIEW_UPDATE',
    'AUDIT_ISSUE_CREATE',
    'AUDIT_RECOMMENDATION_CREATE',
    'AUDIT_FINALIZE',
    'AUDIT_SHARE',
    'AUDIT_READ',
    'AUDIT_REPORT_GENERATE'
);

-- Senior Consultant (SENIOR_CONSULTANT) - Full audit operations with consultancy service
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'SENIOR_CONSULTANT'
AND p.code IN (
    'AUDIT_TEMPLATE_READ',
    'AUDIT_TEMPLATE_COPY',
    'AUDIT_CREATE',
    'AUDIT_RESPONSE',
    'AUDIT_RESPONSE_CREATE',
    'AUDIT_RESPONSE_UPDATE',
    'AUDIT_PHOTO_UPLOAD',
    'AUDIT_REVIEW',
    'AUDIT_REVIEW_CREATE',
    'AUDIT_REVIEW_UPDATE',
    'AUDIT_ISSUE_CREATE',
    'AUDIT_RECOMMENDATION_CREATE',
    'AUDIT_FINALIZE',
    'AUDIT_SHARE',
    'AUDIT_READ',
    'AUDIT_REPORT_GENERATE'
);

-- Consultant (CONSULTANT) - Audit operations without finalization
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'CONSULTANT'
AND p.code IN (
    'AUDIT_TEMPLATE_READ',
    'AUDIT_CREATE',
    'AUDIT_RESPONSE',
    'AUDIT_RESPONSE_CREATE',
    'AUDIT_RESPONSE_UPDATE',
    'AUDIT_PHOTO_UPLOAD',
    'AUDIT_REVIEW',
    'AUDIT_REVIEW_CREATE',
    'AUDIT_REVIEW_UPDATE',
    'AUDIT_ISSUE_CREATE',
    'AUDIT_RECOMMENDATION_CREATE',
    'AUDIT_READ',
    'AUDIT_REPORT_GENERATE'
);

-- Technical Analyst (TECHNICAL_ANALYST) - Audit response and review
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'TECHNICAL_ANALYST'
AND p.code IN (
    'AUDIT_TEMPLATE_READ',
    'AUDIT_CREATE',
    'AUDIT_RESPONSE',
    'AUDIT_RESPONSE_CREATE',
    'AUDIT_RESPONSE_UPDATE',
    'AUDIT_PHOTO_UPLOAD',
    'AUDIT_READ'
);

-- FSP Supervisor (FSP_SUPERVISOR) - Field audit operations
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'FSP_SUPERVISOR'
AND p.code IN (
    'AUDIT_TEMPLATE_READ',
    'AUDIT_CREATE',
    'AUDIT_RESPONSE',
    'AUDIT_RESPONSE_CREATE',
    'AUDIT_RESPONSE_UPDATE',
    'AUDIT_PHOTO_UPLOAD',
    'AUDIT_READ'
);

-- Farming Organization Owner (OWNER) - Recommendation approval and read access
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'OWNER'
AND p.code IN (
    'AUDIT_RECOMMENDATION_APPROVE',
    'AUDIT_READ',
    'AUDIT_REPORT_GENERATE'
);

-- Farming Organization Admin (ADMIN) - Recommendation approval and read access
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'ADMIN'
AND p.code IN (
    'AUDIT_RECOMMENDATION_APPROVE',
    'AUDIT_READ',
    'AUDIT_REPORT_GENERATE'
);

-- Farming Organization Manager (MANAGER) - Read access only
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'MANAGER'
AND p.code IN (
    'AUDIT_READ',
    'AUDIT_REPORT_GENERATE'
);

-- Farming Organization Supervisor (SUPERVISOR) - Read access only
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'SUPERVISOR'
AND p.code IN (
    'AUDIT_READ'
);

-- Farming Organization Worker (WORKER) - Read access only
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'WORKER'
AND p.code IN (
    'AUDIT_READ'
);

-- ============================================
-- SUMMARY
-- ============================================

-- This script creates:
-- 1. Audit Template Management permissions (Requirement 18.1)
-- 2. Audit Create permissions (Requirement 18.2)
-- 3. Audit Response permissions (Requirement 18.3)
-- 4. Audit Review permissions (Requirement 18.4)
-- 5. Audit Finalize permissions (Requirement 18.5)
-- 6. Audit Share permissions (Requirement 18.6)
-- 7. Audit Recommendation Approve permissions (Requirement 18.7)
-- 8. Role-permission mappings for all relevant roles

-- Permission Summary by Role:
-- 
-- System Admin (SUPER_ADMIN):
--   - Full access to all audit operations
--
-- FSP Roles:
--   FSP_OWNER, FSP_ADMIN: Full audit operations including template management
--   FSP_MANAGER: Audit operations without template management
--   SENIOR_CONSULTANT: Full audit operations with template copy
--   CONSULTANT: Audit operations without finalization
--   TECHNICAL_ANALYST: Audit response and basic operations
--   FSP_SUPERVISOR: Field audit operations (create, respond, photo upload)
--
-- Farming Organization Roles:
--   OWNER, ADMIN: Recommendation approval and read access
--   MANAGER: Read access and report generation
--   SUPERVISOR, WORKER: Read access only
--
-- Requirements covered:
-- 18.1: Audit Template Management permission created and mapped
-- 18.2: Audit Create permission created and mapped
-- 18.3: Audit Response permission created and mapped
-- 18.4: Audit Review permission created and mapped
-- 18.5: Audit Finalize permission created and mapped
-- 18.6: Audit Share permission created and mapped
-- 18.7: Audit Recommendation Approve permission created and mapped
