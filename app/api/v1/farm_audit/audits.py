"""
Audits API endpoints for Farm Audit Management in Uzhathunai v2.0.

Provides endpoints for audit creation, retrieval, and structure queries.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import io
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status, Request, UploadFile, File, Form, Body, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.user import User
from app.models.enums import AuditStatus
from app.schemas.audit import (
    AuditCreate,
    AuditResponse,
    AuditListResponse,
    AuditStructureResponse,
    ResponseSubmit,
    ResponseUpdate,
    ResponseBulkSubmit,
    AuditResponseDetail,
    AuditResponseListResponse,
    PhotoUploadResponse,
    PhotoListResponse,
    StatusTransitionRequest,
    ValidationResult,
    AuditStatusEnum,
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    FlagRequest,
    PhotoAnnotationRequest,
    PhotoAnnotationResponse,
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueSeverityEnum,
    IssueListResponse,
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    RecommendationListResponse,
    RecommendationListResponse,
    AuditAssignRequest,
    AuditReportResponse,
    AuditRecommendationCreate,
    AuditRecommendationUpdate,
    AuditRecommendationResponse
)
from app.services.audit_service import AuditService
from app.services.response_service import ResponseService
from app.services.photo_service import PhotoService
from app.services.workflow_service import WorkflowService
from app.services.review_service import ReviewService
from app.services.remote_audit_service import RemoteAuditService
from app.services.finalization_service import FinalizationService
from app.services.sharing_service import SharingService
from app.services.report_service import ReportService
from app.services.audit_report_service import AuditReportService
from app.schemas.response import BaseResponse

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/audits",
    response_model=BaseResponse[AuditResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new audit",
    description="Create a new audit from a template for a specific crop"
)
def create_audit(
    data: AuditCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new audit from a template.
    
    This endpoint:
    - Validates template and crop exist
    - Derives farming_organization_id from crop
    - Generates unique audit_number (AUD-YYYY-NNNN)
    - Creates template snapshot
    - Creates audit_parameter_instances with parameter snapshots
    - Initializes sync_status as 'synced'
    
    **Requirements: 7.1, 18.2, 18.3**
    """
    logger.info(
        "Creating audit via API",
        extra={
            "user_id": str(current_user.id),
            "template_id": str(data.template_id),
            "crop_id": str(data.crop_id)
        }
    )

    service = AuditService(db)
    audit = service.create_audit(
        template_id=data.template_id,
        crop_id=data.crop_id,
        fsp_organization_id=data.fsp_organization_id,
        name=data.name,
        user_id=current_user.id,
        work_order_id=data.work_order_id,
        audit_date=data.audit_date,
        assigned_to=data.assigned_to
    )

    return {
        "success": True,
        "message": "Audit created successfully",
        "data": audit
    }


@router.get(
    "/audits",
    response_model=BaseResponse[AuditListResponse],
    summary="Get audits with filtering and pagination",
    description="Retrieve audits with optional filtering by organization, crop, and status"
)
def get_audits(
    fsp_organization_id: Optional[UUID] = Query(None, alias="fsp_id", description="Filter by FSP organization"),
    fsp_org_id: Optional[UUID] = Query(None, alias="fsp_organization_id", description="Filter by FSP organization"),
    farming_organization_id: Optional[UUID] = Query(None, description="Filter by farming organization"),
    crop_id: Optional[UUID] = Query(None, description="Filter by crop"),
    work_order_id: Optional[UUID] = Query(None, description="Filter by work order"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user (UUID or 'ME')"),
    created_by: Optional[str] = Query(None, description="Filter by creator (UUID or 'ME')"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get audits with filtering and pagination.
    
    Supports filtering by:
    - FSP organization
    - Farming organization
    - Crop
    - Status
    
    **Requirements: 7.1**
    """
    
    actual_fsp_id = fsp_organization_id or fsp_org_id
    
    logger.info(
        "Getting audits via API",
        extra={
            "user_id": str(current_user.id),
            "fsp_organization_id": str(actual_fsp_id) if actual_fsp_id else None,
            "farming_organization_id": str(farming_organization_id) if farming_organization_id else None,
            "work_order_id": str(work_order_id) if work_order_id else None,
            "assigned_to": assigned_to,
            "page": page,
            "limit": limit
        }
    )

    # Convert status string to enum if provided
    status_enum = None
    if status:
        try:
            status_enum = AuditStatus[status.upper()]
        except KeyError:
            pass

    service = AuditService(db)
    audits, total = service.get_audits(
        fsp_organization_id=actual_fsp_id,
        farming_organization_id=farming_organization_id,
        crop_id=crop_id,
        work_order_id=work_order_id,
        status=status_enum,
        assigned_to_user_id=current_user.id if assigned_to == 'ME' else UUID(assigned_to) if assigned_to else None,
        created_by_user_id=current_user.id if created_by == 'ME' else UUID(created_by) if created_by else None,
        page=page,
        limit=limit
    )

    return {
        "success": True,
        "message": "Audits retrieved successfully (vDebug-1)",
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
    response_model=BaseResponse[AuditResponse],
    summary="Get audit by ID",
    description="Retrieve a specific audit by its ID"
)
def get_audit(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get audit by ID.
    
    Returns complete audit details including metadata and status.
    
    **Requirements: 7.1**
    """
    logger.info(
        "Getting audit by ID via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id)
        }
    )

    service = AuditService(db)
    audit = service.get_audit(audit_id)

    return {
        "success": True,
        "message": "Audit details retrieved successfully",
        "data": audit
    }


@router.delete(
    "/audits/{audit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete audit",
    description="Delete an audit"
)
def delete_audit(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an audit.
    
    **Requirements: 7.1**
    """
    logger.info(
        "Deleting audit via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id)
        }
    )

    service = AuditService(db)
    service.delete_audit(audit_id, current_user.id)

    return None


@router.get(
    "/audits/{audit_id}/structure",
    response_model=BaseResponse[AuditStructureResponse],
    summary="Get audit structure",
    description="Get complete audit structure with sections and parameters from snapshots"
)
def get_audit_structure(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get audit structure with sections and parameters.
    
    Returns the complete audit structure including:
    - Template snapshot
    - Sections with translations
    - Parameters with snapshots
    - Parameter instances
    
    This endpoint is useful for rendering the audit form with all
    necessary configuration data.
    
    **Requirements: 7.1**
    """
    logger.info(
        "Getting audit structure via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id)
        }
    )

    service = AuditService(db)
    structure = service.get_audit_structure(audit_id)

    return {
        "success": True,
        "message": "Audit structure retrieved successfully",
        "data": structure
    }


# Removed duplicate get_audit_report (moved to reports.py)



@router.put(
    "/audits/{audit_id}/assign",
    response_model=BaseResponse[AuditResponse],
    summary="Assign audit",
    description="Assign an audit to a field officer or analyst"
)
def assign_audit(
    audit_id: UUID,
    data: AuditAssignRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Assign an audit to a field officer or analyst.
    
    This endpoint allows:
    - Assigning to a field officer (assigned_to)
    - Assigning to an analyst (analyst_id)
    - Changing workflow state based on assignment (handled by service)
    
    **Requirements: 18.2**
    """
    logger.info(
        "Assigning audit via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "assigned_to": str(data.assigned_to) if data.assigned_to else None,
            "analyst_id": str(data.analyst_id) if data.analyst_id else None
        }
    )

    from app.services.audit_service import AuditService
    service = AuditService(db)
    
    audit = service.assign_audit(
        audit_id=audit_id,
        assigned_to=data.assigned_to,
        analyst_id=data.analyst_id,
        user_id=current_user.id
    )

    return {
        "success": True,
        "message": "Audit assigned successfully",
        "data": audit
    }


# Response Submission Endpoints

@router.post(
    "/audits/{audit_id}/responses",
    response_model=BaseResponse[AuditResponseDetail],
    status_code=status.HTTP_201_CREATED,
    summary="Submit audit response",
    description="Submit or update a response to an audit parameter"
)
def submit_response(
    audit_id: UUID,
    data: ResponseSubmit,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit a response to an audit parameter.
    
    This endpoint:
    - Validates response against parameter snapshot
    - Validates parameter type (TEXT, NUMERIC, DATE, SINGLE_SELECT, MULTI_SELECT)
    - Creates new response or updates existing one
    - Prevents modification of finalized/shared audits
    
    **Requirements: 8.1, 18.3**
    """
    logger.info(
        "Submitting audit response via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "parameter_instance_id": str(data.audit_parameter_instance_id)
        }
    )

    service = ResponseService(db)
    response = service.submit_response(
        audit_id=audit_id,
        data=data,
        user_id=current_user.id
    )

    return {
        "success": True,
        "message": "Response submitted successfully",
        "data": response
    }


@router.put(
    "/audits/{audit_id}/responses/{response_id}",
    response_model=BaseResponse[AuditResponseDetail],
    summary="Update audit response",
    description="Update an existing audit response"
)
def update_response(
    audit_id: UUID,
    response_id: UUID,
    data: ResponseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing audit response.
    
    This endpoint:
    - Validates response against parameter snapshot
    - Updates response fields
    - Prevents modification of finalized/shared audits
    
    **Requirements: 8.1, 18.3**
    """
    logger.info(
        "Updating audit response via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "response_id": str(response_id)
        }
    )

    service = ResponseService(db)
    response = service.update_response(
        audit_id=audit_id,
        response_id=response_id,
        data=data,
        user_id=current_user.id
    )

    return {
        "success": True,
        "message": "Response updated successfully",
        "data": response
    }


@router.put(
    "/audits/{audit_id}/responses/{response_id}/flag",
    response_model=BaseResponse[dict],
    summary="Toggle flag on audit response",
    description="Toggle the flagged status of a response for report generation"
)
def toggle_response_flag(
    audit_id: UUID,
    response_id: UUID,
    data: FlagRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle flag details for an audit response.
    
    This is used during curation to mark responses for inclusion in the final report.
    """
    logger.info(
        "Toggling response flag via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "response_id": str(response_id),
            "is_flagged": data.is_flagged
        }
    )

    from app.services.review_service import ReviewService
    service = ReviewService(db)
    
    # Check if a review exists for this response
    review = service.get_review_by_response(audit_id, response_id)
    
    if review:
        # Update existing review
        updated_review = service.update_review_flag(audit_id, review.id, data.is_flagged, current_user.id)
        result = updated_review
    else:
        # Create new review entry solely for the flag
        review_data = ReviewCreate(
            audit_response_id=response_id,
            is_flagged_for_report=data.is_flagged,
            reviewer_comment="" # Empty comment for simple flag
        )
        result = service.create_review(audit_id, review_data, current_user.id)

    return {
        "success": True,
        "message": "Flag updated successfully",
        "data": {
            "id": str(result.id),
            "is_flagged": result.is_flagged_for_report
        }
    }


from fastapi import Request
from fastapi.concurrency import run_in_threadpool

@router.post(
    "/audits/{audit_id}/responses/save",
    response_model=BaseResponse[AuditResponseListResponse],
    summary="Save audit responses",
    description="Save multiple responses for an audit (Simplified endpoint)"
)
async def save_audit_responses(
    audit_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Save multiple responses to audit parameters.
    Uses generic Request object to bypass validation caching issues and provide deep debugging.
    """
    print(f"DEBUG: [SimpleSave] Entered async endpoint for audit {audit_id}", flush=True)
    
    try:
        # 1. Read Raw Body
        body_bytes = await request.body()
        print(f"DEBUG: [SimpleSave] Raw body length: {len(body_bytes)} bytes", flush=True)
        
        if len(body_bytes) == 0:
             print("DEBUG: [SimpleSave] Empty body received!", flush=True)
             return {
                "success": False,
                "message": "Empty request body",
                "data": {"items": [], "total": 0}
            }

        # 2. Parse JSON
        json_data = await request.json()
        print(f"DEBUG: [SimpleSave] JSON parsed, type: {type(json_data)}", flush=True)
        
        # 3. Manual Validation / Reconstruction
        # Expecting List[Dict] directly
        if isinstance(json_data, list):
            responses_data = json_data
        elif isinstance(json_data, dict) and "responses" in json_data:
            responses_data = json_data["responses"]
        else:
            print(f"DEBUG: [SimpleSave] Unexpected format: {json_data}", flush=True)
            responses_data = []

        print(f"DEBUG: [SimpleSave] Processing {len(responses_data)} items", flush=True)

        # Convert to Pydantic models manually to ensure valid data for service
        pydantic_responses = []
        for item in responses_data:
            # Hotfix: Client sending photos in response_date
            if "response_date" in item and isinstance(item["response_date"], list):
                print(f"DEBUG: [SimpleSave] Found list in response_date (len={len(item['response_date'])}), moving to evidence_urls", flush=True)
                if not item.get("evidence_urls"):
                    item["evidence_urls"] = item["response_date"]
                else:
                    item["evidence_urls"].extend(item["response_date"])
                item["response_date"] = None
            
            # Hotfix: Client sending photos in response_options (for Select types)
            # Check if non-empty list and first item is string with '/' (path) -> likely photos
            if ("response_options" in item and 
                isinstance(item["response_options"], list) and 
                item["response_options"] and 
                isinstance(item["response_options"][0], str) and 
                "/" in item["response_options"][0]):
                
                print(f"DEBUG: [SimpleSave] Found paths in response_options (len={len(item['response_options'])}), moving to evidence_urls", flush=True)
                if not item.get("evidence_urls"):
                    item["evidence_urls"] = item["response_options"]
                else:
                    item["evidence_urls"].extend(item["response_options"])
                item["response_options"] = None

            # Hotfix: Client sending photos in response_numeric
            if "response_numeric" in item and isinstance(item["response_numeric"], list):
                print(f"DEBUG: [SimpleSave] Found list in response_numeric (len={len(item['response_numeric'])}), moving to evidence_urls", flush=True)
                if not item.get("evidence_urls"):
                    item["evidence_urls"] = item["response_numeric"]
                else:
                    item["evidence_urls"].extend(item["response_numeric"])
                item["response_numeric"] = None

            pydantic_responses.append(ResponseSubmit(**item))

        # 4. Service Call (in threadpool)
        print("DEBUG: [SimpleSave] Initialising ResponseService", flush=True)
        service = ResponseService(db)
        
        bulk_data = ResponseBulkSubmit(responses=pydantic_responses)
        
        print("DEBUG: [SimpleSave] Awaiting service.submit_bulk_responses in threadpool", flush=True)
        t_start = datetime.now()
        
        # run_in_threadpool is essential for async def calling sync DB code
        saved_responses = await run_in_threadpool(
            service.submit_bulk_responses,
            audit_id=audit_id,
            data=bulk_data,
            user_id=current_user.id
        )
        
        duration = (datetime.now() - t_start).total_seconds()
        print(f"DEBUG: [SimpleSave] Service call completed in {duration}s", flush=True)

        return {
            "success": True,
            "message": "Responses saved successfully",
            "data": {
                "items": saved_responses,
                "total": len(saved_responses)
            }
        }
    except Exception as e:
        print(f"ERROR: [SimpleSave] Failed: {e}", flush=True)
        logger.error(f"Save responses failed: {e}", exc_info=True)
        raise


@router.get(
    "/audits/{audit_id}/responses",
    response_model=BaseResponse[AuditResponseListResponse],
    summary="Get audit responses",
    description="Get all responses for an audit"
)
def get_audit_responses(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all responses for an audit.
    
    Returns all submitted responses for the audit, ordered by creation time.
    
    **Requirements: 8.1, 18.3**
    """
    logger.info(
        "Getting audit responses via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id)
        }
    )

    service = ResponseService(db)
    responses = service.get_audit_responses(audit_id)

    return {
        "success": True,
        "message": "Audit responses retrieved successfully",
        "data": {
            "items": responses,
            "total": len(responses)
        }
    }


# Photo Management Endpoints

@router.post(
    "/audits/{audit_id}/responses/{response_id}/photos",
    response_model=BaseResponse[PhotoUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload photo for audit response",
    description="Upload a photo for an audit response with validation and compression"
)
async def upload_photo(
    audit_id: UUID,
    response_id: UUID,
    file: UploadFile = File(..., description="Photo file (JPEG/PNG, max 10MB)"),
    caption: Optional[str] = Form(None, description="Optional photo caption"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a photo for an audit response.
    
    This endpoint:
    - Validates photo count against min_photos/max_photos from parameter_metadata
    - Validates file size (max 10MB)
    - Validates file format (JPEG, PNG)
    - Compresses image to reduce size
    - Uploads to storage (S3 or local)
    - Creates photo record
    
    **Requirements: 9.1, 18.3**
    """
    logger.info(
        "Uploading photo via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "response_id": str(response_id),
            "filename": file.filename
        }
    )

    service = PhotoService(db)
    
    # Read file data
    file_data = await file.read()
    
    # Upload photo
    photo = service.upload_photo(
        audit_id=audit_id,
        response_id=response_id,
        file_data=io.BytesIO(file_data),
        filename=file.filename,
        caption=caption,
        user_id=current_user.id
    )

    return {
        "success": True,
        "message": "Photo uploaded successfully",
        "data": photo
    }


@router.post(
    "/audits/{audit_id}/evidence",
    response_model=BaseResponse[PhotoUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload evidence photo",
    description="Upload a photo as evidence for an audit (not yet linked to a response)"
)
async def upload_evidence(
    audit_id: UUID,
    file: UploadFile = File(..., description="Photo file (JPEG/PNG, max 10MB)"),
    caption: Optional[str] = Form(None, description="Optional photo caption"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a photo as evidence.
    
    This endpoint allows uploading photos before submitting the response.
    The returned URL can be included in the response submission.
    
    **Requirements: 9.1**
    """
    logger.info(
        "Uploading evidence via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "filename": file.filename
        }
    )

    service = PhotoService(db)
    
    # Read file data
    file_data = await file.read()
    
    # Upload photo
    photo = service.upload_evidence(
        audit_id=audit_id,
        file_data=io.BytesIO(file_data),
        filename=file.filename,
        caption=caption,
        user_id=current_user.id
    )

    return {
        "success": True,
        "message": "Evidence uploaded successfully",
        "data": photo
    }


@router.get(
    "/audits/{audit_id}/evidence",
    response_model=BaseResponse[PhotoListResponse],
    summary="Get evidence photos",
    description="Get all evidence photos for an audit (including those not linked to responses)"
)
def get_audit_evidence(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all evidence photos for an audit.
    
    Returns all photos associated with the audit, regardless of whether
    they are linked to a specific response or strictly 'evidence'.
    
    **Requirements: 9.1**
    """
    logger.info(
        "Getting audit evidence via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id)
        }
    )

    from app.models.audit import AuditResponsePhoto
    
    # Query all photos for this audit
    photos = db.query(AuditResponsePhoto).filter(
        AuditResponsePhoto.audit_id == audit_id
    ).order_by(AuditResponsePhoto.uploaded_at.desc()).all()

    return {
        "success": True,
        "message": "Evidence retrieved successfully",
        "data": {
            "items": photos,
            "total": len(photos)
        }
    }


@router.get(
    "/audits/{audit_id}/responses/{response_id}/photos",
    response_model=BaseResponse[PhotoListResponse],
    summary="Get photos for audit response",
    description="Get all photos for an audit response"
)
def get_photos(
    audit_id: UUID,
    response_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all photos for an audit response.
    
    Returns all photos ordered by upload time.
    
    **Requirements: 9.1, 18.3**
    """
    logger.info(
        "Getting photos via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "response_id": str(response_id)
        }
    )

    service = PhotoService(db)
    photos = service.get_photos(audit_id, response_id)

    return {
        "success": True,
        "message": "Photos retrieved successfully",
        "data": {
            "items": photos,
            "total": len(photos)
        }
    }


@router.delete(
    "/audits/{audit_id}/responses/{response_id}/photos/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete audit photo",
    description="Delete a photo from an audit response"
)
def delete_photo(
    audit_id: UUID,
    response_id: UUID,
    photo_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a photo from an audit response.
    
    **Requirements: 9.1**
    """
    logger.info(
        "Deleting photo via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "response_id": str(response_id),
            "photo_id": str(photo_id)
        }
    )

    service = PhotoService(db)
    service.delete_photo(audit_id, response_id, photo_id, current_user.id)

    return None


@router.put(
    "/audits/{audit_id}/evidence/{evidence_id}/flag",
    response_model=BaseResponse[dict],
    summary="Toggle flag on evidence photo",
    description="Toggle the flagged status of an evidence photo for report generation"
)
def toggle_evidence_flag(
    audit_id: UUID,
    evidence_id: UUID,
    data: FlagRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle flag for an evidence photo.
    
    This is used during curation to select photos for the final report.
    """
    logger.info(
        "Toggling evidence flag via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "evidence_id": str(evidence_id),
            "is_flagged": data.is_flagged
        }
    )

    service = PhotoService(db)
    photo = service.toggle_photo_flag(audit_id, evidence_id, data.is_flagged, current_user.id)

    return {
        "success": True,
        "message": "Flag updated successfully",
        "data": {
            "id": str(photo.id),
            "is_flagged": photo.is_flagged_for_report
        }
    }


# Report Endpoints

@router.get(
    "/audits/{audit_id}/report",
    response_model=BaseResponse[AuditReportResponse],
    summary="Get farmer audit report",
    description="Get the curated audit report for farmers"
)
def get_farmer_report(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the curated audit report for farmers.
    
    Includes:
    - Audit Summary
    - Issues (with stats)
    - Recommendations (standalone & schedule)
    - Flagged Items (Responses & Evidence)
    """
    logger.info(
        "Getting farmer report via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id)
        }
    )

    # Generate report using standardized ReportService
    report_service = ReportService(db)
    report = report_service.generate_report(audit_id, "en") # Standardizing on report service
    
    # Enrich with Rich Text Report if available (matching reports.py logic)
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
    
    return {
        "success": True,
        "message": "Report retrieved successfully (Standardized)",
        "data": report
    }


# Standalone Recommendations Endpoints

@router.post(
    "/audits/{audit_id}/recommendations",
    response_model=BaseResponse[AuditRecommendationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create standalone recommendation",
    description="Create a recommendation not linked to specific schedule tasks"
)
def create_audit_recommendation(
    audit_id: UUID,
    data: AuditRecommendationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a standalone recommendation.
    """
    logger.info(
        "Creating recommendation via API",
        extra={"audit_id": str(audit_id), "user_id": str(current_user.id)}
    )
    
    from app.models.audit import AuditRecommendation
    
    recommendation = AuditRecommendation(
        audit_id=audit_id,
        title=data.title,
        description=data.description,
        created_by=current_user.id
    )
    
    print(f"DEBUG: [StandaloneRec] Committing recommendation for audit {audit_id}", flush=True)
    db.add(recommendation)
    db.commit()
    print(f"DEBUG: [StandaloneRec] Committed recommendation for audit {audit_id}", flush=True)
    db.refresh(recommendation)
    
    return {
        "success": True,
        "message": "Recommendation created successfully",
        "data": recommendation
    }

@router.delete(
    "/audits/{audit_id}/recommendations/{recommendation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete standalone recommendation",
    description="Delete a standalone recommendation"
)
def delete_audit_recommendation(
    audit_id: UUID,
    recommendation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a standalone recommendation.
    """
    from app.models.audit import AuditRecommendation
    
    rec = db.query(AuditRecommendation).filter(
        AuditRecommendation.id == recommendation_id,
        AuditRecommendation.audit_id == audit_id
    ).first()
    
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
        
    db.delete(rec)
    db.commit()
    
    return None




@router.post(
    "/audits/{audit_id}/capture",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Capture remote audit snapshot",
    description="Capture a live snapshot from a Zoom video call and attach it to an audit."
)
async def capture_snapshot(
    audit_id: UUID,
    background_tasks: BackgroundTasks,
    session_id: UUID = Form(...),
    file: UploadFile = File(...),
    response_id: Optional[UUID] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Capture a live snapshot from a video session.
    
    Validates that the audit and video session are linked to the same work order.
    Processes the image in the background to avoid blocking the video call stream.
    """
    service = RemoteAuditService(db)
    
    # 1. Validate session and audit link
    service.validate_snapshot_session(audit_id, session_id)
    
    # 2. Read file data
    file_data = await file.read()
    
    # 3. Queue background processing
    background_tasks.add_task(
        service.process_snapshot,
        audit_id=audit_id,
        session_id=session_id,
        file_data=file_data,
        user_id=current_user.id,
        response_id=response_id
    )
    
    return {
        "success": True,
        "message": "Snapshot capture initiated successfully",
        "data": {
            "audit_id": str(audit_id),
            "session_id": str(session_id)
        }
    }


# Status Transition Endpoints

@router.post(
    "/audits/{audit_id}/transition",
    response_model=BaseResponse[AuditResponse],
    summary="Transition audit status",
    description="Transition audit to a new status with validation"
)
async def transition_audit_status(
    audit_id: UUID,
    data: StatusTransitionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Transition audit to a new status.
    
    This endpoint:
    - Validates status transition is valid (follows workflow rules)
    - Validates required responses are complete (for SUBMITTED status)
    - Validates photo requirements are met (for SUBMITTED status)
    - Updates audit status
    
    Valid transitions:
    - DRAFT → IN_PROGRESS
    - IN_PROGRESS → DRAFT, SUBMITTED
    - SUBMITTED → IN_PROGRESS, REVIEWED
    - REVIEWED → SUBMITTED, FINALIZED
    - FINALIZED → SHARED
    - SHARED → (terminal state)
    
    **Requirements: 10.1, 18.3**
    """
    print(f"DEBUG: [AsyncTransition] Entered endpoint for audit {audit_id}", flush=True)
    logger.info(
        "Transitioning audit status via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "to_status": data.to_status
        }
    )

    # Convert string enum to model enum
    try:
        target_status = AuditStatus[data.to_status.upper()]
    except KeyError:
        from app.core.exceptions import ValidationError
        raise ValidationError(
            message=f"Invalid status: {data.to_status}",
            error_code="INVALID_STATUS",
            details={"status": data.to_status}
        )

    print(f"DEBUG: [AsyncTransition] Calling WorkflowService.transition_status for audit {audit_id} to {target_status}")
    service = WorkflowService(db)
    
    # Use run_in_threadpool to unblock event loop during heavy transition logic (emails, PDF, etc.)
    t_start = datetime.now()
    audit = await run_in_threadpool(
        service.transition_status,
        audit_id=audit_id,
        to_status=target_status,
        user_id=current_user.id
    )
    duration = (datetime.now() - t_start).total_seconds()
    print(f"DEBUG: [AsyncTransition] Transition completed in {duration}s", flush=True)

    return {
        "success": True,
        "message": f"Audit transitioned to {target_status.value} successfully",
        "data": audit
    }


@router.post(
    "/audits/{audit_id}/complete",
    response_model=BaseResponse[AuditResponse],
    summary="Complete audit (Internal)",
    description="Mark audit as internally completed and ready for review"
)
def complete_audit(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark audit as internally completed.
    
    Transitions status to COMPLETED.
    Requires all required parameters to be answered.
    """
    logger.info(
        "Completing audit",
        extra={"audit_id": str(audit_id), "user_id": str(current_user.id)}
    )
    
    service = WorkflowService(db)
    audit = service.transition_status(
        audit_id=audit_id,
        to_status=AuditStatus.COMPLETED,
        user_id=current_user.id
    )
    
    return {
        "success": True,
        "message": "Audit completed successfully",
        "data": audit
    }


@router.post(
    "/audits/{audit_id}/publish",
    response_model=BaseResponse[AuditResponse],
    summary="Publish audit to farmer",
    description="Finalize and submit audit to farmer"
)
def publish_audit(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Publish audit to farmer.
    
    Transitions status to SHARED.
    Should be called after review (or directly if no review needed).
    """
    logger.info(
        "Publishing audit",
        extra={"audit_id": str(audit_id), "user_id": str(current_user.id)}
    )
    
    service = WorkflowService(db)
    audit = service.transition_status(
        audit_id=audit_id,
        to_status=AuditStatus.SHARED,
        user_id=current_user.id
    )
    
    return {
        "success": True,
        "message": "Audit published to farmer successfully",
        "data": audit
    }


@router.get(
    "/audits/{audit_id}/validation",
    response_model=BaseResponse[ValidationResult],
    summary="Validate audit submission readiness",
    description="Check if audit is ready for submission without transitioning"
)
def validate_audit_submission(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check if audit is ready for submission.
    
    This endpoint validates:
    - All required parameters have responses
    - Photo requirements are met for all parameters
    
    Returns validation results including any issues that would prevent submission.
    Useful for showing validation errors to users before they attempt to submit.
    
    **Requirements: 10.1, 18.3**
    """
    logger.info(
        "Validating audit submission via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id)
        }
    )

    service = WorkflowService(db)
    result = service.validate_submission_readiness(audit_id)

    return {
        "success": True,
        "message": "Validation complete",
        "data": result
    }


# Review Endpoints

@router.post(
    "/audits/{audit_id}/reviews",
    response_model=BaseResponse[ReviewResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create or update audit review",
    description="Create or update a review for an audit response"
)
def create_review(
    audit_id: UUID,
    data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create or update a review for an audit response.
    
    This endpoint:
    - Creates a new review or updates existing one (one review per response)
    - Allows reviewer to override response values
    - Allows flagging response for report inclusion
    - Enforces UNIQUE constraint on audit_response_id
    
    **Requirements: 11.1, 12.1, 18.4**
    """
    logger.info(
        "Creating/updating audit review via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "audit_response_id": str(data.audit_response_id)
        }
    )

    service = ReviewService(db)
    review = service.create_review(
        audit_response_id=data.audit_response_id,
        user_id=current_user.id,
        response_text=data.response_text,
        response_numeric=data.response_numeric,
        response_date=data.response_date,
        response_option_ids=data.response_option_ids,
        is_flagged_for_report=data.is_flagged_for_report
    )

    return {
        "success": True,
        "message": "Review created successfully",
        "data": review
    }


@router.put(
    "/audits/{audit_id}/reviews/{review_id}",
    response_model=BaseResponse[ReviewResponse],
    summary="Update audit review",
    description="Update an existing audit review"
)
def update_review(
    audit_id: UUID,
    review_id: UUID,
    data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing audit review.
    
    This endpoint:
    - Updates review fields
    - Allows partial updates (only provided fields are updated)
    
    **Requirements: 11.1, 12.1, 18.4**
    """
    logger.info(
        "Updating audit review via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "review_id": str(review_id)
        }
    )

    from app.models.audit import AuditReview
    from app.core.exceptions import NotFoundError

    # Get existing review
    review = db.query(AuditReview).filter(AuditReview.id == review_id).first()
    if not review:
        raise NotFoundError(
            message=f"Review {review_id} not found",
            error_code="REVIEW_NOT_FOUND",
            details={"review_id": str(review_id)}
        )

    # Update fields if provided
    if data.response_text is not None:
        review.response_text = data.response_text
    if data.response_numeric is not None:
        review.response_numeric = data.response_numeric
    if data.response_date is not None:
        review.response_date = data.response_date
    if data.response_option_ids is not None:
        review.response_option_ids = data.response_option_ids
    if data.is_flagged_for_report is not None:
        review.is_flagged_for_report = data.is_flagged_for_report
    
    review.reviewed_by = current_user.id
    review.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(review)

    return review


@router.post(
    "/audits/{audit_id}/reviews/{review_id}/flag",
    response_model=BaseResponse[ReviewResponse],
    summary="Flag response for report",
    description="Flag or unflag an audit response for report inclusion"
)
def flag_response(
    audit_id: UUID,
    review_id: UUID,
    data: FlagRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Flag or unflag an audit response for report inclusion.
    
    This endpoint:
    - Updates the is_flagged_for_report field
    - Creates a review if one doesn't exist
    
    **Requirements: 11.3, 12.1, 18.4**
    """
    logger.info(
        "Flagging response for report via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "review_id": str(review_id),
            "is_flagged": data.is_flagged
        }
    )

    from app.models.audit import AuditReview
    from app.core.exceptions import NotFoundError

    # Get existing review
    review = db.query(AuditReview).filter(AuditReview.id == review_id).first()
    if not review:
        raise NotFoundError(
            message=f"Review {review_id} not found",
            error_code="REVIEW_NOT_FOUND",
            details={"review_id": str(review_id)}
        )

    # Update flag
    review.is_flagged_for_report = data.is_flagged
    review.reviewed_by = current_user.id
    review.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(review)

    return review


@router.post(
    "/audits/{audit_id}/photos/{photo_id}/annotate",
    response_model=BaseResponse[PhotoAnnotationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Annotate photo",
    description="Add or update annotation for an audit response photo"
)
def annotate_photo(
    audit_id: UUID,
    photo_id: UUID,
    data: PhotoAnnotationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Annotate a photo with caption and/or flag for report inclusion.
    
    This endpoint:
    - Creates or updates photo annotation
    - Allows adding/modifying caption
    - Allows flagging photo for report inclusion
    
    **Requirements: 12.1, 12.2, 18.4**
    """
    logger.info(
        "Annotating photo via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "photo_id": str(photo_id)
        }
    )

    service = ReviewService(db)
    annotation = service.annotate_photo(
        audit_response_photo_id=photo_id,
        user_id=current_user.id,
        caption=data.caption,
        is_flagged_for_report=data.is_flagged_for_report
    )

    return {
        "success": True,
        "message": "Photo annotation updated successfully",
        "data": annotation
    }


# ============================================
# ISSUE MANAGEMENT ENDPOINTS
# ============================================

@router.post(
    "/audits/{audit_id}/issues",
    response_model=BaseResponse[IssueResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create audit issue",
    description="Create a new issue for an audit (SUBMITTED, REVIEWED, or FINALIZED status)"
)
def create_issue(
    audit_id: UUID,
    data: IssueCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an audit issue.
    
    Issues can be created during SUBMITTED, REVIEWED, and FINALIZED audit statuses.
    Each issue has a severity level (LOW, MEDIUM, HIGH, CRITICAL) and optional description.
    
    **Requirements: 13.1, 18.4**
    """
    logger.info(
        "Creating audit issue via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "severity": data.severity.value
        }
    )
    
    from app.services.issue_service import IssueService
    from app.models.enums import IssueSeverity
    
    service = IssueService(db)
    issue = service.create_issue(
        audit_id=audit_id,
        title=data.title,
        description=data.description,
        severity=IssueSeverity[data.severity.value],
        user_id=current_user.id
    )
    
    return {
        "success": True,
        "message": "Issue created successfully",
        "data": issue
    }


@router.get(
    "/audits/{audit_id}/issues",
    response_model=BaseResponse[IssueListResponse],
    summary="Get audit issues",
    description="Get all issues for an audit, optionally filtered by severity"
)
def get_audit_issues(
    audit_id: UUID,
    severity: Optional[IssueSeverityEnum] = Query(None, description="Filter by severity"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all issues for an audit.
    
    Issues are returned ordered by severity (CRITICAL first) and creation time.
    Optionally filter by severity level.
    
    **Requirements: 13.1**
    """
    logger.info(
        "Getting audit issues via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "severity_filter": severity.value if severity else None
        }
    )
    
    from app.services.issue_service import IssueService
    from app.models.enums import IssueSeverity
    
    service = IssueService(db)
    issues = service.get_audit_issues(
        audit_id=audit_id,
        severity=IssueSeverity[severity.value] if severity else None
    )
    
    return {
        "success": True,
        "message": "Audit issues retrieved successfully",
        "data": {
            "items": issues,
            "total": len(issues)
        }
    }


@router.put(
    "/audits/{audit_id}/issues/{issue_id}",
    response_model=BaseResponse[IssueResponse],
    summary="Update audit issue",
    description="Update an existing audit issue"
)
def update_issue(
    audit_id: UUID,
    issue_id: UUID,
    data: IssueUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an audit issue.
    
    Can update title, description, and/or severity level.
    
    **Requirements: 13.1**
    """
    logger.info(
        "Updating audit issue via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "issue_id": str(issue_id)
        }
    )
    
    from app.services.issue_service import IssueService
    from app.models.enums import IssueSeverity
    
    service = IssueService(db)
    issue = service.update_issue(
        issue_id=issue_id,
        title=data.title,
        description=data.description,
        severity=IssueSeverity[data.severity.value] if data.severity else None
    )
    
    return {
        "success": True,
        "message": "Issue updated successfully",
        "data": issue
    }


@router.delete(
    "/audits/{audit_id}/issues/{issue_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete audit issue",
    description="Delete an audit issue"
)
def delete_issue(
    audit_id: UUID,
    issue_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an audit issue.
    
    **Requirements: 13.1, 18.5**
    """
    logger.info(
        "Deleting audit issue via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id),
            "issue_id": str(issue_id)
        }
    )
    
    from app.services.issue_service import IssueService
    
    service = IssueService(db)
    service.delete_issue(issue_id)
    
    return None


# ============================================
# RECOMMENDATION ENDPOINTS
# ============================================

@router.post(
    "/audits/{audit_id}/schedule-recommendations",
    response_model=BaseResponse[RecommendationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create schedule recommendation",
    description="Create a recommendation for schedule changes (ADD/MODIFY/DELETE tasks) based on audit findings"
)
def create_schedule_recommendation(
    audit_id: UUID,
    data: RecommendationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a recommendation for schedule changes based on audit findings.
    
    Recommendations are stored in schedule_change_log with:
    - trigger_type = 'AUDIT'
    - trigger_reference_id = audit_id
    - is_applied = False (pending approval)
    
    **Requirements:** 14.1, 18.4
    """
    from app.services.recommendation_service import RecommendationService
    
    service = RecommendationService(db)
    recommendation = service.create_recommendation(
        audit_id=audit_id,
        schedule_id=data.schedule_id,
        change_type=data.change_type,
        task_id=data.task_id,
        task_details_before=data.task_details_before,
        task_details_after=data.task_details_after,
        change_description=data.change_description,
        user_id=current_user.id
    )
    
    print(f"DEBUG: [ScheduleRec] Recommendation object created, about to return", flush=True)
    return {
        "success": True,
        "message": "Recommendation created successfully",
        "data": recommendation
    }


@router.get(
    "/audits/{audit_id}/schedule-recommendations",
    response_model=BaseResponse[RecommendationListResponse],
    summary="Get audit schedule recommendations",
    description="Get all schedule linked recommendations for a specific audit with pagination"
)
def get_audit_schedule_recommendations(
    audit_id: UUID,
    is_applied: Optional[bool] = Query(None, description="Filter by applied status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all recommendations for a specific audit.
    
    Returns paginated list of recommendations with total count.
    
    **Requirements:** 14.1
    """
    from app.services.recommendation_service import RecommendationService
    
    service = RecommendationService(db)
    recommendations, total = service.get_audit_recommendations(
        audit_id=audit_id,
        is_applied=is_applied,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "message": "Audit recommendations retrieved successfully",
        "data": {
            "items": recommendations,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }


@router.put(
    "/audits/{audit_id}/schedule-recommendations/{recommendation_id}",
    response_model=BaseResponse[RecommendationResponse],
    summary="Update schedule recommendation",
    description="Update a schedule recommendation before it's applied"
)
def update_schedule_recommendation(
    audit_id: UUID,
    recommendation_id: UUID,
    data: RecommendationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a recommendation before it's applied.
    
    Only unapplied recommendations can be updated.
    
    **Requirements:** 14.1, 18.4
    """
    from app.services.recommendation_service import RecommendationService
    
    service = RecommendationService(db)
    recommendation = service.update_recommendation(
        recommendation_id=recommendation_id,
        change_description=data.change_description,
        task_details_after=data.task_details_after,
        user_id=current_user.id
    )
    
    return {
        "success": True,
        "message": "Recommendation updated successfully",
        "data": recommendation
    }


@router.delete(
    "/audits/{audit_id}/schedule-recommendations/{recommendation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete schedule recommendation",
    description="Delete a schedule recommendation before it's applied"
)
def delete_schedule_recommendation(
    audit_id: UUID,
    recommendation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a recommendation before it's applied.
    
    Only unapplied recommendations can be deleted.
    
    **Requirements:** 14.1, 18.4
    """
    from app.services.recommendation_service import RecommendationService
    
    service = RecommendationService(db)
    service.delete_recommendation(
        recommendation_id=recommendation_id,
        user_id=current_user.id
    )
    
    logger.info(
        "Recommendation deleted via API",
        extra={
            "recommendation_id": str(recommendation_id),
            "audit_id": str(audit_id),
            "user_id": str(current_user.id)
        }
    )
    
    return None


# ============================================================================
# Recommendation Approval Endpoints
# ============================================================================

@router.get(
    "/recommendations/pending",
    response_model=BaseResponse[RecommendationListResponse],
    summary="Get pending recommendations for farming organization",
    description="Get all pending recommendations for the current user's farming organization"
)
def get_pending_recommendations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all pending recommendations for the current user's farming organization.
    
    This endpoint is used by farming organization users to see all recommendations
    from audits that need their approval.
    
    **Requirements:** 15.1, 18.7
    """
    from app.services.recommendation_service import RecommendationService
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus, OrganizationType
    
    # Get user's farming organization
    # User must be a member of a farming organization
    farming_org_member = db.query(OrgMember).join(
        OrgMember.organization
    ).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == MemberStatus.ACTIVE,
        OrgMember.organization.has(organization_type=OrganizationType.FARMING)
    ).first()
    
    if not farming_org_member:
        raise PermissionError(
            message="User is not a member of any farming organization",
            error_code="NOT_FARMING_ORG_MEMBER"
        )
    
    service = RecommendationService(db)
    recommendations, total = service.get_pending_recommendations_for_organization(
        farming_org_id=farming_org_member.organization_id,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "message": "Pending recommendations retrieved successfully",
        "data": {
            "items": recommendations,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }


@router.post(
    "/recommendations/{recommendation_id}/approve",
    response_model=BaseResponse[RecommendationResponse],
    summary="Approve recommendation",
    description="Approve a recommendation and apply it to the schedule"
)
def approve_recommendation(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Approve a recommendation and apply it to the schedule.
    
    Sets is_applied=True and applies the recommended changes to the schedule.
    Only farming organization users can approve recommendations for their organization.
    
    **Requirements:** 15.3, 18.7
    """
    from app.services.recommendation_service import RecommendationService
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus, OrganizationType
    from app.models.schedule import ScheduleChangeLog
    from app.models.crop import Crop
    from app.models.plot import Plot
    from app.models.farm import Farm
    
    # Get recommendation
    recommendation = db.query(ScheduleChangeLog).filter(
        ScheduleChangeLog.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise NotFoundError(
            message=f"Recommendation {recommendation_id} not found",
            error_code="RECOMMENDATION_NOT_FOUND"
        )
    
    # Get the farming organization that owns the schedule
    schedule = recommendation.schedule
    crop = db.query(Crop).filter(Crop.id == schedule.crop_id).first()
    plot = db.query(Plot).filter(Plot.id == crop.plot_id).first()
    farm = db.query(Farm).filter(Farm.id == plot.farm_id).first()
    farming_org_id = farm.organization_id
    
    # Verify user is a member of the farming organization
    farming_org_member = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.organization_id == farming_org_id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not farming_org_member:
        raise PermissionError(
            message="User is not authorized to approve recommendations for this organization",
            error_code="NOT_AUTHORIZED"
        )
    
    service = RecommendationService(db)
    approved_recommendation = service.approve_recommendation(
        recommendation_id=recommendation_id,
        user_id=current_user.id
    )
    
    return {
        "success": True,
        "message": "Recommendation approved and applied successfully",
        "data": approved_recommendation
    }


@router.post(
    "/recommendations/{recommendation_id}/reject",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reject recommendation",
    description="Reject a recommendation without applying it"
)
def reject_recommendation(
    recommendation_id: UUID,
    rejection_data: dict = Body(..., example={"reason": "Not applicable at this time"}),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reject a recommendation without applying it.
    
    Deletes the recommendation from the change log.
    Only farming organization users can reject recommendations for their organization.
    
    **Requirements:** 15.3, 18.7
    """
    from app.services.recommendation_service import RecommendationService
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus, OrganizationType
    from app.models.schedule import ScheduleChangeLog
    from app.models.crop import Crop
    from app.models.plot import Plot
    from app.models.farm import Farm
    
    # Get recommendation
    recommendation = db.query(ScheduleChangeLog).filter(
        ScheduleChangeLog.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise NotFoundError(
            message=f"Recommendation {recommendation_id} not found",
            error_code="RECOMMENDATION_NOT_FOUND"
        )
    
    # Get the farming organization that owns the schedule
    schedule = recommendation.schedule
    crop = db.query(Crop).filter(Crop.id == schedule.crop_id).first()
    plot = db.query(Plot).filter(Plot.id == crop.plot_id).first()
    farm = db.query(Farm).filter(Farm.id == plot.farm_id).first()
    farming_org_id = farm.organization_id
    
    # Verify user is a member of the farming organization
    farming_org_member = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.organization_id == farming_org_id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not farming_org_member:
        raise PermissionError(
            message="User is not authorized to reject recommendations for this organization",
            error_code="NOT_AUTHORIZED"
        )
    
    # Reject recommendation
    service = RecommendationService(db)
    rejection_reason = rejection_data.get('reason')
    service.reject_recommendation(
        recommendation_id=recommendation_id,
        rejection_reason=rejection_reason,
        user_id=current_user.id
    )
    
    logger.info(
        "Recommendation rejected via API",
        extra={
            "recommendation_id": str(recommendation_id),
            "schedule_id": str(recommendation.schedule_id),
            "rejection_reason": rejection_reason,
            "user_id": str(current_user.id),
            "farming_org_id": str(farming_org_id)
        }
    )
    
    return None


# ============================================================================
# Audit Finalization Endpoint
# ============================================================================

@router.post(
    "/audits/{audit_id}/finalize",
    response_model=BaseResponse[AuditResponse],
    summary="Finalize audit",
    description="Finalize an audit, transitioning from REVIEWED to FINALIZED status"
)
def finalize_audit(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Finalize an audit.
    
    This endpoint:
    - Transitions audit status from REVIEWED to FINALIZED
    - Captures finalized_at timestamp and finalized_by user
    - Makes audit immutable (prevents further modifications)
    
    After finalization:
    - No modifications can be made to audit responses
    - No modifications can be made to reviews
    - No modifications can be made to issues
    - Audit can only transition to SHARED status
    
    **Requirements: 16.1, 18.5**
    """
    logger.info(
        "Finalizing audit via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id)
        }
    )

    service = FinalizationService(db)
    audit = service.finalize_audit(
        audit_id=audit_id,
        user_id=current_user.id
    )

    return {
        "success": True,
        "message": "Audit finalized successfully",
        "data": audit
    }



# ============================================================================
# Audit Sharing Endpoint
# ============================================================================

@router.post(
    "/audits/{audit_id}/share",
    response_model=BaseResponse[AuditResponse],
    summary="Share audit",
    description="Share a finalized audit with the farming organization"
)
def share_audit(
    audit_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Share a finalized audit with the farming organization.
    
    This endpoint:
    - Transitions audit status from FINALIZED to SHARED
    - Captures shared_at timestamp
    - Makes audit read-only for all parties (FSP and farming organizations)
    
    After sharing:
    - Audit becomes visible to farming organization
    - No modifications can be made by anyone
    - Audit is in terminal state (no further status transitions)
    
    **Requirements: 17.1, 18.6**
    """
    logger.info(
        "Sharing audit via API",
        extra={
            "user_id": str(current_user.id),
            "audit_id": str(audit_id)
        }
    )

    service = SharingService(db)
    audit = service.share_audit(
        audit_id=audit_id,
        user_id=current_user.id
    )

    return {
        "success": True,
        "message": "Audit shared successfully",
        "data": audit
    }
