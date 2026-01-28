-- Add assignment columns to audits table
ALTER TABLE audits ADD COLUMN IF NOT EXISTS assigned_to_user_id UUID REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE audits ADD COLUMN IF NOT EXISTS analyst_user_id UUID REFERENCES users(id) ON DELETE SET NULL;

-- Create indices for the new columns
CREATE INDEX IF NOT EXISTS idx_audits_assigned_to ON audits(assigned_to_user_id);
CREATE INDEX IF NOT EXISTS idx_audits_analyst ON audits(analyst_user_id);

-- Update audit_status enum
-- PostgreSQL does not support IF NOT EXISTS for enum values directly in a simple way that is idempotent without PL/SQL, 
-- but we can use ALTER TYPE ... ADD VALUE inside a transaction block is strictly serialized, so we'll do them one by one.
-- Note: 'ALTER TYPE ... ADD VALUE' cannot be run inside a transaction block in some postgres versions/configurations, 
-- but usually it is fine if it's the only command or appropriately managed. 
-- However, for safety in scripts, we often just run it. Even better, we handle the error if it exists.
-- Since this is a raw SQL script, let's assume standard postgres 12+ behavior.

ALTER TYPE audit_status ADD VALUE IF NOT EXISTS 'PENDING' BEFORE 'DRAFT';
ALTER TYPE audit_status ADD VALUE IF NOT EXISTS 'SUBMITTED_FOR_REVIEW' AFTER 'IN_PROGRESS';
ALTER TYPE audit_status ADD VALUE IF NOT EXISTS 'IN_ANALYSIS' AFTER 'SUBMITTED_FOR_REVIEW';

-- Note: 'DRAFT' and 'PENDING' might be redundant depending on interpretation, 
-- but enforcing the user's list: PENDING, IN_PROGRESS, SUBMITTED_FOR_REVIEW, IN_ANALYSIS, FINALIZED.
-- We will keep existing values to avoid data loss or breaking changes, just adding new ones.
