-- Add assigned_to_user_id to work_orders table
ALTER TABLE work_orders
ADD COLUMN assigned_to_user_id UUID REFERENCES users(id);

-- Add index for performance
CREATE INDEX idx_work_orders_assigned_to ON work_orders(assigned_to_user_id);
