
import sys
import os
import uuid
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.template import Template, TemplateSection, TemplateParameter, TemplateTranslation, TemplateSection
from app.models.organization import Organization
from app.models.fsp_service import FSPServiceListing, MasterService
from app.models.schedule_template import ScheduleTemplate, ScheduleTemplateTask, ScheduleTemplateTranslation
from app.models.user import User
from app.models.enums import ServiceStatus

def seed_audit_service():
    db = SessionLocal()
    try:
        print("Starting seed process...")
        
        # 1. Constants
        AUDIT_TEMPLATE_CODE = 'SOIL_AUDIT_V1'
        SCHEDULE_TEMPLATE_CODE = 'SOIL_AUDIT_SCHED'
        SERVICE_NAME = 'Standard Soil Audit'
        
        # 2. Fetch FSP Organization and Owner
        org_name = "GreenOps FSP Services"
        owner_email = "fsp_manager@gmail.com"

        org = db.query(Organization).filter(Organization.name == org_name).first()
        if not org:
            print(f"Error: Organization '{org_name}' not found! Please run seed_farm_fsp_full.py first.")
            return
        FSP_ORG_ID = str(org.id)

        user = db.query(User).filter(User.email == owner_email).first()
        if not user:
             print(f"Error: User '{owner_email}' not found!")
             # Fallback to org creator if specific user not found (though unlikely)
             user = db.query(User).filter(User.id == org.created_by).first()
             if not user:
                 print("Error: Could not determine FSP Owner.")
                 return
        FSP_OWNER_ID = str(user.id)

        print(f"Found Organization: {org.name} ({FSP_ORG_ID})")
        print(f"Found Owner: {user.email} ({FSP_OWNER_ID})")

        # 3. Create Audit Template (Template model)
        print("\nCreating Audit Template...")
        template = db.query(Template).filter(Template.code == AUDIT_TEMPLATE_CODE).first()
        if not template:
            template = Template(
                id=uuid.uuid4(),
                code=AUDIT_TEMPLATE_CODE,
                is_system_defined=False,
                owner_org_id=uuid.UUID(FSP_ORG_ID),
                is_active=True,
                version=1,
                created_by=uuid.UUID(FSP_OWNER_ID),
                updated_by=uuid.UUID(FSP_OWNER_ID)
                # crop_type_id is optional, leaving null for general audit
            )
            db.add(template)
            db.flush()
            
            # Add Translation
            trans = TemplateTranslation(
                template_id=template.id,
                language_code='en',
                name=SERVICE_NAME,
                description="Comprehensive soil health analysis"
            )
            db.add(trans)
            
            # Add Section (SOIL_CONDITION) - Assuming section exists from DML
            section_code = 'SOIL_CONDITION'
            # Find existing section ID from sections table (assuming it's seeded)
            # DML says: ('SOIL_CONDITION', true, NULL, true)
            section_res = db.execute(text(f"SELECT id FROM sections WHERE code = '{section_code}'")).fetchone()
            if section_res:
                section_id = section_res[0]
                
                # Link Section to Template
                tmpl_section = TemplateSection(
                    id=uuid.uuid4(),
                    template_id=template.id,
                    section_id=section_id,
                    sort_order=1
                )
                db.add(tmpl_section)
                db.flush()
                
                # Add Parameter (SOIL_MOISTURE) - Assuming parameter exists from DML
                # DML says: ('SOIL_MOISTURE', 'SINGLE_SELECT', true, NULL, true)
                param_code = 'SOIL_MOISTURE'
                param_res = db.execute(text(f"SELECT id, parameter_metadata FROM parameters WHERE code = '{param_code}'")).fetchone()
                
                if param_res:
                    param_id = param_res[0]
                    param_meta = param_res[1]
                    
                    # Link Parameter to Template Section
                    tmpl_param = TemplateParameter(
                        id=uuid.uuid4(),
                        template_section_id=tmpl_section.id,
                        parameter_id=param_id,
                        is_required=True,
                        sort_order=1,
                        parameter_snapshot={
                             "parameter_id": str(param_id),
                             "code": param_code,
                             "parameter_type": "SINGLE_SELECT",
                             "parameter_metadata": param_meta
                        }
                    )
                    db.add(tmpl_param)
            
            print(f"Created Audit Template: {template.id}")
        else:
            print(f"Audit Template {AUDIT_TEMPLATE_CODE} already exists: {template.id}")

        # 4. Create Schedule Template (Farming Schedule)
        print("\nCreating Farming Schedule Template...")
        sched_template = db.query(ScheduleTemplate).filter(ScheduleTemplate.code == SCHEDULE_TEMPLATE_CODE).first()
        if not sched_template:
            sched_template = ScheduleTemplate(
                id=uuid.uuid4(),
                code=SCHEDULE_TEMPLATE_CODE,
                is_system_defined=False,
                owner_org_id=uuid.UUID(FSP_ORG_ID),
                is_active=True,
                version=1,
                notes="Schedule for Soil Audit Work Order",
                created_by=uuid.UUID(FSP_OWNER_ID),
                updated_by=uuid.UUID(FSP_OWNER_ID)
            )
            db.add(sched_template)
            db.flush()

            # Translation
            sched_trans = ScheduleTemplateTranslation(
                schedule_template_id=sched_template.id,
                language_code='en',
                name=SERVICE_NAME,
                description="Schedule task for soil audit execution"
            )
            db.add(sched_trans)

            # Add Task (CROP_AUDIT) - Day 0
            task_res = db.execute(text("SELECT id FROM tasks WHERE code = 'CROP_AUDIT'")).fetchone()
            if task_res:
                task_id = task_res[0]
                
                sched_task = ScheduleTemplateTask(
                    id=uuid.uuid4(),
                    schedule_template_id=sched_template.id,
                    task_id=task_id,
                    day_offset=0,
                    task_details_template={}, # Empty JSON
                    sort_order=1,
                    created_by=uuid.UUID(FSP_OWNER_ID),
                    updated_by=uuid.UUID(FSP_OWNER_ID)
                )
                db.add(sched_task)
            
            print(f"Created Schedule Template: {sched_template.id}")
        else:
            print(f"Schedule Template {SCHEDULE_TEMPLATE_CODE} already exists: {sched_template.id}")

        # 5. Create FSP Service Listing
        print("\nCreating FSP Service Listing...")
        # Get Master Service ID for CONSULTANCY
        master_service_res = db.execute(text("SELECT id FROM master_services WHERE code = 'CONSULTANCY'")).fetchone()
        if not master_service_res:
             print("Error: CONSULTANCY master service not found!")
             return
        
        master_service_id = master_service_res[0]

        # Check if listing already exists
        listing = db.query(FSPServiceListing).filter(
            FSPServiceListing.fsp_organization_id == uuid.UUID(FSP_ORG_ID),
            FSPServiceListing.service_id == master_service_id,
            FSPServiceListing.title == SERVICE_NAME
        ).first()

        if not listing:
            listing = FSPServiceListing(
                id=uuid.uuid4(),
                fsp_organization_id=uuid.UUID(FSP_ORG_ID),
                service_id=master_service_id,
                title=SERVICE_NAME,
                description="Professional soil testing and analysis service",
                service_area_districts=["Erode", "Coimbatore"], # Sample districts
                pricing_model="FIXED",
                base_price=500.00,
                currency="INR",
                status=ServiceStatus.ACTIVE,
                created_by=uuid.UUID(FSP_OWNER_ID),
                updated_by=uuid.UUID(FSP_OWNER_ID)
            )
            db.add(listing)
            db.commit()
            print(f"Created Service Listing: {listing.id}")
        else:
            print(f"Service Listing already exists: {listing.id}")
            
        print("\n===========================================")
        print(f"SERVICE LISTING ID: {listing.id}")
        print("===========================================")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_audit_service()
