"""
Add task_name, task_details, and notes columns to schedule_tasks table.
"""
from sqlalchemy import text
from app.core.database import SessionLocal

def upgrade():
    db = SessionLocal()
    try:
        # Add task_name
        db.execute(text("ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS task_name VARCHAR(200)"))
        # Add task_details
        db.execute(text("ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS task_details JSONB"))
        # Add notes
        db.execute(text("ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS notes TEXT"))
        db.commit()
        print("Successfully added columns to schedule_tasks table.")
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    upgrade()
