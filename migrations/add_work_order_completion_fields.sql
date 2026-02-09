-- Migration: Add completion_notes and completion_photo_url to work_orders table
-- Date: 2026-02-09
-- Description: Adds missing columns that exist in the model but not in the database

-- Add completion_notes column
ALTER TABLE work_orders 
ADD COLUMN IF NOT EXISTS completion_notes TEXT;

-- Add completion_photo_url column
ALTER TABLE work_orders 
ADD COLUMN IF NOT EXISTS completion_photo_url VARCHAR(500);

-- Add comments for documentation
COMMENT ON COLUMN work_orders.completion_notes IS 'Notes added when work order is completed';
COMMENT ON COLUMN work_orders.completion_photo_url IS 'URL to completion photo stored in S3';
