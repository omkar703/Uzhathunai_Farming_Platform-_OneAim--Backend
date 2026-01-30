import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_URL = "postgresql://postgres:postgres@db:5432/farm_db"

def fix_data():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("--- Fixing Parameter Translations ---")
            # Update all 'Question' to a better name based on code or generic
            # We'll use a CASE statement or just update all for now since it's test data
            
            # 1. Update parameter_translations
            # We'll try to generate a name from the Code if possible, or just "Parameter {id}"
            # Actually, let's just specific ones if we can, but bulk update is easier for test data.
            
            # Fetch all that are 'Question'
            result = conn.execute(text("SELECT id, parameter_id, language_code FROM parameter_translations WHERE name = 'Question'"))
            rows = result.fetchall()
            
            print(f"Found {len(rows)} translations to fix.")
            
            for row in rows:
                p_trans_id = row[0]
                p_id = row[1]
                
                # Get param code
                p_res = conn.execute(text("SELECT code, parameter_type FROM parameters WHERE id = :pid"), {"pid": p_id}).fetchone()
                if p_res:
                    code = p_res[0]
                    p_type = p_res[1]
                    
                    # Make a nice name
                    new_name = code.replace("PRM_", "").replace("_", " ").title()
                    if "Question" in new_name or len(new_name) < 3:
                         new_name = f"{p_type.replace('_', ' ').title()} Parameter"

                    conn.execute(text(
                        "UPDATE parameter_translations SET name = :name WHERE id = :id"
                    ), {"name": new_name, "id": p_trans_id})
                    print(f"Updated Translation {p_trans_id} -> {new_name}")

            print("\n--- Fixing Template Parameter Snapshots ---")
            # 2. Update template_parameters
            result = conn.execute(text("SELECT id, parameter_snapshot FROM template_parameters"))
            rows = result.fetchall()
            
            for row in rows:
                tp_id = row[0]
                snapshot = row[1]
                
                if not isinstance(snapshot, dict):
                    continue
                    
                updated = False
                translations = snapshot.get("translations", {})
                
                for lang in translations:
                    if translations[lang].get("name") == "Question":
                        # Fix it
                        current_code = snapshot.get("code", "UNKNOWN")
                        new_name = current_code.replace("PRM_", "").replace("_", " ").title()
                        if "Question" in new_name or len(new_name) < 3:
                             new_name = f"{snapshot.get('parameter_type', 'Parameter').replace('_', ' ').title()} Parameter"
                        
                        translations[lang]["name"] = new_name
                        updated = True
                
                if updated:
                    snapshot["translations"] = translations
                    # Update DB
                    conn.execute(text(
                        "UPDATE template_parameters SET parameter_snapshot = :snap WHERE id = :id"
                    ), {"snap": json.dumps(snapshot), "id": tp_id})
                    print(f"Updated Snapshot {tp_id}")

            trans.commit()
            print("Successfully fixed data.")
            
        except Exception as e:
            trans.rollback()
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    fix_data()
