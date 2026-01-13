"""
Option Set service for managing option sets and options with ownership validation.
Supports system-defined and organization-specific option sets for Farm Audit Management.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, PermissionError, ValidationError
from app.core.audit_permissions import check_audit_permission, AuditPermissions
from app.core.audit_ownership import validate_entity_modification
from app.models.option_set import OptionSet, Option, OptionTranslation
from app.models.user import User
from app.schemas.option_set import (
    OptionSetCreate, OptionSetUpdate, OptionSetResponse, OptionSetDetailResponse,
    OptionCreate, OptionUpdate, OptionResponse, OptionTranslationResponse
)

logger = get_logger(__name__)


class OptionSetService:
    """Service for option set operations with ownership validation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_option_sets(
        self,
        org_id: UUID,
        language: str = "en",
        include_system: bool = True
    ) -> List[OptionSetResponse]:
        """
        Get option sets (system-defined and org-specific).
        
        Args:
            org_id: Organization ID
            language: Language code for translations (default: en)
            include_system: Include system-defined option sets (default: True)
            
        Returns:
            List of option sets
        """
        from sqlalchemy.orm import joinedload
        
        query = self.db.query(OptionSet).filter(
            OptionSet.is_active == True
        ).options(
            joinedload(OptionSet.options).joinedload(Option.translations)
        )
        
        # Filter by ownership
        if include_system:
            # Include both system-defined and org-specific
            query = query.filter(
                or_(
                    OptionSet.is_system_defined == True,
                    OptionSet.owner_org_id == org_id
                )
            )
        else:
            # Only org-specific
            query = query.filter(
                and_(
                    OptionSet.is_system_defined == False,
                    OptionSet.owner_org_id == org_id
                )
            )
        
        option_sets = query.order_by(OptionSet.code).all()
        
        logger.info(
            "Retrieved option sets",
            extra={
                "org_id": str(org_id),
                "count": len(option_sets),
                "include_system": include_system,
                "language": language
            }
        )
        
        return [self._to_option_set_response(os, language) for os in option_sets]
    
    def get_option_set(
        self,
        option_set_id: UUID,
        org_id: UUID,
        language: str = "en"
    ) -> OptionSetDetailResponse:
        """
        Get option set by ID with all options.
        
        Args:
            option_set_id: Option set ID
            org_id: Organization ID
            language: Language code for translations (default: en)
            
        Returns:
            Option set with all options
            
        Raises:
            NotFoundError: If option set not found
            PermissionError: If option set is not accessible by organization
        """
        from sqlalchemy.orm import joinedload
        
        option_set = self.db.query(OptionSet).filter(
            OptionSet.id == option_set_id
        ).options(
            joinedload(OptionSet.options).joinedload(Option.translations)
        ).first()
        
        if not option_set:
            raise NotFoundError(
                message=f"Option set {option_set_id} not found",
                error_code="OPTION_SET_NOT_FOUND",
                details={"option_set_id": str(option_set_id)}
            )
        
        # Validate access
        if not option_set.is_system_defined and option_set.owner_org_id != org_id:
            raise PermissionError(
                message="Cannot access option set owned by another organization",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "option_set_id": str(option_set_id),
                    "owner_org_id": str(option_set.owner_org_id),
                    "requesting_org_id": str(org_id)
                }
            )
        
        logger.info(
            "Retrieved option set",
            extra={
                "option_set_id": str(option_set_id),
                "org_id": str(org_id),
                "language": language
            }
        )
        
        return self._to_option_set_response(option_set, language)
    
    def create_org_option_set(
        self,
        data: OptionSetCreate,
        org_id: UUID,
        user_id: UUID
    ) -> OptionSetDetailResponse:
        """
        Create organization-specific option set.
        
        Requirement 18.1: Enforce "Audit Template Management" permission
        
        Args:
            data: Option set creation data
            org_id: Organization ID
            user_id: User ID creating the option set
            
        Returns:
            Created option set
            
        Raises:
            ValidationError: If option set code already exists for organization
            PermissionError: If user lacks template management permission
        """
        # Get user object for permission check
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND",
                details={"user_id": str(user_id)}
            )
        
        # Check permission (Requirement 18.1)
        check_audit_permission(
            db=self.db,
            user=user,
            organization_id=org_id,
            resource=AuditPermissions.TEMPLATE_CREATE[0],
            action=AuditPermissions.TEMPLATE_CREATE[1]
        )
        # Check if option set code already exists for this org
        existing = self.db.query(OptionSet).filter(
            and_(
                OptionSet.code == data.code,
                OptionSet.owner_org_id == org_id,
                OptionSet.is_active == True
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Option set with code '{data.code}' already exists for this organization",
                error_code="DUPLICATE_OPTION_SET_CODE",
                details={"code": data.code}
            )
        
        # Create option set
        option_set = OptionSet(
            code=data.code,
            is_system_defined=False,
            owner_org_id=org_id,
            is_active=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(option_set)
        self.db.flush()
        
        # Create options if provided
        if data.options:
            for option_data in data.options:
                self._create_option(option_set.id, option_data)
        
        self.db.commit()
        self.db.refresh(option_set)
        
        logger.info(
            "Created organization-specific option set",
            extra={
                "option_set_id": str(option_set.id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "code": data.code,
                "options_count": len(data.options) if data.options else 0
            }
        )
        
        return self._to_option_set_response(option_set, "en")
    
    def update_org_option_set(
        self,
        option_set_id: UUID,
        data: OptionSetUpdate,
        org_id: UUID,
        user_id: UUID
    ) -> OptionSetDetailResponse:
        """
        Update organization-specific option set.
        
        Requirements:
        - 18.1: Enforce "Audit Template Management" permission
        - 19.1: Prevent modification of system-defined entities
        - 19.3: Prevent cross-organization modifications
        
        Args:
            option_set_id: Option set ID
            data: Option set update data
            org_id: Organization ID
            user_id: User ID updating the option set
            
        Returns:
            Updated option set
            
        Raises:
            NotFoundError: If option set not found
            PermissionError: If user lacks permission or entity is immutable
        """
        # Get user object for permission check
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND",
                details={"user_id": str(user_id)}
            )
        
        # Check permission (Requirement 18.1)
        check_audit_permission(
            db=self.db,
            user=user,
            organization_id=org_id,
            resource=AuditPermissions.TEMPLATE_UPDATE[0],
            action=AuditPermissions.TEMPLATE_UPDATE[1]
        )
        option_set = self.db.query(OptionSet).filter(
            OptionSet.id == option_set_id
        ).first()
        
        if not option_set:
            raise NotFoundError(
                message=f"Option set {option_set_id} not found",
                error_code="OPTION_SET_NOT_FOUND",
                details={"option_set_id": str(option_set_id)}
            )
        
        # Validate ownership (Requirements 19.1, 19.3)
        validate_entity_modification(
            is_system_defined=option_set.is_system_defined,
            owner_org_id=option_set.owner_org_id,
            user=user,
            user_org_id=org_id,
            entity_type="option_set",
            entity_id=option_set_id
        )
        
        # Update fields
        if data.is_active is not None:
            option_set.is_active = data.is_active
        
        option_set.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(option_set)
        
        logger.info(
            "Updated organization-specific option set",
            extra={
                "option_set_id": str(option_set_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_option_set_response(option_set, "en")
    
    def delete_org_option_set(
        self,
        option_set_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete (soft delete) organization-specific option set.
        
        Requirements:
        - 18.1: Enforce "Audit Template Management" permission
        - 19.1: Prevent modification of system-defined entities
        - 19.3: Prevent cross-organization modifications
        
        Args:
            option_set_id: Option set ID
            org_id: Organization ID
            user_id: User ID deleting the option set
            
        Raises:
            NotFoundError: If option set not found
            PermissionError: If user lacks permission or entity is immutable
        """
        # Get user object for permission check
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND",
                details={"user_id": str(user_id)}
            )
        
        # Check permission (Requirement 18.1)
        check_audit_permission(
            db=self.db,
            user=user,
            organization_id=org_id,
            resource=AuditPermissions.TEMPLATE_DELETE[0],
            action=AuditPermissions.TEMPLATE_DELETE[1]
        )
        option_set = self.db.query(OptionSet).filter(
            OptionSet.id == option_set_id
        ).first()
        
        if not option_set:
            raise NotFoundError(
                message=f"Option set {option_set_id} not found",
                error_code="OPTION_SET_NOT_FOUND",
                details={"option_set_id": str(option_set_id)}
            )
        
        # Validate ownership (Requirements 19.1, 19.3)
        validate_entity_modification(
            is_system_defined=option_set.is_system_defined,
            owner_org_id=option_set.owner_org_id,
            user=user,
            user_org_id=org_id,
            entity_type="option_set",
            entity_id=option_set_id
        )
        
        # Soft delete
        option_set.is_active = False
        option_set.updated_by = user_id
        
        self.db.commit()
        
        logger.info(
            "Deleted organization-specific option set",
            extra={
                "option_set_id": str(option_set_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def add_option_to_set(
        self,
        option_set_id: UUID,
        data: OptionCreate,
        org_id: UUID,
        user_id: UUID
    ) -> OptionResponse:
        """
        Add option to option set.
        
        Requirements:
        - 18.1: Enforce "Audit Template Management" permission
        - 19.1: Prevent modification of system-defined entities
        - 19.3: Prevent cross-organization modifications
        
        Args:
            option_set_id: Option set ID
            data: Option creation data
            org_id: Organization ID
            user_id: User ID adding the option
            
        Returns:
            Created option
            
        Raises:
            NotFoundError: If option set not found
            PermissionError: If user lacks permission or entity is immutable
            ValidationError: If option code already exists in set
        """
        # Get user object for permission check
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND",
                details={"user_id": str(user_id)}
            )
        
        # Check permission (Requirement 18.1)
        check_audit_permission(
            db=self.db,
            user=user,
            organization_id=org_id,
            resource=AuditPermissions.TEMPLATE_UPDATE[0],
            action=AuditPermissions.TEMPLATE_UPDATE[1]
        )
        option_set = self.db.query(OptionSet).filter(
            OptionSet.id == option_set_id
        ).first()
        
        if not option_set:
            raise NotFoundError(
                message=f"Option set {option_set_id} not found",
                error_code="OPTION_SET_NOT_FOUND",
                details={"option_set_id": str(option_set_id)}
            )
        
        # Validate ownership (Requirements 19.1, 19.3)
        validate_entity_modification(
            is_system_defined=option_set.is_system_defined,
            owner_org_id=option_set.owner_org_id,
            user=user,
            user_org_id=org_id,
            entity_type="option_set",
            entity_id=option_set_id
        )
        
        # Check if option code already exists in this set
        existing = self.db.query(Option).filter(
            and_(
                Option.option_set_id == option_set_id,
                Option.code == data.code
            )
        ).first()
        
        if existing:
            raise ValidationError(
                message=f"Option with code '{data.code}' already exists in this option set",
                error_code="DUPLICATE_OPTION_CODE",
                details={"code": data.code, "option_set_id": str(option_set_id)}
            )
        
        # Create option
        option = self._create_option(option_set_id, data)
        
        # Update option set timestamp
        option_set.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(option)
        
        logger.info(
            "Added option to option set",
            extra={
                "option_id": str(option.id),
                "option_set_id": str(option_set_id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "code": data.code
            }
        )
        
        return self._to_option_response(option, "en")
    
    def update_option(
        self,
        option_id: UUID,
        data: OptionUpdate,
        org_id: UUID,
        user_id: UUID
    ) -> OptionResponse:
        """
        Update option in option set.
        
        Requirements:
        - 18.1: Enforce "Audit Template Management" permission
        - 19.1: Prevent modification of system-defined entities
        - 19.3: Prevent cross-organization modifications
        
        Args:
            option_id: Option ID
            data: Option update data
            org_id: Organization ID
            user_id: User ID updating the option
            
        Returns:
            Updated option
            
        Raises:
            NotFoundError: If option not found
            PermissionError: If user lacks permission or entity is immutable
        """
        # Get user object for permission check
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND",
                details={"user_id": str(user_id)}
            )
        
        # Check permission (Requirement 18.1)
        check_audit_permission(
            db=self.db,
            user=user,
            organization_id=org_id,
            resource=AuditPermissions.TEMPLATE_UPDATE[0],
            action=AuditPermissions.TEMPLATE_UPDATE[1]
        )
        option = self.db.query(Option).filter(
            Option.id == option_id
        ).first()
        
        if not option:
            raise NotFoundError(
                message=f"Option {option_id} not found",
                error_code="OPTION_NOT_FOUND",
                details={"option_id": str(option_id)}
            )
        
        # Validate ownership via option set (Requirements 19.1, 19.3)
        option_set = self.db.query(OptionSet).filter(
            OptionSet.id == option.option_set_id
        ).first()
        
        validate_entity_modification(
            is_system_defined=option_set.is_system_defined,
            owner_org_id=option_set.owner_org_id,
            user=user,
            user_org_id=org_id,
            entity_type="option_set",
            entity_id=option.option_set_id
        )
        
        # Update fields
        if data.sort_order is not None:
            option.sort_order = data.sort_order
        
        if data.is_active is not None:
            option.is_active = data.is_active
        
        # Update translations
        if data.translations:
            for trans_data in data.translations:
                lang = trans_data['language_code']
                translation = self.db.query(OptionTranslation).filter(
                    and_(
                        OptionTranslation.option_id == option_id,
                        OptionTranslation.language_code == lang
                    )
                ).first()
                
                if translation:
                    translation.display_text = trans_data['display_text']
                else:
                    translation = OptionTranslation(
                        option_id=option_id,
                        language_code=lang,
                        display_text=trans_data['display_text']
                    )
                    self.db.add(translation)
        
        # Update option set timestamp
        option_set.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(option)
        
        logger.info(
            "Updated option",
            extra={
                "option_id": str(option_id),
                "option_set_id": str(option.option_set_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_option_response(option, "en")
    
    def delete_option(
        self,
        option_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete option from option set.
        
        Requirements:
        - 18.1: Enforce "Audit Template Management" permission
        - 19.1: Prevent modification of system-defined entities
        - 19.3: Prevent cross-organization modifications
        
        Args:
            option_id: Option ID
            org_id: Organization ID
            user_id: User ID deleting the option
            
        Raises:
            NotFoundError: If option not found
            PermissionError: If user lacks permission or entity is immutable
        """
        # Get user object for permission check
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND",
                details={"user_id": str(user_id)}
            )
        
        # Check permission (Requirement 18.1)
        check_audit_permission(
            db=self.db,
            user=user,
            organization_id=org_id,
            resource=AuditPermissions.TEMPLATE_DELETE[0],
            action=AuditPermissions.TEMPLATE_DELETE[1]
        )
        option = self.db.query(Option).filter(
            Option.id == option_id
        ).first()
        
        if not option:
            raise NotFoundError(
                message=f"Option {option_id} not found",
                error_code="OPTION_NOT_FOUND",
                details={"option_id": str(option_id)}
            )
        
        # Validate ownership via option set (Requirements 19.1, 19.3)
        option_set = self.db.query(OptionSet).filter(
            OptionSet.id == option.option_set_id
        ).first()
        
        validate_entity_modification(
            is_system_defined=option_set.is_system_defined,
            owner_org_id=option_set.owner_org_id,
            user=user,
            user_org_id=org_id,
            entity_type="option_set",
            entity_id=option.option_set_id
        )
        
        # Delete option (hard delete as per DDL cascade)
        self.db.delete(option)
        
        # Update option set timestamp
        option_set.updated_by = user_id
        
        self.db.commit()
        
        logger.info(
            "Deleted option",
            extra={
                "option_id": str(option_id),
                "option_set_id": str(option.option_set_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def _create_option(
        self,
        option_set_id: UUID,
        data: OptionCreate
    ) -> Option:
        """
        Internal method to create an option.
        
        Args:
            option_set_id: Option set ID
            data: Option creation data
            
        Returns:
            Created option
        """
        option = Option(
            option_set_id=option_set_id,
            code=data.code,
            sort_order=data.sort_order,
            is_active=data.is_active
        )
        
        self.db.add(option)
        self.db.flush()
        
        # Create translations
        for trans_data in data.translations:
            translation = OptionTranslation(
                option_id=option.id,
                language_code=trans_data['language_code'],
                display_text=trans_data['display_text']
            )
            self.db.add(translation)
        
        return option
    
    def _validate_ownership(
        self,
        option_set: OptionSet,
        org_id: UUID,
        operation: str
    ) -> None:
        """
        Validate option set ownership for modification operations.
        
        Args:
            option_set: Option set to validate
            org_id: Organization ID attempting the operation
            operation: Operation being performed (update/delete/modify)
            
        Raises:
            PermissionError: If option set is system-defined or owned by another org
        """
        if option_set.is_system_defined:
            raise PermissionError(
                message=f"Cannot {operation} system-defined option set",
                error_code="SYSTEM_DEFINED_IMMUTABLE",
                details={
                    "option_set_id": str(option_set.id),
                    "operation": operation
                }
            )
        
        if option_set.owner_org_id != org_id:
            raise PermissionError(
                message=f"Cannot {operation} option set owned by another organization",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "option_set_id": str(option_set.id),
                    "owner_org_id": str(option_set.owner_org_id),
                    "requesting_org_id": str(org_id),
                    "operation": operation
                }
            )
    
    def _to_option_set_response(
        self,
        option_set: OptionSet,
        language: str
    ) -> OptionSetDetailResponse:
        """Convert option set model to response schema."""
        # Convert options
        options_list = [
            self._to_option_response(opt, language)
            for opt in sorted(option_set.options, key=lambda x: (x.sort_order, x.code))
            if opt.is_active
        ]
        
        return OptionSetDetailResponse(
            id=option_set.id,
            code=option_set.code,
            is_system_defined=option_set.is_system_defined,
            owner_org_id=option_set.owner_org_id,
            is_active=option_set.is_active,
            created_at=option_set.created_at,
            updated_at=option_set.updated_at,
            created_by=option_set.created_by,
            updated_by=option_set.updated_by,
            options=options_list
        )
    
    def _to_option_response(
        self,
        option: Option,
        language: str
    ) -> OptionResponse:
        """Convert option model to response schema."""
        # Convert all translations
        translations_list = [
            OptionTranslationResponse(
                id=t.id,
                option_id=t.option_id,
                language_code=t.language_code,
                display_text=t.display_text,
                created_at=t.created_at
            )
            for t in option.translations
        ]
        
        # Extract translated display text for requested language
        display_text = None
        for t in option.translations:
            if t.language_code == language:
                display_text = t.display_text
                break
        
        # Fallback to English if requested language not found
        if not display_text:
            for t in option.translations:
                if t.language_code == 'en':
                    display_text = t.display_text
                    break
        
        # Fallback to code if no translation found
        if not display_text:
            display_text = option.code
        
        return OptionResponse(
            id=option.id,
            option_set_id=option.option_set_id,
            code=option.code,
            sort_order=option.sort_order,
            is_active=option.is_active,
            created_at=option.created_at,
            translations=translations_list,
            display_text=display_text
        )
