-- Create audit_reports table
CREATE TABLE IF NOT EXISTS audit_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID NOT NULL REFERENCES audits(id) ON DELETE CASCADE,
    report_html TEXT,
    report_images JSONB DEFAULT '[]'::jsonb,
    pdf_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID REFERENCES users(id),
    CONSTRAINT audit_reports_audit_id_key UNIQUE (audit_id)
);

CREATE INDEX IF NOT EXISTS idx_audit_reports_audit ON audit_reports(audit_id);
