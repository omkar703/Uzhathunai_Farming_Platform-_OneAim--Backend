
import os
import sys
import uuid
import subprocess

def create_audit_reports_table():
    print("--- Creating audit_reports table via Docker ---")
    
    sql = """
    CREATE TABLE IF NOT EXISTS audit_reports (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        audit_id UUID NOT NULL UNIQUE REFERENCES audits(id) ON DELETE CASCADE,
        report_html TEXT,
        report_images JSONB DEFAULT '[]',
        pdf_url TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        created_by UUID REFERENCES users(id) ON DELETE SET NULL
    );
    
    CREATE INDEX IF NOT EXISTS idx_audit_reports_audit_id ON audit_reports(audit_id);
    """
    
    try:
        # Use docker exec psql to run the SQL
        cmd = f"docker exec aggroconnect_db psql -U postgres -d farm_db -c \"{sql}\" "
        subprocess.check_call(cmd, shell=True)
        print("Successfully created audit_reports table")
        return True
    except Exception as e:
        print(f"Failed to create table: {e}")
        return False

if __name__ == "__main__":
    create_audit_reports_table()
