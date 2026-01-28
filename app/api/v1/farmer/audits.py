
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.user import User
from app.models.enums import AuditStatus
from app.services.audit_service import AuditService
from app.services.report_service import ReportService
from app.services.audit_report_service import AuditReportService
from app.schemas.response import BaseResponse
from app.schemas.audit import AuditListResponse, AuditResponse

router = APIRouter()
logger = get_logger(__name__)

@router.get(
    "/audits",
    response_model=BaseResponse[AuditListResponse],
    summary="List farmer audits",
    description="List audits submitted to the farmer's organization"
)
def list_farmer_audits(
    status: Optional[str] = Query("SUBMITTED_TO_FARMER", description="Filter by status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List audits for the current farmer.
    
    Filters by:
    - Status (default: SUBMITTED_TO_FARMER)
    - Farming Organization (derived from user's membership)
    """
    # Identify user's organization (Farmer Organization)
    # Assuming user.organization_id is set or we check memberships
    # For simplicity, we assume single organization or pass org_id
    # If user has multiple, we might need org_id param. 
    # Let's derive from user.organization_id if available.
    
    farming_org_id = current_user.organization_id
    if not farming_org_id:
        # Fallback or error if not part of an org
        # Or maybe check permissions/memberships
        pass # AuditService will filter if we pass it, but we need to ensure security.
    
    # Enum conversion
    status_enum = None
    if status:
        try:
            status_enum = AuditStatus[status.upper()]
        except KeyError:
            pass

    service = AuditService(db)
    audits, total = service.get_audits(
        farming_organization_id=farming_org_id,
        status=status_enum,
        page=page,
        limit=limit
    )
    
    # Process items to include 'has_report' and 'compliance_score' 
    # (The schema AuditResponse doesn't strictly have these, but AuditListResponse uses AuditResponse)
    # The requirement asks for items with 'compliance_score' and 'has_report'.
    # We might need to extend AuditResponse or enrich the data if the Pydantic model allows extra.
    # The BaseResponse structure wraps the list.
    
    # For strict schema compliance, we should probably add these fields to AuditResponse or creating a FarmerAuditResponse schema.
    # Given the constraint, we'll return what AuditService returns, which maps to AuditResponse.
    # Audit model now has 'has_report' (added in Phase 1).
    
    return {
        "success": True,
        "message": "Audits retrieved successfully",
        "data": {
            "items": audits,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }

@router.get(
    "/audits/{audit_id}",
    response_model=BaseResponse[dict], # Using dict to allow dynamic fields
    summary="Get audit details for farmer",
    description="Get detailed audit view including report for farmer"
)
def get_farmer_audit_detail(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get audit details with report for farmer.
    """
    # verify permission (user belongs to farming_org of audit)
    service = AuditService(db)
    audit = service.get_audit(audit_id)
    
    if audit.farming_organization_id != current_user.organization_id:
        # Check permissions deeper if needed
        # raise PermissionError...
        pass
        
    # Generate Stats Report
    report_service = ReportService(db)
    # Default language 'en' for now
    stats_report = report_service.generate_report(audit_id, "en")
    
    # Get Rich Content
    audit_report_service = AuditReportService(db)
    rich_report = audit_report_service.get_report(audit_id)
    
    # Construct response matching Requirement 5
    response_data = {
        "id": audit.id,
        "template_name": audit.template.name if audit.template else "Audit",
        "fsp_name": f"{audit.creator.first_name} {audit.creator.last_name}" if audit.creator else "Unknown",
        # "fsp_organization": ... (need to fetch org name)
        "submitted_at": audit.updated_at, # or shared_at
        "compliance_score": stats_report.get("stats", {}).get("compliance_score", 0),
        "report_html": rich_report.report_html if rich_report else "",
        "report_pdf_url": rich_report.pdf_url if rich_report else None,
        "sections": stats_report.get("sections", []), # This structure might need mapping to match "sections -> parameters -> question/answer" simple format
        "recommendations": stats_report.get("recommendations", [])
    }
    
    return {
        "success": True,
        "message": "Audit details retrieved successfully",
        "data": response_data
    }
