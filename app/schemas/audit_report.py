
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# Report Content Schemas

class AuditReportCreate(BaseModel):
    """Schema for saving/updating audit report content"""
    report_html: Optional[str] = Field(None, description="Rich text HTML content")
    report_images: Optional[List[str]] = Field(default=[], description="List of image URLs used in report")

    class Config:
        json_schema_extra = {
            "example": {
                "report_html": "<h1>Audit Summary</h1><p>Farm is in good condition...</p>",
                "report_images": [
                    "https://storage.example.com/image1.jpg"
                ]
            }
        }

class AuditReportResponse(BaseModel):
    """Schema for returning audit report content"""
    audit_id: UUID
    report_html: Optional[str]
    report_images: List[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[UUID]

    class Config:
        from_attributes = True

# Image Upload Schema

class ImageUploadResponse(BaseModel):
    """Schema for image upload response"""
    image_url: str

# PDF Generation Schemas

class PDFGenerateRequest(BaseModel):
    """Schema for PDF generation options"""
    include_responses: bool = Field(True, description="Include question responses in PDF")
    include_photos: bool = Field(True, description="Include evidence photos in PDF")

class PDFGenerateResponse(BaseModel):
    """Schema for PDF generation response"""
    pdf_url: str
    expires_at: Optional[datetime] = None
