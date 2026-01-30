import sys
import os
import uuid
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.models.organization import Organization
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.template import Template, TemplateSection, TemplateParameter
from app.models.parameter import Parameter
from app.models.audit import Audit, AuditParameterInstance, AuditResponse
from app.models.enums import AuditStatus
from app.services.workflow_service import WorkflowService

def verify_audit_transition():
    db = SessionLocal()
    try:
        print("Starting verification process...")
        
        # 1. Fetch necessary entities
        print("Fetching entities...")
        fsp_manager = db.query(User).filter(User.email == "fsp_manager@gmail.com").first()
        if not fsp_manager:
            print("Error: FSP Manager not found")
            return

        fsp_org = db.query(Organization).filter(Organization.name == "GreenOps FSP Services").first()
        if not fsp_org:
            print("Error: FSP Org not found")
            return

        # Fetch Farm (Green Valley Farm from seed)
        farm = db.query(Farm).filter(Farm.name == "Green Valley Farm").first()
        if not farm:
            print("Error: Farm not found")
            return
            
        farmer_org_id = farm.organization_id # Helper property or field? Farm has organization_id

        # Fetch Crop (Wheat Season 2026)
        crop = db.query(Crop).filter(Crop.name == "Wheat Season 2026").first()
        if not crop:
            print("Error: Crop not found")
            return

        # Fetch Template
        template = db.query(Template).filter(Template.code == "SOIL_AUDIT_V1").first()
        if not template:
            print("Error: Template not found")
            return

        print(f"Using: FSP={fsp_org.name}, Farm={farm.name}, Template={template.code}")

        # 2. Create Audit
        print("Creating Audit...")
        audit_id = uuid.uuid4()
        audit = Audit(
            id=audit_id,
            fsp_organization_id=fsp_org.id,
            farming_organization_id=farmer_org_id,
            crop_id=crop.id,
            template_id=template.id,
            name=f"Verification Audit {int(time.time())}",
            status=AuditStatus.DRAFT,
            created_by=fsp_manager.id,
            audit_date=time.strftime('%Y-%m-%d'),
            template_snapshot={}
        )
        db.add(audit)
        db.flush()
        print(f"Created Audit: {audit.id}")

        # 3. Create Parameter Instances and Responses
        print("Creating Parameters and Responses...")
        
        # Get Template Parameters
        # Assuming we have one section and one parameter from seed
        sections = db.query(TemplateSection).filter(TemplateSection.template_id == template.id).all()
        
        count = 0
        for section in sections:
            # Join with TemplateParameter
            tmpl_params = db.query(TemplateParameter).filter(TemplateParameter.template_section_id == section.id).all()
            
            for tmpl_param in tmpl_params:
                param = db.query(Parameter).filter(Parameter.id == tmpl_param.parameter_id).first()
                if not param:
                    continue
                
                # Create Instance
                instance_id = uuid.uuid4()
                instance = AuditParameterInstance(
                    id=instance_id,
                    audit_id=audit.id,
                    template_section_id=section.id,
                    parameter_id=param.id,
                    is_required=tmpl_param.is_required,
                    parameter_snapshot=tmpl_param.parameter_snapshot
                )
                db.add(instance)
                db.flush()

                # Create Response
                # Check options if Single Select
                response_val = None
                options = []
                if param.parameter_metadata and 'options' in param.parameter_metadata:
                     # Pick first option
                     opts = param.parameter_metadata['options']
                     if opts and len(opts) > 0:
                         options = [uuid.UUID(opts[0]['id'])]
                
                response = AuditResponse(
                     id=uuid.uuid4(),
                     audit_id=audit.id,
                     audit_parameter_instance_id=instance.id,
                     response_options=options,
                     response_text="Verified",
                     created_by=fsp_manager.id
                )
                db.add(response)
                count += 1
        
        db.commit()
        print(f"Created {count} parameter instances and responses.")

        # 4. Transition Status
        service = WorkflowService(db)
        
        # DRAFT -> IN_PROGRESS
        print("Transitioning DRAFT -> IN_PROGRESS...")
        service.transition_status(audit_id, AuditStatus.IN_PROGRESS, fsp_manager.id)
        
        print("Attempting Transition to SUBMITTED_FOR_REVIEW...")
        start_time = time.time()
        
        updated_audit = service.transition_status(
            audit_id=audit_id,
            to_status=AuditStatus.SUBMITTED_FOR_REVIEW,
            user_id=fsp_manager.id
        )
        
        end_time = time.time()
        print(f"Transition Successful! Time taken: {end_time - start_time:.4f} seconds")
        print(f"New Status: {updated_audit.status}")

        if updated_audit.status == AuditStatus.SUBMITTED_FOR_REVIEW:
            print("VERIFICATION PASSED")
        else:
            print("VERIFICATION FAILED: Status mismatch")

    except Exception as e:
        print(f"Error during verification: {e}")
        if hasattr(e, 'details'):
            print(f"Details: {e.details}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verify_audit_transition()
