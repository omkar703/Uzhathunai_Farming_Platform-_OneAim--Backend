"""
Answer Audit Template Questions for Frontend Team
"""
from app.core.database import SessionLocal
from sqlalchemy import text
import uuid
from datetime import datetime

db = SessionLocal()

print("=" * 80)
print("QUESTION 1: List all audit templates in the database")
print("=" * 80)

# Query all templates with their translations and organization info
result = db.execute(text("""
    SELECT 
        t.id, 
        t.code,
        t.is_system_defined,
        t.owner_org_id,
        tt.name as template_name,
        tt.language_code,
        o.name as org_name
    FROM templates t
    LEFT JOIN template_translations tt ON t.id = tt.template_id AND tt.language_code = 'en'
    LEFT JOIN organizations o ON t.owner_org_id = o.id
    WHERE t.is_active = true
    ORDER BY t.created_at DESC
""")).fetchall()

print(f"\n✅ Found {len(result)} audit template(s):\n")
print(f"{'ID':<38} | {'Name':<30} | {'Organization':<40}")
print("-" * 115)

for r in result:
    template_id = str(r.id)
    template_name = r.template_name or r.code
    org_info = r.org_name if r.org_name else ("System-wide template" if r.is_system_defined else "No organization")
    print(f"{template_id:<38} | {template_name:<30} | {org_info:<40}")

print("\n" + "=" * 80)
print("QUESTION 2: Create a simple audit template for FSP organization")
print("=" * 80)

# The FSP organization ID
fsp_org_id = "5504357f-21a4-4877-b78e-37f8fe7dfec5"

# Check if organization exists
org_check = db.execute(text(f"""
    SELECT id, name FROM organizations WHERE id = '{fsp_org_id}'
""")).fetchone()

if not org_check:
    print(f"\n❌ ERROR: Organization {fsp_org_id} not found!")
else:
    print(f"\n✅ Organization found: {org_check.name}")
    
    # Generate IDs
    template_id = str(uuid.uuid4())
    section_id = str(uuid.uuid4())
    template_section_id = str(uuid.uuid4())
    param1_id = str(uuid.uuid4())
    param2_id = str(uuid.uuid4())
    param3_id = str(uuid.uuid4())
    template_param1_id = str(uuid.uuid4())
    template_param2_id = str(uuid.uuid4())
    template_param3_id = str(uuid.uuid4())
    
    # Create timestamp
    now = datetime.utcnow().isoformat()
    
    # Get any user for created_by (not critical for test template)
    user = db.execute(text(f"""
        SELECT id FROM users LIMIT 1
    """)).fetchone()
    
    created_by = str(user.id) if user else None
    
    try:
        # 1. Create the template
        db.execute(text(f"""
            INSERT INTO templates (
                id, code, crop_type_id, is_system_defined, owner_org_id, 
                version, is_active, created_at, updated_at, created_by, updated_by
            ) VALUES (
                '{template_id}', 'FSP_TEST_TEMPLATE_V1', NULL, false, '{fsp_org_id}',
                1, true, '{now}', '{now}', '{created_by}', '{created_by}'
            )
        """))
        
        # 2. Create template translation
        db.execute(text(f"""
            INSERT INTO template_translations (
                id, template_id, language_code, name, description
            ) VALUES (
                '{uuid.uuid4()}', '{template_id}', 'en', 
                'FSP Test Audit Template', 
                'A simple test template for FSP testing purposes with basic quality checks'
            )
        """))
        
        # 3. Create the section
        db.execute(text(f"""
            INSERT INTO sections (
                id, code, is_system_defined, created_at, updated_at
            ) VALUES (
                '{section_id}', 'QUALITY_CHECK', false, '{now}', '{now}'
            )
        """))
        
        # 4. Create section translation
        db.execute(text(f"""
            INSERT INTO section_translations (
                id, section_id, language_code, name, description
            ) VALUES (
                '{uuid.uuid4()}', '{section_id}', 'en',
                'Quality Check',
                'Basic quality assessment parameters'
            )
        """))
        
        # 5. Link section to template
        db.execute(text(f"""
            INSERT INTO template_sections (
                id, template_id, section_id, sort_order, created_at
            ) VALUES (
                '{template_section_id}', '{template_id}', '{section_id}', 1, '{now}'
            )
        """))
        
        # 6. Create parameters
        # Parameter 1: Crop Health (options)
        db.execute(text(f"""
            INSERT INTO parameters (
                id, code, data_type, unit_of_measurement_id, option_set_id, 
                is_mandatory, validation_rules, is_system_defined, 
                created_at, updated_at
            ) VALUES (
                '{param1_id}', 'CROP_HEALTH_STATUS', 'options', NULL, NULL,
                true, '{{"min_options": 1, "max_options": 1}}', false,
                '{now}', '{now}'
            )
        """))
        
        db.execute(text(f"""
            INSERT INTO parameter_translations (
                id, parameter_id, language_code, name, description, help_text
            ) VALUES (
                '{uuid.uuid4()}', '{param1_id}', 'en',
                'Crop Health Status',
                'Overall health assessment of the crop',
                'Select the current health status of the crop'
            )
        """))
        
        # Parameter 2: Pest Presence (boolean)
        db.execute(text(f"""
            INSERT INTO parameters (
                id, code, data_type, unit_of_measurement_id, option_set_id, 
                is_mandatory, validation_rules, is_system_defined, 
                created_at, updated_at
            ) VALUES (
                '{param2_id}', 'PEST_PRESENCE', 'boolean', NULL, NULL,
                true, '{{}}', false,
                '{now}', '{now}'
            )
        """))
        
        db.execute(text(f"""
            INSERT INTO parameter_translations (
                id, parameter_id, language_code, name, description, help_text
            ) VALUES (
                '{uuid.uuid4()}', '{param2_id}', 'en',
                'Pest Presence',
                'Indicate if pests are present',
                'Check this if any pests are observed on the crop'
            )
        """))
        
        # Parameter 3: Growth Rating (decimal)
        db.execute(text(f"""
            INSERT INTO parameters (
                id, code, data_type, unit_of_measurement_id, option_set_id, 
                is_mandatory, validation_rules, is_system_defined, 
                created_at, updated_at
            ) VALUES (
                '{param3_id}', 'GROWTH_RATING', 'decimal', NULL, NULL,
                false, '{{"min": 0, "max": 10, "decimal_places": 1}}', false,
                '{now}', '{now}'
            )
        """))
        
        db.execute(text(f"""
            INSERT INTO parameter_translations (
                id, parameter_id, language_code, name, description, help_text
            ) VALUES (
                '{uuid.uuid4()}', '{param3_id}', 'en',
                'Growth Rating',
                'Rate the crop growth progress',
                'Provide a rating from 0 to 10 (0 = poor, 10 = excellent)'
            )
        """))
        
        # 7. Link parameters to template section
        # Note: is_required based on the validation_rules from parameter definition
        params_config = [
            (param1_id, template_param1_id, True),  # Crop Health - mandatory
            (param2_id, template_param2_id, True),  # Pest Presence - mandatory
            (param3_id, template_param3_id, False), # Growth Rating - optional
        ]
        
        for i, (param_id, template_param_id, is_required) in enumerate(params_config, start=1):
            db.execute(text(f"""
                INSERT INTO template_parameters (
                    id, template_section_id, parameter_id, is_required, 
                    sort_order, created_at
                ) VALUES (
                    '{template_param_id}', '{template_section_id}', '{param_id}', {is_required},
                    {i}, '{now}'
                )
            """))
        
        db.commit()
        
        print(f"\n✅ Successfully created test audit template!")
        print(f"\n📋 Template Details:")
        print(f"   Template ID: {template_id}")
        print(f"   Template Name: FSP Test Audit Template")
        print(f"   Template Code: FSP_TEST_TEMPLATE_V1")
        print(f"   Organization: {org_check.name} ({fsp_org_id})")
        print(f"\n📁 Section: Quality Check")
        print(f"   Section ID: {section_id}")
        print(f"\n🔧 Parameters:")
        print(f"   1. Crop Health Status (options) - Mandatory")
        print(f"   2. Pest Presence (boolean) - Mandatory")
        print(f"   3. Growth Rating (decimal 0-10) - Optional")
        
        print(f"\n🎯 TEMPLATE ID FOR FRONTEND: {template_id}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating template: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("SUMMARY FOR FRONTEND TEAM")
print("=" * 80)

# Re-query all templates after creation
final_result = db.execute(text("""
    SELECT 
        t.id, 
        t.code,
        tt.name as template_name,
        o.name as org_name,
        COUNT(DISTINCT ts.id) as section_count
    FROM templates t
    LEFT JOIN template_translations tt ON t.id = tt.template_id AND tt.language_code = 'en'
    LEFT JOIN organizations o ON t.owner_org_id = o.id
    LEFT JOIN template_sections ts ON t.id = ts.template_id
    WHERE t.is_active = true
    GROUP BY t.id, t.code, tt.name, o.name
    ORDER BY t.created_at DESC
""")).fetchall()

print(f"\n📊 Total Templates Available: {len(final_result)}")
for r in final_result:
    print(f"\n   • {r.template_name or r.code}")
    print(f"     ID: {r.id}")
    print(f"     Organization: {r.org_name or 'System'}")
    print(f"     Sections: {r.section_count}")

db.close()
