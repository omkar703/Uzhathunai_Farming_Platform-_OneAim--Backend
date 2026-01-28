"""
Create a test audit template using the API service approach
"""
from app.core.database import SessionLocal
from app.models.template import Template, TemplateTranslation, TemplateSection, TemplateParameter
from app.models.section import Section, SectionTranslation
from app.models.parameter import Parameter, ParameterTranslation, ParameterType
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

db = SessionLocal()

print("=" * 80)
print("Creating Test Audit Template for FSP Organization")
print("=" * 80)

fsp_org_id = uuid.UUID("5504357f-21a4-4877-b78e-37f8fe7dfec5")

try:
    # Get any user for created_by
    from app.models.user import User
    user = db.query(User).first()
    user_id = user.id if user else None
    
    # 1. Create the template
    template = Template(
        id=uuid.uuid4(),
        code="FSP_TEST_TEMPLATE_V1",
        is_system_defined=False,
        owner_org_id=fsp_org_id,
        crop_type_id=None,
        is_active=True,
        version=1,
        created_by=user_id,
        updated_by=user_id
    )
    db.add(template)
    db.flush()
    
    # 2. Add template translation
    template_trans = TemplateTranslation(
        id=uuid.uuid4(),
        template_id=template.id,
        language_code="en",
        name="FSP Test Audit Template",
        description="A simple test template for FSP organization testing with basic quality assessment parameters"
    )
    db.add(template_trans)
    
    # 3. Create a section
    section = Section(
        id=uuid.uuid4(),
        code="QUALITY_ASSESSMENT",
        is_system_defined=False,
        is_active=True
    )
    db.add(section)
    db.flush()
    
    # 4. Add section translation
    section_trans = SectionTranslation(
        id=uuid.uuid4(),
        section_id=section.id,
        language_code="en",
        name="Quality Assessment",
        description="Basic quality checks for farm auditing"
    )
    db.add(section_trans)
    
    # 5. Link section to template
    template_section = TemplateSection(
        id=uuid.uuid4(),
        template_id=template.id,
        section_id=section.id,
        sort_order=1
    )
    db.add(template_section)
    db.flush()
    
    # 6. Create parameters
    # Parameter 1: Crop Health Status (Single Select)
    param1 = Parameter(
        id=uuid.uuid4(),
        code="CROP_HEALTH_STATUS_TEST",
        parameter_type=ParameterType.SINGLE_SELECT,
        is_system_defined=False,
        owner_org_id=fsp_org_id,
        is_active=True,
        parameter_metadata={"options": ["Excellent", "Good", "Fair", "Poor", "Critical"]},
        created_by=user_id,
        updated_by=user_id
    )
    db.add(param1)
    
    param1_trans = ParameterTranslation(
        id=uuid.uuid4(),
        parameter_id=param1.id,
        language_code="en",
        name="Crop Health Status",
        description="Overall health assessment of the crop",
        help_text="Select the current health status based on visual inspection"
    )
    db.add(param1_trans)
    
    # Parameter 2: Pest Presence (Single Select - Yes/No)
    param2 = Parameter(
        id=uuid.uuid4(),
        code="PEST_PRESENCE_TEST",
        parameter_type=ParameterType.SINGLE_SELECT,
        is_system_defined=False,
        owner_org_id=fsp_org_id,
        is_active=True,
        parameter_metadata={"options": ["Yes", "No"]},
        created_by=user_id,
        updated_by=user_id
    )
    db.add(param2)
    
    param2_trans = ParameterTranslation(
        id=uuid.uuid4(),
        parameter_id=param2.id,
        language_code="en",
        name="Pest Presence Detected",
        description="Indicate if any pests are present on the crop",
        help_text="Select 'Yes' if any pests or pest damage is observed"
    )
    db.add(param2_trans)
    
    # Parameter 3: Additional Notes (Text)
    param3 = Parameter(
        id=uuid.uuid4(),
        code="AUDIT_NOTES_TEST",
        parameter_type=ParameterType.TEXT,
        is_system_defined=False,
        owner_org_id=fsp_org_id,
        is_active=True,
        parameter_metadata={"max_length": 500, "multiline": True},
        created_by=user_id,
        updated_by=user_id
    )
    db.add(param3)
    
    param3_trans = ParameterTranslation(
        id=uuid.uuid4(),
        parameter_id=param3.id,
        language_code="en",
        name="Additional Notes",
        description="Any additional observations or comments",
        help_text="Provide detailed notes about the audit findings"
    )
    db.add(param3_trans)
    
    db.flush()
    
    # 7. Link parameters to template section
    template_param1 = TemplateParameter(
        id=uuid.uuid4(),
        template_section_id=template_section.id,
        parameter_id=param1.id,
        is_required=True,
        sort_order=1
    )
    db.add(template_param1)
    
    template_param2 = TemplateParameter(
        id=uuid.uuid4(),
        template_section_id=template_section.id,
        parameter_id=param2.id,
        is_required=True,
        sort_order=2
    )
    db.add(template_param2)
    
    template_param3 = TemplateParameter(
        id=uuid.uuid4(),
        template_section_id=template_section.id,
        parameter_id=param3.id,
        is_required=False,
        sort_order=3
    )
    db.add(template_param3)
    
    # Commit all changes
    db.commit()
    
    print(f"\n✅ Successfully created test audit template!")
    print(f"\n📋 Template Details:")
    print(f"   Template ID: {template.id}")
    print(f"   Template Code: {template.code}")
    print(f"   Template Name: FSP Test Audit Template")
    print(f"   Organization ID: {fsp_org_id}")
    print(f"\n📁 Section: Quality Assessment")
    print(f"   Section ID: {section.id}")
    print(f"\n🔧 Parameters:")
    print(f"   1. Crop Health Status (SINGLE_SELECT) - ✓ Required")
    print(f"      Options: Excellent, Good, Fair, Poor, Critical")
    print(f"   2. Pest Presence Detected (SINGLE_SELECT) - ✓ Required")
    print(f"      Options: Yes, No")
    print(f"   3. Additional Notes (TEXT) - ○ Optional")
    print(f"      Max length: 500 characters")
    print(f"\n🎯 TEMPLATE ID FOR FRONTEND: {template.id}")
    print(f"\n✅ This template is now available via the API endpoint:")
    print(f"   GET /api/v1/farm-audit/templates/{template.id}")
    
except Exception as e:
    db.rollback()
    print(f"\n❌ Error creating template: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
