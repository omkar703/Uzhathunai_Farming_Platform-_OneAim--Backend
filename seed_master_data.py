
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

        # 3. Seed Reference Data Types & Data (Application Methods)
        from app.models.reference_data import ReferenceDataType, ReferenceData, ReferenceDataTranslation
        
        # 3.1 Create Type
        type_code = "application_methods"
        ref_type = db.query(ReferenceDataType).filter(ReferenceDataType.code == type_code).first()
        if not ref_type:
            ref_type = ReferenceDataType(
                id=uuid4(),
                code=type_code,
                name="Application Methods",
                description="Methods of applying inputs like fertilizer or pesticide"
            )
            db.add(ref_type)
            db.flush()
            print(f"Created ReferenceDataType: {type_code}")

        # 3.2 Create Methods
        methods = [
            {"code": "FOLIAR_SPRAY", "name": "Foliar Spray", "requires_concentration": True, "order": 1},
            {"code": "SOIL_APPLICATION", "name": "Soil Application", "requires_concentration": False, "order": 2},
            {"code": "DRIP_IRRIGATION", "name": "Drip Irrigation", "requires_concentration": True, "order": 3},
            {"code": "BROADCASTING", "name": "Broadcasting", "requires_concentration": False, "order": 4},
            {"code": "SEED_TREATMENT", "name": "Seed Treatment", "requires_concentration": True, "order": 5},
            {"code": "DRENCHING", "name": "Drenching", "requires_concentration": True, "order": 6}
        ]

        print("\nSeeding Application Methods...")
        for m in methods:
            existing = db.query(ReferenceData).filter(
                ReferenceData.type_id == ref_type.id,
                ReferenceData.code == m["code"]
            ).first()

            if not existing:
                ref_data = ReferenceData(
                    id=uuid4(),
                    type_id=ref_type.id,
                    code=m["code"],
                    sort_order=m["order"],
                    is_active=True,
                    reference_metadata={"requires_concentration": m["requires_concentration"]}
                )
                db.add(ref_data)
                db.flush()

                trans = ReferenceDataTranslation(
                    reference_data_id=ref_data.id,
                    language_code="en",
                    display_name=m["name"],
                    description=m["name"]
                )
                db.add(trans)
                print(f"Created method: {m['code']}")
            else:
                print(f"Method {m['code']} already exists.")
        
        # 4. Seed Tasks
        from app.models.reference_data import Task, TaskTranslation
        from app.models.enums import TaskCategory
        
        tasks = [
            {
                "code": "GENERAL_APPLICATION",
                "category": TaskCategory.FARMING,
                "name": "General Application",
                "desc": "General task for applying inputs or performing activities",
                "requires_input": True,
                "requires_conc": True,
                "requires_labor": True
            }
        ]
        
        print("\nSeeding Tasks...")
        for t_data in tasks:
            existing = db.query(Task).filter(Task.code == t_data["code"]).first()
            if not existing:
                task = Task(
                    id=uuid4(),
                    code=t_data["code"],
                    category=t_data["category"],
                    requires_input_items=t_data["requires_input"],
                    requires_concentration=t_data["requires_conc"],
                    requires_labor=t_data["requires_labor"],
                    sort_order=99,
                    is_active=True
                )
                db.add(task)
                db.flush()
                
                trans = TaskTranslation(
                    task_id=task.id,
                    language_code="en",
                    name=t_data["name"],
                    description=t_data["desc"]
                )
                db.add(trans)
                print(f"Created task: {t_data['code']}")
            else:
                print(f"Task {t_data['code']} already exists.")

        db.commit()

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
