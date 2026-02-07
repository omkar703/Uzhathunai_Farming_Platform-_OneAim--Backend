"""
Add completion_notes and completion_photo_url columns to work_orders table.
"""
from sqlalchemy import text
from app.core.database import SessionLocal

def upgrade():
    db = SessionLocal()
    try:
        # Add completion_notes
        db.execute(text("ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS completion_notes TEXT"))
        # Add completion_photo_url
        db.execute(text("ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS completion_photo_url VARCHAR(500)"))
        # Add assigned_to_user_id
        db.execute(text("ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS assigned_to_user_id UUID REFERENCES users(id)"))
        db.commit()
        print("Successfully added completion columns to work_orders table.")
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    upgrade()
