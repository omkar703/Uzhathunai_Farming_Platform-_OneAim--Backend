"""
Seed Indian crop categories, types (with season + year), and common varieties.

Seasons used:
  - Kharif 2025   : Sown Jun-Jul, harvested Sep-Oct 2025
  - Rabi 2025-26  : Sown Oct-Nov 2025, harvested Mar-Apr 2026
  - Zaid 2026     : Sown Mar, harvested Jun 2026
  - Rabi 2024-25  : Previous year (for historical records)
  - Kharif 2024   : Previous year

Crops that grow in multiple seasons get one entry per season with different codes.

Usage:
    cd <backend-dir>
    python seed_crop_types.py
"""

import sys
import os
from uuid import uuid4

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.crop_data import (
    CropCategory, CropCategoryTranslation,
    CropType, CropTypeTranslation,
)


# ---------------------------------------------------------------------------
# Master data definition
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "code": "cereals_millets",
        "sort_order": 1,
        "name_en": "Cereals & Millets",
        "desc_en": "Staple food grains including rice, wheat, maize, and millets",
    },
    {
        "code": "pulses_legumes",
        "sort_order": 2,
        "name_en": "Pulses & Legumes",
        "desc_en": "Protein-rich crops such as chickpea, lentil, and soybean",
    },
    {
        "code": "oilseeds",
        "sort_order": 3,
        "name_en": "Oilseeds",
        "desc_en": "Oil-yielding crops including groundnut, mustard, and sunflower",
    },
    {
        "code": "cash_crops",
        "sort_order": 4,
        "name_en": "Cash Crops",
        "desc_en": "Commercial crops such as sugarcane, cotton, and jute",
    },
    {
        "code": "vegetables",
        "sort_order": 5,
        "name_en": "Vegetables",
        "desc_en": "Vegetable crops including potato, onion, tomato, and cucumber",
    },
    {
        "code": "horticulture",
        "sort_order": 6,
        "name_en": "Horticulture & Fruits",
        "desc_en": "Fruit and plantation crops like mango, banana, and coconut",
    },
    {
        "code": "spices_condiments",
        "sort_order": 7,
        "name_en": "Spices & Condiments",
        "desc_en": "Spice crops such as turmeric, chilli, coriander, and cumin",
    },
    {
        "code": "fodder_forage",
        "sort_order": 8,
        "name_en": "Fodder & Forage",
        "desc_en": "Crops grown for animal feed",
    },
]

# Each entry: (category_code, crop_code, display_name, sort_order, desc)
# Crops that can be grown in multiple seasons have one entry per season.
CROP_TYPES = [
    # ── CEREALS & MILLETS ──────────────────────────────────────────────────
    # Rice: primarily Kharif, but can be Rabi in irrigated south/east India
    ("cereals_millets", "rice_kharif_2025",      "Rice – Kharif 2025",        1,  "Paddy crop sown Jun-Jul 2025, harvested Sep-Oct 2025"),
    ("cereals_millets", "rice_rabi_2025_26",     "Rice – Rabi 2025-26",       2,  "Irrigated Rabi paddy; sown Nov 2025, harvested Mar 2026"),
    ("cereals_millets", "rice_kharif_2024",      "Rice – Kharif 2024",        3,  "Paddy crop sown Jun-Jul 2024, harvested Sep-Oct 2024"),

    # Wheat: strictly Rabi
    ("cereals_millets", "wheat_rabi_2025_26",    "Wheat – Rabi 2025-26",      4,  "Sown Oct-Nov 2025, harvested Apr 2026"),
    ("cereals_millets", "wheat_rabi_2024_25",    "Wheat – Rabi 2024-25",      5,  "Sown Oct-Nov 2024, harvested Apr 2025"),

    # Maize: Kharif (main) + Rabi possible in south India
    ("cereals_millets", "maize_kharif_2025",     "Maize – Kharif 2025",       6,  "Sown Jun-Jul 2025, harvested Sep-Oct 2025"),
    ("cereals_millets", "maize_rabi_2025_26",    "Maize – Rabi 2025-26",      7,  "South India sowing; Nov 2025, harvested Feb-Mar 2026"),

    # Jowar (Sorghum): Kharif + Rabi
    ("cereals_millets", "jowar_kharif_2025",     "Jowar – Kharif 2025",       8,  "Sown Jun 2025, harvested Oct 2025"),
    ("cereals_millets", "jowar_rabi_2025_26",    "Jowar – Rabi 2025-26",      9,  "Rabi dual-purpose jowar; sown Oct 2025, harvested Feb 2026"),

    # Bajra (Pearl Millet): Kharif only
    ("cereals_millets", "bajra_kharif_2025",     "Bajra – Kharif 2025",       10, "Sown Jun-Jul 2025, harvested Sep-Oct 2025"),
    ("cereals_millets", "bajra_kharif_2024",     "Bajra – Kharif 2024",       11, "Sown Jun-Jul 2024, harvested Sep-Oct 2024"),

    # Ragi (Finger Millet): Kharif
    ("cereals_millets", "ragi_kharif_2025",      "Ragi – Kharif 2025",        12, "Sown Jun 2025, harvested Oct 2025"),

    # Barley: Rabi
    ("cereals_millets", "barley_rabi_2025_26",   "Barley – Rabi 2025-26",     13, "Sown Oct-Nov 2025, harvested Mar 2026"),

    # ── PULSES & LEGUMES ──────────────────────────────────────────────────
    # Chickpea (Gram/Chana): Rabi only
    ("pulses_legumes", "chickpea_rabi_2025_26",  "Chickpea – Rabi 2025-26",   1,  "Gram/Chana; sown Oct-Nov 2025, harvested Feb-Mar 2026"),
    ("pulses_legumes", "chickpea_rabi_2024_25",  "Chickpea – Rabi 2024-25",   2,  "Gram/Chana; sown Oct-Nov 2024, harvested Feb-Mar 2025"),

    # Arhar / Tur Dal (Pigeon Pea): Kharif
    ("pulses_legumes", "arhar_kharif_2025",      "Arhar (Tur Dal) – Kharif 2025", 3, "Sown Jun-Jul 2025, harvested Nov-Dec 2025"),

    # Moong / Green Gram: Kharif + Zaid
    ("pulses_legumes", "moong_kharif_2025",      "Moong – Kharif 2025",       4,  "Sown Jun 2025, harvested Aug-Sep 2025"),
    ("pulses_legumes", "moong_zaid_2026",        "Moong – Zaid 2026",         5,  "Summer crop; sown Mar 2026, harvested Jun 2026"),

    # Urad Dal (Black Gram): Kharif + Rabi (south India)
    ("pulses_legumes", "urad_kharif_2025",       "Urad Dal – Kharif 2025",    6,  "Sown Jun-Jul 2025, harvested Sep-Oct 2025"),
    ("pulses_legumes", "urad_rabi_2025_26",      "Urad Dal – Rabi 2025-26",   7,  "South India; sown Oct 2025, harvested Jan 2026"),

    # Lentil (Masoor): Rabi
    ("pulses_legumes", "lentil_rabi_2025_26",    "Lentil (Masoor) – Rabi 2025-26", 8, "Sown Oct-Nov 2025, harvested Feb-Mar 2026"),

    # Soybean: Kharif
    ("pulses_legumes", "soybean_kharif_2025",    "Soybean – Kharif 2025",     9,  "Sown Jun-Jul 2025, harvested Oct 2025"),

    # Peas: Rabi + Zaid
    ("pulses_legumes", "peas_rabi_2025_26",      "Peas – Rabi 2025-26",       10, "Sown Oct-Nov 2025, harvested Jan-Feb 2026"),
    ("pulses_legumes", "peas_zaid_2026",         "Peas – Zaid 2026",          11, "Early summer crop; sown Feb 2026, harvested May 2026"),

    # ── OILSEEDS ──────────────────────────────────────────────────────────
    # Groundnut: Kharif (main) + Rabi in south India
    ("oilseeds", "groundnut_kharif_2025",        "Groundnut – Kharif 2025",   1,  "Sown Jun-Jul 2025, harvested Oct-Nov 2025"),
    ("oilseeds", "groundnut_rabi_2025_26",       "Groundnut – Rabi 2025-26",  2,  "Irrigated south India; sown Nov 2025, harvested Feb 2026"),

    # Mustard / Rapeseed: Rabi only
    ("oilseeds", "mustard_rabi_2025_26",         "Mustard – Rabi 2025-26",    3,  "Sown Oct-Nov 2025, harvested Feb-Mar 2026"),
    ("oilseeds", "mustard_rabi_2024_25",         "Mustard – Rabi 2024-25",    4,  "Sown Oct-Nov 2024, harvested Feb-Mar 2025"),

    # Sunflower: Kharif + Rabi
    ("oilseeds", "sunflower_kharif_2025",        "Sunflower – Kharif 2025",   5,  "Sown May-Jun 2025, harvested Sep 2025"),
    ("oilseeds", "sunflower_rabi_2025_26",       "Sunflower – Rabi 2025-26",  6,  "Sown Oct 2025, harvested Feb 2026"),

    # Sesame (Til): Kharif + Rabi
    ("oilseeds", "sesame_kharif_2025",           "Sesame (Til) – Kharif 2025", 7, "Sown Jun-Jul 2025, harvested Sep 2025"),
    ("oilseeds", "sesame_rabi_2025_26",          "Sesame (Til) – Rabi 2025-26", 8, "Sown Oct 2025, harvested Dec 2025"),

    # Linseed: Rabi
    ("oilseeds", "linseed_rabi_2025_26",         "Linseed – Rabi 2025-26",    9,  "Sown Oct-Nov 2025, harvested Feb-Mar 2026"),

    # ── CASH CROPS ────────────────────────────────────────────────────────
    # Cotton: Kharif only
    ("cash_crops", "cotton_kharif_2025",         "Cotton – Kharif 2025",      1,  "Sown Apr-Jun 2025, harvested Nov-Dec 2025"),
    ("cash_crops", "cotton_kharif_2024",         "Cotton – Kharif 2024",      2,  "Sown Apr-Jun 2024, harvested Nov-Dec 2024"),

    # Sugarcane: long-duration; planted in spring and autumn cycles
    ("cash_crops", "sugarcane_spring_2025",      "Sugarcane – Spring 2025",   3,  "Planted Feb-Mar 2025, harvested Nov 2025-Jan 2026"),
    ("cash_crops", "sugarcane_autumn_2025",      "Sugarcane – Autumn 2025",   4,  "Planted Sep-Oct 2025, harvested Aug-Oct 2026"),
    ("cash_crops", "sugarcane_spring_2026",      "Sugarcane – Spring 2026",   5,  "Planted Feb-Mar 2026, harvested Nov 2026-Jan 2027"),

    # Jute: Kharif, eastern India
    ("cash_crops", "jute_kharif_2025",           "Jute – Kharif 2025",        6,  "Sown Mar-May 2025, harvested Jul-Sep 2025"),

    # Tobacco: Rabi
    ("cash_crops", "tobacco_rabi_2025_26",       "Tobacco – Rabi 2025-26",    7,  "Sown Oct 2025, transplanted Nov, harvested Feb 2026"),

    # ── VEGETABLES ────────────────────────────────────────────────────────
    # Potato: Rabi (main) + Kharif (hills)
    ("vegetables", "potato_rabi_2025_26",        "Potato – Rabi 2025-26",     1,  "Sown Oct-Nov 2025, harvested Jan-Feb 2026"),
    ("vegetables", "potato_kharif_2025",         "Potato – Kharif 2025 (Hills)", 2, "Hill stations; sown Apr-May 2025, harvested Aug-Sep 2025"),

    # Onion: Kharif + Rabi
    ("vegetables", "onion_kharif_2025",          "Onion – Kharif 2025",       3,  "Sown Jun 2025, harvested Sep-Oct 2025"),
    ("vegetables", "onion_rabi_2025_26",         "Onion – Rabi 2025-26",      4,  "Sown Oct-Nov 2025, transplanted Nov, harvested Mar 2026"),

    # Tomato: Year-round; main periods
    ("vegetables", "tomato_kharif_2025",         "Tomato – Kharif 2025",      5,  "Sown Jun-Jul 2025, harvested Sep-Nov 2025"),
    ("vegetables", "tomato_rabi_2025_26",        "Tomato – Rabi 2025-26",     6,  "Sown Oct 2025, transplanted Nov, harvested Jan-Mar 2026"),
    ("vegetables", "tomato_zaid_2026",           "Tomato – Zaid 2026",        7,  "Summer crop; sown Feb 2026, harvested May-Jun 2026"),

    # Chilli: Kharif + Rabi
    ("vegetables", "chilli_kharif_2025",         "Chilli – Kharif 2025",      8,  "Sown May-Jun 2025, harvested Oct-Nov 2025"),
    ("vegetables", "chilli_rabi_2025_26",        "Chilli – Rabi 2025-26",     9,  "Sown Sep-Oct 2025, harvested Jan-Mar 2026"),

    # Bottle Gourd / Watermelon / Cucumber: Zaid specialty
    ("vegetables", "cucumber_zaid_2026",         "Cucumber – Zaid 2026",      10, "Summer crop; sown Mar 2026, harvested May-Jun 2026"),
    ("vegetables", "watermelon_zaid_2026",       "Watermelon – Zaid 2026",    11, "Summer crop; sown Feb-Mar 2026, harvested May 2026"),
    ("vegetables", "bitter_gourd_zaid_2026",     "Bitter Gourd – Zaid 2026",  12, "Summer crop; sown Mar 2026, harvested Jun 2026"),

    # Brinjal / Eggplant
    ("vegetables", "brinjal_kharif_2025",        "Brinjal – Kharif 2025",     13, "Sown Jun 2025, harvested Sep-Nov 2025"),
    ("vegetables", "brinjal_rabi_2025_26",       "Brinjal – Rabi 2025-26",    14, "Sown Oct 2025, harvested Jan-Mar 2026"),

    # ── HORTICULTURE & FRUITS ─────────────────────────────────────────────
    # Perennial/plantation crops don't have seasonal codes — use year of planting
    ("horticulture", "mango_2025",               "Mango – 2025",              1,  "Flowers Jan-Mar; fruit harvested May-Jul 2025"),
    ("horticulture", "banana_2025",              "Banana – 2025",             2,  "12-15 month crop; planted 2025"),
    ("horticulture", "coconut_2025",             "Coconut – 2025",            3,  "Perennial; year 2025 tracking"),
    ("horticulture", "papaya_2025",              "Papaya – 2025",             4,  "Planted 2025; fruits from 9th month"),
    ("horticulture", "guava_2025",               "Guava – 2025",              5,  "Feb-Mar flowering; harvested May-Jul 2025"),
    ("horticulture", "pomegranate_2025",         "Pomegranate – 2025",        6,  "Ambe bahar / Mrig bahar 2025"),
    ("horticulture", "grapes_2025_26",           "Grapes – 2025-26",          7,  "Pruned Jun-Jul 2025, harvested Jan-Feb 2026"),

    # ── SPICES & CONDIMENTS ───────────────────────────────────────────────
    # Turmeric: Kharif
    ("spices_condiments", "turmeric_kharif_2025",   "Turmeric – Kharif 2025",  1, "Sown May-Jun 2025, harvested Jan-Mar 2026 (9-10 months)"),

    # Coriander: Rabi
    ("spices_condiments", "coriander_rabi_2025_26", "Coriander – Rabi 2025-26", 2, "Sown Oct-Nov 2025, harvested Feb-Mar 2026"),

    # Cumin (Jeera): Rabi
    ("spices_condiments", "cumin_rabi_2025_26",     "Cumin (Jeera) – Rabi 2025-26", 3, "Sown Oct-Nov 2025, harvested Feb 2026"),

    # Fenugreek: Rabi
    ("spices_condiments", "fenugreek_rabi_2025_26", "Fenugreek – Rabi 2025-26", 4, "Sown Oct-Nov 2025, harvested Jan-Feb 2026"),

    # Cardamom: perennial
    ("spices_condiments", "cardamom_2025",           "Cardamom – 2025",          5, "Perennial spice; 2025 growth cycle"),

    # Ginger: Kharif
    ("spices_condiments", "ginger_kharif_2025",      "Ginger – Kharif 2025",     6, "Sown May-Jun 2025, harvested Jan-Feb 2026"),

    # Black Pepper: perennial
    ("spices_condiments", "black_pepper_2025",       "Black Pepper – 2025",      7, "Perennial vine; 2025 harvest cycle"),

    # ── FODDER & FORAGE ───────────────────────────────────────────────────
    ("fodder_forage", "napier_grass_2025",         "Napier Grass – 2025",       1, "Perennial fast-growing fodder; 2025"),
    ("fodder_forage", "lucerne_rabi_2025_26",      "Lucerne (Alfalfa) – Rabi 2025-26", 2, "Sown Sep-Oct 2025, cut multiple times"),
    ("fodder_forage", "berseem_rabi_2025_26",      "Berseem – Rabi 2025-26",    3, "Egyptian clover; sown Oct-Nov 2025, multiple cuts till Apr 2026"),
    ("fodder_forage", "sorghum_fodder_kharif_2025","Sorghum Fodder – Kharif 2025", 4, "Green fodder sorghum; Jun-Jul 2025"),
]


# ---------------------------------------------------------------------------
# Seeder function
# ---------------------------------------------------------------------------

def seed_crop_types():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("  Seeding Indian Crop Categories and Types")
        print("=" * 60)

        # ── 1. Categories ─────────────────────────────────────────────────
        cat_map = {}  # code → CropCategory instance
        for cat_data in CATEGORIES:
            existing = db.query(CropCategory).filter(CropCategory.code == cat_data["code"]).first()
            if existing:
                print(f"  [SKIP]  Category already exists: {cat_data['code']}")
                cat_map[cat_data["code"]] = existing
                continue

            cat = CropCategory(
                id=uuid4(),
                code=cat_data["code"],
                sort_order=cat_data["sort_order"],
                is_active=True,
            )
            db.add(cat)
            db.flush()

            trans = CropCategoryTranslation(
                id=uuid4(),
                crop_category_id=cat.id,
                language_code="en",
                name=cat_data["name_en"],
                description=cat_data["desc_en"],
            )
            db.add(trans)
            cat_map[cat_data["code"]] = cat
            print(f"  [NEW]   Category: {cat_data['name_en']}")

        db.flush()

        # ── 2. Crop Types ─────────────────────────────────────────────────
        created = 0
        skipped = 0
        for (cat_code, crop_code, crop_name, sort_order, desc) in CROP_TYPES:
            existing = db.query(CropType).filter(CropType.code == crop_code).first()
            if existing:
                skipped += 1
                continue

            category = cat_map.get(cat_code)
            if not category:
                print(f"  [WARN]  Category '{cat_code}' not found for crop '{crop_code}'. Skipping.")
                continue

            crop_type = CropType(
                id=uuid4(),
                category_id=category.id,
                code=crop_code,
                sort_order=sort_order,
                is_active=True,
            )
            db.add(crop_type)
            db.flush()

            trans = CropTypeTranslation(
                id=uuid4(),
                crop_type_id=crop_type.id,
                language_code="en",
                name=crop_name,
                description=desc,
            )
            db.add(trans)
            created += 1

        db.commit()
        print(f"\n  Done! Created {created} crop types, skipped {skipped} existing.")

    except Exception as e:
        db.rollback()
        print(f"\n  ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_crop_types()
