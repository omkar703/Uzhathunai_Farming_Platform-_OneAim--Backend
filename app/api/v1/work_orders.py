"""
Work Order API endpoints for Uzhathunai v2.0.
Handles work order CRUD operations, acceptance workflow, and scope management.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
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
    WorkOrderScopePermissionsUpdate
)
from app.services.work_order_service import WorkOrderService
from app.services.work_order_scope_service import WorkOrderScopeService

router = APIRouter()


@router.post(
    "",
    response_model=WorkOrderWithScopeResponse,
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
    
    - **farming_organization_id**: Farming organization ID (required)
    - **fsp_organization_id**: FSP organization ID (required)
    - **title**: Work order title (required, 1-200 chars)
    - **description**: Work order description (optional)
    - **service_listing_id**: Reference to FSP service listing (optional)
    - **terms_and_conditions**: Terms and conditions (optional)
    - **start_date**: Start date (optional)
    - **end_date**: End date (optional)
    - **total_amount**: Total amount (optional)
    - **currency**: Currency code (default: INR)
    - **scope_items**: List of scope items (optional, can be added later)
    
    Initial status is PENDING. FSP must accept before work order becomes active.
    """
    work_order_service = WorkOrderService(db)
    scope_service = WorkOrderScopeService(db)
    
    # Create work order
    work_order = work_order_service.create_work_order(
        farming_organization_id=data.farming_organization_id,
        fsp_organization_id=data.fsp_organization_id,
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
    
    # Add scope items if provided
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
        
        # Refresh to get updated scope_metadata
        db.refresh(work_order)
    
    # Get scope items for response
    scope_items = scope_service.get_work_order_scope(work_order.id)
    
    # Build response
    response_data = WorkOrderResponse.from_orm(work_order).dict()
    response_data['scope_items'] = [
        WorkOrderScopeResponse.from_orm(item) for item in scope_items
    ]
    
    return response_data


@router.get(
    "",
    response_model=WorkOrderListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get work orders",
    description="Get work orders with pagination and filtering"
)
def get_work_orders(
    organization_id: Optional[UUID] = Query(None, description="Filter by organization (farming or FSP)"),
    status_filter: Optional[WorkOrderStatus] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get work orders with pagination.
    
    Supports filtering by organization and status.
    Returns paginated results with metadata.
    """
    service = WorkOrderService(db)
    work_orders, total = service.get_work_orders(
        user_id=current_user.id,
        organization_id=organization_id,
        status=status_filter,
        page=page,
        limit=limit
    )
    
    return {
        "items": work_orders,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 0
    }


@router.get(
    "/{work_order_id}",
    response_model=WorkOrderWithScopeResponse,
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
    
    return response_data


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
    response_model=WorkOrderResponse,
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
    return work_order


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
    response_model=WorkOrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete work order",
    description="Mark work order as completed (changes status to COMPLETED)"
)
def complete_work_order(
    work_order_id: UUID,
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
        user_id=current_user.id
    )
    return work_order


@router.post(
    "/{work_order_id}/cancel",
    response_model=WorkOrderResponse,
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
    return work_order


@router.get(
    "/{work_order_id}/scope",
    response_model=List[WorkOrderScopeResponse],
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
    return scope_items


@router.post(
    "/{work_order_id}/scope",
    response_model=List[WorkOrderScopeResponse],
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
    
    return scope_items


@router.put(
    "/{work_order_id}/scope/{scope_id}",
    response_model=WorkOrderScopeResponse,
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
    return scope_item
