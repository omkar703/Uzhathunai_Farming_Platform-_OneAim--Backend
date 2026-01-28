"""
Diagnostic script to test schedule template access for FSP user.
"""
import sys
import os
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.services.schedule_template_service import ScheduleTemplateService
from sqlalchemy import text

def test_fsp_template_access():
    db = SessionLocal()
    try:
        # FSP user ID from previous inspection
        fsp_user_id = '74b6458f-e7ee-46f3-8261-eb98eda69bd2'
        
        print(f"Testing template access for FSP user: {fsp_user_id}")
        print("=" * 60)
        
        # Check user's organizations
        print("\n1. Checking user's organization memberships:")
        org_memberships = db.execute(text(f"""
            SELECT om.organization_id, o.name, o.organization_type
            FROM org_members om
            JOIN organizations o ON om.organization_id = o.id
            WHERE om.user_id = '{fsp_user_id}'
        """)).fetchall()
        
        if not org_memberships:
            print("   ❌ User has NO organization memberships!")
        else:
            for om in org_memberships:
                print(f"   ✓ Org: {om.name} ({om.organization_type}) - ID: {om.organization_id}")
        
        # Check system templates
        print("\n2. Checking system-defined templates:")
        system_templates = db.execute(text("""
            SELECT COUNT(*) as count
            FROM schedule_templates
            WHERE is_system_defined = true AND is_active = true
        """)).fetchone()
        print(f"   Total system templates: {system_templates.count}")
        
        # Test the service method
        print("\n3. Testing ScheduleTemplateService.get_templates():")
        service = ScheduleTemplateService(db)
        templates, total = service.get_templates(
            user_id=fsp_user_id,
            page=1,
            limit=20
        )
        
        print(f"   Templates returned: {len(templates)}")
        print(f"   Total count: {total}")
        
        if templates:
            print("\n   Sample templates:")
            for t in templates[:3]:
                print(f"   - {t.code} (System: {t.is_system_defined}, Owner: {t.owner_org_id})")
        else:
            print("   ❌ NO TEMPLATES RETURNED!")
            
            # Debug: Check what the query would return
            print("\n4. Debugging - Manual query simulation:")
            user_org_ids = db.execute(text(f"""
                SELECT organization_id FROM org_members WHERE user_id = '{fsp_user_id}'
            """)).fetchall()
            user_org_ids_list = [str(org[0]) for org in user_org_ids]
            
            print(f"   User org IDs: {user_org_ids_list}")
            
            # Try direct query
            if user_org_ids_list:
                org_ids_str = "', '".join(user_org_ids_list)
                query = f"""
                    SELECT id, code, is_system_defined, owner_org_id
                    FROM schedule_templates
                    WHERE is_active = true
                    AND (is_system_defined = true OR owner_org_id IN ('{org_ids_str}'))
                    LIMIT 5
                """
            else:
                query = """
                    SELECT id, code, is_system_defined, owner_org_id
                    FROM schedule_templates
                    WHERE is_active = true AND is_system_defined = true
                    LIMIT 5
                """
            
            results = db.execute(text(query)).fetchall()
            print(f"   Direct query returned: {len(results)} templates")
            for r in results:
                print(f"   - {r.code}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_fsp_template_access()
