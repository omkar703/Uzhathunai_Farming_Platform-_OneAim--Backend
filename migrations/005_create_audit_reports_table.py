
import os
import sys
import psycopg2

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('POSTGRES_SERVER', 'aggroconnect_db'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'farm_db'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
}

def create_audit_reports_table():
    print("--- Creating audit_reports table via psycopg2 ---")
    
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
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
        """)
        
        conn.commit()
        print("Successfully created audit_reports table")
        return True
        
    except Exception as e:
        print(f"Failed to create table: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = create_audit_reports_table()
    sys.exit(0 if success else 1)
