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


class AuditStatusEnum(str, Enum):
    """Audit status enum for API"""
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
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

class AuditResponse(BaseModel):
    """Schema for audit response"""
    id: UUID
    fsp_organization_id: UUID
    farming_organization_id: UUID
    work_order_id: Optional[UUID]
    crop_id: UUID
    template_id: UUID
    audit_number: Optional[str]
    name: str
    status: AuditStatusEnum
    audit_date: Optional[date]
    sync_status: Optional[SyncStatusEnum]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    finalized_at: Optional[datetime]
    finalized_by: Optional[UUID]
    shared_at: Optional[datetime]

    class Config:
        orm_mode = True
        use_enum_values = True


class ParameterInstanceResponse(BaseModel):
    """Schema for parameter instance in audit structure"""
    instance_id: str
    parameter_id: str
    is_required: bool
    sort_order: int
    parameter_snapshot: Dict[str, Any]


class SectionStructureResponse(BaseModel):
    """Schema for section structure in audit"""
    section_id: str
    code: str
    translations: Dict[str, Dict[str, str]]
    parameters: List[ParameterInstanceResponse]


class AuditStructureResponse(BaseModel):
    """Schema for complete audit structure"""
    audit_id: str
    audit_number: Optional[str]
    name: str
    status: str
    template_snapshot: Dict[str, Any]
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
    response_options: Optional[List[UUID]] = Field(None, description="Option IDs for SINGLE_SELECT/MULTI_SELECT parameters")
    notes: Optional[str] = Field(None, description="Additional notes")

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
    response_options: Optional[List[UUID]] = Field(None, description="Option IDs for SINGLE_SELECT/MULTI_SELECT parameters")
    notes: Optional[str] = Field(None, description="Additional notes")


class AuditResponseDetail(BaseModel):
    """Schema for audit response detail"""
    id: UUID
    audit_id: UUID
    audit_parameter_instance_id: UUID
    response_text: Optional[str]
    response_numeric: Optional[float]
    response_date: Optional[date]
    response_options: Optional[List[UUID]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]

    class Config:
        orm_mode = True


class AuditResponseListResponse(BaseModel):
    """Schema for list of audit responses"""
    items: List[AuditResponseDetail]
    total: int


# Photo Schemas

class PhotoUploadResponse(BaseModel):
    """Schema for photo upload response"""
    id: UUID
    audit_response_id: UUID
    file_url: str
    file_key: Optional[str]
    caption: Optional[str]
    uploaded_at: datetime
    uploaded_by: Optional[UUID]

    class Config:
        orm_mode = True


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
    response_option_ids: Optional[List[UUID]] = Field(None, description="Option IDs override")
    is_flagged_for_report: Optional[bool] = Field(None, description="Flag for report inclusion")


class ReviewResponse(BaseModel):
    """Schema for audit review response"""
    id: UUID
    audit_response_id: UUID
    response_text: Optional[str]
    response_numeric: Optional[float]
    response_date: Optional[date]
    response_option_ids: Optional[List[UUID]]
    is_flagged_for_report: bool
    reviewed_at: datetime
    reviewed_by: Optional[UUID]

    class Config:
        orm_mode = True


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
        orm_mode = True


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
    description: Optional[str] = Field(None, description="Issue description")
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
    description: Optional[str]
    severity: Optional[IssueSeverityEnum]
    created_at: datetime
    created_by: Optional[UUID]

    class Config:
        orm_mode = True
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


# Recommendation Schemas

class RecommendationCreate(BaseModel):
    """Schema for creating a recommendation"""
    schedule_id: UUID = Field(..., description="UUID of the schedule to modify")
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
    trigger_type: str
    trigger_reference_id: Optional[UUID]
    change_type: str
    task_id: Optional[UUID]
    task_details_before: Optional[Dict[str, Any]]
    task_details_after: Optional[Dict[str, Any]]
    change_description: Optional[str]
    is_applied: bool
    applied_at: Optional[datetime]
    applied_by: Optional[UUID]
    created_at: datetime
    created_by: Optional[UUID]

    class Config:
        orm_mode = True
