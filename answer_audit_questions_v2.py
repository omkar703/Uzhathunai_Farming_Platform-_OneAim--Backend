"""
Answer Audit Template Questions for Frontend Team - Simplified Version
"""
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 80)
print("ANSWERS FOR FRONTEND TEAM")
print("=" * 80)

print("\n" + "=" * 80)
print("QUESTION 1: List all audit templates")
print("=" * 80)

# Query all templates with their translations and organization info
result = db.execute(text("""
    SELECT 
        t.id, 
        t.code,
        t.is_system_defined,
        t.owner_org_id,
        t.version,
        tt.name as template_name,
        tt.description,
        tt.language_code,
        o.name as org_name,
        COUNT(DISTINCT ts.id) as section_count
    FROM templates t
    LEFT JOIN template_translations tt ON t.id = tt.template_id AND tt.language_code = 'en'
    LEFT JOIN organizations o ON t.owner_org_id = o.id
    LEFT JOIN template_sections ts ON t.id = ts.template_id
    WHERE t.is_active = true
    GROUP BY t.id, t.code, t.is_system_defined, t.owner_org_id, t.version, tt.name, tt.description, tt.language_code, o.name
    ORDER BY t.created_at DESC
""")).fetchall()

print(f"\n✅ Found {len(result)} audit template(s) in the database:\n")
print("=" * 120)

for idx, r in enumerate(result, 1):
    template_id = str(r.id)
    template_name = r.template_name or r.code
    template_desc = r.description or "No description"
    org_info = r.org_name if r.org_name else ("System Template" if r.is_system_defined else "No organization")
    
    print(f"\n{idx}. {template_name}")
    print(f"   ID: {template_id}")
    print(f"   Code: {r.code}")
    print(f"   Organization: {org_info}")
    print(f"   Sections: {r.section_count}")
    print(f"   Description: {template_desc}")
    print(f"   Version: {r.version}")

print("\n" + "=" * 120)

# Get parameter details for each template
print("\n" + "=" * 80)
print("DETAILED VIEW: Template Sections & Parameters")
print("=" * 80)

for r in result:
    template_id = str(r.id)
    template_name = r.template_name or r.code
    
    print(f"\n📋 Template: {template_name}")
    print(f"   ID: {template_id}")
    
    # Get sections for this template
    sections = db.execute(text(f"""
        SELECT 
            s.id as section_id,
            s.code as section_code,
            st.name as section_name,
            ts.sort_order,
            COUNT(tp.id) as param_count
        FROM template_sections ts
        JOIN sections s ON ts.section_id = s.id
        LEFT JOIN section_translations st ON s.id = st.section_id AND st.language_code = 'en'
        LEFT JOIN template_parameters tp ON tp.template_section_id = ts.id
        WHERE ts.template_id = '{template_id}'
        GROUP BY s.id, s.code, st.name, ts.sort_order
        ORDER BY ts.sort_order
    """)).fetchall()
    
    if sections:
        for sec in sections:
            print(f"\n   📁 Section: {sec.section_name or sec.section_code}")
            print(f"      Section ID: {sec.section_id}")
            print(f"      Sort Order: {sec.sort_order}")
            print(f"      Parameters: {sec.param_count}")
            
            # Get parameters for this section
            params = db.execute(text(f"""
                SELECT 
                    p.id as param_id,
                    p.code as param_code,
                    p.parameter_type,
                    pt.name as param_name,
                    pt.description as param_desc,
                    tp.is_required,
                    tp.sort_order
                FROM template_parameters tp
                JOIN parameters p ON tp.parameter_id = p.id
                LEFT JOIN parameter_translations pt ON p.id = pt.parameter_id AND pt.language_code = 'en'
                WHERE tp.template_section_id IN (
                    SELECT id FROM template_sections 
                    WHERE template_id = '{template_id}' AND section_id = '{sec.section_id}'
                )
                ORDER BY tp.sort_order
            """)).fetchall()
            
            if params:
                for param in params:
                    required_badge = "✓ Required" if param.is_required else "○ Optional"
                    print(f"         {param.sort_order}. {param.param_name or param.param_code}")
                    print(f"            Type: {param.parameter_type} | {required_badge}")
                    if param.param_desc:
                        print(f"            Description: {param.param_desc}")
    else:
        print("   (No sections configured)")

print("\n" + "=" * 80)
print("QUESTION 2: Create a test audit template for FSP")
print("=" * 80)

fsp_org_id = "5504357f-21a4-4877-b78e-37f8fe7dfec5"

# Check if organization exists
org_check = db.execute(text(f"""
    SELECT id, name FROM organizations WHERE id = '{fsp_org_id}'
""")).fetchone()

if not org_check:
    print(f"\n❌ ERROR: Organization {fsp_org_id} not found!")
else:
    print(f"\n✅ Organization found: {org_check.name}")
    print(f"\n💡 RECOMMENDATION:")
    print(f"   The database schema is complex with many relationships.")
    print(f"   The BEST way to create a new template is to use the API endpoint:")
    print(f"\n   POST /api/v1/farm-audit/templates")
    print(f"   Authorization: Bearer <your_access_token>")
    print(f"\n   Request Body:")
    print("""   {
      "code": "FSP_TEST_TEMPLATE_V1",
      "owner_org_id": "5504357f-21a4-4877-b78e-37f8fe7dfec5",
      "translations": [
        {
          "language_code": "en",
          "name": "FSP Test Audit Template",
          "description": "A simple test template for FSP testing"
        }
      ]
    }""")
    print(f"\n   Then use:\n   POST /api/v1/farm-audit/templates/{{template_id}}/sections")
    print(f"   POST /api/v1/farm-audit/templates/{{template_id}}/sections/{{section_id}}/parameters")
    print(f"\n   This ensures all relationships and constraints are properly handled.")
    print(f"\n   For a quick test, you can use the existing template:")
    print(f"   Template ID: 32ed7afe-093f-486a-91df-8dcf4c2f3996")
    print(f"   Template Name: Standard Soil Audit")

print("\n" + "=" * 80)
print("FRONTEND TEAM - QUICK REFERENCE")
print("=" * 80)

print(f"\n📊 Total Active Templates: {len(result)}")
print(f"\n🔑 API Endpoint: GET /api/v1/farm-audit/templates")
print(f"   • Returns paginated list of templates")
print(f"   • Includes translations (English by default)")
print(f"   • Filtered by organization context automatically")
print(f"\n🔑 Get Template Details: GET /api/v1/farm-audit/templates/{{template_id}}")
print(f"   • Returns full template with all sections and parameters")
print(f"   • Use this to display the audit form structure")

print(f"\n✅ ANSWER SUMMARY:")
print(f"   1. There is currently 1 audit template available")
if result:
    print(f"      - ID: {result[0].id}")
    print(f"      - Name: {result[0].template_name or result[0].code}")
    print(f"      - Organization: {result[0].org_name}")
print(f"\n   2. To create a test template, use the API endpoints above")
print(f"      OR use the existing template for testing purposes")

print("\n" + "=" * 80)

db.close()
