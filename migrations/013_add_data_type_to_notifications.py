"""
Add data column to notifications table and create type alias for notification_type.
"""
from sqlalchemy import text
from app.core.database import SessionLocal

def upgrade():
    """Add data column to notifications table."""
    db = SessionLocal()
    try:
        # Add data column for JSON metadata
        db.execute(text("""
            ALTER TABLE notifications 
            ADD COLUMN IF NOT EXISTS data JSONB;
        """))
        
        # Create an alias/view or we can just rename the column
        # Option 1: Add a computed column (doesn't work well)
        # Option 2: Just add the 'type' column and sync it with notification_type
        # Option 3: Rename notification_type to type (BREAKING for existing code)
        
        # Let's go with adding 'type' column and keeping both for compatibility
        db.execute(text("""
            ALTER TABLE notifications 
            ADD COLUMN IF NOT EXISTS type VARCHAR(50);
        """))
        
        # Copy existing notification_type values to type
        db.execute(text("""
            UPDATE notifications 
            SET type = notification_type::text 
            WHERE type IS NULL;
        """))
        
        # Add index on type
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_notifications_type_new 
            ON notifications(type);
        """))
        
        db.commit()
        print("✅ Successfully added data and type columns to notifications table")
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating notifications table: {e}")
        raise
    finally:
        db.close()

def downgrade():
    """Remove data and type columns from notifications table."""
    db = SessionLocal()
    try:
        # Drop index
        db.execute(text("""
            DROP INDEX IF EXISTS idx_notifications_type_new;
        """))
        
        # Drop columns
        db.execute(text("""
            ALTER TABLE notifications 
            DROP COLUMN IF EXISTS type,
            DROP COLUMN IF EXISTS data;
        """))
        
        db.commit()
        print("✅ Successfully removed data and type columns from notifications table")
    except Exception as e:
        db.rollback()
        print(f"❌ Error removing columns: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Running migration: Add data and type columns to notifications")
    upgrade()
