
import sys
import os
from sqlalchemy import text

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal

def inspect_ref_data():
    db = SessionLocal()
    try:
        print("--- SOIL TYPES ---")
        # Try joining with translations to get names
        query = text("""
            SELECT rd.id, rd.code, rdt.display_name 
            FROM reference_data rd 
            JOIN reference_data_translations rdt ON rd.id = rdt.reference_data_id
            JOIN reference_data_types rdtype ON rd.type_id = rdtype.id
            WHERE rdtype.code = 'SOIL_TYPE'
        """)
        results = db.execute(query).fetchall()
        for r in results:
            print(f"ID: {r.id} | Code: {r.code} | Name: {r.display_name}")

        print("\n--- WATER SOURCES ---")
        query = text("""
            SELECT rd.id, rd.code, rdt.display_name 
            FROM reference_data rd 
            JOIN reference_data_translations rdt ON rd.id = rdt.reference_data_id
            JOIN reference_data_types rdtype ON rd.type_id = rdtype.id
            WHERE rdtype.code = 'WATER_SOURCE'
        """)
        results = db.execute(query).fetchall()
        for r in results:
            print(f"ID: {r.id} | Code: {r.code} | Name: {r.display_name}")

        print("\n--- MEASUREMENT UNITS (Area) ---")
        query = text("""
            SELECT mu.id, mu.code, mut.name 
            FROM measurement_units mu
            JOIN measurement_unit_translations mut ON mu.id = mut.measurement_unit_id
            WHERE mu.category = 'AREA'
        """)
        results = db.execute(query).fetchall()
        for r in results:
            print(f"ID: {r.id} | Code: {r.code} | Name: {r.name}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_ref_data()
