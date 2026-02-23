-- Add pricing_unit column to work_orders table
ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS pricing_unit VARCHAR(50);
