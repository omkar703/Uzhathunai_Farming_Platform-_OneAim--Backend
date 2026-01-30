"""
Parameter service for managing parameters with ownership validation and copy operations.
Supports system-defined and organization-specific parameters for Farm Audit Management.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, PermissionError, ValidationError
from app.models.parameter import Parameter, ParameterTranslation, ParameterOptionSetMap, ParameterType
from app.models.option_set import OptionSet, Option, OptionTranslation
from app.models.user import User
from app.schemas.parameter import (
    ParameterCreate, ParameterUpdate, ParameterCopy, ParameterResponse, ParameterDetailResponse
)

logger = get_logger(__name__)


class ParameterService:
    """Service for parameter operations with ownership validation and copy functionality."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_parameters(
        self,
        org_id: Optional[UUID],
        parameter_type: Optional[ParameterType] = None,
        language: str = "en",
        include_system: bool = True,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[ParameterResponse], int]:
        """
        Get parameters (system-defined and org-specific).
        
        Args:
            org_id: Organization ID
            parameter_type: Filter by parameter type (optional)
            language: Language code for translations (default: en)
            include_system: Include system-defined parameters (default: True)
            
        Returns:
            List of parameters
        """
        from sqlalchemy.orm import joinedload
        
        query = self.db.query(Parameter).filter(
            Parameter.is_active == True
        ).options(
            joinedload(Parameter.translations),
            joinedload(Parameter.option_set_mappings)
        )
        
        # Filter by parameter type
        if parameter_type:
            query = query.filter(Parameter.parameter_type == parameter_type)
        
        # Filter by ownership
        if include_system:
            # Include both system-defined and org-specific
            if org_id:
                query = query.filter(
                    or_(
                        Parameter.is_system_defined == True,
                        Parameter.owner_org_id == org_id
                    )
                )
             # If org_id is None (Super Admin), include everything.
        else:
            # Only org-specific
            if org_id:
                query = query.filter(
                    and_(
                        Parameter.is_system_defined == False,
                        Parameter.owner_org_id == org_id
                    )
                )
            else:
                 # If org_id is None, return all non-system
                 query = query.filter(Parameter.is_system_defined == False)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        parameters = query.order_by(Parameter.code).offset(offset).limit(limit).all()
        
        logger.info(
            "Retrieved parameters",
            extra={
                "org_id": str(org_id),
                "count": len(parameters),
                "total": total,
                "parameter_type": parameter_type.value if parameter_type else None,
                "include_system": include_system,
                "language": language,
                "page": page,
                "limit": limit
            }
        )
        
        return [self._to_parameter_response(p, language) for p in parameters], total
    
    def get_parameter(
        self,
        parameter_id: UUID,
        org_id: Optional[UUID],
        language: str = "en"
    ) -> ParameterDetailResponse:
        """
        Get parameter by ID with all translations and option sets.
        
        Args:
            parameter_id: Parameter ID
            org_id: Organization ID
            language: Language code for translations (default: en)
            
        Returns:
            Parameter with all translations and option sets
            
        Raises:
            NotFoundError: If parameter not found
            PermissionError: If parameter is not accessible by organization
        """
        from sqlalchemy.orm import joinedload
        
        parameter = self.db.query(Parameter).filter(
            Parameter.id == parameter_id
        ).options(
            joinedload(Parameter.translations),
            joinedload(Parameter.option_set_mappings)
        ).first()
        
        if not parameter:
            raise NotFoundError(
                message=f"Parameter {parameter_id} not found",
                error_code="PARAMETER_NOT_FOUND",
                details={"parameter_id": str(parameter_id)}
            )
        
        # Validate access
        if org_id:
            if not parameter.is_system_defined and parameter.owner_org_id != org_id:
                raise PermissionError(
                    message="Cannot access parameter owned by another organization",
                    error_code="INSUFFICIENT_PERMISSIONS",
                    details={
                        "parameter_id": str(parameter_id),
                        "owner_org_id": str(parameter.owner_org_id),
                        "requesting_org_id": str(org_id)
                    }
                )
        
        logger.info(
            "Retrieved parameter",
            extra={
                "parameter_id": str(parameter_id),
                "org_id": str(org_id),
                "language": language
            }
        )
        
        return self._to_parameter_response(parameter, language)
    
    def create_org_parameter(
        self,
        data: ParameterCreate,
        org_id: Optional[UUID],
        user_id: UUID
    ) -> ParameterDetailResponse:
        """
        Create organization-specific parameter.
        
        Args:
            data: Parameter creation data
            org_id: Organization ID
            user_id: User ID creating the parameter
            
        Returns:
            Created parameter
            
        Raises:
            ValidationError: If parameter code already exists for organization
            ValidationError: If option sets are invalid
        """
        # Check if parameter code already exists for this org
        if org_id:
            existing = self.db.query(Parameter).filter(
                and_(
                    Parameter.code == data.code,
                    Parameter.owner_org_id == org_id,
                    Parameter.is_active == True
                )
            ).first()
        else:
             # System defined duplicate check
            existing = self.db.query(Parameter).filter(
                and_(
                    Parameter.code == data.code,
                    Parameter.is_system_defined == True,
                    Parameter.is_active == True
                )
            ).first()

        if existing:
            raise ValidationError(
                message=f"Parameter with code '{data.code}' already exists",
                error_code="DUPLICATE_PARAMETER_CODE",
                details={"code": data.code}
            )
        
        # Validate option sets for SELECT types
        if data.parameter_type in [ParameterType.SINGLE_SELECT, ParameterType.MULTI_SELECT]:
            inline_options = data.options or data.option_set
            
            if not data.option_set_ids and not inline_options:
                raise ValidationError(
                    message=f"{data.parameter_type.value} parameters must have at least one option set or inline options",
                    error_code="MISSING_OPTION_SETS",
                    details={"parameter_type": data.parameter_type.value}
                )
            
            # Handle inline options
            if inline_options and not data.option_set_ids:
                # Create a new option set for these inline options
                os_code = f"OS_{data.code}"[:50]
                
                # Check if it exists
                existing_os = self.db.query(OptionSet).filter(
                    OptionSet.code == os_code,
                    OptionSet.owner_org_id == org_id
                ).first()
                
                if existing_os:
                    # Reuse existing one if it matches code? 
                    # For safety, let's just use it or append uuid
                    import uuid
                    os_code = f"OS_{data.code}_{str(uuid.uuid4())[:8]}"[:50]
                
                new_os = OptionSet(
                    code=os_code,
                    is_system_defined=False,
                    owner_org_id=org_id,
                    is_active=True,
                    created_by=user_id,
                    updated_by=user_id
                )
                self.db.add(new_os)
                self.db.flush()
                
                for i, opt in enumerate(inline_options):
                    new_opt = Option(
                        option_set_id=new_os.id,
                        code=opt.value,
                        sort_order=i,
                        is_active=True
                    )
                    self.db.add(new_opt)
                    self.db.flush()
                    
                    # Add translation (using 'en' as default)
                    new_trans = OptionTranslation(
                        option_id=new_opt.id,
                        language_code="en",
                        display_text=opt.label
                    )
                    self.db.add(new_trans)
                
                data.option_set_ids = [new_os.id]
                logger.info(f"Created inline OptionSet {os_code} for parameter {data.code}")

            # Validate option sets exist and are accessible
            if data.option_set_ids:
                for option_set_id in data.option_set_ids:
                    option_set = self.db.query(OptionSet).filter(
                        OptionSet.id == option_set_id
                    ).first()
                    
                    if not option_set:
                        raise ValidationError(
                            message=f"Option set {option_set_id} not found",
                            error_code="OPTION_SET_NOT_FOUND",
                            details={"option_set_id": str(option_set_id)}
                        )
                    
                    # Validate access to option set
                    if org_id:
                        if not option_set.is_system_defined and option_set.owner_org_id != org_id:
                            raise PermissionError(
                                message="Cannot use option set owned by another organization",
                                error_code="INSUFFICIENT_PERMISSIONS",
                                details={
                                    "option_set_id": str(option_set_id),
                                    "owner_org_id": str(option_set.owner_org_id),
                                    "requesting_org_id": str(org_id)
                                }
                            )
        
        # Create parameter
        is_system = org_id is None
        parameter = Parameter(
            code=data.code,
            parameter_type=data.parameter_type,
            is_system_defined=is_system,
            owner_org_id=org_id,
            is_active=True,
            parameter_metadata=data.parameter_metadata,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(parameter)
        self.db.flush()
        
        # Create translations
        for trans_data in data.translations:
            translation = ParameterTranslation(
                parameter_id=parameter.id,
                language_code=trans_data['language_code'],
                name=trans_data['name'],
                description=trans_data.get('description'),
                help_text=trans_data.get('help_text')
            )
            self.db.add(translation)
        
        # Create option set mappings
        if data.option_set_ids:
            for option_set_id in data.option_set_ids:
                mapping = ParameterOptionSetMap(
                    parameter_id=parameter.id,
                    option_set_id=option_set_id
                )
                self.db.add(mapping)
        
        self.db.commit()
        self.db.refresh(parameter)
        
        logger.info(
            "Created organization-specific parameter",
            extra={
                "parameter_id": str(parameter.id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "code": data.code,
                "parameter_type": data.parameter_type.value,
                "option_sets_count": len(data.option_set_ids) if data.option_set_ids else 0
            }
        )
        
        return self._to_parameter_response(parameter, "en")
    
    def update_org_parameter(
        self,
        parameter_id: UUID,
        data: ParameterUpdate,
        org_id: Optional[UUID],
        user_id: UUID
    ) -> ParameterDetailResponse:
        """
        Update organization-specific parameter.
        
        Args:
            parameter_id: Parameter ID
            data: Parameter update data
            org_id: Organization ID
            user_id: User ID updating the parameter
            
        Returns:
            Updated parameter
            
        Raises:
            NotFoundError: If parameter not found
            PermissionError: If parameter is system-defined or owned by another org
        """
        parameter = self.db.query(Parameter).filter(
            Parameter.id == parameter_id
        ).first()
        
        if not parameter:
            raise NotFoundError(
                message=f"Parameter {parameter_id} not found",
                error_code="PARAMETER_NOT_FOUND",
                details={"parameter_id": str(parameter_id)}
            )
        
        # Validate ownership
        self._validate_ownership(parameter, org_id, "update")
        
        # Update fields
        if data.is_active is not None:
            parameter.is_active = data.is_active
        
        if data.parameter_metadata is not None:
            # Merge with existing metadata
            if parameter.parameter_metadata:
                parameter.parameter_metadata.update(data.parameter_metadata)
            else:
                parameter.parameter_metadata = data.parameter_metadata
        
        # Update translations
        if data.translations:
            for trans_data in data.translations:
                lang = trans_data['language_code']
                translation = self.db.query(ParameterTranslation).filter(
                    and_(
                        ParameterTranslation.parameter_id == parameter_id,
                        ParameterTranslation.language_code == lang
                    )
                ).first()
                
                if translation:
                    translation.name = trans_data['name']
                    translation.description = trans_data.get('description')
                    translation.help_text = trans_data.get('help_text')
                else:
                    translation = ParameterTranslation(
                        parameter_id=parameter_id,
                        language_code=lang,
                        name=trans_data['name'],
                        description=trans_data.get('description'),
                        help_text=trans_data.get('help_text')
                    )
                    self.db.add(translation)
        
        # Handle inline options update
        # If inline options provided, create a new option set and update option_set_ids
        inline_options = data.options or data.option_set
        if inline_options:
            # Create a new option set for these inline options
            # Similar logic to create_org_parameter
            import uuid
            os_code = f"OS_{parameter.code}_{str(uuid.uuid4())[:8]}"[:50]
            
            new_os = OptionSet(
                code=os_code,
                is_system_defined=False,
                owner_org_id=org_id,
                is_active=True,
                created_by=user_id,
                updated_by=user_id
            )
            self.db.add(new_os)
            self.db.flush()
            
            for i, opt in enumerate(inline_options):
                new_opt = Option(
                    option_set_id=new_os.id,
                    code=opt.value,
                    sort_order=i,
                    is_active=True
                )
                self.db.add(new_opt)
                self.db.flush()
                
                # Add translation (using 'en' as default)
                new_trans = OptionTranslation(
                    option_id=new_opt.id,
                    language_code="en",
                    display_text=opt.label
                )
                self.db.add(new_trans)
            
            # Update option_set_ids to point to this new OS
            # This overwrites any existing option_set_ids if provided in the same request
            # or replaces existing ones if not provided.
            data.option_set_ids = [new_os.id]
            logger.info(f"Created new inline OptionSet {os_code} for updated parameter {parameter.code}")

        # Update option set mappings
        if data.option_set_ids is not None:
            # Remove existing mappings
            self.db.query(ParameterOptionSetMap).filter(
                ParameterOptionSetMap.parameter_id == parameter_id
            ).delete()
            
            # Add new mappings
            for option_set_id in data.option_set_ids:
                # Validate option set exists and is accessible
                option_set = self.db.query(OptionSet).filter(
                    OptionSet.id == option_set_id
                ).first()
                
                if not option_set:
                    raise ValidationError(
                        message=f"Option set {option_set_id} not found",
                        error_code="OPTION_SET_NOT_FOUND",
                        details={"option_set_id": str(option_set_id)}
                    )
                
                if org_id:
                    if not option_set.is_system_defined and option_set.owner_org_id != org_id:
                        raise PermissionError(
                            message="Cannot use option set owned by another organization",
                            error_code="INSUFFICIENT_PERMISSIONS",
                            details={
                                "option_set_id": str(option_set_id),
                                "owner_org_id": str(option_set.owner_org_id),
                                "requesting_org_id": str(org_id)
                            }
                        )
                
                mapping = ParameterOptionSetMap(
                    parameter_id=parameter_id,
                    option_set_id=option_set_id
                )
                self.db.add(mapping)
        
        parameter.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(parameter)
        
        logger.info(
            "Updated organization-specific parameter",
            extra={
                "parameter_id": str(parameter_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_parameter_response(parameter, "en")
    
    def delete_org_parameter(
        self,
        parameter_id: UUID,
        org_id: Optional[UUID],
        user_id: UUID
    ) -> None:
        """
        Delete (soft delete) organization-specific parameter.
        
        Args:
            parameter_id: Parameter ID
            org_id: Organization ID
            user_id: User ID deleting the parameter
            
        Raises:
            NotFoundError: If parameter not found
            PermissionError: If parameter is system-defined or owned by another org
        """
        parameter = self.db.query(Parameter).filter(
            Parameter.id == parameter_id
        ).first()
        
        if not parameter:
            raise NotFoundError(
                message=f"Parameter {parameter_id} not found",
                error_code="PARAMETER_NOT_FOUND",
                details={"parameter_id": str(parameter_id)}
            )
        
        # Validate ownership
        self._validate_ownership(parameter, org_id, "delete")
        
        # Soft delete
        parameter.is_active = False
        parameter.updated_by = user_id
        
        self.db.commit()
        
        logger.info(
            "Deleted organization-specific parameter",
            extra={
                "parameter_id": str(parameter_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def copy_parameter(
        self,
        source_parameter_id: UUID,
        data: ParameterCopy,
        org_id: Optional[UUID],
        user_id: UUID,
        user: User
    ) -> ParameterDetailResponse:
        """
        Copy parameter with permission validation.
        
        System users can copy from any parameter.
        Organization users with consultancy service can copy only from their own org parameters.
        
        Args:
            source_parameter_id: Source parameter ID to copy from
            data: Copy data with new code
            org_id: Organization ID
            user_id: User ID performing the copy
            user: User object for permission checking
            
        Returns:
            Copied parameter
            
        Raises:
            NotFoundError: If source parameter not found
            PermissionError: If user doesn't have permission to copy
            ValidationError: If new code already exists
        """
        from sqlalchemy.orm import joinedload
        
        # Get source parameter
        source_parameter = self.db.query(Parameter).filter(
            Parameter.id == source_parameter_id
        ).options(
            joinedload(Parameter.translations),
            joinedload(Parameter.option_set_mappings)
        ).first()
        
        if not source_parameter:
            raise NotFoundError(
                message=f"Source parameter {source_parameter_id} not found",
                error_code="PARAMETER_NOT_FOUND",
                details={"parameter_id": str(source_parameter_id)}
            )
        
        # Validate copy permissions
        self._validate_copy_permission(source_parameter, org_id, user)
        
        # Check if new code already exists for this org
        if org_id:
            existing = self.db.query(Parameter).filter(
                and_(
                    Parameter.code == data.new_code,
                    Parameter.owner_org_id == org_id,
                    Parameter.is_active == True
                )
            ).first()
        else:
             existing = self.db.query(Parameter).filter(
                and_(
                    Parameter.code == data.new_code,
                    Parameter.is_system_defined == True, # System
                    Parameter.is_active == True
                )
            ).first()
        
        if existing:
            raise ValidationError(
                message=f"Parameter with code '{data.new_code}' already exists for this organization",
                error_code="DUPLICATE_PARAMETER_CODE",
                details={"code": data.new_code}
            )
        
        # Create deep copy of parameter
        new_parameter = Parameter(
            code=data.new_code,
            parameter_type=source_parameter.parameter_type,
            is_system_defined=True if org_id is None else False,
            owner_org_id=org_id,
            is_active=True,
            parameter_metadata=source_parameter.parameter_metadata.copy() if source_parameter.parameter_metadata else {},
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(new_parameter)
        self.db.flush()
        
        # Copy translations
        for source_trans in source_parameter.translations:
            new_trans = ParameterTranslation(
                parameter_id=new_parameter.id,
                language_code=source_trans.language_code,
                name=source_trans.name,
                description=source_trans.description,
                help_text=source_trans.help_text
            )
            self.db.add(new_trans)
        
        # Reference same option sets (not copy)
        for source_mapping in source_parameter.option_set_mappings:
            new_mapping = ParameterOptionSetMap(
                parameter_id=new_parameter.id,
                option_set_id=source_mapping.option_set_id
            )
            self.db.add(new_mapping)
        
        self.db.commit()
        self.db.refresh(new_parameter)
        
        logger.info(
            "Copied parameter",
            extra={
                "source_parameter_id": str(source_parameter_id),
                "new_parameter_id": str(new_parameter.id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "new_code": data.new_code
            }
        )
        
        return self._to_parameter_response(new_parameter, "en")
    
    def _validate_ownership(
        self,
        parameter: Parameter,
        org_id: UUID,
        operation: str
    ) -> None:
        """
        Validate parameter ownership for modification operations.
        
        Args:
            parameter: Parameter to validate
            org_id: Organization ID attempting the operation
            operation: Operation being performed (update/delete)
            
        Raises:
            PermissionError: If parameter is system-defined or owned by another org
        """
        if org_id is None:
             # System Admin
             if parameter.is_system_defined:
                 return # Allow
             return # Allow editing org parameters too? Yes, super admin.

        if parameter.is_system_defined:
            raise PermissionError(
                message=f"Cannot {operation} system-defined parameter",
                error_code="SYSTEM_DEFINED_IMMUTABLE",
                details={
                    "parameter_id": str(parameter.id),
                    "operation": operation
                }
            )
        
        if parameter.owner_org_id != org_id:
            raise PermissionError(
                message=f"Cannot {operation} parameter owned by another organization",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "parameter_id": str(parameter.id),
                    "owner_org_id": str(parameter.owner_org_id),
                    "requesting_org_id": str(org_id),
                    "operation": operation
                }
            )
    
    def _validate_copy_permission(
        self,
        source_parameter: Parameter,
        org_id: Optional[UUID],
        user: User
    ) -> None:
        """
        Validate user has permission to copy parameter.
        
        System users can copy from any parameter.
        Organization users with consultancy service can copy only from their own org parameters.
        
        Args:
            source_parameter: Source parameter to copy
            org_id: Organization ID
            user: User performing the copy
            
        Raises:
            PermissionError: If user doesn't have permission to copy
        """
        # Check if user is system user (has system-level roles)
        # For now, we'll check if user has any system-defined roles
        from app.models.rbac import Role
        from app.models.organization import OrgMemberRole
        
        system_roles = self.db.query(Role).join(OrgMemberRole).filter(
            and_(
                OrgMemberRole.user_id == user.id,
                Role.scope == 'SYSTEM'
            )
        ).first()
        
        if system_roles or org_id is None:
            # System users can copy any parameter
            return
        
        # Check if user has consultancy service
        from app.models.fsp_service import FSPServiceListing, MasterService
        
        consultancy_service = self.db.query(FSPServiceListing).join(MasterService).filter(
            and_(
                FSPServiceListing.fsp_organization_id == org_id,
                MasterService.code == 'CONSULTANCY',
                FSPServiceListing.status == 'ACTIVE'
            )
        ).first()
        
        if not consultancy_service:
            # Maybe slightly redundant if org_id is checked later, but safe.
            if org_id:  # Only check if org context exists
                raise PermissionError(
                    message="Organization must have consultancy service to copy parameters",
                    error_code="CONSULTANCY_SERVICE_REQUIRED",
                    details={"org_id": str(org_id)}
                )
        
        # Organization users with consultancy can only copy from their own org
        if not source_parameter.is_system_defined and source_parameter.owner_org_id != org_id:
            raise PermissionError(
                message="Can only copy parameters from your own organization",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "source_parameter_id": str(source_parameter.id),
                    "source_owner_org_id": str(source_parameter.owner_org_id),
                    "requesting_org_id": str(org_id)
                }
            )
    
    def _to_parameter_response(
        self,
        parameter: Parameter,
        language: str
    ) -> ParameterDetailResponse:
        """Convert parameter model to response schema."""
        from app.schemas.parameter import ParameterTranslationResponse, InlineOption
        
        # Convert translations
        translations_list = [
            ParameterTranslationResponse(
                id=t.id,
                parameter_id=t.parameter_id,
                language_code=t.language_code,
                name=t.name,
                description=t.description,
                help_text=t.help_text,
                created_at=t.created_at
            )
            for t in parameter.translations
        ]
        
        # Extract option set IDs
        option_set_ids = [
            mapping.option_set_id
            for mapping in parameter.option_set_mappings
        ]
        
        # Find translation for requested language
        name = next(
            (t.name for t in parameter.translations if t.language_code == language),
            None
        )
        
        # Fallback to English if not found
        if not name:
            name = next(
                (t.name for t in parameter.translations if t.language_code == "en"),
                None
            )
            
        # Fallback to any translation if English not found
        if not name and parameter.translations:
            name = parameter.translations[0].name
            
        # Populate detailed option_set with translations
        option_set_details = []
        if parameter.option_set_mappings:
            # For each mapping, get the option set and its options
            for mapping in parameter.option_set_mappings:
                # We need to fetch the option set and its options if not already loaded
                # The relationship mapping.option_set might not be eagerly loaded depending on query
                # better to rely on what satisfied the query options or fetch if needed
                
                # Assuming simple access for now, but to be robust we should ensure eager loading in query
                # In get_parameters/get_parameter, we loaded option_set_mappings but not the option_set relations deeper
                pass
                
                # REVISIT: Fetching options here might be N+1 if not careful.
                # However, for detail view it's fine. For list view, we might want to optimize.
                # Let's perform a direct query to get options for these sets.
                
                options = self.db.query(Option).filter(
                     and_(
                         Option.option_set_id == mapping.option_set_id,
                         Option.is_active == True
                     )
                ).order_by(Option.sort_order).all()
                
                for opt in options:
                    # Find translation for option
                    # Note: This is a bit inefficient doing query in loop.
                    # Optimally we join OptionTranslation.
                    opt_trans = self.db.query(OptionTranslation).filter(
                        and_(
                            OptionTranslation.option_id == opt.id,
                            OptionTranslation.language_code == language
                        )
                    ).first()
                    
                    if not opt_trans:
                        # Fallback to en
                        opt_trans = self.db.query(OptionTranslation).filter(
                            and_(
                                OptionTranslation.option_id == opt.id,
                                OptionTranslation.language_code == "en"
                            )
                        ).first()
                        
                    label = opt_trans.display_text if opt_trans else opt.code
                    
                    option_set_details.append(
                        InlineOption(
                            label=label,
                            value=opt.code
                        )
                    )

        return ParameterDetailResponse(
            id=parameter.id,
            code=parameter.code,
            parameter_type=parameter.parameter_type,
            is_system_defined=parameter.is_system_defined,
            owner_org_id=parameter.owner_org_id,
            is_active=parameter.is_active,
            parameter_metadata=parameter.parameter_metadata or {},
            created_at=parameter.created_at,
            updated_at=parameter.updated_at,
            created_by=parameter.created_by,
            updated_by=parameter.updated_by,
            name=name,
            translations=translations_list,
            option_set_ids=option_set_ids,
            option_set=option_set_details
        )
