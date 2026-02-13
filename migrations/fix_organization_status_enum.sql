-- Add REJECTED to organization_status enum
ALTER TYPE organization_status ADD VALUE IF NOT EXISTS 'REJECTED';
