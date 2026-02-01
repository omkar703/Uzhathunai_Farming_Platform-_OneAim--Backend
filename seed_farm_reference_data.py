
import sys
import os
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.reference_data import ReferenceDataType, ReferenceData, ReferenceDataTranslation

def seed_farm_reference_data():
    db = SessionLocal()
    try:
        print("Seeding Farm Reference Data...")

        # Define data structure
        data_to_seed = {
            "SOIL_TYPE": {
                "name": "Soil Type",
                "description": "Types of soil found in the farm",
                "values": ["Black", "Red", "Alluvial", "Clay", "Sandy", "Loamy"]
            },
            "WATER_SOURCE": {
                "name": "Water Source",
                "description": "Sources of water for the farm",
                "values": ["Well", "Borewell", "Canal", "River", "Rainfed"]
            },
            "IRRIGATION_MODE": {
                "name": "Irrigation Mode",
                "description": "Methods of irrigation used",
                "values": ["Drip", "Sprinkler", "Flood", "Manual"]
            }
        }

        for type_code, details in data_to_seed.items():
            # 1. Get or Create Type
            ref_type = db.query(ReferenceDataType).filter(ReferenceDataType.code == type_code).first()
            if not ref_type:
                print(f"Creating Type: {type_code}")
                ref_type = ReferenceDataType(
                    id=uuid.uuid4(),
                    code=type_code,
                    name=details["name"],
                    description=details["description"]
                )
                db.add(ref_type)
                db.flush()
            else:
                print(f"Type exists: {type_code}")

            # 2. Seed Values
            for idx, val_name in enumerate(details["values"]):
                # Generate a code from name (e.g., "Black" -> "SOIL_BLACK")
                # But user request implies they might use the raw name as well. 
                # Standard practice is constant code. Let's use UPPERCASE_UNDERSCORE.
                val_code = f"{type_code}_{val_name.upper().replace(' ', '_')}"
                
                # Check if exists by code OR by translation name (matches frontend constants)
                # Checking by code is safer for idempotency.
                
                existing = db.query(ReferenceData).filter(
                    ReferenceData.type_id == ref_type.id,
                    ReferenceData.code == val_code
                ).first()

                if not existing:
                    print(f"  Creating Value: {val_name} ({val_code})")
                    ref_data = ReferenceData(
                        id=uuid.uuid4(),
                        type_id=ref_type.id,
                        code=val_code,
                        sort_order=idx + 1,
                        is_active=True
                    )
                    db.add(ref_data)
                    db.flush()

                    # Add Translation
                    trans = ReferenceDataTranslation(
                        reference_data_id=ref_data.id,
                        language_code="en",
                        display_name=val_name,
                        description=val_name
                    )
                    db.add(trans)
                else:
                    print(f"  Value exists: {val_name}")

        db.commit()
        print("\nSeeding Completed Successfully!")

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_farm_reference_data()
