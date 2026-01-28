"""
FSP Service API endpoints for Uzhathunai v2.0.
Handles FSP service listing operations and approval workflow.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.fsp_service import (
    MasterServiceResponse,
    FSPServiceListingResponse,
    FSPServiceListingCreate,
    FSPServiceListingUpdate,
    FSPApprovalDocumentCreate,
    FSPApprovalDocumentResponse,
    FSPOrganizationApprovalResponse,
    FSPApprovalReviewRequest,
    FSPServiceListingPaginatedResponse,
    FSPOrganizationApprovalPaginatedResponse
)
from app.schemas.response import BaseResponse
from app.schemas.organization import ClientResponse
from app.services.fsp_service_service import FSPServiceService
from app.services.fsp_approval_service import FSPApprovalService
from app.services.organization_service import OrganizationService
from app.models.enums import OrganizationType

router = APIRouter()

@router.get(
    "/clients",
    # ...
    response_model=BaseResponse[List[ClientResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get FSP clients",
    description="Get list of farming organizations served by the current FSP"
)
def get_fsp_clients(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of farming organizations served by the current FSP.
    
    Returns organizations that have at least one PENDING, ACCEPTED, or ACTIVE Work Order.
    User must be an Admin/Owner of an FSP Organization.
    """
    
    # 1. Get organization ID from context with Smart Inference
    fsp_org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FSP)
    
    # 2. Validate this is an FSP organization
    validate_organization_type(fsp_org_id, OrganizationType.FSP, db)
    
    org_service = OrganizationService(db)
    clients = org_service.get_fsp_clients(fsp_org_id, current_user.id)
    
    return {
        "success": True,
        "message": f"Retrieved {len(clients)} clients",
        "data": clients
    }


@router.get(
    "/master-services",
    response_model=BaseResponse[list[MasterServiceResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get master services",
    description="Get all available master services"
)
def get_master_services(
    db: Session = Depends(get_db)
):
    """
    Get all available master services.
    
    Used when creating/updating FSP organizations to select services offered.
    
    Returns list of master services with translations.
    """
    service = FSPServiceService(db)
    master_services = service.get_master_services()
    return {
        "success": True,
        "message": "Master services retrieved successfully",
        "data": master_services
    }


@router.get(
    "/organizations/{org_id}/services",
    response_model=BaseResponse[list[FSPServiceListingResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get organization services",
    description="Get all service listings for an FSP organization"
)
def get_organization_services(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all service listings for an FSP organization.
    
    All members can view their organization's services.
    """
    service = FSPServiceService(db)
    listings = service.get_organization_services(org_id, current_user.id)
    return {
        "success": True,
        "message": f"Retrieved {len(listings)} services",
        "data": listings
    }


@router.post(
    "/organizations/{org_id}/services",
    response_model=BaseResponse[FSPServiceListingResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create service listing",
    description="Create a new service listing for FSP organization"
)
def create_service_listing(
    org_id: UUID,
    data: FSPServiceListingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new service listing.
    
    Only FSP_OWNER/FSP_ADMIN can create service listings.
    
    - **service_id**: Master service ID (required)
    - **title**: Service title (required)
    - **description**: Service description (optional)
    - **service_area_districts**: Districts served (optional)
    - **pricing_model**: Pricing model (PER_HOUR, PER_DAY, etc.)
    - **base_price**: Base price (optional)
    
    Triggers approval process (organization status → IN_PROGRESS).
    """
    service = FSPServiceService(db)
    listing = service.create_service_listing(org_id, current_user.id, data)
    return {
        "success": True,
        "message": "Service listing created successfully",
        "data": listing
    }


@router.put(
    "/organizations/{org_id}/services/{service_id}",
    response_model=BaseResponse[FSPServiceListingResponse],
    status_code=status.HTTP_200_OK,
    summary="Update service listing",
    description="Update an existing service listing"
)
def update_service_listing(
    org_id: UUID,
    service_id: UUID,
    data: FSPServiceListingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update service listing.
    
    Only FSP_OWNER/FSP_ADMIN can update service listings.
    
    Changes trigger approval process (organization status → IN_PROGRESS).
    """
    service = FSPServiceService(db)
    listing = service.update_service_listing(service_id, current_user.id, data)
    return {
        "success": True,
        "message": "Service listing updated successfully",
        "data": listing
    }


@router.delete(
    "/organizations/{org_id}/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete service listing",
    description="Delete a service listing"
)
def delete_service_listing(
    org_id: UUID,
    service_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete service listing.
    
    Only FSP_OWNER/FSP_ADMIN of the owning organization can delete.
    """
    service = FSPServiceService(db)
    service.delete_service_listing(service_id, current_user.id)
    return None


# FSP Marketplace Endpoints

@router.get(
    "/fsp-marketplace/services",
    response_model=BaseResponse[FSPServiceListingPaginatedResponse],
    status_code=status.HTTP_200_OK,
    summary="Browse FSP marketplace",
    description="Get service listings from marketplace with filters"
)
def get_marketplace_services(
    fsp_organization_id: Optional[UUID] = Query(None, description="Filter by FSP organization ID"),
    service_type: Optional[UUID] = Query(None, description="Filter by master service ID"),
    district: Optional[str] = Query(None, description="Filter by service area district"),
    pricing_model: Optional[str] = Query(None, description="Filter by pricing model"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Browse FSP marketplace service listings.
    
    Returns only ACTIVE listings from ACTIVE or IN_PROGRESS FSP organizations.
    
    **Filters:**
    - **fsp_organization_id**: FSP organization ID
    - **service_type**: Master service ID
    - **district**: Service area district
    - **pricing_model**: PER_HOUR, PER_DAY, PER_ACRE, FIXED, CUSTOM
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    
    **Returns:**
    - **items**: List of service listings
    - **total**: Total count
    - **page**: Current page
    - **limit**: Items per page
    - **total_pages**: Total pages
    """
    service = FSPServiceService(db)
    listings, total = service.get_service_listings(
        fsp_organization_id=fsp_organization_id,
        service_type=service_type,
        district=district,
        pricing_model=pricing_model,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "message": "Marketplace services retrieved successfully",
        "data": {
            "items": listings,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


# FSP Approval Endpoints

@router.post(
    "/fsp-organizations/{org_id}/documents",
    response_model=BaseResponse[FSPApprovalDocumentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload approval document",
    description="Upload approval document for FSP organization"
)
def upload_approval_document(
    org_id: UUID,
    data: FSPApprovalDocumentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload approval document for FSP organization.
    
    FSP organization members can upload documents for SuperAdmin review.
    
    **Required fields:**
    - **document_type**: Type of document (e.g., "business_license", "tax_certificate")
    - **file_url**: URL of uploaded file
    - **file_key**: Storage key of file
    - **file_name**: Original file name
    """
    service = FSPApprovalService(db)
    document = service.upload_approval_document(
        fsp_org_id=org_id,
        user_id=current_user.id,
        document_type=data.document_type,
        file_url=data.file_url,
        file_key=data.file_key,
        file_name=data.file_name
    )
    return {
        "success": True,
        "message": "Approval document uploaded successfully",
        "data": document
    }


@router.get(
    "/fsp-organizations/{org_id}/documents",
    response_model=BaseResponse[list[FSPApprovalDocumentResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get approval documents",
    description="Get approval documents for FSP organization"
)
def get_approval_documents(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get approval documents for FSP organization.
    
    Accessible by organization members and SuperAdmin.
    """
    service = FSPApprovalService(db)
    documents = service.get_organization_documents(org_id, current_user.id)
    return {
        "success": True,
        "message": "Approval documents retrieved successfully",
        "data": documents
    }


@router.get(
    "/admin/fsp-approvals",
    response_model=BaseResponse[FSPOrganizationApprovalPaginatedResponse],
    status_code=status.HTTP_200_OK,
    summary="Get pending FSP approvals",
    description="Get FSP organizations pending approval (SuperAdmin only)"
)
def get_pending_approvals(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get FSP organizations pending approval.
    
    **SuperAdmin only**
    
    Returns FSP organizations with NOT_STARTED or IN_PROGRESS status.
    
    **Returns:**
    - **items**: List of organizations
    - **total**: Total count
    - **page**: Current page
    - **limit**: Items per page
    - **total_pages**: Total pages
    """
    service = FSPApprovalService(db)
    organizations, total = service.get_pending_approvals(
        user_id=current_user.id,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "message": "Pending approvals retrieved successfully",
        "data": {
            "items": organizations,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.post(
    "/admin/fsp-approvals/{org_id}/approve",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Approve/Reject FSP organization",
    description="Approve or reject FSP organization (SuperAdmin only)"
)
def review_fsp_organization(
    org_id: UUID,
    data: FSPApprovalReviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Approve or reject FSP organization.
    
    **SuperAdmin only**
    
    **Request body:**
    - **approve**: True to approve, False to reject
    - **notes**: Optional review notes
    
    **Approval:**
    - Sets organization status to ACTIVE
    - Allows FSP to create service listings
    
    **Rejection:**
    - Sets organization status back to NOT_STARTED
    - FSP must resubmit for approval
    """
    service = FSPApprovalService(db)
    organization = service.review_fsp_organization(
        fsp_org_id=org_id,
        admin_user_id=current_user.id,
        approve=data.approve,
        notes=data.notes
    )
    
    return {
        "success": True,
        "message": "Organization approved successfully" if data.approve else "Organization rejected",
        "data": {
            "id": str(organization.id),
            "name": organization.name,
            "status": organization.status
        }
    }
