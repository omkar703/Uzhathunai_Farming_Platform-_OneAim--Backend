
import sys
import os
from uuid import uuid4
from sqlalchemy.orm import Session

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.reference_data import Task, TaskTranslation
from app.models.enums import TaskCategory

def fix_missing_task():
    db = SessionLocal()
    try:
        generic_code = "GENERAL_APPLICATION"
        print(f"Checking for task: {generic_code}...")
        
        existing = db.query(Task).filter(Task.code == generic_code).first()
        if not existing:
            print(f"Task {generic_code} not found. Creating...")
            task = Task(
                id=uuid4(),
                code=generic_code,
                category=TaskCategory.FARMING,
                requires_input_items=True,
                requires_concentration=True,
                requires_machinery=False,
                requires_labor=True,
                sort_order=99,
                is_active=True
            )
            db.add(task)
            db.flush()
            
            # Add English translation
            trans = TaskTranslation(
                task_id=task.id,
                language_code="en",
                name="General Application",
                description="General task for applying inputs or performing activities"
            )
            db.add(trans)
            db.commit()
            print(f"Successfully created task: {generic_code} ({task.id})")
        else:
            print(f"Task {generic_code} already exists ({existing.id}).")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_missing_task()
