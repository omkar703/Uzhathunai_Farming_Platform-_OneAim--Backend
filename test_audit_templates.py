"""Test audit templates endpoint"""
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Check if we have the template we created
print("=== Audit Templates in Database ===")
result = db.execute(text("""
    SELECT id, code, is_system_defined
    FROM templates
    WHERE is_active = true
    LIMIT 5
""")).fetchall()

print(f"Found {len(result)} templates:")
for r in result:
    print(f"  - Code: {r.code} | System: {r.is_system_defined} | ID: {r.id}")

# Get a detailed look at one template
if result:
    template_id = result[0].id
    print(f"\n=== Template Details for {result[0].code} ===")
    
    # Get translations
    trans = db.execute(text(f"""
        SELECT language_code, name, description
        FROM template_translations
        WHERE template_id = '{template_id}'
    """)).fetchall()
    
    print(f"Translations: {len(trans)}")
    for t in trans:
        print(f"  - {t.language_code}: {t.name}")
    
    # Get sections
    sections = db.execute(text(f"""
        SELECT ts.id, s.code, COUNT(tp.id) as param_count
        FROM template_sections ts
        JOIN sections s ON ts.section_id = s.id
        LEFT JOIN template_parameters tp ON tp.template_section_id = ts.id
        WHERE ts.template_id = '{template_id}'
        GROUP BY ts.id, s.code
    """)).fetchall()
    
    print(f"Sections: {len(sections)}")
    for s in sections:
        print(f"  - Section: {s.code} | Parameters: {s.param_count}")

db.close()
