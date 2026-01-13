"""
Report API endpoints for Farm Audit Management System.

Provides endpoints for generating audit reports in JSON and PDF formats.

Requirements: 18.1, 18.8
"""

from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.audit_permissions import require_audit_permission
from app.models.user import User
from app.services.report_service import ReportService
from app.services.pdf_service import PDFService

router = APIRouter()


@router.get("/audits/{audit_id}/report")
def get_audit_report(
    audit_id: UUID,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get audit report in JSON format.
    
    Returns comprehensive audit report including:
    - Audit details
    - Template information
    - Crop and organization information
    - Flagged responses (is_flagged_for_report = true)
    - Flagged photos (is_flagged_for_report = true)
    - All issues categorized by severity
    - All recommendations
    
    Supports multilingual content based on language parameter.
    
    Args:
        audit_id: UUID of the audit
        language: Language code (en, ta, ml)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dictionary containing complete report data
        
    Requirements: 18.1
    """
    # Check permissions
    require_audit_permission(
        db=db,
        user=current_user,
        permission_code="AUDIT_REVIEW",
        audit_id=audit_id
    )
    
    # Generate report
    report_service = ReportService(db)
    report = report_service.generate_report(audit_id, language)
    
    return report


@router.get("/audits/{audit_id}/report/pdf")
def get_audit_report_pdf(
    audit_id: UUID,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Response:
    """
    Get audit report as PDF download.
    
    Generates formatted PDF report with organization branding
    and proper section formatting.
    
    Args:
        audit_id: UUID of the audit
        language: Language code (en, ta, ml)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PDF file as download
        
    Requirements: 18.8
    """
    # Check permissions
    require_audit_permission(
        db=db,
        user=current_user,
        permission_code="AUDIT_REVIEW",
        audit_id=audit_id
    )
    
    # Generate PDF
    report_service = ReportService(db)
    pdf_service = PDFService(report_service)
    pdf_bytes = pdf_service.generate_pdf(audit_id, language)
    
    # Get audit number for filename
    report = report_service.generate_report(audit_id, language)
    audit_number = report.get("audit_details", {}).get("audit_number", "audit")
    filename = f"{audit_number}_report.pdf"
    
    # Return PDF as download
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

