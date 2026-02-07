-- Fix ALL missing columns in the database

-- Fix work_orders table
ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS completion_notes TEXT;
ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS completion_photo_url VARCHAR(500);
ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS assigned_to_user_id UUID REFERENCES users(id);

-- Fix schedule_tasks table
ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS task_name VARCHAR(200);
ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS task_details JSONB;
ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS notes TEXT;

-- Fix audit_response_photos table
ALTER TABLE audit_response_photos ADD COLUMN IF NOT EXISTS audit_id UUID REFERENCES audits(id) ON DELETE CASCADE;

-- Fix audit_issues table
ALTER TABLE audit_issues ADD COLUMN IF NOT EXISTS recommendation TEXT;
