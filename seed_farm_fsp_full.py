
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
from app.core.security import get_password_hash
from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.fsp_service import FSPServiceListing, MasterService, MasterServiceTranslation
from app.models.template import Template, TemplateTranslation, TemplateSection, TemplateParameter
from app.models.schedule_template import ScheduleTemplate, ScheduleTemplateTranslation, ScheduleTemplateTask
from app.models.farm import Farm
from app.models.plot import Plot
from app.models.crop import Crop
from app.models.crop import Crop
from app.models.crop_data import CropCategory, CropCategoryTranslation, CropType, CropTypeTranslation
from app.models.enums import (
    OrganizationType, OrganizationStatus, MemberStatus, ServiceStatus, 
    AuditStatus, CropLifecycle, MeasurementUnitCategory, TaskStatus
)
from app.models.rbac import Role

def seed_farm_fsp_full():
    db = SessionLocal()
    try:
        print("Starting FULL Farm-FSP seed process...")
        
        # --- 1. User Creation ---
        print("\n--- 1. Users ---")
        
        users_to_create = [
            {"email": "fsp1@gmail.com", "name": "FSP Admin", "password": "Test@12345"},
            {"email": "niren@gmail.com", "name": "Niren Farmer", "password": "Test@12345"},
            {"email": "fsp_manager@gmail.com", "name": "FSP Manager", "password": "Test@12345"},
            {"email": "fsp_agent@gmail.com", "name": "FSP Agent", "password": "Test@12345"},
            {"email": "fsp_expert@gmail.com", "name": "FSP Expert", "password": "Test@12345"},
        ]
        
        created_users = {}
        
        for u_data in users_to_create:
            user = db.query(User).filter(User.email == u_data["email"]).first()
            if not user:
                user = User(
                    id=uuid.uuid4(),
                    email=u_data["email"],
                    password_hash=get_password_hash(u_data["password"]),
                    first_name=u_data["name"].split()[0],
                    last_name=u_data["name"].split()[1] if len(u_data["name"].split()) > 1 else "",
                    phone=f"+91{uuid.uuid4().int % 10000000000:010d}", # Random phone
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                db.commit()
                print(f"Created User: {u_data['email']}")
            else:
                print(f"User exists: {u_data['email']}")
            
            created_users[u_data["email"]] = user

        fsp_admin = created_users["fsp1@gmail.com"]
        farmer_admin = created_users["niren@gmail.com"]
        
        # --- 2. FSP Organization ---
        print("\n--- 2. FSP Organization ---")
        
        fsp_org_name = "GreenOps FSP Services"
        fsp_org = db.query(Organization).filter(Organization.name == fsp_org_name).first()
        
        if not fsp_org:
            fsp_org = Organization(
                id=uuid.uuid4(),
                name=fsp_org_name,
                organization_type=OrganizationType.FSP,
                status=OrganizationStatus.ACTIVE,
                contact_email="contact@greenops.com",
                created_by=fsp_admin.id,
                updated_by=fsp_admin.id
            )
            db.add(fsp_org)
            db.commit()
            
            # Also add fsp_admin as FSP_OWNER
            role = db.query(Role).filter(Role.code == "FSP_OWNER").first()
            if role:
                member = OrgMember(id=uuid.uuid4(), user_id=fsp_admin.id, organization_id=fsp_org.id, status=MemberStatus.ACTIVE)
                db.add(member)
                db.add(OrgMemberRole(id=uuid.uuid4(), user_id=fsp_admin.id, organization_id=fsp_org.id, role_id=role.id, is_primary=True))
                db.commit()
            
            print(f"Created FSP Org: {fsp_org.name}")
        else:
            print(f"FSP Org exists: {fsp_org.name}")

        # Add Members to FSP Org
        fsp_members = [
            {"email": "fsp_manager@gmail.com", "role_code": "FSP_MANAGER"},
            {"email": "fsp_agent@gmail.com", "role_code": "FSP_SUPERVISOR"}, # Usage of supervisor for agent
            {"email": "fsp_expert@gmail.com", "role_code": "CONSULTANT"}, # Usage of consultant for expert
        ]
        
        # Verify roles exist
        for m_data in fsp_members:
            role_code = m_data["role_code"]
            role = db.query(Role).filter(Role.code == role_code).first()
            if not role:
                print(f"Warning: Role {role_code} not found. skipping role assignment.")
                continue
                
            u = created_users[m_data["email"]]
            member = db.query(OrgMember).filter(OrgMember.user_id == u.id, OrgMember.organization_id == fsp_org.id).first()
            if not member:
                member = OrgMember(
                    id=uuid.uuid4(),
                    user_id=u.id,
                    organization_id=fsp_org.id,
                    status=MemberStatus.ACTIVE
                )
                db.add(member)
                db.flush()
                
                # Add Role
                omr = OrgMemberRole(
                    id=uuid.uuid4(),
                    user_id=u.id,
                    organization_id=fsp_org.id,
                    role_id=role.id,
                    is_primary=True,
                    assigned_by=fsp_admin.id
                )
                db.add(omr)
                db.commit()
                print(f"Added member {u.email} as {role_code}")
            else:
                 print(f"Member {u.email} already in FSP Org")

        # --- 3. Services ---
        print("\n--- 3. Services ---")
        # Master Service: General Crop Consultation
        ms_code = "GEN_CROP_CONSULT"
        ms_name = "General Crop Consultation"
        
        master_service = db.query(MasterService).filter(MasterService.code == ms_code).first()
        if not master_service:
            master_service = MasterService(
                id=uuid.uuid4(),
                code=ms_code,
                name=ms_name,
                description="General consultation for crop health and yield",
                status=ServiceStatus.ACTIVE
            )
            db.add(master_service)
            db.commit() # commit to get ID
            
            # Translation
            ms_trans = MasterServiceTranslation(
                id=uuid.uuid4(),
                service_id=master_service.id,
                language_code="en",
                display_name=ms_name,
                description=master_service.description
            )
            db.add(ms_trans)
            db.commit()
            print(f"Created Master Service: {ms_name}")
        else:
            print(f"Master Service exists: {ms_name}")
            
        # Organization Service Listing
        listing = db.query(FSPServiceListing).filter(
            FSPServiceListing.fsp_organization_id == fsp_org.id, 
            FSPServiceListing.service_id == master_service.id
        ).first()
        
        if not listing:
            listing = FSPServiceListing(
                id=uuid.uuid4(),
                fsp_organization_id=fsp_org.id,
                service_id=master_service.id,
                title="GreenOps Expert Consultation",
                description="Expert advice from our top agronomists",
                pricing_model="FIXED",
                base_price=1000.0,
                currency="INR",
                status=ServiceStatus.ACTIVE,
                created_by=fsp_admin.id
            )
            db.add(listing)
            db.commit()
            print(f"Created Service Listing: {listing.title}")
        else:
            print(f"Service Listing exists: {listing.title}")

        # --- 4. Templates ---
        print("\n--- 4. Templates ---")
        
        # Audit Template
        at_code = "GEN_CROP_HEALTH_V1"
        audit_template = db.query(Template).filter(Template.code == at_code).first()
        
        if not audit_template:
            audit_template = Template(
                id=uuid.uuid4(),
                code=at_code,
                is_system_defined=False,
                owner_org_id=fsp_org.id,
                is_active=True,
                version=1,
                created_by=fsp_admin.id
            )
            db.add(audit_template)
            db.flush()
            
            # Translation
            db.add(TemplateTranslation(
                template_id=audit_template.id,
                language_code="en",
                name="General Crop Health Audit",
                description="Audit for general crop health"
            ))
            
            # Sections
            sections_data = ["SOIL_SECTION", "PEST_SECTION", "GROWTH_SECTION"]
            
            # Check if these sections exist in DB metadata, if not we might need to create them or fetch existing valid ones
            # For this script I will try to fetch ANY generic sections if my specific ones don't exist
            # Or just use the one we saw in other script: SOIL_CONDITION
            
            # Let's use what we saw in the other script plus generic ones if available
            # We will query the 'sections' table for IDs.
            
            # Fetch 'SOIL_CONDITION'
            section_res = db.execute(text("SELECT id FROM sections WHERE code = 'SOIL_CONDITION'")).fetchone()
            if section_res:
                 # Link Section
                ts_soil = TemplateSection(
                    id=uuid.uuid4(),
                    template_id=audit_template.id,
                    section_id=section_res[0],
                    sort_order=1
                )
                db.add(ts_soil)
                
                # Add Parameter to Section
                param_res = db.execute(text("SELECT id, parameter_metadata FROM parameters WHERE code = 'SOIL_MOISTURE'")).fetchone()
                if param_res:
                    db.add(TemplateParameter(
                        id=uuid.uuid4(),
                        template_section_id=ts_soil.id,
                        parameter_id=param_res[0],
                        is_required=True,
                        sort_order=1,
                        parameter_snapshot={"code": "SOIL_MOISTURE", "parameter_type": "SINGLE_SELECT", "parameter_metadata": param_res[1]}
                    ))
            
            db.commit()
            print(f"Created Audit Template: {at_code}")
        else:
             print(f"Audit Template exists: {at_code}")

        # Schedule Templates
        st_codes = ["WHEAT_120_PLAN", "TOMATO_FERT_CYCLE"]
        st_names = ["Wheat 120-Day Plan", "Tomato Fertilization Cycle"]
        
        created_sched_templates = []
        
        for i, code in enumerate(st_codes):
            st = db.query(ScheduleTemplate).filter(ScheduleTemplate.code == code).first()
            if not st:
                st = ScheduleTemplate(
                    id=uuid.uuid4(),
                    code=code,
                    is_system_defined=False,
                    owner_org_id=fsp_org.id,
                    is_active=True,
                    version=1,
                    created_by=fsp_admin.id
                )
                db.add(st)
                db.flush()
                
                db.add(ScheduleTemplateTranslation(
                    schedule_template_id=st.id,
                    language_code="en",
                    name=st_names[i],
                    description=f"Standard schedule for {st_names[i]}"
                ))
                
                # Add a dummy task
                task_res = db.execute(text("SELECT id FROM tasks LIMIT 1")).fetchone()
                if task_res:
                    db.add(ScheduleTemplateTask(
                        id=uuid.uuid4(),
                        schedule_template_id=st.id,
                        task_id=task_res[0],
                        day_offset=5,
                        task_details_template={},
                        sort_order=1,
                        created_by=fsp_admin.id
                    ))
                
                db.commit()
                created_sched_templates.append(st)
                print(f"Created Schedule Template: {code}")
            else:
                created_sched_templates.append(st)
                print(f"Schedule Template exists: {code}")

        # --- 5. Farmer Data ---
        print("\n--- 5. Farm Data ---")
        
        # Farm Org (Farmer needs an Org too, usually type FARMING)
        farmer_org = db.query(Organization).filter(Organization.created_by == farmer_admin.id).first()
        if not farmer_org:
            farmer_org = Organization(
                id=uuid.uuid4(),
                name="Green Valley Farm Stats",
                organization_type=OrganizationType.FARMING,
                status=OrganizationStatus.ACTIVE,
                created_by=farmer_admin.id,
                updated_by=farmer_admin.id
            )
            db.add(farmer_org)
            db.commit()

            # Also add farmer_admin as OWNER
            role = db.query(Role).filter(Role.code == "OWNER").first()
            if role:
                member = OrgMember(id=uuid.uuid4(), user_id=farmer_admin.id, organization_id=farmer_org.id, status=MemberStatus.ACTIVE)
                db.add(member)
                db.add(OrgMemberRole(id=uuid.uuid4(), user_id=farmer_admin.id, organization_id=farmer_org.id, role_id=role.id, is_primary=True))
                db.commit()

            print(f"Created Farmer Org: {farmer_org.name}")
        else:
            print(f"Farmer Org exists: {farmer_org.name}")

        # Farm
        farm = db.query(Farm).filter(Farm.name == "Green Valley Farm").first()
        if not farm:
            farm = Farm(
                id=uuid.uuid4(),
                organization_id=farmer_org.id,
                name="Green Valley Farm",
                area=10.0,
                area_unit_id=(db.execute(text("SELECT id FROM measurement_units WHERE code = 'ACRE'")).fetchone() or [None])[0],
                created_by=farmer_admin.id
            )
            # Actually let's assume 'ACRE' is valid or leave it null if nullable
            # farm.area_unit_id might be needed instead?
            # Let's look at farm table structure from error if needed.
            db.add(farm)
            db.commit()
            print(f"Created Farm: {farm.name}")
        else:
             print(f"Farm exists: {farm.name}")

        # Plot
        plot = db.query(Plot).filter(Plot.farm_id == farm.id, Plot.name == "Plot A - North Field").first()
        if not plot:
            plot = Plot(
                id=uuid.uuid4(),
                farm_id=farm.id,
                name="Plot A - North Field",
                area=2.5,
                created_by=farmer_admin.id
            )
            db.add(plot)
            db.commit()
            print(f"Created Plot: {plot.name}")
        else:
            print(f"Plot exists: {plot.name}")

        # Crop
        crop = db.query(Crop).filter(Crop.plot_id == plot.id).first()
        if not crop:
            # Get Crop Type 'Wheat'
            # Get or Create Crop Hierarchy for "Wheat"
            # 1. Category
            cat_code = "CEREALS"
            category = db.query(CropCategory).filter(CropCategory.code == cat_code).first()
            if not category:
                category = CropCategory(
                    id=uuid.uuid4(),
                    code=cat_code,
                    is_active=True
                )
                db.add(category)
                db.flush()
                db.add(CropCategoryTranslation(
                    id=uuid.uuid4(),
                    crop_category_id=category.id,
                    language_code="en",
                    name="Cereals",
                    description="Cereal crops"
                ))
                db.commit()
            
            # 2. Type
            type_code = "WHEAT"
            crop_type = db.query(CropType).filter(CropType.code == type_code).first()
            if not crop_type:
                crop_type = CropType(
                    id=uuid.uuid4(),
                    category_id=category.id,
                    code=type_code,
                    is_active=True
                )
                db.add(crop_type)
                db.flush()
                db.add(CropTypeTranslation(
                    id=uuid.uuid4(),
                    crop_type_id=crop_type.id,
                    language_code="en",
                    name="Wheat",
                    description="Wheat crop"
                ))
                db.commit()
            
            crop = Crop(
                id=uuid.uuid4(),
                plot_id=plot.id,
                name="Wheat Season 2026",
                crop_type_id=crop_type.id if crop_type else None,
                lifecycle=CropLifecycle.PRODUCTION,
                planted_date=datetime.now(),
                created_by=farmer_admin.id
            )
            db.add(crop)
            db.commit()
            print(f"Created Crop: {crop.name}")
        else:
            print(f"Crop exists: {crop.name}")

        # --- 6. Report ---
        print("\n--- SEEDING COMPLETE ---")
        report = {
            "fsp_org_id": str(fsp_org.id),
            "farmer_org_id": str(farmer_org.id),
            "audit_template_id": str(audit_template.id),
            "schedule_template_ids": [str(t.id) for t in created_sched_templates],
            "service_id": str(listing.id),
            "service_listing_id": str(listing.id)
        }
        print(json.dumps(report, indent=2))

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_farm_fsp_full()
