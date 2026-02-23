import sys
import os
from sqlalchemy import text
from app.core.database import SessionLocal

# Removed hardcoded DATABASE_URL to allow settings to load from environment

def update_enum():
    db = SessionLocal()
    try:
        print("Checking for existing enum values...")
        # Check if values exist before adding
        res = db.execute(text("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'input_item_type'"))
        existing_values = [r[0] for r in res]
        print(f"Current values: {existing_values}")
        
        new_values = ['MACHINERY', 'LABOUR', 'BIO_FERTILIZER', 'ORGANIC_FERTILIZER']
        
        # We need to run these outside of a transaction or with autocommit because ALTER TYPE ADD VALUE cannot run in a transaction block
        # In SQLAlchemy, we can use the engine directly or set execution_options(isolation_level="AUTOCOMMIT")
        engine = db.get_bind()
        connection = engine.raw_connection()
        connection.set_isolation_level(0) # AUTOCOMMIT
        cursor = connection.cursor()
        
        for val in new_values:
            if val not in existing_values:
                print(f"Adding value: {val}")
                try:
                    cursor.execute(f"ALTER TYPE input_item_type ADD VALUE '{val}'")
                    print(f"Successfully added {val}")
                except Exception as ex:
                    print(f"Failed to add {val}: {ex}")
            else:
                print(f"Value {val} already exists.")
        
        cursor.close()
        connection.close()
        print("Enum update complete.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_enum()
