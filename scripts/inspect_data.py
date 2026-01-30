import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_URL = "postgresql://postgres:postgres@db:5432/farm_db"

def inspect_data():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        print("--- Parameter Translations (Name = 'Question') ---")
        result = conn.execute(text("SELECT * FROM parameter_translations WHERE name = 'Question'"))
        rows = result.fetchall()
        print(f"Found {len(rows)} translations with name 'Question'")
        for row in rows[:5]:
            print(row)

        print("\n--- Template Parameter Snapshots (Name = 'Question') ---")
        result = conn.execute(text("SELECT id, parameter_snapshot FROM template_parameters"))
        rows = result.fetchall()
        count = 0
        for row in rows:
            snapshot = row[1]
            # Check deep inside snapshot for "Question"
            is_question = False
            if isinstance(snapshot, dict):
                translations = snapshot.get("translations", {})
                for lang in translations:
                    if translations[lang].get("name") == "Question":
                        is_question = True
                        break
            
            if is_question:
                count += 1
                if count <= 5:
                    print(f"ID: {row[0]}")
                    print(json.dumps(snapshot, indent=2))
        print(f"\nTotal snapshots with 'Question': {count}")

if __name__ == "__main__":
    inspect_data()
