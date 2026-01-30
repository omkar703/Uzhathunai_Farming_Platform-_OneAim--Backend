-- Migration: Add access_granted column to work_orders
-- Description: Adds a boolean flag to grant global access to the FSP organization for the duration of the work order.

ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS access_granted BOOLEAN DEFAULT TRUE;

-- Add comment
COMMENT ON COLUMN work_orders.access_granted IS 'If true, FSP has read access to all resources in visibility/scope belonging to the farming org';
