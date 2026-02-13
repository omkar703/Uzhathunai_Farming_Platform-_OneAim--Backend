"""
Template Service for Farm Audit Management System.

This service manages templates, template sections, and template parameters.
Supports CRUD operations, template copying, and permission validation.
"""

from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload

# ... (existing imports) ...


from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError, ConflictError
from app.models.template import Template, TemplateTranslation, TemplateSection, TemplateParameter
from app.models.section import Section, SectionTranslation
from app.models.parameter import Parameter
from app.models.user import User
from app.models.organization import Organization
from app.schemas.template import (
    TemplateCreate, TemplateUpdate, TemplateCopy,
    TemplateSectionAdd, TemplateParameterAdd
)
from app.services.snapshot_service import SnapshotService

logger = get_logger(__name__)


class TemplateService:
    """
    Service for managing templates, template sections, and template parameters.
    
    Handles CRUD operations, template copying with permission validation,
    and section/parameter management.
    """

    def __init__(self, db: Session):
        self.db = db
        self.snapshot_service = SnapshotService(db)

    def create_template(
        self,
        data: TemplateCreate,
        user_id: UUID,
        organization_id: Optional[UUID] = None
    ) -> Template:
        """
        Create a new template.
        
        Args:
            data: Template creation data
            user_id: ID of the user creating the template
            organization_id: ID of the user's organization (None for system users)
            
        Returns:
            Created template
            
        Raises:
            ConflictError: If template code already exists
            ValidationError: If validation fails
        """
        logger.info(
            "Creating template",
            extra={
                "user_id": str(user_id),
                "code": data.code,
                "organization_id": str(organization_id) if organization_id else None
            }
        )

        # Check if code already exists
        existing = self.db.query(Template).filter(Template.code == data.code).first()
        if existing:
            raise ConflictError(
                message=f"Template with code '{data.code}' already exists",
                error_code="TEMPLATE_CODE_EXISTS",
                details={"code": data.code}
            )

        # Determine ownership
        is_system_defined = organization_id is None
        owner_org_id = None if is_system_defined else organization_id

        # Create template
        template = Template(
            code=data.code,
            is_system_defined=is_system_defined,
            owner_org_id=owner_org_id,
            crop_type_id=data.crop_type_id,
            is_active=data.is_active,
            version=1,
            created_by=user_id,
            updated_by=user_id
        )

        self.db.add(template)
        self.db.flush()

        # Create translations
        for trans_data in data.translations:
            translation = TemplateTranslation(
                template_id=template.id,
                language_code=trans_data.language_code,
                name=trans_data.name,
                description=trans_data.description
            )
            self.db.add(translation)

        self.db.flush()

        # Handle nested sections and parameters
        for section_data in data.sections:
            # Check if section exists
            section = self.db.query(Section).filter(Section.id == section_data.section_id).first()
            if not section:
                raise NotFoundError(
                    message=f"Section {section_data.section_id} not found",
                    error_code="SECTION_NOT_FOUND",
                    details={"section_id": str(section_data.section_id)}
                )

            # Create template section
            template_section = TemplateSection(
                template_id=template.id,
                section_id=section_data.section_id,
                sort_order=section_data.sort_order
            )
            self.db.add(template_section)
            self.db.flush()

            # Handle parameters for this section
            for param_data in section_data.parameters:
                # Check if parameter exists
                parameter = self.db.query(Parameter).filter(Parameter.id == param_data.parameter_id).first()
                if not parameter:
                    raise NotFoundError(
                        message=f"Parameter {param_data.parameter_id} not found",
                        error_code="PARAMETER_NOT_FOUND",
                        details={"parameter_id": str(param_data.parameter_id)}
                    )

                # Create parameter snapshot
                parameter_snapshot = self.snapshot_service.create_parameter_snapshot(param_data.parameter_id)

                # Create template parameter
                template_parameter = TemplateParameter(
                    template_section_id=template_section.id,
                    parameter_id=param_data.parameter_id,
                    is_required=param_data.is_required,
                    sort_order=param_data.sort_order,
                    parameter_snapshot=parameter_snapshot
                )
                self.db.add(template_parameter)

        self.db.commit()
        self.db.refresh(template)

        logger.info(
            "Template created",
            extra={
                "template_id": str(template.id),
                "code": template.code,
                "is_system_defined": template.is_system_defined
            }
        )

        return template

    def get_templates(
        self,
        organization_id: Optional[UUID] = None,
        crop_type_id: Optional[UUID] = None,
        owner_org_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Template], int]:
        """
        Get templates with filtering and pagination.
        
        Args:
            organization_id: Filter by organization (None for system user)
            crop_type_id: Filter by crop type
            is_active: Filter by active status
            page: Page number (1-indexed)
            limit: Items per page
            
        Returns:
            Tuple of (templates list, total count)
        """
        query = self.db.query(Template).options(
            joinedload(Template.owner_organization),
            joinedload(Template.translations)
        )

        # Filter by visibility
        if organization_id is None:
            # System user sees all templates
            pass
        else:
            # Organization user sees system templates and their own
            query = query.filter(
                or_(
                    Template.is_system_defined == True,
                    Template.owner_org_id == organization_id
                )
            )

        # Apply filters
        if crop_type_id is not None:
            query = query.filter(Template.crop_type_id == crop_type_id)

        if owner_org_id is not None:
            query = query.filter(Template.owner_org_id == owner_org_id)

        if is_active is not None:
            query = query.filter(Template.is_active == is_active)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * limit
        templates = query.order_by(Template.created_at.desc()).offset(offset).limit(limit).all()

        return templates, total

    def get_template(self, template_id: UUID) -> Template:
        """
        Get template by ID.
        
        Args:
            template_id: UUID of the template
            
        Returns:
            Template
            
        Raises:
            NotFoundError: If template not found
        """
        # Eager load sections and parameters for full details
        template = self.db.query(Template).options(
            joinedload(Template.template_sections)
            .joinedload(TemplateSection.section),
            joinedload(Template.template_sections)
            .joinedload(TemplateSection.template_parameters)
            .joinedload(TemplateParameter.parameter)
            .joinedload(Parameter.translations),
            joinedload(Template.translations)
        ).filter(Template.id == template_id).first()
        
        if not template:
            raise NotFoundError(
                message=f"Template {template_id} not found",
                error_code="TEMPLATE_NOT_FOUND",
                details={"template_id": str(template_id)}
            )
        return template

    def update_template(
        self,
        template_id: UUID,
        data: TemplateUpdate,
        user_id: UUID,
        organization_id: Optional[UUID] = None
    ) -> Template:
        """
        Update template.
        
        Args:
            template_id: UUID of the template
            data: Update data
            user_id: ID of the user updating
            organization_id: ID of the user's organization
            
        Returns:
            Updated template
            
        Raises:
            NotFoundError: If template not found
            PermissionError: If user cannot modify template
            ConflictError: If code already exists
        """
        logger.info(
            "Updating template",
            extra={
                "template_id": str(template_id),
                "user_id": str(user_id)
            }
        )

        template = self.get_template(template_id)

        # Validate permissions
        self._validate_modification_permission(template, organization_id)

        # Check code uniqueness if changing
        if data.code and data.code != template.code:
            existing = self.db.query(Template).filter(
                Template.code == data.code,
                Template.id != template_id
            ).first()
            if existing:
                raise ConflictError(
                    message=f"Template with code '{data.code}' already exists",
                    error_code="TEMPLATE_CODE_EXISTS",
                    details={"code": data.code}
                )

        # Update fields
        if data.code is not None:
            template.code = data.code
        if data.crop_type_id is not None:
            template.crop_type_id = data.crop_type_id
        if data.is_active is not None:
            template.is_active = data.is_active

        template.updated_by = user_id

        # Update translations if provided
        if data.translations is not None:
            # Delete existing translations
            self.db.query(TemplateTranslation).filter(
                TemplateTranslation.template_id == template_id
            ).delete()

            # Create new translations
            for trans_data in data.translations:
                translation = TemplateTranslation(
                    template_id=template.id,
                    language_code=trans_data.language_code,
                    name=trans_data.name,
                    description=trans_data.description
                )
                self.db.add(translation)

        self.db.commit()
        self.db.refresh(template)

        logger.info(
            "Template updated",
            extra={"template_id": str(template.id)}
        )

        return template

    def delete_template(
        self,
        template_id: UUID,
        organization_id: Optional[UUID] = None
    ) -> None:
        """
        Delete template.
        
        Args:
            template_id: UUID of the template
            organization_id: ID of the user's organization
            
        Raises:
            NotFoundError: If template not found
            PermissionError: If user cannot delete template
        """
        logger.info(
            "Deleting template",
            extra={"template_id": str(template_id)}
        )

        template = self.get_template(template_id)

        # Validate permissions
        self._validate_modification_permission(template, organization_id)

        try:
            self.db.delete(template)
            self.db.commit()

            logger.info(
                "Template deleted",
                extra={"template_id": str(template_id)}
            )
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(
                message="Cannot delete template because it is being used by existing audits.",
                error_code="TEMPLATE_IN_USE",
                details={"template_id": str(template_id)}
            )

    def add_section_to_template(
        self,
        template_id: UUID,
        data: TemplateSectionAdd,
        organization_id: Optional[UUID] = None
    ) -> TemplateSection:
        """
        Add section to template.
        
        Args:
            template_id: UUID of the template
            data: Section addition data
            organization_id: ID of the user's organization
            
        Returns:
            Created template section
            
        Raises:
            NotFoundError: If template or section not found
            PermissionError: If user cannot modify template
            ConflictError: If section already in template
        """
        logger.info(
            "Adding section to template",
            extra={
                "template_id": str(template_id),
                "section_id": str(data.section_id)
            }
        )

        template = self.get_template(template_id)

        # Validate permissions
        self._validate_modification_permission(template, organization_id)

        # Check if section exists
        section = self.db.query(Section).filter(Section.id == data.section_id).first()
        if not section:
            raise NotFoundError(
                message=f"Section {data.section_id} not found",
                error_code="SECTION_NOT_FOUND",
                details={"section_id": str(data.section_id)}
            )

        # Check if section already in template
        existing = self.db.query(TemplateSection).filter(
            TemplateSection.template_id == template_id,
            TemplateSection.section_id == data.section_id
        ).first()
        if existing:
            raise ConflictError(
                message="Section already in template",
                error_code="SECTION_ALREADY_IN_TEMPLATE",
                details={
                    "template_id": str(template_id),
                    "section_id": str(data.section_id)
                }
            )

        # Create template section
        template_section = TemplateSection(
            template_id=template_id,
            section_id=data.section_id,
            sort_order=data.sort_order
        )

        self.db.add(template_section)
        self.db.commit()
        self.db.refresh(template_section)

        logger.info(
            "Section added to template",
            extra={
                "template_section_id": str(template_section.id),
                "template_id": str(template_id),
                "section_id": str(data.section_id)
            }
        )

        return template_section

    def remove_section_from_template(
        self,
        template_id: UUID,
        section_id: UUID,
        organization_id: Optional[UUID] = None
    ) -> None:
        """
        Remove section from template.
        
        Args:
            template_id: UUID of the template
            section_id: UUID of the section
            organization_id: ID of the user's organization
            
        Raises:
            NotFoundError: If template or template section not found
            PermissionError: If user cannot modify template
        """
        logger.info(
            "Removing section from template",
            extra={
                "template_id": str(template_id),
                "section_id": str(section_id)
            }
        )

        template = self.get_template(template_id)

        # Validate permissions
        self._validate_modification_permission(template, organization_id)

        # Find template section
        template_section = self.db.query(TemplateSection).filter(
            TemplateSection.template_id == template_id,
            TemplateSection.section_id == section_id
        ).first()

        if not template_section:
            raise NotFoundError(
                message="Section not found in template",
                error_code="TEMPLATE_SECTION_NOT_FOUND",
                details={
                    "template_id": str(template_id),
                    "section_id": str(section_id)
                }
            )

        self.db.delete(template_section)
        self.db.commit()

        logger.info(
            "Section removed from template",
            extra={
                "template_id": str(template_id),
                "section_id": str(section_id)
            }
        )

    def add_parameter_to_template_section(
        self,
        template_id: UUID,
        section_id: UUID,
        data: TemplateParameterAdd,
        organization_id: Optional[UUID] = None
    ) -> TemplateParameter:
        """
        Add parameter to template section.
        
        Args:
            template_id: UUID of the template
            section_id: UUID of the section
            data: Parameter addition data
            organization_id: ID of the user's organization
            
        Returns:
            Created template parameter
            
        Raises:
            NotFoundError: If template, section, or parameter not found
            PermissionError: If user cannot modify template
            ConflictError: If parameter already in section
        """
        logger.info(
            "Adding parameter to template section",
            extra={
                "template_id": str(template_id),
                "section_id": str(section_id),
                "parameter_id": str(data.parameter_id)
            }
        )

        template = self.get_template(template_id)

        # Validate permissions
        self._validate_modification_permission(template, organization_id)

        # Find template section
        template_section = self.db.query(TemplateSection).filter(
            TemplateSection.template_id == template_id,
            TemplateSection.section_id == section_id
        ).first()

        if not template_section:
            raise NotFoundError(
                message="Section not found in template",
                error_code="TEMPLATE_SECTION_NOT_FOUND",
                details={
                    "template_id": str(template_id),
                    "section_id": str(section_id)
                }
            )

        # Check if parameter exists
        parameter = self.db.query(Parameter).options(
            joinedload(Parameter.translations)
        ).filter(Parameter.id == data.parameter_id).first()
        if not parameter:
            raise NotFoundError(
                message=f"Parameter {data.parameter_id} not found",
                error_code="PARAMETER_NOT_FOUND",
                details={"parameter_id": str(data.parameter_id)}
            )

        # Check if parameter already in section
        existing = self.db.query(TemplateParameter).filter(
            TemplateParameter.template_section_id == template_section.id,
            TemplateParameter.parameter_id == data.parameter_id
        ).first()
        if existing:
            raise ConflictError(
                message="Parameter already in template section",
                error_code="PARAMETER_ALREADY_IN_SECTION",
                details={
                    "template_section_id": str(template_section.id),
                    "parameter_id": str(data.parameter_id)
                }
            )

        # Create parameter snapshot
        parameter_snapshot = self.snapshot_service.create_parameter_snapshot(data.parameter_id)

        # Create template parameter
        template_parameter = TemplateParameter(
            template_section_id=template_section.id,
            parameter=parameter,
            is_required=data.is_required,
            sort_order=data.sort_order,
            parameter_snapshot=parameter_snapshot
        )

        self.db.add(template_parameter)
        self.db.commit()
        self.db.refresh(template_parameter)

        logger.info(
            "Parameter added to template section",
            extra={
                "template_parameter_id": str(template_parameter.id),
                "template_section_id": str(template_section.id),
                "parameter_id": str(data.parameter_id)
            }
        )

        return template_parameter

    def remove_parameter_from_template_section(
        self,
        template_id: UUID,
        section_id: UUID,
        parameter_id: UUID,
        organization_id: Optional[UUID] = None
    ) -> None:
        """
        Remove parameter from template section.
        
        Args:
            template_id: UUID of the template
            section_id: UUID of the section
            parameter_id: UUID of the parameter
            organization_id: ID of the user's organization
            
        Raises:
            NotFoundError: If template, section, or parameter not found
            PermissionError: If user cannot modify template
        """
        logger.info(
            "Removing parameter from template section",
            extra={
                "template_id": str(template_id),
                "section_id": str(section_id),
                "parameter_id": str(parameter_id)
            }
        )

        template = self.get_template(template_id)

        # Validate permissions
        self._validate_modification_permission(template, organization_id)

        # Find template section
        template_section = self.db.query(TemplateSection).filter(
            TemplateSection.template_id == template_id,
            TemplateSection.section_id == section_id
        ).first()

        if not template_section:
            raise NotFoundError(
                message="Section not found in template",
                error_code="TEMPLATE_SECTION_NOT_FOUND",
                details={
                    "template_id": str(template_id),
                    "section_id": str(section_id)
                }
            )

        # Find template parameter
        template_parameter = self.db.query(TemplateParameter).filter(
            TemplateParameter.template_section_id == template_section.id,
            TemplateParameter.parameter_id == parameter_id
        ).first()

        if not template_parameter:
            raise NotFoundError(
                message="Parameter not found in template section",
                error_code="TEMPLATE_PARAMETER_NOT_FOUND",
                details={
                    "template_section_id": str(template_section.id),
                    "parameter_id": str(parameter_id)
                }
            )

        self.db.delete(template_parameter)
        self.db.commit()

        logger.info(
            "Parameter removed from template section",
            extra={
                "template_section_id": str(template_section.id),
                "parameter_id": str(parameter_id)
            }
        )

    def copy_template(
        self,
        source_template_id: UUID,
        data: TemplateCopy,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        has_consultancy_service: bool = False
    ) -> Template:
        """
        Copy template with deep copy of sections and parameters.
        
        Permission rules:
        - System users can copy any template (system or organization)
        - Organization users with consultancy service can copy only their own org templates
        - Regular organization users cannot copy templates
        
        Args:
            source_template_id: UUID of the template to copy
            data: Copy data (new code, translations)
            user_id: ID of the user copying
            organization_id: ID of the user's organization (None for system users)
            has_consultancy_service: Whether user has consultancy service
            
        Returns:
            Copied template
            
        Raises:
            NotFoundError: If source template not found
            PermissionError: If user cannot copy template
            ConflictError: If new code already exists
        """
        logger.info(
            "Copying template",
            extra={
                "source_template_id": str(source_template_id),
                "user_id": str(user_id),
                "organization_id": str(organization_id) if organization_id else None,
                "new_code": data.new_code
            }
        )

        # Get source template
        source_template = self.get_template(source_template_id)

        # Validate copy permissions
        self._validate_copy_permission(
            source_template,
            organization_id,
            has_consultancy_service
        )

        # Check if new code already exists
        existing = self.db.query(Template).filter(Template.code == data.new_code).first()
        if existing:
            raise ConflictError(
                message=f"Template with code '{data.new_code}' already exists",
                error_code="TEMPLATE_CODE_EXISTS",
                details={"code": data.new_code}
            )

        # Determine ownership for new template
        is_system_defined = organization_id is None
        owner_org_id = None if is_system_defined else organization_id

        # Create new template
        new_template = Template(
            code=data.new_code,
            is_system_defined=is_system_defined,
            owner_org_id=owner_org_id,
            crop_type_id=data.crop_type_id if data.crop_type_id else source_template.crop_type_id,
            is_active=True,
            version=1,
            created_by=user_id,
            updated_by=user_id
        )

        self.db.add(new_template)
        self.db.flush()

        # Copy translations (use new names if provided, otherwise copy from source)
        source_translations = self.db.query(TemplateTranslation).filter(
            TemplateTranslation.template_id == source_template_id
        ).all()

        for source_trans in source_translations:
            # Use new name if provided, otherwise use source name
            new_name = data.new_name_translations.get(
                source_trans.language_code,
                source_trans.name
            )

            translation = TemplateTranslation(
                template_id=new_template.id,
                language_code=source_trans.language_code,
                name=new_name,
                description=source_trans.description
            )
            self.db.add(translation)

        # Copy template sections
        source_sections = self.db.query(TemplateSection).filter(
            TemplateSection.template_id == source_template_id
        ).order_by(TemplateSection.sort_order).all()

        for source_section in source_sections:
            # Create new template section (references same section entity)
            new_template_section = TemplateSection(
                template_id=new_template.id,
                section_id=source_section.section_id,
                sort_order=source_section.sort_order
            )
            self.db.add(new_template_section)
            self.db.flush()

            # Copy template parameters
            source_parameters = self.db.query(TemplateParameter).filter(
                TemplateParameter.template_section_id == source_section.id
            ).order_by(TemplateParameter.sort_order).all()

            for source_param in source_parameters:
                # Create new parameter snapshot
                parameter_snapshot = self.snapshot_service.create_parameter_snapshot(
                    source_param.parameter_id
                )

                # Create new template parameter (references same parameter entity)
                new_template_param = TemplateParameter(
                    template_section_id=new_template_section.id,
                    parameter_id=source_param.parameter_id,
                    is_required=source_param.is_required,
                    sort_order=source_param.sort_order,
                    parameter_snapshot=parameter_snapshot
                )
                self.db.add(new_template_param)

        self.db.commit()
        self.db.refresh(new_template)

        logger.info(
            "Template copied",
            extra={
                "source_template_id": str(source_template_id),
                "new_template_id": str(new_template.id),
                "new_code": new_template.code
            }
        )

        return new_template

    def _validate_modification_permission(
        self,
        template: Template,
        organization_id: Optional[UUID]
    ) -> None:
        """
        Validate user can modify template.
        
        Rules:
        - System-defined templates cannot be modified by organization users
        - Organization users can only modify their own templates
        
        Args:
            template: Template to validate
            organization_id: ID of the user's organization (None for system users)
            
        Raises:
            PermissionError: If user cannot modify template
        """
        # System users can modify anything
        if organization_id is None:
            return

        # Cannot modify system-defined templates
        if template.is_system_defined:
            raise PermissionError(
                message="Cannot modify system-defined template",
                error_code="CANNOT_MODIFY_SYSTEM_TEMPLATE",
                details={"template_id": str(template.id)}
            )

        # Can only modify own organization's templates
        if template.owner_org_id != organization_id:
            raise PermissionError(
                message="Cannot modify template owned by another organization",
                error_code="CANNOT_MODIFY_OTHER_ORG_TEMPLATE",
                details={
                    "template_id": str(template.id),
                    "owner_org_id": str(template.owner_org_id)
                }
            )

    def _validate_copy_permission(
        self,
        source_template: Template,
        organization_id: Optional[UUID],
        has_consultancy_service: bool
    ) -> None:
        """
        Validate user can copy template.
        
        Rules:
        - System users can copy any template
        - Organization users with consultancy service can copy only their own org templates
        - Regular organization users cannot copy templates
        
        Args:
            source_template: Template to copy
            organization_id: ID of the user's organization (None for system users)
            has_consultancy_service: Whether user has consultancy service
            
        Raises:
            PermissionError: If user cannot copy template
        """
        # System users can copy anything
        if organization_id is None:
            return

        # Organization users must have consultancy service
        if not has_consultancy_service:
            raise PermissionError(
                message="Consultancy service required to copy templates",
                error_code="CONSULTANCY_SERVICE_REQUIRED",
                details={"template_id": str(source_template.id)}
            )

        # Can only copy own organization's templates
        if source_template.owner_org_id != organization_id:
            raise PermissionError(
                message="Can only copy templates from your own organization",
                error_code="CANNOT_COPY_OTHER_ORG_TEMPLATE",
                details={
                    "template_id": str(source_template.id),
                    "source_owner_org_id": str(source_template.owner_org_id),
                    "user_org_id": str(organization_id)
                }
            )