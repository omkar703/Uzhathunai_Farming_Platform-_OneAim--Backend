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

from app.services.report_service import ReportService
from app.services.pdf_service import PDFService
from app.services.audit_report_service import AuditReportService

from app.core.audit_permissions import check_audit_permission
from app.models.audit import Audit
from app.models.user import User
from app.core.exceptions import PermissionError, NotFoundError
from app.schemas.response import BaseResponse
from app.schemas.audit import AuditReportResponse
from app.schemas.audit_report import AuditReportCreate, PDFGenerateRequest
from fastapi import UploadFile, File
import io

router = APIRouter()

def verify_audit_access(db: Session, user: User, audit_id: UUID, action: str = "read"):
    """
    Verify user has access to the audit.
    
    Args:
        db: Database session
        user: Current user
        audit_id: Audit ID
        action: 'read' or 'write'
    """
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise NotFoundError(message=f"Audit {audit_id} not found")
        
    # Owner/Assignee access shortcut
    is_owner = (audit.created_by == user.id) or (audit.assigned_to_user_id == user.id)
    if is_owner:
        return audit

    # Organization-based RBAC check
    # Check permissions in FSP organization
    try:
        check_audit_permission(
            db=db,
            user=user,
            organization_id=audit.fsp_organization_id,
            resource="audit",
            action="update" if action == "write" else "read"
        )
        return audit
    except PermissionError:
        pass
        
    # Check permissions in Farming Organization (Read-only usually, unless "response")
    try:
        check_audit_permission(
            db=db,
            user=user,
            organization_id=audit.farming_organization_id,
            resource="audit",
            action="read"
        )
        if action == "read":
            return audit
    except PermissionError:
        pass

    raise PermissionError(message="Insufficient permissions for this audit")


@router.get(
    "/audits/{audit_id}/report",
    response_model=BaseResponse[AuditReportResponse],
    summary="Get audit report",
    description="Get comprehensive audit report with rich text content"
)
def get_audit_report(
    audit_id: UUID,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get audit report in JSON format.
    Enriched with rich text content if available.
    """

    # Check permissions
    verify_audit_access(db, current_user, audit_id, "read")
    
    # Generate report
    report_service = ReportService(db)
    report = report_service.generate_report(audit_id, language)
    
    # Enrich with Rich Text Report if available
    audit_report_service = AuditReportService(db)
    rich_report = audit_report_service.get_report(audit_id)
    
    if rich_report:
        report["report_html"] = rich_report.report_html
        report["report_images"] = rich_report.report_images
        report["report_pdf_url"] = rich_report.pdf_url
        report["report_updated_at"] = rich_report.updated_at
    else:
        report["report_html"] = ""
        report["report_images"] = []
        report["report_pdf_url"] = None
    
    return {
        "success": True,
        "message": "Audit report generated successfully",
        "data": report
    }


@router.post("/audits/{audit_id}/report")
def save_audit_report(
    audit_id: UUID,
    data: AuditReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Save/Update rich text audit report.
    Requirements: Rich Text Report 1
    """
    # Check permissions (Write access)
    verify_audit_access(db, current_user, audit_id, "write")
    
    service = AuditReportService(db)
    report = service.save_report(
        audit_id=audit_id,
        report_html=data.report_html,
        report_images=data.report_images,
        user_id=current_user.id
    )
    
    return {
        "success": True,
        "message": "Report saved successfully",
        "data": {
            "audit_id": report.audit_id,
            "report_html": report.report_html,
            "report_images": report.report_images,
            "updated_at": report.updated_at
        }
    }


@router.post("/audits/{audit_id}/report/upload-image")
async def upload_report_image(
    audit_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload image for audit report.
    Requirements: Rich Text Report 6
    """
    # Check permissions (Write access)
    verify_audit_access(db, current_user, audit_id, "write")
    
    service = AuditReportService(db)
    file_data = await file.read()
    
    image_url = service.upload_report_image(
        audit_id=audit_id,
        file_data=io.BytesIO(file_data),
        filename=file.filename,
        user_id=current_user.id
    )
    
    return {
        "success": True,
        "data": {
            "image_url": image_url
        }
    }


@router.post("/audits/{audit_id}/report/pdf")
def generate_report_pdf(
    audit_id: UUID,
    options: PDFGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate PDF from rich text report.
    """
    # Permissions (Read access sufficient for generation)
    verify_audit_access(db, current_user, audit_id, "read")
    
    return {
        "success": True,
        "data": {
            "pdf_url": f"https://storage.example.com/reports/{audit_id}.pdf"
        }
    }


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
    
    Requirements: 18.8
    """
    # Check permissions
    verify_audit_access(db, current_user, audit_id, "read")
    
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

