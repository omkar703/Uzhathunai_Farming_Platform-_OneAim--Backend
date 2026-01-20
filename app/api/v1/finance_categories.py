"""
Finance Categories API endpoints for Uzhathunai v2.0.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.enums import TransactionType
from app.schemas.finance_category import (
    FinanceCategoryCreate,
    FinanceCategoryUpdate,
    FinanceCategoryResponse
)
from app.services.finance_category_service import FinanceCategoryService

router = APIRouter()


@router.get("/", response_model=List[FinanceCategoryResponse])
def get_finance_categories(
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type (INCOME, EXPENSE)"),
    include_system: bool = Query(True, description="Include system-defined categories"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get finance categories for the current user's organization.
    
    - **transaction_type**: Optional filter by transaction type (INCOME or EXPENSE)
    - **include_system**: Include system-defined categories (default: true)
    - **language**: Language code for translations (default: en)
    
    Returns list of finance categories (system and org-specific).
    """
    service = FinanceCategoryService(db)
    
    from app.core.organization_context import get_organization_id
    
    # Get organization ID from JWT token
    org_id = get_organization_id(current_user, db)
    
    return service.get_categories(org_id, transaction_type, language, include_system)


@router.post("/", response_model=FinanceCategoryResponse, status_code=201)
def create_finance_category(
    data: FinanceCategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an organization-specific finance category.
    
    Only organization admins can create categories.
    System-defined categories cannot be created through this endpoint.
    
    - **transaction_type**: INCOME or EXPENSE
    - **code**: Unique code for the category
    - **translations**: Multilingual names and descriptions
    """
    service = FinanceCategoryService(db)
    
    from app.core.organization_context import get_organization_id
    
    # Get organization ID from JWT token
    org_id = get_organization_id(current_user, db)
    
    # TODO: Add RBAC check for admin role
    
    return service.create_org_category(org_id, data, current_user.id)


@router.put("/{category_id}", response_model=FinanceCategoryResponse)
def update_finance_category(
    category_id: UUID,
    data: FinanceCategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an organization-specific finance category.
    
    Only organization admins can update categories.
    System-defined categories cannot be updated.
    """
    service = FinanceCategoryService(db)
    
    from app.core.organization_context import get_organization_id
    
    # Get organization ID from JWT token
    org_id = get_organization_id(current_user, db)
    
    # TODO: Add RBAC check for admin role
    
    return service.update_org_category(category_id, org_id, data, current_user.id)


@router.delete("/{category_id}", status_code=204)
def delete_finance_category(
    category_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an organization-specific finance category.
    
    Only organization admins can delete categories.
    System-defined categories cannot be deleted.
    """
    service = FinanceCategoryService(db)
    
    from app.core.organization_context import get_organization_id
    
    # Get organization ID from JWT token
    org_id = get_organization_id(current_user, db)
    
    # TODO: Add RBAC check for admin role
    
    service.delete_org_category(category_id, org_id, current_user.id)
    return None
