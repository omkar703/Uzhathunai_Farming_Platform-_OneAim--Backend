-- Fix missing columns in work_orders table
ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS completion_notes TEXT;
ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS completion_photo_url VARCHAR(500);
