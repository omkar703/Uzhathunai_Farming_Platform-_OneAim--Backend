"""
Pydantic schemas for Audit Management in Uzhathunai v2.0.

Request and response schemas for audit operations including creation,
retrieval, and structure queries.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime
from enum import Enum
from app.schemas.user import UserResponse


class AuditStatusEnum(str, Enum):
    """Audit status enum for API"""
    PENDING = "PENDING"
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    SUBMITTED_TO_FARMER = "SUBMITTED_TO_FARMER"
    SUBMITTED_FOR_REVIEW = "SUBMITTED_FOR_REVIEW"
    IN_ANALYSIS = "IN_ANALYSIS"
    REVIEWED = "REVIEWED"
    FINALIZED = "FINALIZED"
    SHARED = "SHARED"


class SyncStatusEnum(str, Enum):
    """Sync status enum for API"""
    PENDING_SYNC = "pending_sync"
    SYNCED = "synced"
    SYNC_FAILED = "sync_failed"


# Request Schemas

class AuditCreate(BaseModel):
    """Schema for creating a new audit"""
    template_id: UUID = Field(..., description="UUID of the template to use")
    crop_id: UUID = Field(..., description="UUID of the crop being audited")
    fsp_organization_id: UUID = Field(..., description="UUID of the FSP organization")
    name: str = Field(..., min_length=1, max_length=200, description="Name for the audit")
    work_order_id: Optional[UUID] = Field(None, description="Optional work order ID")
    audit_date: Optional[date] = Field(None, description="Audit date (defaults to today)")
    assigned_to: Optional[UUID] = Field(None, description="UUID of the user to assign the audit to")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "template_id": "123e4567-e89b-12d3-a456-426614174000",
                "crop_id": "123e4567-e89b-12d3-a456-426614174001",
                "fsp_organization_id": "123e4567-e89b-12d3-a456-426614174002",
                "name": "Tomato Crop Audit - January 2024",
                "work_order_id": "123e4567-e89b-12d3-a456-426614174003",
                "audit_date": "2024-01-15"
            }
        }


# Response Schemas

class AuditAssignRequest(BaseModel):
    """Schema for assigning an audit"""
    assigned_to: Optional[UUID] = Field(None, description="UUID of the user to assign the audit to (Field Officer)")
    analyst_id: Optional[UUID] = Field(None, description="UUID of the user to assign as analyst")


class AuditUpdate(BaseModel):
    """Schema for updating an audit"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Name for the audit")
    audit_date: Optional[date] = Field(None, description="Audit date")
    notes: Optional[str] = Field(None, description="Audit notes")

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else None



class FSPContactInfo(BaseModel):
    """Schema for FSP contact info"""
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class AuditResponse(BaseModel):
    """Schema for audit response"""
    id: UUID
    fsp_organization_id: UUID
    farming_organization_id: UUID
    work_order_id: Optional[UUID] = None
    crop_id: UUID
    template_id: UUID
    audit_number: Optional[str] = None
    name: str
    audit_name: Optional[str] = None # Alias for frontend
    status: AuditStatusEnum
    audit_date: Optional[date] = None
    notes: Optional[str] = None
    scheduled_date: Optional[date] = None # Alias for frontend
    sync_status: Optional[SyncStatusEnum] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    finalized_at: Optional[datetime] = None
    finalized_by: Optional[UUID] = None
    shared_at: Optional[datetime] = None
    assigned_to: Optional[UserResponse] = Field(None, description="User assigned to execute the audit")
    analyst: Optional[UserResponse] = Field(None, description="User assigned to analyze the audit")
    progress: float = Field(0.0, description="Audit completion progress percentage")
    
    # Enriched fields
    fsp_organization_name: Optional[str] = Field(None, description="Name of the FSP organization")
    fsp_contact_info: Optional[FSPContactInfo] = Field(None, description="Contact details of the FSP")

    class Config:
        from_attributes = True
        use_enum_values = True


class ParameterInstanceResponse(BaseModel):
    """Schema for parameter instance in audit structure"""
    instance_id: str
    parameter_id: str
    is_required: bool
    sort_order: int
    name: Optional[str] = None
    parameter_snapshot: Dict[str, Any]


class SectionStructureResponse(BaseModel):
    """Schema for section structure in audit"""
    section_id: str
    code: str
    translations: Dict[str, Dict[str, Optional[str]]]
    parameters: List[ParameterInstanceResponse]


class AuditStructureResponse(BaseModel):
    """Schema for complete audit structure"""
    audit_id: str
    audit_number: Optional[str]
    name: str
    status: str
    template_snapshot: Optional[Dict[str, Any]] = None
    sections: List[SectionStructureResponse]


class AuditListResponse(BaseModel):
    """Schema for paginated audit list"""
    items: List[AuditResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# Response Submission Schemas

class ResponseSubmit(BaseModel):
    """Schema for submitting an audit response"""
    audit_parameter_instance_id: UUID = Field(..., description="UUID of the parameter instance")
    response_text: Optional[str] = Field(None, description="Text response for TEXT parameters")
    response_numeric: Optional[float] = Field(None, description="Numeric response for NUMERIC parameters")
    response_date: Optional[date] = Field(None, description="Date response for DATE parameters")
    response_boolean: Optional[bool] = Field(None, description="Boolean response for BOOLEAN parameters")
    response_options: Optional[List[UUID]] = Field(None, description="Option IDs for SINGLE_SELECT/MULTI_SELECT parameters")
    notes: Optional[str] = Field(None, description="Additional notes")
    evidence_urls: Optional[List[str]] = Field(None, description="List of evidence photo URLs")

    class Config:
        schema_extra = {
            "example": {
                "audit_parameter_instance_id": "123e4567-e89b-12d3-a456-426614174000",
                "response_numeric": 45.5,
                "notes": "Plant height measured at base"
            }
        }



class ResponseUpdate(BaseModel):
    """Schema for updating an audit response"""
    response_text: Optional[str] = Field(None, description="Text response for TEXT parameters")
    response_numeric: Optional[float] = Field(None, description="Numeric response for NUMERIC parameters")
    response_date: Optional[date] = Field(None, description="Date response for DATE parameters")
    response_boolean: Optional[bool] = Field(None, description="Boolean response for BOOLEAN parameters")
    response_options: Optional[List[UUID]] = Field(None, description="Option IDs for SINGLE_SELECT/MULTI_SELECT parameters")
    notes: Optional[str] = Field(None, description="Additional notes")
    evidence_urls: Optional[List[str]] = Field(None, description="List of evidence photo URLs")


class ResponseBulkSubmit(BaseModel):
    """Schema for bulk submitting audit responses"""
    responses: List[ResponseSubmit]

    class Config:
        schema_extra = {
            "example": {
                "responses": [
                    {
                        "audit_parameter_instance_id": "123e4567-e89b-12d3-a456-426614174000",
                        "response_numeric": 45.5,
                        "notes": "Plant height measured at base"
                    },
                    {
                        "audit_parameter_instance_id": "123e4567-e89b-12d3-a456-426614174001",
                        "response_text": "Green",
                        "notes": "Healthy leaf color"
                    }
                ]
            }
        }



class AuditResponseDetail(BaseModel):
    """Schema for audit response detail"""
    id: UUID
    audit_id: UUID
    audit_parameter_instance_id: UUID
    
    # Metadata fields
    parameter_name: Optional[str] = None
    parameter_type: Optional[str] = None
    parameter_code: Optional[str] = None
    
    # Response values
    response_text: Optional[str]
    response_numeric: Optional[float]
    response_date: Optional[date]
    response_boolean: Optional[bool] = None
    response_options: Optional[List[UUID]]
    response_option_labels: Optional[List[str]] = None
    
    # Evidence & Notes
    notes: Optional[str]
    evidence_urls: Optional[List[str]] = None
    
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True


class AuditResponseListResponse(BaseModel):
    """Schema for list of audit responses"""
    items: List[AuditResponseDetail]
    total: int


# Photo Schemas

class PhotoUploadResponse(BaseModel):
    """Schema for photo upload response"""
    id: UUID
    audit_response_id: Optional[UUID] = None
    file_url: str
    file_key: Optional[str]
    caption: Optional[str]
    is_flagged_for_report: bool = False
    uploaded_at: datetime
    uploaded_by: Optional[UUID]

    class Config:
        from_attributes = True


class PhotoListResponse(BaseModel):
    """Schema for list of photos"""
    items: List[PhotoUploadResponse]
    total: int


# Status Transition Schemas

class StatusTransitionRequest(BaseModel):
    """Schema for status transition request"""
    to_status: AuditStatusEnum = Field(..., description="Target status")

    class Config:
        schema_extra = {
            "example": {
                "to_status": "SUBMITTED"
            }
        }


class ValidationResult(BaseModel):
    """Schema for validation result"""
    ready: bool = Field(..., description="Whether audit is ready for submission")
    current_status: str = Field(..., description="Current audit status")
    missing_required_responses: Optional[List[str]] = Field(None, description="List of missing required parameters")
    photo_requirement_violations: Optional[List[Dict[str, str]]] = Field(None, description="List of photo requirement violations")
    error: Optional[str] = Field(None, description="Error message if validation failed")

    class Config:
        schema_extra = {
            "example": {
                "ready": False,
                "current_status": "IN_PROGRESS",
                "missing_required_responses": ["Plant Height", "Leaf Color"],
                "photo_requirement_violations": [
                    {
                        "parameter": "Plant Condition",
                        "error": "Minimum 2 photos required, but only 1 provided"
                    }
                ]
            }
        }


# Review Schemas

class ReviewCreate(BaseModel):
    """Schema for creating an audit review"""
    audit_response_id: UUID = Field(..., description="UUID of the audit response being reviewed")
    response_text: Optional[str] = Field(None, description="Text response override")
    response_numeric: Optional[float] = Field(None, description="Numeric response override")
    response_date: Optional[date] = Field(None, description="Date response override")
    response_boolean: Optional[bool] = Field(None, description="Boolean response override")
    response_option_ids: Optional[List[UUID]] = Field(None, description="Option IDs override")
    is_flagged_for_report: bool = Field(False, description="Flag for report inclusion")

    class Config:
        schema_extra = {
            "example": {
                "audit_response_id": "123e4567-e89b-12d3-a456-426614174000",
                "response_numeric": 50.0,
                "is_flagged_for_report": True
            }
        }


class ReviewUpdate(BaseModel):
    """Schema for updating an audit review"""
    response_text: Optional[str] = Field(None, description="Text response override")
    response_numeric: Optional[float] = Field(None, description="Numeric response override")
    response_date: Optional[date] = Field(None, description="Date response override")
    response_boolean: Optional[bool] = Field(None, description="Boolean response override")
    response_option_ids: Optional[List[UUID]] = Field(None, description="Option IDs override")
    is_flagged_for_report: Optional[bool] = Field(None, description="Flag for report inclusion")


class ReviewResponse(BaseModel):
    """Schema for audit review response"""
    id: UUID
    audit_response_id: UUID
    response_text: Optional[str]
    response_numeric: Optional[float]
    response_date: Optional[date]
    response_boolean: Optional[bool] = None
    response_option_ids: Optional[List[UUID]]
    is_flagged_for_report: bool
    reviewed_at: datetime
    reviewed_by: Optional[UUID]

    class Config:
        from_attributes = True


class FlagRequest(BaseModel):
    """Schema for flagging a response for report"""
    is_flagged: bool = Field(..., description="True to flag, False to unflag")

    class Config:
        schema_extra = {
            "example": {
                "is_flagged": True
            }
        }


class PhotoAnnotationRequest(BaseModel):
    """Schema for annotating a photo"""
    caption: Optional[str] = Field(None, description="Caption for the photo")
    is_flagged_for_report: bool = Field(False, description="Flag for report inclusion")

    class Config:
        schema_extra = {
            "example": {
                "caption": "Severe pest damage on leaves",
                "is_flagged_for_report": True
            }
        }


class PhotoAnnotationResponse(BaseModel):
    """Schema for photo annotation response"""
    id: UUID
    audit_response_photo_id: UUID
    caption: Optional[str]
    is_flagged_for_report: bool
    reviewed_at: datetime
    reviewed_by: Optional[UUID]

    class Config:
        from_attributes = True


# ============================================
# ISSUE SCHEMAS
# ============================================

class IssueSeverityEnum(str, Enum):
    """Issue severity enum for API"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IssueCreate(BaseModel):
    """Schema for creating an audit issue"""
    title: str = Field(..., min_length=1, max_length=200, description="Issue title")
    title: str = Field(..., min_length=1, max_length=200, description="Issue title")
    description: Optional[str] = Field(None, description="Issue description")
    recommendation: Optional[str] = Field(None, description="Optional recommendation for the issue")
    severity: IssueSeverityEnum = Field(..., description="Issue severity level")

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "title": "Severe pest infestation detected",
                "description": "Multiple plants showing signs of aphid damage in section A",
                "severity": "HIGH"
            }
        }


class IssueUpdate(BaseModel):
    """Schema for updating an audit issue"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Issue title")
    description: Optional[str] = Field(None, description="Issue description")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Issue title")
    description: Optional[str] = Field(None, description="Issue description")
    recommendation: Optional[str] = Field(None, description="Optional recommendation for the issue")
    severity: Optional[IssueSeverityEnum] = Field(None, description="Issue severity level")

    @validator('title')
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else None

    class Config:
        schema_extra = {
            "example": {
                "title": "Updated issue title",
                "description": "Updated description with more details",
                "severity": "CRITICAL"
            }
        }


class IssueResponse(BaseModel):
    """Schema for audit issue response"""
    id: UUID
    audit_id: UUID
    title: str
    description: Optional[str] = None
    title: str
    description: Optional[str] = None
    recommendation: Optional[str] = None
    severity: Optional[IssueSeverityEnum] = None
    created_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "audit_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Severe pest infestation detected",
                "description": "Multiple plants showing signs of aphid damage",
                "severity": "HIGH",
                "created_at": "2024-01-15T10:30:00Z",
                "created_by": "123e4567-e89b-12d3-a456-426614174002"
            }
        }


class IssueListResponse(BaseModel):
    """Schema for list of audit issues"""
    items: List[IssueResponse]
    total: int


# Recommendation Schemas

class RecommendationCreate(BaseModel):
    """Schema for creating a recommendation"""
    schedule_id: Optional[UUID] = Field(None, description="UUID of the schedule to modify (Optional, auto-detected from audit if missing)")
    change_type: str = Field(..., description="Type of change: ADD, MODIFY, DELETE")
    task_id: Optional[UUID] = Field(None, description="UUID of schedule task (for MODIFY/DELETE)")
    task_details_before: Optional[Dict[str, Any]] = Field(None, description="Task details before change (NULL for ADD)")
    task_details_after: Optional[Dict[str, Any]] = Field(None, description="Task details after change (NULL for DELETE)")
    change_description: str = Field(..., min_length=1, description="Description of the recommendation")

    @validator('change_type')
    def validate_change_type(cls, v):
        valid_types = ['ADD', 'MODIFY', 'DELETE']
        if v not in valid_types:
            raise ValueError(f'change_type must be one of {valid_types}')
        return v

    @validator('change_description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('change_description cannot be empty')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "schedule_id": "123e4567-e89b-12d3-a456-426614174000",
                "change_type": "ADD",
                "task_id": None,
                "task_details_before": None,
                "task_details_after": {
                    "task_id": "123e4567-e89b-12d3-a456-426614174001",
                    "due_date": "2024-02-15",
                    "task_details": {
                        "input_items": [
                            {
                                "input_item_id": "123e4567-e89b-12d3-a456-426614174002",
                                "quantity": 10.5,
                                "quantity_unit_id": "123e4567-e89b-12d3-a456-426614174003"
                            }
                        ]
                    },
                    "notes": "Apply additional fertilizer based on audit findings"
                },
                "change_description": "Add fertilizer application task based on nutrient deficiency observed in audit"
            }
        }


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation"""
    change_description: Optional[str] = Field(None, description="Updated description")
    task_details_after: Optional[Dict[str, Any]] = Field(None, description="Updated task details")

    @validator('change_description')
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('change_description cannot be empty')
        return v.strip() if v else v


class RecommendationResponse(BaseModel):
    """Schema for recommendation response"""
    id: UUID
    schedule_id: UUID
    trigger_type: Optional[str] = None
    trigger_reference_id: Optional[UUID] = None
    change_type: str
    task_id: Optional[UUID] = None
    task_details_before: Optional[Dict[str, Any]] = None
    task_details_after: Optional[Dict[str, Any]] = None
    change_description: Optional[str] = None
    is_applied: bool
    applied_at: Optional[datetime] = None
    applied_by: Optional[UUID] = None
    created_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True


class RecommendationListResponse(BaseModel):
    """Schema for list of recommendations"""
    items: List[RecommendationResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# Report Schemas

class AuditReportStats(BaseModel):
    """Schema for audit report statistics"""
    compliance_score: float = Field(..., ge=0, le=100, description="Compliance score percentage")
    total_mandatory: int = Field(..., ge=0, description="Total mandatory questions")
    answered_mandatory: int = Field(..., ge=0, description="Answered mandatory questions")
    total_optional: int = Field(..., ge=0, description="Total optional questions")
    answered_optional: int = Field(..., ge=0, description="Answered optional questions")
    issues_by_severity: Dict[str, int] = Field(..., description="Count of issues by severity")


class AuditRecommendationCreate(BaseModel):
    """Schema for creating a standalone audit recommendation"""
    title: str = Field("Recommendation", min_length=1, max_length=200, description="Recommendation title")
    description: Optional[str] = Field(None, description="Recommendation description")

    @validator('title', pre=True, always=True)
    def validate_title(cls, v):
        if v is None:
            return "Recommendation"
        if isinstance(v, str) and not v.strip():
            return "Recommendation"
        return v.strip() if isinstance(v, str) else v


class AuditRecommendationUpdate(BaseModel):
    """Schema for updating a standalone audit recommendation"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Recommendation title")
    description: Optional[str] = Field(None, description="Recommendation description")

    @validator('title')
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else None


class AuditRecommendationResponse(BaseModel):
    """Schema for standalone audit recommendation response"""
    id: UUID
    audit_id: UUID
    title: str
    description: Optional[str]
    created_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True



class AuditReportResponse(BaseModel):
    """Schema for complete audit report"""
    audit: AuditResponse
    stats: AuditReportStats
    issues: List[IssueResponse]
    recommendations: List[Dict[str, Any]] = []
    
    # Enriched Content
    template_info: Optional[Dict[str, Any]] = None
    crop_info: Optional[Dict[str, Any]] = None
    organization_info: Optional[Dict[str, Any]] = None
    flagged_responses: Optional[List[Dict[str, Any]]] = []
    flagged_photos: Optional[List[Dict[str, Any]]] = []
    
    # Rich text fields
    report_html: Optional[str] = ""
    report_images: Optional[List[str]] = []
    report_pdf_url: Optional[str] = None
    report_updated_at: Optional[datetime] = None
    
    # Metadata
    generated_at: Optional[str] = None
    language: Optional[str] = "en"


