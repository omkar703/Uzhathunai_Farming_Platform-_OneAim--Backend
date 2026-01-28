
import sys
import os
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.input_item import InputItemCategory, InputItemCategoryTranslation
from app.models.measurement_unit import MeasurementUnit, MeasurementUnitTranslation
from app.models.enums import MeasurementUnitCategory

def seed_master_data():
    db = SessionLocal()
    try:
        # 1. Seed Input Item Categories
        categories = [
            {"code": "FERTILIZER", "name": "Fertilizer", "desc": "Chemical and biological fertilizers"},
            {"code": "PESTICIDE", "name": "Pesticide", "desc": "Pest control substances"},
            {"code": "BIO", "name": "Bio", "desc": "Biological inputs"},
            {"code": "ORGANIC", "name": "Organic", "desc": "Organic fertilizers and inputs"}
        ]

        print("Seeding Input Item Categories...")
        for cat_data in categories:
            existing = db.query(InputItemCategory).filter(InputItemCategory.code == cat_data["code"]).first()
            if not existing:
                cat = InputItemCategory(
                    id=uuid4(),
                    code=cat_data["code"],
                    is_system_defined=True,
                    owner_org_id=None,
                    sort_order=0,
                    is_active=True
                )
                db.add(cat)
                db.flush()
                
                # Add English translation
                trans = InputItemCategoryTranslation(
                    category_id=cat.id,
                    language_code="en",
                    name=cat_data["name"],
                    description=cat_data["desc"]
                )
                db.add(trans)
                print(f"Created category: {cat_data['code']}")
            else:
                print(f"Category {cat_data['code']} already exists.")

        # 2. Seed Measurement Units
        units = [
            # Weight
            {"category": MeasurementUnitCategory.WEIGHT, "code": "KG", "symbol": "kg", "name": "Kilogram", "is_base": True, "factor": 1.0},
            {"category": MeasurementUnitCategory.WEIGHT, "code": "G", "symbol": "g", "name": "Gram", "is_base": False, "factor": 0.001},
            {"category": MeasurementUnitCategory.WEIGHT, "code": "MG", "symbol": "mg", "name": "Milligram", "is_base": False, "factor": 0.000001},
            # Volume
            {"category": MeasurementUnitCategory.VOLUME, "code": "L", "symbol": "l", "name": "Liter", "is_base": True, "factor": 1.0},
            {"category": MeasurementUnitCategory.VOLUME, "code": "ML", "symbol": "ml", "name": "Milliliter", "is_base": False, "factor": 0.001},
            # Area
            {"category": MeasurementUnitCategory.AREA, "code": "ACRE", "symbol": "ac", "name": "Acre", "is_base": True, "factor": 1.0},
            {"category": MeasurementUnitCategory.AREA, "code": "HECTARE", "symbol": "ha", "name": "Hectare", "is_base": False, "factor": 2.47105},
            # Count
            {"category": MeasurementUnitCategory.COUNT, "code": "PIECES", "symbol": "pcs", "name": "Pieces", "is_base": True, "factor": 1.0},
            {"category": MeasurementUnitCategory.COUNT, "code": "PLANTS", "symbol": "plants", "name": "Plants", "is_base": False, "factor": 1.0}
        ]

        print("\nSeeding Measurement Units...")
        for unit_data in units:
            existing = db.query(MeasurementUnit).filter(MeasurementUnit.code == unit_data["code"]).first()
            if not existing:
                unit = MeasurementUnit(
                    id=uuid4(),
                    category=unit_data["category"],
                    code=unit_data["code"],
                    symbol=unit_data["symbol"],
                    is_base_unit=unit_data["is_base"],
                    conversion_factor=unit_data["factor"],
                    sort_order=0
                )
                db.add(unit)
                db.flush()
                
                # Add English translation
                trans = MeasurementUnitTranslation(
                    measurement_unit_id=unit.id,
                    language_code="en",
                    name=unit_data["name"]
                )
                db.add(trans)
                print(f"Created unit: {unit_data['code']}")
            else:
                print(f"Unit {unit_data['code']} already exists.")

        db.commit()
        print("\nSeeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_master_data()
