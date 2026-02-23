-- Fix audit_response_photos table to support unlinked evidence and flagged status
-- Requirement: Add audit_id and is_flagged_for_report, make audit_response_id nullable

-- 1. Add columns if they don't exist
ALTER TABLE audit_response_photos 
ADD COLUMN IF NOT EXISTS audit_id UUID REFERENCES audits(id) ON DELETE CASCADE;

ALTER TABLE audit_response_photos 
ADD COLUMN IF NOT EXISTS is_flagged_for_report BOOLEAN DEFAULT false;

-- 2. Populate audit_id for existing rows from their respective responses
UPDATE audit_response_photos p
SET audit_id = r.audit_id
FROM audit_responses r
WHERE p.audit_response_id = r.id AND p.audit_id IS NULL;

-- 3. Make audit_response_id nullable (important for unlinked evidence)
ALTER TABLE audit_response_photos 
ALTER COLUMN audit_response_id DROP NOT NULL;

-- 4. Set is_flagged_for_report to NOT NULL after adding (with default false already set)
ALTER TABLE audit_response_photos
ALTER COLUMN is_flagged_for_report SET NOT NULL;

-- 5. Add index for performance on audit_id
CREATE INDEX IF NOT EXISTS idx_audit_response_photos_audit ON audit_response_photos(audit_id);

COMMENT ON COLUMN audit_response_photos.audit_id IS 'Audit ID this photo belongs to (nullable if linked via response, but model expects it)';
COMMENT ON COLUMN audit_response_photos.is_flagged_for_report IS 'Whether this photo is flagged to be included in the audit report';
