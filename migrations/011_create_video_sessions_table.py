from sqlalchemy import text
from app.core.database import SessionLocal

def upgrade():
    print("--- Creating video_sessions table via SQLAlchemy ---")
    db = SessionLocal()
    try:
        # Create video_session_status enum if it doesn't exist
        db.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'video_session_status') THEN
                    CREATE TYPE video_session_status AS ENUM ('PENDING', 'ACTIVE', 'COMPLETED', 'CANCELLED');
                END IF;
            END
            $$;
        """))
        
        # Create video_sessions table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS video_sessions (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
                audit_id UUID REFERENCES audits(id) ON DELETE SET NULL,
                zoom_meeting_id VARCHAR(50),
                join_url TEXT,
                start_url TEXT,
                topic VARCHAR(255),
                start_time TIMESTAMP WITH TIME ZONE,
                duration INTEGER,
                password VARCHAR(50),
                status video_session_status DEFAULT 'PENDING',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_by UUID REFERENCES users(id)
            );
        """))
        
        # Create indexes
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_video_sessions_work_order_id ON video_sessions(work_order_id);"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_video_sessions_audit_id ON video_sessions(audit_id);"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_video_sessions_zoom_meeting_id ON video_sessions(zoom_meeting_id);"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_video_sessions_status ON video_sessions(status);"))
        
        db.commit()
        print("Successfully created video_sessions table and enum type.")
        return True
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    upgrade()
