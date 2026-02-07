"""
Work Order API endpoints for Uzhathunai v2.0.
Handles work order CRUD operations, acceptance workflow, and scope management.
"""
import io
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.enums import WorkOrderStatus
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderUpdate,
    WorkOrderResponse,
    WorkOrderWithScopeResponse,
    WorkOrderListResponse,
    WorkOrderStatusUpdate,
    WorkOrderScopeResponse,
    AddWorkOrderScopeRequest,
    WorkOrderScopePermissionsUpdate,
    WorkOrderScopePermissionsUpdate,
    WorkOrderAssignRequest,
    WorkOrderAccessUpdate,
    WorkOrderCompleteRequest
)
from app.schemas.response import BaseResponse
from app.services.work_order_service import WorkOrderService
from app.services.work_order_scope_service import WorkOrderScopeService

from app.core.organization_context import get_organization_id, validate_organization_type
from app.models.enums import OrganizationType, WorkOrderStatus

router = APIRouter()


@router.post(
    "",
    response_model=BaseResponse[WorkOrderWithScopeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create work order",
    description="Create a new work order between farming and FSP organizations"
)
def create_work_order(
    data: WorkOrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new work order.
    """
    # 1. Get initiator organization from context with SMART INFERENCE
    # Work orders are typically created by FARMERS hiring FSPs.
    # So we expect a FARMING context by default for creation.
    active_org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # 2. Logic: Ensure the participating organization matches the context
    # If the user is active in a FARMING org, force that as the farming_organization_id
    from app.models.organization import Organization
    active_org = db.query(Organization).filter(Organization.id == active_org_id).first()
    
    if active_org and active_org.organization_type == OrganizationType.FARMING:
        farming_org_id = active_org_id
        fsp_org_id = data.fsp_organization_id
    elif active_org and active_org.organization_type == OrganizationType.FSP:
        # FSP creating work order? (Less common but supported)
        farming_org_id = data.farming_organization_id
        fsp_org_id = active_org_id
    else:
        farming_org_id = data.farming_organization_id
        fsp_org_id = data.fsp_organization_id

    work_order_service = WorkOrderService(db)
    scope_service = WorkOrderScopeService(db)
    
    # Create work order
    work_order = work_order_service.create_work_order(
        farming_organization_id=farming_org_id,
        fsp_organization_id=fsp_org_id,
        title=data.title,
        description=data.description,
        service_listing_id=data.service_listing_id,
        terms_and_conditions=data.terms_and_conditions,
        start_date=data.start_date,
        end_date=data.end_date,
        total_amount=data.total_amount,
        currency=data.currency,
        user_id=current_user.id
    )
    
    # ... scope logic continues ...
    if data.scope_items:
        scope_items_data = [
            {
                "scope": item.scope.value,
                "scope_id": item.scope_id,
                "access_permissions": item.access_permissions,
                "sort_order": item.sort_order
            }
            for item in data.scope_items
        ]
        scope_service.add_work_order_scope(
            work_order_id=work_order.id,
            scope_items=scope_items_data,
            user_id=current_user.id
        )
        db.refresh(work_order)

    scope_items = scope_service.get_work_order_scope(work_order.id)
    response_data = WorkOrderResponse.from_orm(work_order).dict()
    response_data['scope_items'] = [
        WorkOrderScopeResponse.from_orm(item) for item in scope_items
    ]
    
    return {
        "success": True,
        "message": "Work order created successfully",
        "data": response_data
    }


@router.get(
    "",
    response_model=BaseResponse[WorkOrderListResponse],
    status_code=status.HTTP_200_OK,
    summary="Get work orders",
    description="Get work orders with pagination and filtering"
)
def get_work_orders(
    organization_id: Optional[UUID] = Query(None, description="Filter by any organization (farming or FSP)"),
    fsp_id: Optional[UUID] = Query(None, description="Filter specifically by FSP organization ID"),
    farming_id: Optional[UUID] = Query(None, description="Filter specifically by Farming organization ID"),
    status_filter: Optional[WorkOrderStatus] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get work orders with pagination.
    """
    from app.core.organization_context import get_organization_id
    
    # 1. Force the active organization ID as the base filter
    active_org_id = get_organization_id(current_user, db)
    
    service = WorkOrderService(db)
    work_orders, total = service.get_work_orders(
        user_id=current_user.id,
        organization_id=active_org_id if not organization_id else organization_id,
        fsp_organization_id=fsp_id,
        farming_organization_id=farming_id,
        status=status_filter,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "message": "Work orders retrieved successfully",
        "data": {
            "items": work_orders,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }
    
    return {
        "success": True,
        "message": "Work orders retrieved successfully",
        "data": {
            "items": work_orders,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }


@router.get(
    "/{work_order_id}",
    response_model=BaseResponse[WorkOrderWithScopeResponse],
    status_code=status.HTTP_200_OK,
    summary="Get work order details",
    description="Get work order details by ID including scope items"
)
def get_work_order(
    work_order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get work order details.
    
    Returns work order with all scope items.
    """
    work_order_service = WorkOrderService(db)
    scope_service = WorkOrderScopeService(db)
    
    # Get work order
    work_order = work_order_service.get_work_order(
        work_order_id=work_order_id,
        user_id=current_user.id
    )
    
    # Get scope items
    scope_items = scope_service.get_work_order_scope(work_order_id)
    
    # Build response
    response_data = WorkOrderResponse.from_orm(work_order).dict()
    response_data['scope_items'] = [
        WorkOrderScopeResponse.from_orm(item) for item in scope_items
    ]
    
    return {
        "success": True,
        "message": "Work order details retrieved successfully",
        "data": response_data
    }


@router.put(
    "/{work_order_id}",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update work order",
    description="Update work order details"
)
def update_work_order(
    work_order_id: UUID,
    data: WorkOrderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update work order details.
    
    Only non-status fields can be updated through this endpoint.
    Use status-specific endpoints for status changes.
    """
    # This would be implemented in WorkOrderService
    # For now, return not implemented
    from fastapi import HTTPException
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Work order update not yet implemented"
    )


@router.post(
    "/{work_order_id}/accept",
    response_model=BaseResponse[WorkOrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Accept work order",
    description="FSP accepts work order (changes status from PENDING to ACCEPTED)"
)
def accept_work_order(
    work_order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    FSP accepts work order.
    
    - Changes status from PENDING to ACCEPTED
    - Records acceptance timestamp and user
    - Grants FSP access to resources defined in scope
    
    Only FSP organization members can accept work orders.
    """
    service = WorkOrderService(db)
    work_order = service.accept_work_order(
        work_order_id=work_order_id,
        user_id=current_user.id
    )
    return {
        "success": True,
        "message": "Work order accepted successfully",
        "data": work_order
    }


@router.post(
    "/{work_order_id}/start",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Start work order",
    description="Mark work order as active (changes status to ACTIVE)"
)
def start_work_order(
    work_order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Start work order.
    
    - Changes status to ACTIVE
    - Indicates work has commenced
    
    Can be done by either farming or FSP organization.
    """
    service = WorkOrderService(db)
    work_order = service.update_work_order_status(
        work_order_id=work_order_id,
        new_status=WorkOrderStatus.ACTIVE,
        user_id=current_user.id
    )
    return work_order


@router.post(
    "/{work_order_id}/complete",
    response_model=BaseResponse[WorkOrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Complete work order",
    description="Mark work order as completed (changes status to COMPLETED)"
)
def complete_work_order(
    work_order_id: UUID,
    data: WorkOrderCompleteRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Complete work order.
    
    - Changes status to COMPLETED
    - Records completion timestamp
    - Revokes FSP access to farming organization resources
    
    Can be done by either farming or FSP organization.
    """
    service = WorkOrderService(db)
    work_order = service.update_work_order_status(
        work_order_id=work_order_id,
        new_status=WorkOrderStatus.COMPLETED,
        user_id=current_user.id,
        completion_notes=data.completion_notes,
        completion_photo_url=data.completion_photo_url
    )
    return {
        "success": True,
        "message": "Work order marked as completed",
        "data": work_order
    }


@router.post(
    "/{work_order_id}/cancel",
    response_model=BaseResponse[WorkOrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Cancel work order",
    description="Cancel work order (changes status to CANCELLED)"
)
def cancel_work_order(
    work_order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel work order.
    
    - Changes status to CANCELLED
    - Records cancellation timestamp
    - Revokes FSP access to farming organization resources
    
    Can be done by either farming or FSP organization.
    """
    service = WorkOrderService(db)
    work_order = service.update_work_order_status(
        work_order_id=work_order_id,
        new_status=WorkOrderStatus.CANCELLED,
        user_id=current_user.id
    )
    return {
        "success": True,
        "message": "Work order cancelled",
        "data": work_order
    }


@router.put(
    "/{work_order_id}/assign",
    response_model=BaseResponse[WorkOrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Assign work order",
    description="Assign work order to an FSP member"
)
def assign_work_order_member(
    work_order_id: UUID,
    data: WorkOrderAssignRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Assign work order to a member.
    
    - Updates assigned_to_user_id
    - Member must be part of FSP organization
    - Only FSP Admin/Manager can assign
    """
    service = WorkOrderService(db)
    work_order = service.assign_work_order(
        work_order_id=work_order_id,
        assigned_to_user_id=data.assigned_to_user_id,
        assigner_user_id=current_user.id
    )
    return {
        "success": True,
        "message": "Work order assigned successfully",
        "data": work_order
    }


@router.post(
    "/{work_order_id}/start",
    response_model=BaseResponse[WorkOrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Start work order",
    description="Start work order (changes status to ACTIVE)"
)
def start_work_order(
    work_order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Start work order project.
    
    - Changes status from ACCEPTED to ACTIVE
    - Sets start_date if not set
    - Only FSP Admin/Manager or Assigned Member can start
    """
    service = WorkOrderService(db)
    work_order = service.start_work_order(
        work_order_id=work_order_id,
        user_id=current_user.id
    )
    return {
        "success": True,
        "message": "Work order started successfully",
        "data": work_order
    }


@router.get(
    "/{work_order_id}/scope",
    response_model=BaseResponse[list[WorkOrderScopeResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get work order scope",
    description="Get all scope items for a work order"
)
def get_work_order_scope(
    work_order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get work order scope items.
    
    Returns list of all resources (organizations, farms, plots, crops)
    included in the work order scope with their access permissions.
    """
    service = WorkOrderScopeService(db)
    scope_items = service.get_work_order_scope(work_order_id)
    return {
        "success": True,
        "message": "Work order scope retrieved successfully",
        "data": scope_items
    }


@router.post(
    "/{work_order_id}/scope",
    response_model=BaseResponse[list[WorkOrderScopeResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="Add work order scope items",
    description="Add scope items to work order"
)
def add_work_order_scope(
    work_order_id: UUID,
    data: AddWorkOrderScopeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add scope items to work order.
    
    - **scope_items**: List of scope items to add
    
    Each scope item includes:
    - **scope**: Scope type (ORGANIZATION, FARM, PLOT, CROP)
    - **scope_id**: Resource ID
    - **access_permissions**: Permissions dict (read, write, track)
    - **sort_order**: Display order (optional)
    
    Supports mixed scope (multiple farms, plots, crops in single work order).
    """
    service = WorkOrderScopeService(db)
    
    scope_items_data = [
        {
            "scope": item.scope.value,
            "scope_id": item.scope_id,
            "access_permissions": item.access_permissions,
            "sort_order": item.sort_order
        }
        for item in data.scope_items
    ]
    
    scope_items = service.add_work_order_scope(
        work_order_id=work_order_id,
        scope_items=scope_items_data,
        user_id=current_user.id
    )
    
    return {
        "success": True,
        "message": "Scope items added successfully",
        "data": scope_items
    }


@router.put(
    "/{work_order_id}/scope/{scope_id}",
    response_model=BaseResponse[WorkOrderScopeResponse],
    status_code=status.HTTP_200_OK,
    summary="Update scope permissions",
    description="Update access permissions for a scope item"
)
def update_scope_permissions(
    work_order_id: UUID,
    scope_id: UUID,
    data: WorkOrderScopePermissionsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update scope item permissions.
    
    - **access_permissions**: New permissions dict (read, write, track)
    
    Permissions can be updated even after work order is accepted.
    Changes take effect immediately.
    """
    service = WorkOrderScopeService(db)
    scope_item = service.update_scope_permissions(
        scope_id=scope_id,
        permissions=data.access_permissions,
        user_id=current_user.id
    )
    return {
        "success": True,
        "message": "Scope permissions updated successfully",
        "data": scope_item
    }


@router.put(
    "/{work_order_id}/access",
    response_model=BaseResponse[WorkOrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Toggle work order access",
    description="Grant or revoke FSP access to farm data for this work order"
)
def toggle_work_order_access(
    work_order_id: UUID,
    data: WorkOrderAccessUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle work order access.
    
    - **access_granted**: Boolean (true to grant access, false to revoke)
    
    Farmers can use this to temporarily or permanently revoke FSP access 
    without cancelling the contract.
    """
    service = WorkOrderService(db)
    work_order = service.toggle_work_order_access(
        work_order_id=work_order_id,
        access_granted=data.access_granted,
        user_id=current_user.id
    )
    
    return {
        "success": True,
        "message": f"Access {'granted' if data.access_granted else 'revoked'} successfully",
        "data": work_order
    }


@router.post(
    "/{work_order_id}/upload-proof",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Upload work order completion proof",
    description="Upload a photo as proof of work completion"
)
async def upload_work_order_proof(
    work_order_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload completion proof photo.
    """
    service = WorkOrderService(db)
    
    # Read file data
    file_data = await file.read()
    
    # Upload proof
    file_url = service.upload_completion_proof(
        work_order_id=work_order_id,
        file_data=io.BytesIO(file_data),
        filename=file.filename,
        user_id=current_user.id
    )
    
    return {
        "success": True,
        "message": "Completion proof uploaded successfully",
        "data": {"file_url": file_url}
    }
