"""
Input Item service for managing input item categories and items with ownership validation.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, PermissionError, ValidationError
from app.models.input_item import (
    InputItemCategory, InputItemCategoryTranslation,
    InputItem, InputItemTranslation
)
from app.models.measurement_unit import MeasurementUnit
from app.schemas.input_item import (
    InputItemCategoryCreate, InputItemCategoryUpdate, InputItemCategoryResponse,
    InputItemCreate, InputItemUpdate, InputItemResponse
)

logger = get_logger(__name__)


class InputItemService:
    """Service for input item operations with ownership validation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_categories(
        self, 
        org_id: UUID, 
        language: str = "en", 
        include_system: bool = True
    ) -> List[InputItemCategoryResponse]:
        """
        Get input item categories (system-defined and org-specific).
        
        Args:
            org_id: Organization ID
            language: Language code for translations (default: en)
            include_system: Include system-defined categories (default: True)
            
        Returns:
            List of input item categories
        """
        query = self.db.query(InputItemCategory).filter(
            InputItemCategory.is_active == True
        )
        
        # Filter by ownership
        if include_system:
            # Include both system-defined and org-specific
            query = query.filter(
                or_(
                    InputItemCategory.is_system_defined == True,
                    InputItemCategory.owner_org_id == org_id
                )
            )
        else:
            # Only org-specific
            query = query.filter(
                and_(
                    InputItemCategory.is_system_defined == False,
                    InputItemCategory.owner_org_id == org_id
                )
            )
        
        categories = query.order_by(
            InputItemCategory.sort_order, 
            InputItemCategory.code
        ).all()
        
        logger.info(
            "Retrieved input item categories",
            extra={
                "org_id": str(org_id),
                "count": len(categories),
                "include_system": include_system,
                "language": language
            }
        )
        
        return [self._to_category_response(cat, language) for cat in categories]
    
    def create_org_category(
        self,
        data: InputItemCategoryCreate,
        org_id: UUID,
        user_id: UUID
    ) -> InputItemCategoryResponse:
        """
        Create organization-specific input item category.
        
        Args:
            data: Category creation data
            org_id: Organization ID
            user_id: User ID creating the category
            
        Returns:
            Created category
            
        Raises:
            ValidationError: If category code already exists for organization
        """
        # Check if category code already exists for this org
        existing = self.db.query(InputItemCategory).filter(
            and_(
                InputItemCategory.code == data.code,
                InputItemCategory.owner_org_id == org_id,
                InputItemCategory.is_active == True
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Category with code '{data.code}' already exists for this organization",
                error_code="DUPLICATE_CATEGORY_CODE",
                details={"code": data.code}
            )
        
        # Create category
        category = InputItemCategory(
            code=data.code,
            is_system_defined=False,
            owner_org_id=org_id,
            sort_order=data.sort_order or 0,
            is_active=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(category)
        self.db.flush()
        
        # Create translations
        for trans_data in data.translations:
            translation = InputItemCategoryTranslation(
                category_id=category.id,
                language_code=trans_data['language_code'],
                name=trans_data['name'],
                description=trans_data.get('description')
            )
            self.db.add(translation)
        
        self.db.commit()
        self.db.refresh(category)
        
        logger.info(
            "Created organization-specific input item category",
            extra={
                "category_id": str(category.id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "code": data.code
            }
        )
        
        return self._to_category_response(category, "en")
    
    def update_org_category(
        self,
        category_id: UUID,
        data: InputItemCategoryUpdate,
        org_id: UUID,
        user_id: UUID
    ) -> InputItemCategoryResponse:
        """
        Update organization-specific input item category.
        
        Args:
            category_id: Category ID
            data: Category update data
            org_id: Organization ID
            user_id: User ID updating the category
            
        Returns:
            Updated category
            
        Raises:
            NotFoundError: If category not found
            PermissionError: If category is system-defined or owned by another org
        """
        category = self.db.query(InputItemCategory).filter(
            InputItemCategory.id == category_id
        ).first()
        
        if not category:
            raise NotFoundError(
                message=f"Input item category {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
                details={"category_id": str(category_id)}
            )
        
        # Validate ownership
        self._validate_ownership(category, org_id, "update")
        
        # Update fields
        if data.sort_order is not None:
            category.sort_order = data.sort_order
        
        category.updated_by = user_id
        
        # Update translations
        if data.translations:
            for trans_data in data.translations:
                lang = trans_data['language_code']
                translation = self.db.query(InputItemCategoryTranslation).filter(
                    and_(
                        InputItemCategoryTranslation.category_id == category_id,
                        InputItemCategoryTranslation.language_code == lang
                    )
                ).first()
                
                if translation:
                    translation.name = trans_data['name']
                    if 'description' in trans_data:
                        translation.description = trans_data['description']
                else:
                    translation = InputItemCategoryTranslation(
                        category_id=category_id,
                        language_code=lang,
                        name=trans_data['name'],
                        description=trans_data.get('description')
                    )
                    self.db.add(translation)
        
        self.db.commit()
        self.db.refresh(category)
        
        logger.info(
            "Updated organization-specific input item category",
            extra={
                "category_id": str(category_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_category_response(category, "en")
    
    def delete_org_category(
        self,
        category_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete (soft delete) organization-specific input item category.
        
        Args:
            category_id: Category ID
            org_id: Organization ID
            user_id: User ID deleting the category
            
        Raises:
            NotFoundError: If category not found
            PermissionError: If category is system-defined or owned by another org
        """
        category = self.db.query(InputItemCategory).filter(
            InputItemCategory.id == category_id
        ).first()
        
        if not category:
            raise NotFoundError(
                message=f"Input item category {category_id} not found",
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
            "Deleted organization-specific input item category",
            extra={
                "category_id": str(category_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def get_items(
        self,
        org_id: UUID,
        category_id: Optional[UUID] = None,
        language: str = "en",
        include_system: bool = True,
        page: int = 1,
        limit: int = 50,
        search: Optional[str] = None,
        item_type: Optional[str] = None
    ) -> dict:
        """
        Get paginated input items (system-defined and org-specific).
        
        Args:
            org_id: Organization ID
            category_id: Optional category ID to filter by
            language: Language code for translations (default: en)
            include_system: Include system-defined items (default: True)
            page: Page number (default: 1)
            limit: Items per page (default: 50, max: 100)
            search: Optional search query for item name or code
            item_type: Optional item type (FERTILIZER, PESTICIDE, etc.)
            
        Returns:
            Dict containing items list and pagination metadata
        """
        from sqlalchemy.orm import selectinload
        from sqlalchemy import exists
        import math
        
        # Ensure limit is reasonable
        limit = min(max(1, limit), 100)
        page = max(1, page)
        offset = (page - 1) * limit
        
        query = self.db.query(InputItem).filter(
            InputItem.is_active == True
        )
        
        # Filter by category
        if category_id:
            query = query.filter(InputItem.category_id == category_id)
            
        # Filter by type
        if item_type:
            # Join with category to filter by category code (which serves as type for system items)
            query = query.join(InputItem.category)
            
            query = query.filter(
                or_(
                    InputItem.type == item_type,
                    InputItemCategory.code == item_type
                )
            )
        
        # Filter by ownership
        if include_system:
            # Include both system-defined and org-specific
            query = query.filter(
                or_(
                    InputItem.is_system_defined == True,
                    InputItem.owner_org_id == org_id
                )
            )
        else:
            # Only org-specific
            query = query.filter(
                and_(
                    InputItem.is_system_defined == False,
                    InputItem.owner_org_id == org_id
                )
            )
            
        # Filter by search query
        if search:
            search_pattern = f"%{search}%"
            # Use exists() for translations to avoid duplicates and the need for distinct()
            translation_exists = exists().where(
                and_(
                    InputItemTranslation.input_item_id == InputItem.id,
                    InputItemTranslation.name.ilike(search_pattern)
                )
            )
            query = query.filter(
                or_(
                    InputItem.code.ilike(search_pattern),
                    translation_exists
                )
            )
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and sorting
        # Sort system items first, then by sort_order and code
        # Use selectinload for efficient eager loading of relationships
        items = query.options(
            selectinload(InputItem.translations),
            selectinload(InputItem.category).selectinload(InputItemCategory.translations),
            selectinload(InputItem.default_unit).selectinload(MeasurementUnit.translations)
        ).order_by(
            InputItem.is_system_defined.desc(),
            InputItem.sort_order,
            InputItem.code
        ).offset(offset).limit(limit).all()
        
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        
        logger.info(
            "Retrieved paginated input items",
            extra={
                "org_id": str(org_id),
                "category_id": str(category_id) if category_id else None,
                "count": len(items),
                "total": total_count,
                "page": page,
                "limit": limit,
                "search": search
            }
        )
        
        return {
            "items": [self._to_item_response(item, language) for item in items],
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    
    def create_org_item(
        self,
        data: InputItemCreate,
        org_id: UUID,
        user_id: UUID
    ) -> InputItemResponse:
        """
        Create organization-specific input item.
        
        Args:
            data: Item creation data
            org_id: Organization ID
            user_id: User ID creating the item
            
        Returns:
            Created item
            
        Raises:
            ValidationError: If item code already exists for organization
            NotFoundError: If category not found
        """
        # Validate category exists
        category = self.db.query(InputItemCategory).filter(
            InputItemCategory.id == data.category_id
        ).first()
        
        if not category:
            raise NotFoundError(
                message=f"Input item category {data.category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
                details={"category_id": str(data.category_id)}
            )
        
        # Check if item code already exists for this org
        existing = self.db.query(InputItem).filter(
            and_(
                InputItem.code == data.code,
                InputItem.owner_org_id == org_id,
                InputItem.is_active == True
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Item with code '{data.code}' already exists for this organization",
                error_code="DUPLICATE_ITEM_CODE",
                details={"code": data.code}
            )
        
        # Create item
        item = InputItem(
            code=data.code,
            category_id=data.category_id,
            is_system_defined=False,
            owner_org_id=org_id,
            item_metadata=data.item_metadata or {},
            sort_order=data.sort_order or 0,
            is_active=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(item)
        self.db.flush()
        
        # Create translations
        for trans_data in data.translations:
            translation = InputItemTranslation(
                input_item_id=item.id,
                language_code=trans_data['language_code'],
                name=trans_data['name'],
                description=trans_data.get('description')
            )
            self.db.add(translation)
        
        self.db.commit()
        self.db.refresh(item)
        
        logger.info(
            "Created organization-specific input item",
            extra={
                "item_id": str(item.id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "code": data.code,
                "category_id": str(data.category_id)
            }
        )
        
        return self._to_item_response(item, "en")
    
    def update_org_item(
        self,
        item_id: UUID,
        data: InputItemUpdate,
        org_id: UUID,
        user_id: UUID
    ) -> InputItemResponse:
        """
        Update organization-specific input item.
        
        Args:
            item_id: Item ID
            data: Item update data
            org_id: Organization ID
            user_id: User ID updating the item
            
        Returns:
            Updated item
            
        Raises:
            NotFoundError: If item not found
            PermissionError: If item is system-defined or owned by another org
        """
        item = self.db.query(InputItem).filter(
            InputItem.id == item_id
        ).first()
        
        if not item:
            raise NotFoundError(
                message=f"Input item {item_id} not found",
                error_code="ITEM_NOT_FOUND",
                details={"item_id": str(item_id)}
            )
        
        # Validate ownership
        self._validate_item_ownership(item, org_id, "update")
        
        # Update fields
        if data.item_metadata is not None:
            item.item_metadata = data.item_metadata
        
        if data.sort_order is not None:
            item.sort_order = data.sort_order
        
        item.updated_by = user_id
        
        # Update translations
        if data.translations:
            for trans_data in data.translations:
                lang = trans_data['language_code']
                translation = self.db.query(InputItemTranslation).filter(
                    and_(
                        InputItemTranslation.input_item_id == item_id,
                        InputItemTranslation.language_code == lang
                    )
                ).first()
                
                if translation:
                    translation.name = trans_data['name']
                    if 'description' in trans_data:
                        translation.description = trans_data['description']
                else:
                    translation = InputItemTranslation(
                        input_item_id=item_id,
                        language_code=lang,
                        name=trans_data['name'],
                        description=trans_data.get('description')
                    )
                    self.db.add(translation)
        
        self.db.commit()
        self.db.refresh(item)
        
        logger.info(
            "Updated organization-specific input item",
            extra={
                "item_id": str(item_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_item_response(item, "en")
    
    def delete_org_item(
        self,
        item_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete (soft delete) organization-specific input item.
        
        Args:
            item_id: Item ID
            org_id: Organization ID
            user_id: User ID deleting the item
            
        Raises:
            NotFoundError: If item not found
            PermissionError: If item is system-defined or owned by another org
        """
        item = self.db.query(InputItem).filter(
            InputItem.id == item_id
        ).first()
        
        if not item:
            raise NotFoundError(
                message=f"Input item {item_id} not found",
                error_code="ITEM_NOT_FOUND",
                details={"item_id": str(item_id)}
            )
        
        # Validate ownership
        self._validate_item_ownership(item, org_id, "delete")
        
        # Soft delete
        item.is_active = False
        item.updated_by = user_id
        
        self.db.commit()
        
        logger.info(
            "Deleted organization-specific input item",
            extra={
                "item_id": str(item_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def _validate_ownership(
        self,
        category: InputItemCategory,
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
                message=f"Cannot {operation} system-defined input item category",
                error_code="SYSTEM_DEFINED_IMMUTABLE",
                details={
                    "category_id": str(category.id),
                    "operation": operation
                }
            )
        
        if category.owner_org_id != org_id:
            raise PermissionError(
                message=f"Cannot {operation} input item category owned by another organization",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "category_id": str(category.id),
                    "owner_org_id": str(category.owner_org_id),
                    "requesting_org_id": str(org_id),
                    "operation": operation
                }
            )
    
    def _validate_item_ownership(
        self,
        item: InputItem,
        org_id: UUID,
        operation: str
    ) -> None:
        """
        Validate item ownership for modification operations.
        
        Args:
            item: Item to validate
            org_id: Organization ID attempting the operation
            operation: Operation being performed (update/delete)
            
        Raises:
            PermissionError: If item is system-defined or owned by another org
        """
        if item.is_system_defined:
            raise PermissionError(
                message=f"Cannot {operation} system-defined input item",
                error_code="SYSTEM_DEFINED_IMMUTABLE",
                details={
                    "item_id": str(item.id),
                    "operation": operation
                }
            )
        
        if item.owner_org_id != org_id:
            raise PermissionError(
                message=f"Cannot {operation} input item owned by another organization",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "item_id": str(item.id),
                    "owner_org_id": str(item.owner_org_id),
                    "requesting_org_id": str(org_id),
                    "operation": operation
                }
            )
    
    def _to_category_response(
        self,
        category: InputItemCategory,
        language: str
    ) -> InputItemCategoryResponse:
        """Convert category model to response schema."""
        from app.schemas.input_item import InputItemCategoryTranslationResponse
        
        # Convert all translations
        translations_list = [
            InputItemCategoryTranslationResponse(
                language_code=t.language_code,
                name=t.name,
                description=t.description
            )
            for t in category.translations
        ]
        
        # Extract translated fields for requested language
        translated_name = None
        translated_description = None
        for t in category.translations:
            if t.language_code == language:
                translated_name = t.name
                translated_description = t.description
                break
        
        # Fallback to English if requested language not found
        if not translated_name:
            for t in category.translations:
                if t.language_code == 'en':
                    translated_name = t.name
                    translated_description = t.description
                    break
        
        # Fallback to code if no translation found
        if not translated_name:
            translated_name = category.code
        
        return InputItemCategoryResponse(
            id=category.id,
            code=category.code,
            is_system_defined=category.is_system_defined,
            owner_org_id=category.owner_org_id,
            sort_order=category.sort_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            created_by=category.created_by,
            updated_by=category.updated_by,
            translations=translations_list,
            name=translated_name,
            description=translated_description
        )
    
    def _to_item_response(
        self,
        item: InputItem,
        language: str
    ) -> InputItemResponse:
        """Convert item model to response schema."""
        from app.schemas.input_item import InputItemTranslationResponse
        
        # Convert all translations
        translations_list = [
            InputItemTranslationResponse(
                language_code=t.language_code,
                name=t.name,
                description=t.description
            )
            for t in item.translations
        ]
        
        # Extract translated fields for requested language
        translated_name = None
        translated_description = None
        for t in item.translations:
            if t.language_code == language:
                translated_name = t.name
                translated_description = t.description
                break
        
        # Fallback to English if requested language not found
        if not translated_name:
            for t in item.translations:
                if t.language_code == 'en':
                    translated_name = t.name
                    translated_description = t.description
                    break
        
        # Fallback to code if no translation found
        if not translated_name:
            translated_name = item.code
        
        # Get category details if available
        category_response = None
        if item.category:
            category_response = self._to_category_response(item.category, language)
        
        # Convert default unit if present
        default_unit_response = None
        if item.default_unit:
             from app.schemas.measurement_unit import MeasurementUnitResponse, MeasurementUnitTranslationResponse
             
             # Unit translations
             unit_trans_list = [
                 MeasurementUnitTranslationResponse(
                     language_code=t.language_code,
                     name=t.name,
                     description=t.description
                 ) for t in item.default_unit.translations
             ]
             
             # Unit translated name
             unit_name = None
             for t in item.default_unit.translations:
                 if t.language_code == language:
                     unit_name = t.name
                     break
             if not unit_name: # fallback en
                 for t in item.default_unit.translations:
                     if t.language_code == 'en':
                         unit_name = t.name
                         break
             if not unit_name: # fallback name field
                 unit_name = item.default_unit.code.lower().capitalize() # approximation if name not on model base

             default_unit_response = MeasurementUnitResponse(
                 id=str(item.default_unit.id),
                 category=item.default_unit.category,
                 code=item.default_unit.code,
                 symbol=item.default_unit.symbol,
                 is_base_unit=item.default_unit.is_base_unit,
                 conversion_factor=item.default_unit.conversion_factor,
                 sort_order=item.default_unit.sort_order,
                 name=unit_name,
                 translations=unit_trans_list
             )

        return InputItemResponse(
            id=item.id,
            code=item.code,
            category_id=item.category_id,
            is_system_defined=item.is_system_defined,
            owner_org_id=item.owner_org_id,
            type=item.type,
            default_unit_id=item.default_unit_id,
            default_unit=default_unit_response,
            item_metadata=item.item_metadata,
            sort_order=item.sort_order,
            is_active=item.is_active,
            created_at=item.created_at,
            updated_at=item.updated_at,
            created_by=item.created_by,
            updated_by=item.updated_by,
            translations=translations_list,
            name=translated_name,
            description=translated_description,
            category=category_response
        )
