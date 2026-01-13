-- Insert additional permissions there were missed earlier
INSERT INTO permissions (code, name, resource, action, description) VALUES
-- Audit Template Management (Requirement 18.1)
('AUDIT_TEMPLATE_CREATE', 'audit.template.create', 'audit_template', 'create', 'Create audit templates'),
('AUDIT_TEMPLATE_READ', 'audit.template.read', 'audit_template', 'read', 'View audit templates'),
('AUDIT_TEMPLATE_UPDATE', 'audit.template.update', 'audit_template', 'update', 'Update audit templates'),
('AUDIT_TEMPLATE_DELETE', 'audit.template.delete', 'audit_template', 'delete', 'Delete audit templates'),
('AUDIT_TEMPLATE_COPY', 'audit.template.copy', 'audit_template', 'copy', 'Copy audit templates'),

-- Audit Response Submission (Requirement 18.3)
('AUDIT_RESPONSE', 'audit.response', 'audit', 'response', 'Submit audit responses and upload photos'),

-- Audit Finalization (Requirement 18.5)
('AUDIT_FINALIZE', 'audit.finalize', 'audit', 'finalize', 'Finalize audits and lock data'),

-- Audit Recommendation Approval (Requirement 18.7)
('AUDIT_RECOMMENDATION_APPROVE', 'audit.recommendation.approve', 'audit', 'recommendation_approve', 'Approve or reject audit recommendations. For farmers'),

-- AK: Query Recommendation Approval
('QUERY_RECOMMENDATION_APPROVE', 'query.recommendation.approve', 'query', 'recommendation_approve', 'Approve or reject query recommendations. For farmers'),

-- Audit Read Access (explicitly added permission for report generation)
('AUDIT_REPORT_GENERATE', 'audit.report.generate', 'audit', 'report_generate', 'Generate audit reports'),

-- AK: Schedule Template Management
('SCHEDULE_TEMPLATE_CREATE', 'schedule.template.create', 'schedule_template', 'create', 'Create schedule templates'),
('SCHEDULE_TEMPLATE_READ', 'schedule.template.read', 'schedule_template', 'read', 'View schedule templates'),
('SCHEDULE_TEMPLATE_UPDATE', 'schedule.template.update', 'schedule_template', 'update', 'Update schedule templates'),
('SCHEDULE_TEMPLATE_DELETE', 'schedule.template.delete', 'schedule_template', 'delete', 'Delete schedule templates'),
('SCHEDULE_TEMPLATE_COPY', 'schedule.template.copy', 'schedule_template', 'copy', 'Copy schedule templates'),

-- AK: System permissions
('SYSTEM_MANAGE', 'system.manage', 'system', 'manage', 'Full access to the system'),

-- AK: FSP Services Management
('FSP_SERVICE_MANAGE', 'fsp_service.manage', 'fsp_service', 'manage', 'Manage FSP services which includes CRUD and all other permissions too');


-- SUPERADMIN Full Access
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'SUPER_ADMIN'
AND p.code NOT IN (
    'ORGANIZATION_INVITEMEMBERS',
    'ORGANIZATION_MANAGELISTINGS',
    'ORGANIZATION_REMOVEMEMBERS');

-- OWNER Access (Farming organization)
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'OWNER'
AND p.code IN (
    'AUDIT_READ',
    'AUDIT_RECOMMENDATION_APPROVE',
    'AUDIT_REPORT_GENERATE',
    'CROP_CREATE',
    'CROP_DELETE',
    'CROP_READ',
    'CROP_UPDATE',
    'FARM_CREATE',
    'FARM_DELETE',
    'FARM_READ',
    'FARM_UPDATE',
    'ORGANIZATION_DELETE',
    'ORGANIZATION_UPDATE',
    'PLOT_CREATE',
    'PLOT_DELETE',
    'PLOT_READ',
    'PLOT_UPDATE',
    'QUERY_CREATE',
    'QUERY_READ',
    'QUERY_RECOMMENDATION_APPROVE',
    'SCHEDULE_CREATE',
    'SCHEDULE_DELETE',
    'SCHEDULE_READ',
    'SCHEDULE_UPDATE',
    'SCHEDULE_TEMPLATE_COPY',
    'SCHEDULE_TEMPLATE_CREATE',
    'SCHEDULE_TEMPLATE_DELETE',
    'SCHEDULE_TEMPLATE_READ',
    'SCHEDULE_TEMPLATE_UPDATE',
    'USER_INVITE',
    'USER_MANAGE');

-- Manager Access (Farming Organization)
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'MANAGER'
AND p.code IN (
    'AUDIT_READ',
    'AUDIT_RECOMMENDATION_APPROVE',
    'AUDIT_REPORT_GENERATE',
    'CROP_CREATE',
    'CROP_READ',
    'CROP_UPDATE',
    'FARM_READ',
    'FARM_UPDATE',
    'PLOT_READ',
    'PLOT_UPDATE',
    'QUERY_CREATE',
    'QUERY_READ',
    'QUERY_RECOMMENDATION_APPROVE',
    'SCHEDULE_CREATE',
    'SCHEDULE_DELETE',
    'SCHEDULE_READ',
    'SCHEDULE_UPDATE',
    'SCHEDULE_TEMPLATE_COPY',
    'SCHEDULE_TEMPLATE_CREATE',
    'SCHEDULE_TEMPLATE_DELETE',
    'SCHEDULE_TEMPLATE_READ',
    'SCHEDULE_TEMPLATE_UPDATE');

-- FSP Owner Access
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'FSP_OWNER'
AND p.code IN (
    'AUDIT_CREATE',
    'AUDIT_FINALIZE',
    'AUDIT_REPORT_GENERATE',
    'AUDIT_RESPONSE',
    'AUDIT_REVIEW',
    'AUDIT_SHARE',
    'AUDIT_UPDATE',
    'AUDIT_TEMPLATE_COPY',
    'AUDIT_TEMPLATE_CREATE',
    'AUDIT_TEMPLATE_DELETE',
    'AUDIT_TEMPLATE_READ',
    'AUDIT_TEMPLATE_UPDATE',
    'CROP_READ',
    'CROP_UPDATE',
    'FARM_READ',
    'FSP_SERVICE_MANAGE',
    'ORGANIZATION_DELETE',
    'ORGANIZATION_UPDATE',
    'PLOT_READ',
    'QUERY_READ',
    'QUERY_RESPOND',
    'SCHEDULE_CREATE',
    'SCHEDULE_DELETE',
    'SCHEDULE_READ',
    'SCHEDULE_UPDATE',
    'SCHEDULE_TEMPLATE_COPY',
    'SCHEDULE_TEMPLATE_CREATE',
    'SCHEDULE_TEMPLATE_DELETE',
    'SCHEDULE_TEMPLATE_READ',
    'SCHEDULE_TEMPLATE_UPDATE',
    'USER_INVITE',
    'USER_MANAGE');

-- FSP Manager Access
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'FSP_MANAGER'
AND p.code IN (
    'AUDIT_CREATE',
    'AUDIT_FINALIZE',
    'AUDIT_REPORT_GENERATE',
    'AUDIT_RESPONSE',
    'AUDIT_REVIEW',
    'AUDIT_SHARE',
    'AUDIT_UPDATE',
    'AUDIT_TEMPLATE_COPY',
    'AUDIT_TEMPLATE_CREATE',
    'AUDIT_TEMPLATE_DELETE',
    'AUDIT_TEMPLATE_READ',
    'AUDIT_TEMPLATE_UPDATE',
    'CROP_READ',
    'CROP_UPDATE',
    'FARM_READ',
    'FSP_SERVICE_MANAGE',
    'PLOT_READ',
    'QUERY_READ',
    'QUERY_RESPOND',
    'SCHEDULE_CREATE',
    'SCHEDULE_DELETE',
    'SCHEDULE_READ',
    'SCHEDULE_UPDATE',
    'SCHEDULE_TEMPLATE_COPY',
    'SCHEDULE_TEMPLATE_CREATE',
    'SCHEDULE_TEMPLATE_DELETE',
    'SCHEDULE_TEMPLATE_READ',
    'SCHEDULE_TEMPLATE_UPDATE');

-- FSP Senior Consultant Access
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'SENIOR_CONSULTANT'
AND p.code IN (
    'AUDIT_CREATE',
    'AUDIT_FINALIZE',
    'AUDIT_REPORT_GENERATE',
    'AUDIT_RESPONSE',
    'AUDIT_REVIEW',
    'AUDIT_SHARE',
    'AUDIT_UPDATE',
    'AUDIT_TEMPLATE_COPY',
    'AUDIT_TEMPLATE_CREATE',
    'AUDIT_TEMPLATE_DELETE',
    'AUDIT_TEMPLATE_READ',
    'AUDIT_TEMPLATE_UPDATE',
    'CROP_READ',
    'CROP_UPDATE',
    'FARM_READ',
    'PLOT_READ',
    'QUERY_READ',
    'QUERY_RESPOND',
    'SCHEDULE_CREATE',
    'SCHEDULE_DELETE',
    'SCHEDULE_READ',
    'SCHEDULE_UPDATE',
    'SCHEDULE_TEMPLATE_COPY',
    'SCHEDULE_TEMPLATE_CREATE',
    'SCHEDULE_TEMPLATE_DELETE',
    'SCHEDULE_TEMPLATE_READ',
    'SCHEDULE_TEMPLATE_UPDATE');

-- FSP Consultant Access
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'CONSULTANT'
AND p.code IN (
    'AUDIT_CREATE',
    'AUDIT_FINALIZE',
    'AUDIT_REPORT_GENERATE',
    'AUDIT_RESPONSE',
    'AUDIT_REVIEW',
    'AUDIT_UPDATE',
    'AUDIT_TEMPLATE_CREATE',
    'AUDIT_TEMPLATE_READ',
    'AUDIT_TEMPLATE_UPDATE',
    'CROP_READ',
    'CROP_UPDATE',
    'FARM_READ',
    'PLOT_READ',
    'QUERY_READ',
    'QUERY_RESPOND',
    'SCHEDULE_CREATE',
    'SCHEDULE_DELETE',
    'SCHEDULE_READ',
    'SCHEDULE_UPDATE',
    'SCHEDULE_TEMPLATE_READ');

-- FSP Technical Analyst Access
INSERT INTO role_permissions (role_id, permission_id, effect)
SELECT r.id, p.id, 'ALLOW'
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'TECHNICAL_ANALYST'
AND p.code IN (
    'AUDIT_CREATE',
    'AUDIT_REPORT_GENERATE',
    'AUDIT_RESPONSE',
    'AUDIT_UPDATE',
    'CROP_READ',
    'CROP_UPDATE',
    'FARM_READ',
    'PLOT_READ',
    'QUERY_READ',
    'QUERY_RESPOND');

