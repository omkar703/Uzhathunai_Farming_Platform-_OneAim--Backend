
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
from app.models.organization import Organization
from app.models.template import Template, TemplateTranslation, TemplateSection, TemplateParameter
from app.models.parameter import Parameter, ParameterTranslation, ParameterType, ParameterOptionSetMap
from app.models.section import Section, SectionTranslation
from app.models.option_set import OptionSet, Option, OptionTranslation
from app.models.user import User

def seed_liomonk_templates():
    db = SessionLocal()
    try:
        print("Starting Liomonk Detailed Templates Seed...")

        # 1. Get Organization
        org_name = "LioMonk"
        org = db.query(Organization).filter(Organization.name.ilike(f"%{org_name}%")).first()
        if not org:
            print(f"ERROR: Organization containing '{org_name}' not found.")
            return

        print(f"Found Organization: {org.name} ({org.id})")
        
        # Get FSP Admin user (fsp1@gmail.com)
        user = db.query(User).filter(User.email == "fsp1@gmail.com").first()
        if not user:
             # Fallback to org creator or created_by
             user_id = org.created_by
        else:
             user_id = user.id

        # ==========================================
        # 1. Create Option Sets (for Select Parameters)
        # ==========================================
        
        # 1.1 Moisture Levels
        os_moisture = OptionSet(
            id=uuid.uuid4(),
            code="OS_MOISTURE_LEVEL",
            is_system_defined=False,
            owner_org_id=org.id,
            is_active=True,
            created_by=user_id
        )
        db.add(os_moisture)
        db.flush()
        # No translation for Option Set itself in this model, skipping name translation
        
        moisture_opts = ["Dry", "Moist", "Wet", "Saturated"]
        for idx, val in enumerate(moisture_opts):
            ov = Option(
                id=uuid.uuid4(), option_set_id=os_moisture.id,
                code=f"MOISTURE_{val.upper()}", sort_order=idx
            )
            db.add(ov)
            db.flush()
            db.add(OptionTranslation(
                option_id=ov.id, language_code="en", display_text=val
            ))

        # 1.2 Pest Severity
        os_severity = OptionSet(
            id=uuid.uuid4(),
            code="OS_PEST_SEVERITY",
            is_system_defined=False,
            owner_org_id=org.id,
            is_active=True,
            created_by=user_id
        )
        db.add(os_severity)
        db.flush()
        
        severity_opts = ["Low", "Medium", "High", "Critical"]
        for idx, val in enumerate(severity_opts):
            ov = Option(
                id=uuid.uuid4(), option_set_id=os_severity.id,
                code=f"SEVERITY_{val.upper()}", sort_order=idx
            )
            db.add(ov)
            db.flush()
            db.add(OptionTranslation(
                option_id=ov.id, language_code="en", display_text=val
            ))
            
        db.commit()
        print("Created Option Sets")

        # ==========================================
        # 2. Create Parameters
        # ==========================================
        
        params = []
        
        # P1: Soil Moisture (Single Select)
        p_moisture = Parameter(
            id=uuid.uuid4(),
            code="PARAM_SOIL_MOISTURE_V2",
            parameter_type=ParameterType.SINGLE_SELECT,
            is_system_defined=False,
            owner_org_id=org.id,
            created_by=user_id,
            parameter_metadata={}
        )
        db.add(p_moisture)
        db.flush()
        db.add(ParameterTranslation(
            parameter_id=p_moisture.id, language_code="en", name="Soil Moisture Status", description="Current moisture level of the soil"
        ))
        # Map to Option Set
        db.add(ParameterOptionSetMap(
            id=uuid.uuid4(), parameter_id=p_moisture.id, option_set_id=os_moisture.id
        ))
        params.append(p_moisture)
        
        # P2: pH Value (Numeric)
        p_ph = Parameter(
            id=uuid.uuid4(),
            code="PARAM_SOIL_PH",
            parameter_type=ParameterType.NUMERIC,
            is_system_defined=False,
            owner_org_id=org.id,
            created_by=user_id,
            parameter_metadata={"min_value": 0, "max_value": 14, "decimal_places": 1}
        )
        db.add(p_ph)
        db.flush()
        db.add(ParameterTranslation(
            parameter_id=p_ph.id, language_code="en", name="Soil pH Level", description="Measured pH value"
        ))
        params.append(p_ph)
        
        # P3: Pest Observed? (Boolean - modeled as Single Select Yes/No usually, let's create simple Yes/No OS or assume generic)
        # Actually let's just make it a TEXT for 'Pest Name' and Select for 'Severity'
        
        # P3: Pest Name (Text)
        p_pest_name = Parameter(
            id=uuid.uuid4(),
            code="PARAM_PEST_NAME",
            parameter_type=ParameterType.TEXT,
            is_system_defined=False,
            owner_org_id=org.id,
            created_by=user_id
        )
        db.add(p_pest_name)
        db.flush()
        db.add(ParameterTranslation(
            parameter_id=p_pest_name.id, language_code="en", name="Observed Pest Name", description="Name of the pest if observed"
        ))
        params.append(p_pest_name)
        
        # P4: Severity (Single Select)
        p_severity = Parameter(
            id=uuid.uuid4(),
            code="PARAM_PEST_SEVERITY",
            parameter_type=ParameterType.SINGLE_SELECT,
            is_system_defined=False,
            owner_org_id=org.id,
            created_by=user_id
        )
        db.add(p_severity)
        db.flush()
        db.add(ParameterTranslation(
            parameter_id=p_severity.id, language_code="en", name="Infestation Severity", description="Severity of pest infestation"
        ))
        db.add(ParameterOptionSetMap(
            id=uuid.uuid4(), parameter_id=p_severity.id, option_set_id=os_severity.id
        ))
        params.append(p_severity)
        
        # P5: Recommendations (Text)
        p_reco = Parameter(
            id=uuid.uuid4(),
            code="PARAM_RECOMMENDATION",
            parameter_type=ParameterType.TEXT,
            is_system_defined=False,
            owner_org_id=org.id,
            created_by=user_id,
            parameter_metadata={"multiline": True}
        )
        db.add(p_reco)
        db.flush()
        db.add(ParameterTranslation(
            parameter_id=p_reco.id, language_code="en", name="Expert Recommendations", description="Advice for the farmer"
        ))
        params.append(p_reco)
        
        db.commit()
        print("Created Parameters")

        # ==========================================
        # 3. Create Sections
        # ==========================================
        
        # S1: Soil Analysis
        s_soil = Section(
            id=uuid.uuid4(),
            code="SEC_SOIL_ANALYSIS",
            is_system_defined=False,
            owner_org_id=org.id,
            created_by=user_id
        )
        db.add(s_soil)
        db.flush()
        db.add(SectionTranslation(
             section_id=s_soil.id, language_code="en", name="Soil Analysis", description="Physical and chemical soil properties"
        ))
        
        # S2: Pest Scouting
        s_pest = Section(
            id=uuid.uuid4(),
            code="SEC_PEST_SCOUTING",
            is_system_defined=False,
            owner_org_id=org.id,
            created_by=user_id
        )
        db.add(s_pest)
        db.flush()
        db.add(SectionTranslation(
             section_id=s_pest.id, language_code="en", name="Pest Scouting", description="Pest and disease observations"
        ))
        
        # S3: Summary
        s_summary = Section(
             id=uuid.uuid4(),
             code="SEC_SUMMARY_RECO",
             is_system_defined=False,
             owner_org_id=org.id,
             created_by=user_id
        )
        db.add(s_summary)
        db.flush()
        db.add(SectionTranslation(
             section_id=s_summary.id, language_code="en", name="Action Plan", description="Summary and recommendations"
        ))
        
        db.commit()
        print("Created Sections")

        # ==========================================
        # 4. Create Template
        # ==========================================
        
        tmpl_code = "COMP_SOIL_PEST_AUDIT"
        template = Template(
            id=uuid.uuid4(),
            code=tmpl_code,
            is_system_defined=False,
            owner_org_id=org.id,
            is_active=True,
            version=1,
            created_by=user_id,
            updated_by=user_id
        )
        db.add(template)
        db.flush()
        
        db.add(TemplateTranslation(
            template_id=template.id,
            language_code="en",
            name="Comprehensive Soil & Pest Audit",
            description="Detailed audit covering soil health and pest status"
        ))
        
        # Link Sections
        ts_soil = TemplateSection(
            id=uuid.uuid4(), template_id=template.id, section_id=s_soil.id, sort_order=1
        )
        db.add(ts_soil)
        
        ts_pest = TemplateSection(
            id=uuid.uuid4(), template_id=template.id, section_id=s_pest.id, sort_order=2
        )
        db.add(ts_pest)
        
        ts_summ = TemplateSection(
            id=uuid.uuid4(), template_id=template.id, section_id=s_summary.id, sort_order=3
        )
        db.add(ts_summ)
        db.flush()
        
        # Link Parameters to Sections
        # Soil -> Moisture, pH
        db.add(TemplateParameter(
            id=uuid.uuid4(), template_section_id=ts_soil.id, parameter_id=p_moisture.id, 
            is_required=True, sort_order=1, parameter_snapshot={"code": p_moisture.code, "parameter_type": "SINGLE_SELECT"}
        ))
        db.add(TemplateParameter(
            id=uuid.uuid4(), template_section_id=ts_soil.id, parameter_id=p_ph.id, 
            is_required=False, sort_order=2, parameter_snapshot={"code": p_ph.code, "parameter_type": "NUMERIC"}
        ))
        
        # Pest -> Name, Severity
        db.add(TemplateParameter(
            id=uuid.uuid4(), template_section_id=ts_pest.id, parameter_id=p_pest_name.id, 
            is_required=False, sort_order=1, parameter_snapshot={"code": p_pest_name.code, "parameter_type": "TEXT"}
        ))
        db.add(TemplateParameter(
            id=uuid.uuid4(), template_section_id=ts_pest.id, parameter_id=p_severity.id, 
            is_required=False, sort_order=2, parameter_snapshot={"code": p_severity.code, "parameter_type": "SINGLE_SELECT"}
        ))
        
        # Summary -> Reco
        db.add(TemplateParameter(
            id=uuid.uuid4(), template_section_id=ts_summ.id, parameter_id=p_reco.id, 
            is_required=True, sort_order=1, parameter_snapshot={"code": p_reco.code, "parameter_type": "TEXT"}
        ))
        
        db.commit()
        print(f"Created Template: {template.id}")
        
        print("\nSUCCESS!")
        print(f"Template Name: Comprehensive Soil & Pest Audit")
        print(f"Template ID: {template.id}")
        print(f"Organization: {org.name} ({org.id})")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_liomonk_templates()
