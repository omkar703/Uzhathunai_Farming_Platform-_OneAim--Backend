"""
Input Items API endpoints for Uzhathunai v2.0.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.input_item import (
    InputItemCategoryCreate,
    InputItemCategoryUpdate,
    InputItemCategoryResponse,
    InputItemCreate,
    InputItemUpdate,
    InputItemResponse,
    InputItemListResponse
)
from app.services.input_item_service import InputItemService

from app.core.organization_context import get_organization_id
from app.models.enums import OrganizationType, InputItemType

router = APIRouter()


# ============================================================================
# Input Item Category Endpoints
# ============================================================================

@router.get("/categories", response_model=List[InputItemCategoryResponse])
def get_input_item_categories(
    include_system: bool = Query(True, description="Include system-defined categories"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get input item categories for the current user's organization.
    
    - **include_system**: Include system-defined categories (default: true)
    - **language**: Language code for translations (default: en)
    
    Returns list of input item categories (system and org-specific).
    """
    service = InputItemService(db)
    
    # Check for system user privilege
    if current_user.is_system_user():
        org_id = None
    else:
        # Get organization ID from JWT token with Smart Inference
        org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    return service.get_categories(org_id, language, include_system)


@router.post("/categories", response_model=InputItemCategoryResponse, status_code=201)
def create_input_item_category(
    data: InputItemCategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an organization-specific input item category.
    
    Only organization admins can create categories.
    System-defined categories cannot be created through this endpoint.
    """
    service = InputItemService(db)
    
    # Check for system user privilege
    if current_user.is_system_user():
        org_id = None
    else:
        # Get organization ID from JWT token with Smart Inference
        org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # TODO: Add RBAC check for admin role
    
    return service.create_org_category(data, org_id, current_user.id)


@router.put("/categories/{category_id}", response_model=InputItemCategoryResponse)
def update_input_item_category(
    category_id: UUID,
    data: InputItemCategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an organization-specific input item category.
    
    Only organization admins can update categories.
    System-defined categories cannot be updated.
    """
    service = InputItemService(db)
    
    # Check for system user privilege
    if current_user.is_system_user():
        org_id = None
    else:
        # Get organization ID from JWT token with Smart Inference
        org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # TODO: Add RBAC check for admin role
    
    return service.update_org_category(category_id, data, org_id, current_user.id)


@router.delete("/categories/{category_id}", status_code=204)
def delete_input_item_category(
    category_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an organization-specific input item category.
    
    Only organization admins can delete categories.
    System-defined categories cannot be deleted.
    """
    service = InputItemService(db)
    
    # Check for system user privilege
    if current_user.is_system_user():
        org_id = None
    else:
        # Get organization ID from JWT token with Smart Inference
        org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # TODO: Add RBAC check for admin role
    
    service.delete_org_category(category_id, org_id, current_user.id)
    return None


# ============================================================================
# Input Item Endpoints
# ============================================================================

@router.get("/", response_model=InputItemListResponse)
def get_input_items(
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    include_system: bool = Query(True, description="Include system-defined items"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query for name or code"),
    type: Optional[InputItemType] = Query(None, description="Filter by item type (FERTILIZER, PESTICIDE)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated input items for the current user's organization.
    
    - **category_id**: Optional filter by category UUID
    - **include_system**: Include system-defined items (default: true)
    - **language**: Language code for translations (default: en)
    - **page**: Page number for pagination (default: 1)
    - **limit**: Number of items per page (default: 50, max: 100)
    - **search**: Search string for item name or code
    - **type**: Filter by item type (FERTILIZER, PESTICIDE, etc.)
    
    Returns a paginated list of input items.
    """
    service = InputItemService(db)
    
    # Check for system user privilege
    if current_user.is_system_user():
        org_id = None
    else:
        # Get organization ID from JWT token with Smart Inference
        org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    data = service.get_items(org_id, category_id, language, include_system, page, limit, search, item_type=type)
    return {"success": True, "data": data}


@router.post("/", response_model=InputItemResponse, status_code=201)
def create_input_item(
    data: InputItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an organization-specific input item.
    
    Only organization admins can create items.
    System-defined items cannot be created through this endpoint.
    """
    service = InputItemService(db)
    
    # Check for system user privilege
    if current_user.is_system_user():
        org_id = None
    else:
        # Get organization ID from JWT token with Smart Inference
        org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # TODO: Add RBAC check for admin role
    
    return service.create_org_item(data, org_id, current_user.id)


@router.put("/{item_id}", response_model=InputItemResponse)
def update_input_item(
    item_id: UUID,
    data: InputItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an organization-specific input item.
    
    Only organization admins can update items.
    System-defined items cannot be updated.
    """
    service = InputItemService(db)
    
    # Check for system user privilege
    if current_user.is_system_user():
        org_id = None
    else:
        # Get organization ID from JWT token with Smart Inference
        org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # TODO: Add RBAC check for admin role
    
    return service.update_org_item(item_id, data, org_id, current_user.id)


@router.delete("/{item_id}", status_code=204)
def delete_input_item(
    item_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an organization-specific input item.
    
    Only organization admins can delete items.
    System-defined items cannot be deleted.
    """
    service = InputItemService(db)
    
    # Check for system user privilege
    if current_user.is_system_user():
        org_id = None
    else:
        # Get organization ID from JWT token with Smart Inference
        org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # TODO: Add RBAC check for admin role
    
    service.delete_org_item(item_id, org_id, current_user.id)
    return None
