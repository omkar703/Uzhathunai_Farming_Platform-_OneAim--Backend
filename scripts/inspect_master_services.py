import os
import sys
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal

def inspect_master_services():
    with SessionLocal() as db:
        result = db.execute(text("SELECT id, code, name, status FROM master_services"))
        services = result.fetchall()
        print("Master Services in Database:")
        for s in services:
            print(f"- ID: {s.id}, Code: {s.code}, Name: {s.name}, Status: {s.status}")

if __name__ == "__main__":
    inspect_master_services()
