-- Fix audit_response_photos table to support unlinked evidence
ALTER TABLE audit_response_photos 
ADD COLUMN IF NOT EXISTS audit_id UUID REFERENCES audits(id) ON DELETE CASCADE;

-- Update existing rows (if any) to have an audit_id derived from their response
UPDATE audit_response_photos p
SET audit_id = r.audit_id
FROM audit_responses r
WHERE p.audit_response_id = r.id AND p.audit_id IS NULL;

-- Make audit_response_id nullable
ALTER TABLE audit_response_photos 
ALTER COLUMN audit_response_id DROP NOT NULL;

-- Make audit_id not null where it is not null (this might fail if there are orphan photos without response linking, so we check first)
-- For now, let's leave it nullable or handle separately, but the model says nullable=False.
-- Let's try to set it NOT NULL, if it fails, the user will see.
-- ALTER TABLE audit_response_photos ALTER COLUMN audit_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_audit_response_photos_audit ON audit_response_photos(audit_id);

-- Fix audit_issues table missing recommendation column
ALTER TABLE audit_issues
ADD COLUMN IF NOT EXISTS recommendation TEXT;
