-- Fix missing enum values
ALTER TYPE audit_status ADD VALUE IF NOT EXISTS 'SUBMITTED_TO_FARMER';
ALTER TYPE audit_status ADD VALUE IF NOT EXISTS 'COMPLETED';

-- Fix missing columns
ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS task_name VARCHAR(200);
ALTER TABLE schedule_template_tasks ADD COLUMN IF NOT EXISTS task_name VARCHAR(200);
