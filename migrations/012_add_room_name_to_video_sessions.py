"""
Add room_name column to video_sessions table for Jitsi support.
"""
from sqlalchemy import text
from app.core.database import SessionLocal

def upgrade():
    """Add room_name column to video_sessions table."""
    db = SessionLocal()
    try:
        # Add room_name column
        db.execute(text("""
            ALTER TABLE video_sessions 
            ADD COLUMN IF NOT EXISTS room_name VARCHAR(255);
        """))
        
        # Add index on room_name for faster lookups
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_video_sessions_room_name 
            ON video_sessions(room_name);
        """))
        
        db.commit()
        print("✅ Successfully added room_name column to video_sessions table")
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding room_name column: {e}")
        raise
    finally:
        db.close()

def downgrade():
    """Remove room_name column from video_sessions table."""
    db = SessionLocal()
    try:
        # Drop index first
        db.execute(text("""
            DROP INDEX IF EXISTS idx_video_sessions_room_name;
        """))
        
        # Drop column
        db.execute(text("""
            ALTER TABLE video_sessions 
            DROP COLUMN IF EXISTS room_name;
        """))
        
        db.commit()
        print("✅ Successfully removed room_name column from video_sessions table")
    except Exception as e:
        db.rollback()
        print(f"❌ Error removing room_name column: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Running migration: Add room_name to video_sessions")
    upgrade()
