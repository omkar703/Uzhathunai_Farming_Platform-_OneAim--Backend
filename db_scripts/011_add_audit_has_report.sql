-- Migration: Add has_report column to audits
-- Description: Adds a boolean flag to indicate if an audit has an associated report.

ALTER TABLE audits ADD COLUMN IF NOT EXISTS has_report BOOLEAN DEFAULT FALSE;

-- Add comment
COMMENT ON COLUMN audits.has_report IS 'If true, an audit report has been generated for this audit';
