-- 004_add_is_approved_to_orgs.sql
-- Purpose: Add is_approved column to organizations table
-- DATE: 2026-01-16

ALTER TABLE organizations
ADD COLUMN is_approved BOOLEAN DEFAULT false;

COMMENT ON COLUMN organizations.is_approved IS 'Approve status for FSP/Farming organizations';
