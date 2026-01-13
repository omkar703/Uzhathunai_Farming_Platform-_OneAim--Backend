"""
Query schemas for Uzhathunai v2.0.

Pydantic schemas for query management API.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator

from app.models.enums import QueryStatus


class QueryCreate(BaseModel):
    """Schema for creating a query."""
    
    farming_organization_id: UUID
    fsp_organization_id: UUID
    work_order_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    farm_id: Optional[UUID] = None
    plot_id: Optional[UUID] = None
    crop_id: Optional[UUID] = None
    priority: str = Field(default='MEDIUM')
    
    @validator('title', 'description')
    def validate_not_empty(cls, v):
        """Validate strings are not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority level."""
        valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "farming_organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "fsp_organization_id": "123e4567-e89b-12d3-a456-426614174001",
                "work_order_id": "123e4567-e89b-12d3-a456-426614174002",
                "title": "Pest infestation on tomato crop",
                "description": "Noticed white flies on tomato plants in Plot A. Need advice on treatment.",
                "crop_id": "123e4567-e89b-12d3-a456-426614174003",
                "priority": "HIGH"
            }
        }


class QueryUpdate(BaseModel):
    """Schema for updating a query."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[str] = None
    
    @validator('title', 'description')
    def validate_not_empty(cls, v):
        """Validate strings are not empty or whitespace only."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty')
        return v.strip() if v else v
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority level."""
        if v is not None:
            valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
            if v not in valid_priorities:
                raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v


class QueryStatusUpdate(BaseModel):
    """Schema for updating query status."""
    
    status: QueryStatus
    resolved_by: Optional[UUID] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "RESOLVED",
                "resolved_by": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class QueryPhotoCreate(BaseModel):
    """Schema for creating a query photo."""
    
    file_url: str = Field(..., min_length=1, max_length=500)
    file_key: str = Field(..., min_length=1, max_length=500)
    caption: Optional[str] = None
    
    @validator('file_url', 'file_key')
    def validate_not_empty(cls, v):
        """Validate strings are not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "file_url": "https://s3.amazonaws.com/bucket/query-photos/photo.jpg",
                "file_key": "query-photos/photo.jpg",
                "caption": "White flies on tomato leaves"
            }
        }


class QueryPhotoResponse(BaseModel):
    """Schema for query photo response."""
    
    id: UUID
    query_id: Optional[UUID]
    query_response_id: Optional[UUID]
    file_url: str
    file_key: str
    caption: Optional[str]
    uploaded_at: datetime
    uploaded_by: UUID
    
    class Config:
        orm_mode = True


class QueryResponseCreate(BaseModel):
    """Schema for creating a query response."""
    
    response_text: str = Field(..., min_length=1)
    has_recommendation: bool = Field(default=False)
    
    @validator('response_text')
    def validate_not_empty(cls, v):
        """Validate response text is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Response text cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "response_text": "For white fly control, I recommend using neem oil spray. Apply in the evening at 5ml per liter of water. Repeat every 7 days for 3 weeks.",
                "has_recommendation": True
            }
        }


class QueryResponseResponse(BaseModel):
    """Schema for query response response."""
    
    id: UUID
    query_id: UUID
    response_text: str
    has_recommendation: bool
    created_at: datetime
    created_by: UUID
    photos: List[QueryPhotoResponse] = []
    
    class Config:
        orm_mode = True


class ScheduleChangeProposal(BaseModel):
    """Schema for proposing schedule changes via query."""
    
    schedule_id: UUID
    changes: List[dict] = Field(..., min_items=1)
    
    @validator('changes')
    def validate_changes(cls, v):
        """Validate change structure."""
        for change in v:
            if 'change_type' not in change:
                raise ValueError('Each change must have change_type')
            
            valid_types = ['ADD', 'MODIFY', 'DELETE']
            if change['change_type'] not in valid_types:
                raise ValueError(f'change_type must be one of: {", ".join(valid_types)}')
            
            # Validate required fields based on change type
            if change['change_type'] == 'ADD':
                if 'task_details_after' not in change:
                    raise ValueError('ADD changes must have task_details_after')
            elif change['change_type'] == 'MODIFY':
                if 'task_details_before' not in change or 'task_details_after' not in change:
                    raise ValueError('MODIFY changes must have task_details_before and task_details_after')
            elif change['change_type'] == 'DELETE':
                if 'task_details_before' not in change:
                    raise ValueError('DELETE changes must have task_details_before')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "schedule_id": "123e4567-e89b-12d3-a456-426614174000",
                "changes": [
                    {
                        "change_type": "ADD",
                        "task_id": "123e4567-e89b-12d3-a456-426614174001",
                        "task_details_after": {
                            "input_items": [
                                {
                                    "input_item_id": "123e4567-e89b-12d3-a456-426614174002",
                                    "quantity": 50,
                                    "quantity_unit_id": "123e4567-e89b-12d3-a456-426614174003"
                                }
                            ]
                        },
                        "change_description": "Add neem oil spray task"
                    }
                ]
            }
        }


class QueryResponse(BaseModel):
    """Schema for query response."""
    
    id: UUID
    farming_organization_id: UUID
    fsp_organization_id: UUID
    work_order_id: UUID
    query_number: str
    title: str
    description: str
    farm_id: Optional[UUID]
    plot_id: Optional[UUID]
    crop_id: Optional[UUID]
    status: QueryStatus
    priority: str
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID
    resolved_at: Optional[datetime]
    resolved_by: Optional[UUID]
    closed_at: Optional[datetime]
    responses: List[QueryResponseResponse] = []
    photos: List[QueryPhotoResponse] = []
    
    class Config:
        orm_mode = True


class QueryListResponse(BaseModel):
    """Schema for paginated query list response."""
    
    items: List[QueryResponse]
    total: int
    page: int
    limit: int
    total_pages: int
