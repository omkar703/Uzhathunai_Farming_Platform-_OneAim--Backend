"""
Finance Category Service for Uzhathunai v2.0.

Handles finance category operations with ownership validation.
Supports both system-defined and organization-specific categories.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.finance_category import FinanceCategory, FinanceCategoryTranslation
from app.models.enums import TransactionType
from app.schemas.finance_category import (
    FinanceCategoryCreate,
    FinanceCategoryUpdate,
    FinanceCategoryResponse,
    FinanceCategoryTranslationResponse
)
from app.core.exceptions import (
    NotFoundError,
    PermissionError,
    ValidationError
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class FinanceCategoryService:
    """Service for managing finance categories with ownership validation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_categories(
        self,
        org_id: UUID,
        transaction_type: Optional[TransactionType] = None,
        language: str = "en",
        include_system: bool = True
    ) -> List[FinanceCategoryResponse]:
        """
        Get finance categories (system-defined and org-specific).
        
        Args:
            org_id: Organization ID
            transaction_type: Optional transaction type filter (INCOME or EXPENSE)
            language: Language code for translations (default: en)
            include_system: Include system-defined categories (default: True)
            
        Returns:
            List of finance categories
        """
        query = self.db.query(FinanceCategory).filter(
            FinanceCategory.is_active == True
        )
        
        # Filter by transaction type
        if transaction_type:
            query = query.filter(FinanceCategory.transaction_type == transaction_type)
        
        # Filter by ownership
        if include_system:
            # Include both system-defined and org-specific
            query = query.filter(
                or_(
                    FinanceCategory.is_system_defined == True,
                    FinanceCategory.owner_org_id == org_id
                )
            )
        else:
            # Only org-specific
            query = query.filter(
                and_(
                    FinanceCategory.is_system_defined == False,
                    FinanceCategory.owner_org_id == org_id
                )
            )
        
        categories = query.order_by(
            FinanceCategory.transaction_type,
            FinanceCategory.sort_order,
            FinanceCategory.code
        ).all()
        
        logger.info(
            "Retrieved finance categories",
            extra={
                "org_id": str(org_id),
                "transaction_type": transaction_type.value if transaction_type else None,
                "count": len(categories),
                "include_system": include_system,
                "language": language
            }
        )
        
        return [self._to_response(cat, language) for cat in categories]
    
    def create_org_category(
        self,
        org_id: UUID,
        data: FinanceCategoryCreate,
        user_id: UUID
    ) -> FinanceCategoryResponse:
        """
        Create organization-specific finance category.
        
        Args:
            org_id: Organization ID
            data: Category creation data
            user_id: User ID creating the category
            
        Returns:
            Created category
            
        Raises:
            ValidationError: If category code already exists for organization
        """
        # Check if category code already exists for this org and transaction type
        existing = self.db.query(FinanceCategory).filter(
            and_(
                FinanceCategory.transaction_type == data.transaction_type,
                FinanceCategory.code == data.code,
                FinanceCategory.owner_org_id == org_id,
                FinanceCategory.is_active == True
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Finance category with code '{data.code}' already exists for this organization and transaction type",
                error_code="DUPLICATE_CATEGORY_CODE",
                details={
                    "code": data.code,
                    "transaction_type": data.transaction_type.value
                }
            )
        
        # Create category
        category = FinanceCategory(
            transaction_type=data.transaction_type,
            code=data.code,
            is_system_defined=False,
            owner_org_id=org_id,
            sort_order=data.sort_order,
            is_active=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(category)
        self.db.flush()
        
        # Create translations
        for trans_data in data.translations:
            translation = FinanceCategoryTranslation(
                category_id=category.id,
                language_code=trans_data['language_code'],
                name=trans_data['name'],
                description=trans_data.get('description')
            )
            self.db.add(translation)
        
        self.db.commit()
        self.db.refresh(category)
        
        logger.info(
            "Created organization-specific finance category",
            extra={
                "category_id": str(category.id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "code": data.code,
                "transaction_type": data.transaction_type.value
            }
        )
        
        return self._to_response(category, "en")
    
    def update_org_category(
        self,
        category_id: UUID,
        org_id: UUID,
        data: FinanceCategoryUpdate,
        user_id: UUID
    ) -> FinanceCategoryResponse:
        """
        Update organization-specific finance category.
        
        Args:
            category_id: Category ID
            org_id: Organization ID
            data: Category update data
            user_id: User ID updating the category
            
        Returns:
            Updated category
            
        Raises:
            NotFoundError: If category not found
            PermissionError: If category is system-defined or owned by another org
        """
        category = self.db.query(FinanceCategory).filter(
            FinanceCategory.id == category_id
        ).first()
        
        if not category:
            raise NotFoundError(
                message=f"Finance category {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
                details={"category_id": str(category_id)}
            )
        
        # Validate ownership
        self._validate_ownership(category, org_id, "update")
        
        # Update fields
        if data.sort_order is not None:
            category.sort_order = data.sort_order
        
        if data.is_active is not None:
            category.is_active = data.is_active
        
        category.updated_by = user_id
        
        # Update translations
        if data.translations:
            for trans_data in data.translations:
                lang_code = trans_data['language_code']
                translation = self.db.query(FinanceCategoryTranslation).filter(
                    and_(
                        FinanceCategoryTranslation.category_id == category_id,
                        FinanceCategoryTranslation.language_code == lang_code
                    )
                ).first()
                
                if translation:
                    translation.name = trans_data['name']
                    if 'description' in trans_data:
                        translation.description = trans_data['description']
                else:
                    translation = FinanceCategoryTranslation(
                        category_id=category_id,
                        language_code=lang_code,
                        name=trans_data['name'],
                        description=trans_data.get('description')
                    )
                    self.db.add(translation)
        
        self.db.commit()
        self.db.refresh(category)
        
        logger.info(
            "Updated organization-specific finance category",
            extra={
                "category_id": str(category_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_response(category, "en")
    
    def delete_org_category(
        self,
        category_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete (soft delete) organization-specific finance category.
        
        Args:
            category_id: Category ID
            org_id: Organization ID
            user_id: User ID deleting the category
            
        Raises:
            NotFoundError: If category not found
            PermissionError: If category is system-defined or owned by another org
        """
        category = self.db.query(FinanceCategory).filter(
            FinanceCategory.id == category_id
        ).first()
        
        if not category:
            raise NotFoundError(
                message=f"Finance category {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
                details={"category_id": str(category_id)}
            )
        
        # Validate ownership
        self._validate_ownership(category, org_id, "delete")
        
        # Soft delete
        category.is_active = False
        category.updated_by = user_id
        
        self.db.commit()
        
        logger.info(
            "Deleted organization-specific finance category",
            extra={
                "category_id": str(category_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def _validate_ownership(
        self,
        category: FinanceCategory,
        org_id: UUID,
        operation: str
    ) -> None:
        """
        Validate category ownership for modification operations.
        
        Args:
            category: Category to validate
            org_id: Organization ID attempting the operation
            operation: Operation being performed (update/delete)
            
        Raises:
            PermissionError: If category is system-defined or owned by another org
        """
        if category.is_system_defined:
            raise PermissionError(
                message=f"Cannot {operation} system-defined finance category",
                error_code="SYSTEM_DEFINED_IMMUTABLE",
                details={
                    "category_id": str(category.id),
                    "operation": operation
                }
            )
        
        if category.owner_org_id != org_id:
            raise PermissionError(
                message=f"Cannot {operation} finance category owned by another organization",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "category_id": str(category.id),
                    "owner_org_id": str(category.owner_org_id),
                    "requesting_org_id": str(org_id),
                    "operation": operation
                }
            )
    
    def _to_response(
        self,
        category: FinanceCategory,
        language: str
    ) -> FinanceCategoryResponse:
        """Convert category model to response schema."""
        # Get all translations
        translations = [
            FinanceCategoryTranslationResponse(
                language_code=t.language_code,
                name=t.name,
                description=t.description
            )
            for t in category.translations
        ]
        
        return FinanceCategoryResponse(
            id=str(category.id),
            transaction_type=category.transaction_type,
            code=category.code,
            is_system_defined=category.is_system_defined,
            owner_org_id=str(category.owner_org_id) if category.owner_org_id else None,
            sort_order=category.sort_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            created_by=str(category.created_by) if category.created_by else None,
            updated_by=str(category.updated_by) if category.updated_by else None,
            translations=translations
        )
