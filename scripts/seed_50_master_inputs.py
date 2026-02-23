from app.core.database import SessionLocal
from app.models.input_item import InputItem, InputItemCategory, InputItemCategoryTranslation, InputItemTranslation
from app.models.enums import InputItemType
from sqlalchemy import text
import uuid

def seed_inputs():
    db = SessionLocal()
    try:
        # 1. Define Categories to match Frontend labels
        categories_data = [
            {"code": "FERTILIZER", "name": "Fertilizer", "type": InputItemType.FERTILIZER},
            {"code": "PESTICIDE", "name": "Pesticide", "type": InputItemType.PESTICIDE},
            {"code": "BIO_FERTILIZER", "name": "Bio Fertilizer", "type": InputItemType.BIO_FERTILIZER},
            {"code": "ORGANIC_FERTILIZER", "name": "Organic Fertilizer", "type": InputItemType.ORGANIC_FERTILIZER},
            {"code": "MACHINERY", "name": "Machinery", "type": InputItemType.MACHINERY},
            {"code": "LABOUR", "name": "Labour", "type": InputItemType.LABOUR},
        ]

        category_map = {}
        for cat in categories_data:
            existing = db.query(InputItemCategory).filter(InputItemCategory.code == cat["code"]).first()
            if not existing:
                new_cat = InputItemCategory(
                    code=cat["code"],
                    is_system_defined=True
                )
                db.add(new_cat)
                db.flush()
                # Translation
                trans = InputItemCategoryTranslation(
                    category_id=new_cat.id,
                    language_code="en",
                    name=cat["name"]
                )
                db.add(trans)
                category_map[cat["code"]] = new_cat.id
                print(f"Created category: {cat['name']}")
            else:
                category_map[cat["code"]] = existing.id
                # Ensure translation exists
                trans_existing = db.query(InputItemCategoryTranslation).filter(
                    InputItemCategoryTranslation.category_id == existing.id,
                    InputItemCategoryTranslation.language_code == "en"
                ).first()
                if not trans_existing:
                    db.add(InputItemCategoryTranslation(category_id=existing.id, language_code="en", name=cat["name"]))
                print(f"Category exists: {cat['name']}")

        # 2. Define 50 Items
        items_data = []
        
        # Fertilizers (10)
        items_data += [{"cat": "FERTILIZER", "name": n, "type": InputItemType.FERTILIZER} for n in [
            "Urea", "DAP", "NPK 19-19-19", "MOP", "SSP", "Calcium Nitrate", 
            "Magnesium Sulphate", "Potassium Nitrate", "Ammonium Sulphate", "Zinc Sulphate"
        ]]
        
        # Pesticides (10)
        items_data += [{"cat": "PESTICIDE", "name": n, "type": InputItemType.PESTICIDE} for n in [
            "Chlorpyrifos", "Imidacloprid", "Mancozeb", "Glyphosate", "Neem Oil",
            "Atrazine", "Carbendazim", "Cypermethrin", "Dimethoate", "Malathion"
        ]]
        
        # Bio Fertilizers (10)
        items_data += [{"cat": "BIO_FERTILIZER", "name": n, "type": InputItemType.BIO_FERTILIZER} for n in [
            "Azospirillum", "Phosphobacteria", "Rhizobium", "VAM", "Acetobacter",
            "Potash Mobilizing Bacteria", "Zinc Solubilizing Bacteria", "Pseudomonas", "Trichoderma Viride", "Bacillus Thuringiensis"
        ]]
        
        # Organic Fertilizers (10)
        items_data += [{"cat": "ORGANIC_FERTILIZER", "name": n, "type": InputItemType.ORGANIC_FERTILIZER} for n in [
            "Farm Yard Manure", "Vermicompost", "Poultry Manure", "Sheep/Goat Manure", "Green Manure",
            "Oil Cakes", "Bone Meal", "Fish Meal", "Jeevamrutha", "Panchagavya"
        ]]
        
        # Machinery (5)
        items_data += [{"cat": "MACHINERY", "name": n, "type": InputItemType.MACHINERY} for n in [
            "Tractor", "Power Tiller", "Rotavator", "Combine Harvester", "Power Sprayer"
        ]]
        
        # Labour (5)
        items_data += [{"cat": "LABOUR", "name": n, "type": InputItemType.LABOUR} for n in [
            "Skilled Male Labour", "Skilled Female Labour", "General Labour", "Land Clearing Team", "Harvesting Team"
        ]]

        for item in items_data:
            code = item["name"].upper().replace(" ", "_").replace("/", "_").replace("-", "_")
            existing = db.query(InputItem).filter(InputItem.code == code, InputItem.is_system_defined == True).first()
            if not existing:
                new_item = InputItem(
                    category_id=category_map[item["cat"]],
                    code=code,
                    is_system_defined=True,
                    type=item["type"]
                )
                db.add(new_item)
                db.flush()
                # Translation
                db.add(InputItemTranslation(
                    input_item_id=new_item.id,
                    language_code="en",
                    name=item["name"]
                ))
                print(f"Seeded item: {item['name']}")
            else:
                print(f"Item exists: {item['name']}")

        db.commit()
        print("Seeding complete.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_inputs()
