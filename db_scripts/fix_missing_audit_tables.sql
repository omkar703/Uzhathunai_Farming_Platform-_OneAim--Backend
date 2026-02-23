-- Create missing audit_recommendations table
-- Requirement: Standalone audit recommendations

CREATE TABLE IF NOT EXISTS audit_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID NOT NULL REFERENCES audits(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL DEFAULT 'Recommendation',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_audit_recommendations_audit ON audit_recommendations(audit_id);

COMMENT ON TABLE audit_recommendations IS 'Standalone recommendations generated during or after an audit';
