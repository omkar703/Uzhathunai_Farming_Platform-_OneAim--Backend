
-- Fix audit_response_photos table to support unlinked evidence
ALTER TABLE audit_response_photos 
ADD COLUMN audit_id UUID REFERENCES audits(id) ON DELETE CASCADE;

-- Update existing rows (if any) to have an audit_id derived from their response
UPDATE audit_response_photos p
SET audit_id = r.audit_id
FROM audit_responses r
WHERE p.audit_response_id = r.id;

-- Make audit_response_id nullable
ALTER TABLE audit_response_photos 
ALTER COLUMN audit_response_id DROP NOT NULL;

-- Make audit_id not null after populating existing rows
-- Actually, let's keep it nullable if some photos might not be linked to audits (unlikely but safer for now)
-- No, it should be linked to an audit.
ALTER TABLE audit_response_photos
ALTER COLUMN audit_id SET NOT NULL;

CREATE INDEX idx_audit_response_photos_audit ON audit_response_photos(audit_id);
