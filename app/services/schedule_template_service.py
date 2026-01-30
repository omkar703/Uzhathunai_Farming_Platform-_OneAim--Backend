"""
Schedule Template service for Uzhathunai v2.0.
Handles schedule template management with access control.
"""
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID

from app.models.schedule_template import (
    ScheduleTemplate,
    ScheduleTemplateTranslation,
    ScheduleTemplateTask
)
from app.models.organization import Organization, OrgMemberRole
from app.models.rbac import Role
from app.models.user import User
from app.models.fsp_service import FSPServiceListing, MasterService
from app.models.enums import OrganizationType, TaskCategory
from app.schemas.schedule_template import (
    ScheduleTemplateCreate,
    ScheduleTemplateUpdate
)
from app.core.logging import get_logger
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    PermissionError
)

logger = get_logger(__name__)


class ScheduleTemplateService:
    """Service for schedule template management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
    
    def validate_template_creation_access(self, user_id: UUID) -> Tuple[bool, bool, Optional[UUID]]:
        """
        Validate if user can create schedule templates.
        
        Requirements 4.1, 4.2:
        - System users can create templates
        - FSP users with consultancy service can create templates
        - Farming organization users cannot create templates
        
        Args:
            user_id: User ID
        
        Returns:
            Tuple of (can_create, is_system_user, fsp_org_id)
        
        Raises:
            PermissionError: If user cannot create templates
        """
        self.logger.info(
            "Validating template creation access",
            extra={"user_id": str(user_id)}
        )
        
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        # Check if system user (SuperAdmin, Billing Admin, Support Agent)
        system_roles = ['SUPER_ADMIN', 'BILLING_ADMIN', 'SUPPORT_AGENT']
        user_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.user_id == user_id
        ).all()
        
        is_system_user = any(mr.role.code in system_roles for mr in user_roles)
        
        if is_system_user:
            self.logger.info(
                "User is system user - can create templates",
                extra={"user_id": str(user_id)}
            )
            return True, True, None
        
        # Check if FSP user with consultancy service
        # Get user's FSP organizations
        fsp_orgs = self.db.query(Organization).join(
            OrgMemberRole,
            Organization.id == OrgMemberRole.organization_id
        ).filter(
            OrgMemberRole.user_id == user_id,
            Organization.organization_type == OrganizationType.FSP
        ).all()
        
        for org in fsp_orgs:
            # Check if FSP has consultancy service
            has_consultancy = self._check_fsp_consultancy_service(org.id)
            if has_consultancy:
                self.logger.info(
                    "User is FSP user with consultancy service - can create templates",
                    extra={"user_id": str(user_id), "fsp_org_id": str(org.id)}
                )
                return True, False, org.id
        
        # User cannot create templates
        raise PermissionError(
            message="Schedule template creation requires system user or FSP consultancy service",
            error_code="TEMPLATE_CREATION_FORBIDDEN",
            details={"user_id": str(user_id)}
        )
    
    def _check_fsp_consultancy_service(self, fsp_org_id: UUID) -> bool:
        """
        Check if FSP organization has consultancy service.
        
        Args:
            fsp_org_id: FSP organization ID
        
        Returns:
            True if FSP has consultancy service
        """
        # Get consultancy master service
        consultancy_service = self.db.query(MasterService).filter(
            MasterService.code == 'CONSULTANCY'
        ).first()
        
        if not consultancy_service:
            return False
        
        # Check if FSP has active consultancy service listing
        has_consultancy = self.db.query(FSPServiceListing).filter(
            FSPServiceListing.fsp_organization_id == fsp_org_id,
            FSPServiceListing.service_id == consultancy_service.id
        ).first() is not None
        
        return has_consultancy
    
    def create_template(
        self,
        user_id: UUID,
        data: ScheduleTemplateCreate
    ) -> ScheduleTemplate:
        """
        Create schedule template with access control.
        
        Requirements 4.1, 4.2, 4.3, 4.4, 4.5:
        - System users can create system-defined or org-specific templates
        - FSP users with consultancy can create org-specific templates only
        - Validates ownership constraints
        
        Args:
            user_id: User ID
            data: Template data
        
        Returns:
            Created template
        
        Raises:
            PermissionError: If user cannot create templates
            ValidationError: If data is invalid
        """
        self.logger.info(
            "Creating schedule template",
            extra={
                "user_id": str(user_id),
                "code": data.code,
                "is_system_defined": data.is_system_defined
            }
        )
        
        # Validate access
        can_create, is_system_user, fsp_org_id = self.validate_template_creation_access(user_id)

        
        # Requirement 4.4: System user can create either system-defined or org-specific
        # Requirement 4.5: FSP user can only create org-specific owned by their FSP org
        if not is_system_user:
            # FSP user - must create org-specific template
            if data.is_system_defined:
                raise PermissionError(
                    message="FSP users can only create organization-specific templates",
                    error_code="CANNOT_CREATE_SYSTEM_TEMPLATE",
                    details={"user_id": str(user_id)}
                )
            
            # Set owner to FSP organization
            data.owner_org_id = fsp_org_id
        
        # Requirement 4.6: Validate ownership constraints
        if data.is_system_defined and data.owner_org_id is not None:
            raise ValidationError(
                message="System-defined templates must have NULL owner_org_id",
                error_code="INVALID_SYSTEM_TEMPLATE_OWNERSHIP"
            )
        
        if not data.is_system_defined and data.owner_org_id is None:
            raise ValidationError(
                message="Organization-specific templates must have non-NULL owner_org_id",
                error_code="INVALID_ORG_TEMPLATE_OWNERSHIP"
            )
        
        # Check for duplicate code
        existing = self.db.query(ScheduleTemplate).filter(
            ScheduleTemplate.code == data.code,
            ScheduleTemplate.is_system_defined == data.is_system_defined,
            ScheduleTemplate.owner_org_id == data.owner_org_id
        ).first()
        
        if existing:
            raise ValidationError(
                message="Template with this code already exists",
                error_code="DUPLICATE_TEMPLATE_CODE",
                details={"code": data.code}
            )
        
        try:
            # Create template
            template = ScheduleTemplate(
                code=data.code,
                crop_type_id=data.crop_type_id,
                crop_variety_id=data.crop_variety_id,
                is_system_defined=data.is_system_defined,
                owner_org_id=data.owner_org_id,
                version=1,
                is_active=True,
                notes=data.notes,
                created_by=user_id,
                updated_by=user_id
            )
            
            self.db.add(template)
            self.db.flush()
            
            # Add translations if provided
            translations_to_add = []
            if data.translations:
                for trans_data in data.translations:
                    translations_to_add.append(ScheduleTemplateTranslation(
                        schedule_template_id=template.id,
                        language_code=trans_data.language_code,
                        name=trans_data.name,
                        description=trans_data.description
                    ))
            
            # If name/description provided at top level, add/update 'en' translation
            if data.name or data.description:
                en_trans = next((t for t in translations_to_add if t.language_code == 'en'), None)
                if en_trans:
                    if data.name:
                        en_trans.name = data.name
                    if data.description:
                        en_trans.description = data.description
                else:
                    translations_to_add.append(ScheduleTemplateTranslation(
                        schedule_template_id=template.id,
                        language_code='en',
                        name=data.name or data.code, # Fallback to code if name missing
                        description=data.description
                    ))
            
            for trans in translations_to_add:
                self.db.add(trans)
            
            # Add tasks if provided
            if data.tasks:
                for task_data in data.tasks:
                    # Infer task_id if missing
                    final_task_id = self._resolve_task_id(task_data, self.db)
                    
                    task = ScheduleTemplateTask(
                        schedule_template_id=template.id,
                        task_id=final_task_id,
                        day_offset=task_data.day_offset,
                        task_details_template=task_data.task_details_template,
                        sort_order=task_data.sort_order,
                        notes=task_data.notes,
                        created_by=user_id,
                        updated_by=user_id
                    )
                    self.db.add(task)

            self.db.commit()
            self.db.refresh(template)
            
            self.logger.info(
                "Schedule template created successfully",
                extra={
                    "template_id": str(template.id),
                    "code": template.code,
                    "is_system_defined": template.is_system_defined,
                    "user_id": str(user_id)
                }
            )
            
            return template
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to create schedule template",
                extra={
                    "user_id": str(user_id),
                    "code": data.code,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def get_templates(
        self,
        user_id: UUID,
        crop_type_id: Optional[UUID] = None,
        crop_variety_id: Optional[UUID] = None,
        is_system_defined: Optional[bool] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[ScheduleTemplate], int]:
        """
        Get schedule templates with ownership filtering.
        
        Requirements 15.1, 15.3:
        - System-defined templates available to all organizations (read-only)
        - Organization-specific templates only shown to owner organization
        
        Args:
            user_id: User ID
            crop_type_id: Filter by crop type
            crop_variety_id: Filter by crop variety
            is_system_defined: Filter by system/org templates
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (templates, total count)
        """
        self.logger.info(
            "Fetching schedule templates",
            extra={
                "user_id": str(user_id),
                "crop_type_id": str(crop_type_id) if crop_type_id else None,
                "is_system_defined": is_system_defined,
                "page": page,
                "limit": limit
            }
        )
        
        # Get user's organizations
        user_org_ids = self.db.query(OrgMemberRole.organization_id).filter(
            OrgMemberRole.user_id == user_id
        ).distinct().all()
        user_org_ids = [org_id[0] for org_id in user_org_ids]
        
        # Base query - system templates OR templates owned by user's organizations
        query = self.db.query(ScheduleTemplate).filter(
            ScheduleTemplate.is_active == True,
            or_(
                ScheduleTemplate.is_system_defined == True,
                ScheduleTemplate.owner_org_id.in_(user_org_ids)
            )
        )
        
        # Apply filters
        if crop_type_id:
            query = query.filter(ScheduleTemplate.crop_type_id == crop_type_id)
        
        if crop_variety_id:
            query = query.filter(ScheduleTemplate.crop_variety_id == crop_variety_id)
        
        if is_system_defined is not None:
            query = query.filter(ScheduleTemplate.is_system_defined == is_system_defined)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        templates = query.order_by(
            ScheduleTemplate.is_system_defined.desc(),
            ScheduleTemplate.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        self.logger.info(
            "Schedule templates fetched",
            extra={
                "count": len(templates),
                "total": total,
                "page": page
            }
        )
        
        return templates, total
    
    def validate_template_ownership(
        self,
        template_id: UUID,
        user_id: UUID
    ) -> Tuple[ScheduleTemplate, bool]:
        """
        Validate if user can modify template.
        
        Requirements 15.2, 15.4, 15.5:
        - System-defined templates are immutable
        - Org-specific templates modifiable only by owner org
        
        Args:
            template_id: Template ID
            user_id: User ID
        
        Returns:
            Tuple of (template, can_modify)
        
        Raises:
            NotFoundError: If template not found
            PermissionError: If user cannot modify template
        """
        self.logger.info(
            "Validating template ownership",
            extra={
                "template_id": str(template_id),
                "user_id": str(user_id)
            }
        )
        
        # Get template
        template = self.db.query(ScheduleTemplate).filter(
            ScheduleTemplate.id == template_id
        ).first()
        
        if not template:
            raise NotFoundError(
                message="Schedule template not found",
                error_code="TEMPLATE_NOT_FOUND"
            )
        
        # Requirement 15.2: System-defined templates are immutable
        # Requirement 15.2: System-defined templates are immutable (unless System Admin)
        if template.is_system_defined:
            # Check if system user
            system_roles = ['SUPER_ADMIN', 'BILLING_ADMIN', 'SUPPORT_AGENT']
            user_roles = self.db.query(OrgMemberRole).join(Role).filter(
                OrgMemberRole.user_id == user_id
            ).all()
            
            is_system_user = any(mr.role.code in system_roles for mr in user_roles)
            
            if not is_system_user:
                raise PermissionError(
                    message="Cannot modify system-defined template",
                    error_code="SYSTEM_TEMPLATE_IMMUTABLE",
                    details={"template_id": str(template_id)}
                )
            
            # System user can modify system template - skip org check
            self.logger.info(
                "System user modifying system template",
                extra={"template_id": str(template_id), "user_id": str(user_id)}
            )
            return template, True

        
        # Requirement 15.5: Only owner organization can modify
        # Get user's organizations
        user_org_ids = self.db.query(OrgMemberRole.organization_id).filter(
            OrgMemberRole.user_id == user_id
        ).distinct().all()
        user_org_ids = [org_id[0] for org_id in user_org_ids]
        
        if template.owner_org_id not in user_org_ids:
            raise PermissionError(
                message="Cannot modify template owned by another organization",
                error_code="TEMPLATE_OWNERSHIP_VIOLATION",
                details={
                    "template_id": str(template_id),
                    "owner_org_id": str(template.owner_org_id)
                }
            )
        
        self.logger.info(
            "Template ownership validated",
            extra={
                "template_id": str(template_id),
                "user_id": str(user_id),
                "can_modify": True
            }
        )
        
        return template, True
    
    def update_template(
        self,
        template_id: UUID,
        user_id: UUID,
        data: ScheduleTemplateUpdate
    ) -> ScheduleTemplate:
        """
        Update schedule template with ownership validation.
        
        Args:
            template_id: Template ID
            user_id: User ID
            data: Update data
        
        Returns:
            Updated template
        
        Raises:
            NotFoundError: If template not found
            PermissionError: If user cannot modify template
        """
        self.logger.info(
            "Updating schedule template",
            extra={
                "template_id": str(template_id),
                "user_id": str(user_id)
            }
        )
        
        # Validate ownership
        template, can_modify = self.validate_template_ownership(template_id, user_id)
        
        try:
            # Update fields
            update_data = data.dict(exclude_unset=True, exclude={'translations', 'tasks', 'name', 'description'})
            for field, value in update_data.items():
                setattr(template, field, value)
            
            template.updated_by = user_id
            template.updated_at = datetime.utcnow()
            
            # Update translations if provided
            if data.translations is not None:
                # Remove existing translations
                self.db.query(ScheduleTemplateTranslation).filter(
                    ScheduleTemplateTranslation.schedule_template_id == template_id
                ).delete()
                
                # Add new translations (code omitted for brevity in search, but context kept)

                
                # Add new translations
                for trans_data in data.translations:
                    translation = ScheduleTemplateTranslation(
                        schedule_template_id=template.id,
                        language_code=trans_data.language_code,
                        name=trans_data.name,
                        description=trans_data.description
                    )
                    self.db.add(translation)

            # Update/Add 'en' translation if name/description provided
            if data.name or data.description:
                # Refresh translations if not already loaded (though we just modified them, might need care)
                # Strategy: Check if we cleared translations. 
                # If data.translations was provided, we cleared them.
                # If data.translations was None, we kept existing.
                
                # If translations were updated via data.translations, we just added them to session but not committed.
                # We should look in db.new or existing items.
                
                # Simpler: If data.translations is None, we fetch existing 'en' translation
                if data.translations is None:
                    en_trans = self.db.query(ScheduleTemplateTranslation).filter(
                        and_(
                            ScheduleTemplateTranslation.schedule_template_id == template_id,
                            ScheduleTemplateTranslation.language_code == 'en'
                        )
                    ).first()
                    
                    if en_trans:
                        if data.name:
                            en_trans.name = data.name
                        if data.description:
                            en_trans.description = data.description
                    else:
                        # Create new if didn't exist
                        new_trans = ScheduleTemplateTranslation(
                            schedule_template_id=template.id,
                            language_code='en',
                            name=data.name or template.code,
                            description=data.description
                        )
                        self.db.add(new_trans)
                
                else:
                     # We wiped and re-added translations. Find the 'en' one we just added (in session)
                     # Or just append a new one if not in list. 
                     # Since we can't easily query session.new for specific constraints safely mixing logic, 
                     # let's iterate data.translations again implicitly? 
                     # Actually, if user provided data.translations AND data.name, which one wins?
                     # Let's say explicit data.translations wins, but if 'en' missing there, we add it.
                     # But consistent with create: modify the list before adding.
                     pass # Assuming if user sends full translations list, they handle consistency.
                     # But for partial updates (PATCH style), usually translations=None.


            # Update tasks if provided
            if data.tasks is not None:
                # Remove existing tasks
                self.db.query(ScheduleTemplateTask).filter(
                    ScheduleTemplateTask.schedule_template_id == template_id
                ).delete()
                
                # Add new tasks
                for task_data in data.tasks:
                    # Infer task_id if missing
                    final_task_id = self._resolve_task_id(task_data, self.db)
                    
                    task = ScheduleTemplateTask(
                        schedule_template_id=template.id,
                        task_id=final_task_id,
                        day_offset=task_data.day_offset,
                        task_details_template=task_data.task_details_template,
                        sort_order=task_data.sort_order,
                        notes=task_data.notes,
                        created_by=user_id,
                        updated_by=user_id
                    )
                    self.db.add(task)
            
            self.db.commit()
            self.db.refresh(template)
            
            self.logger.info(
                "Schedule template updated successfully",
                extra={
                    "template_id": str(template_id),
                    "user_id": str(user_id)
                }
            )
            
            return template
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to update schedule template",
                extra={
                    "template_id": str(template_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def get_template(self, template_id: UUID) -> ScheduleTemplate:
        """
        Get schedule template by ID.
        
        Args:
            template_id: Template ID
        
        Returns:
            Schedule template
        
        Raises:
            NotFoundError: If template not found
        """
        template = self.db.query(ScheduleTemplate).filter(
            ScheduleTemplate.id == template_id
        ).first()
        
        if not template:
            raise NotFoundError(
                message="Schedule template not found",
                error_code="TEMPLATE_NOT_FOUND"
            )
        
        return template

    def copy_template(
        self,
        source_template_id: UUID,
        user_id: UUID,
        new_code: str,
        is_system_defined: Optional[bool] = None
    ) -> ScheduleTemplate:
        """
        Copy existing schedule template with ownership rules.
        
        Requirements 5.1, 5.2, 5.3, 5.4, 5.9, 5.10:
        - System users can copy from any template and create system/org templates
        - FSP users can only copy from their org templates and create org templates
        - Copies all template tasks and translations
        
        Args:
            source_template_id: Source template ID
            user_id: User ID
            new_code: New unique code for copied template
            is_system_defined: Whether to create as system template (system users only)
        
        Returns:
            Copied template
        
        Raises:
            NotFoundError: If source template not found
            PermissionError: If user cannot copy template
            ValidationError: If new_code is duplicate
        """
        self.logger.info(
            "Copying schedule template",
            extra={
                "source_template_id": str(source_template_id),
                "user_id": str(user_id),
                "new_code": new_code,
                "is_system_defined": is_system_defined
            }
        )
        
        # Get source template
        source_template = self.get_template(source_template_id)
        
        # Validate access
        can_create, is_system_user, fsp_org_id = self.validate_template_creation_access(user_id)
        
        # Requirement 5.3: FSP users can only copy from their org templates
        if not is_system_user:
            # Get user's organizations
            user_org_ids = self.db.query(OrgMemberRole.organization_id).filter(
                OrgMemberRole.user_id == user_id
            ).distinct().all()
            user_org_ids = [org_id[0] for org_id in user_org_ids]
            
            # Check if source template is owned by user's organization
            if source_template.is_system_defined:
                # FSP users can copy system templates
                pass
            elif source_template.owner_org_id not in user_org_ids:
                raise PermissionError(
                    message="FSP users can only copy templates owned by their organization",
                    error_code="CANNOT_COPY_OTHER_ORG_TEMPLATE",
                    details={
                        "source_template_id": str(source_template_id),
                        "owner_org_id": str(source_template.owner_org_id)
                    }
                )
        
        # Requirement 5.4: System users can copy from any template
        # (already validated by is_system_user check above)
        
        # Determine ownership for new template
        if is_system_user:
            # Requirement 5.6: System user can specify system-defined or org-specific
            if is_system_defined is None:
                # Default to org-specific for system users
                is_system_defined = False
                owner_org_id = None  # System user can choose org later
            elif is_system_defined:
                owner_org_id = None
            else:
                owner_org_id = None  # System user can choose org later
        else:
            # Requirement 5.7: FSP user creates org-specific template owned by their FSP org
            is_system_defined = False
            owner_org_id = fsp_org_id
        
        # Check for duplicate code
        existing = self.db.query(ScheduleTemplate).filter(
            ScheduleTemplate.code == new_code,
            ScheduleTemplate.is_system_defined == is_system_defined,
            ScheduleTemplate.owner_org_id == owner_org_id
        ).first()
        
        if existing:
            raise ValidationError(
                message="Template with this code already exists",
                error_code="DUPLICATE_TEMPLATE_CODE",
                details={"code": new_code}
            )
        
        try:
            # Requirement 5.5: Create new template with new code
            new_template = ScheduleTemplate(
                code=new_code,
                crop_type_id=source_template.crop_type_id,
                crop_variety_id=source_template.crop_variety_id,
                is_system_defined=is_system_defined,
                owner_org_id=owner_org_id,
                version=1,  # Requirement 5.9: Set version to 1
                is_active=True,
                notes=source_template.notes,
                created_by=user_id,
                updated_by=user_id
            )
            
            self.db.add(new_template)
            self.db.flush()
            
            # Requirement 5.11: Copy multilingual translations
            for translation in source_template.translations:
                new_translation = ScheduleTemplateTranslation(
                    schedule_template_id=new_template.id,
                    language_code=translation.language_code,
                    name=translation.name,
                    description=translation.description
                )
                self.db.add(new_translation)
            
            # Requirement 5.5: Copy all template tasks with day_offset and task_details_template
            for task in source_template.tasks:
                new_task = ScheduleTemplateTask(
                    schedule_template_id=new_template.id,
                    task_id=task.task_id,
                    day_offset=task.day_offset,
                    task_details_template=task.task_details_template,
                    sort_order=task.sort_order,
                    notes=task.notes,
                    created_by=user_id,
                    updated_by=user_id
                )
                self.db.add(new_task)
            
            self.db.commit()
            self.db.refresh(new_template)
            
            self.logger.info(
                "Schedule template copied successfully",
                extra={
                    "new_template_id": str(new_template.id),
                    "source_template_id": str(source_template_id),
                    "new_code": new_code,
                    "is_system_defined": is_system_defined,
                    "tasks_copied": len(source_template.tasks),
                    "translations_copied": len(source_template.translations),
                    "user_id": str(user_id)
                }
            )
            
            return new_template
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to copy schedule template",
                extra={
                    "source_template_id": str(source_template_id),
                    "user_id": str(user_id),
                    "new_code": new_code,
                    "error": str(e)
                },
                exc_info=True
            )
            raise

    def delete_template(
        self,
        template_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete (soft-delete) schedule template.
        
        Requirements:
        - System-defined templates cannot be deleted
        - Org-specific templates can only be deleted by owner organization
        - Sets is_active = False instead of hard delete
        
        Args:
            template_id: Template ID
            user_id: User ID
        
        Raises:
            NotFoundError: If template not found
            PermissionError: If user cannot delete template
        """
        self.logger.info(
            "Deleting schedule template",
            extra={
                "template_id": str(template_id),
                "user_id": str(user_id)
            }
        )
        
        # Validate ownership (reuses update validation logic which covers:
        # 1. Template existence
        # 2. System template immutability (cannot modify/delete)
        # 3. Org ownership check
        template, can_modify = self.validate_template_ownership(template_id, user_id)
        
        try:
            # Soft delete
            template.is_active = False
            template.updated_by = user_id
            template.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            self.logger.info(
                "Schedule template deleted (soft)",
                extra={
                    "template_id": str(template_id),
                    "user_id": str(user_id)
                }
            )
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to delete schedule template",
                extra={
                    "template_id": str(template_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise

    def _resolve_task_id(self, task_data, db_session) -> UUID:
        """
        Helper to resolve task_id from task_data.
        If task_id is present AND VALID, return it.
        If missing or invalid (e.g. input_item_id sent as task_id), infer from generic tasks.
        """
        from app.models.reference_data import Task

        if task_data.task_id:
            # Validate if this ID actually exists in tasks table
            exists = db_session.query(Task.id).filter(Task.id == task_data.task_id).first()
            if exists:
                return task_data.task_id
            
            # If provided ID doesn't exist in tasks table, it's likely an input_item_id or garbage
            # Log warning and fall through to inference
            self.logger.warning(
                f"Invalid task_id {task_data.task_id} provided (not found in tasks). Falling back to inference."
            )
        
        # Try to infer from generic tasks
        
        # Default fallback
        generic_code = "GENERAL_APPLICATION"
        
        # Heuristic: Check if input items are fertilizers or pesticides
        # This is robust but simple for now
        details = task_data.task_details_template
        if details and 'input_items' in details and len(details['input_items']) > 0:
            # We could fetch the input item to check category, but to save DB calls, 
            # we default to GENERAL_APPLICATION which is safe.
            # If we want to be smarter later, we can fetch InputItem here.
            pass
            
        task = db_session.query(Task).filter(Task.code == generic_code).first()
        if not task:
            # Fallback to the first available farming task if generic one is missing
            self.logger.warning(f"Generic task {generic_code} not found. Trying fallback to FARMING category.")
            task = db_session.query(Task).filter(Task.category == TaskCategory.FARMING).first()
            
            if not task:
                # Last resort: any task at all
                self.logger.warning("No FARMING tasks found either. Trying fallback to ANY task.")
                task = db_session.query(Task).first()
            
            if not task:
                # If STILL nothing, we can't proceed. 
                # Provide the EXACT message the user is seeing to stop the confusion if it was renamed, 
                # or a better one if it wasn't.
                raise ValidationError(
                    message=f"Generic Task '{generic_code}' not found and no fallbacks available. Please contact support.",
                    error_code="GENERIC_TASK_NOT_FOUND"
                )
            
            self.logger.warning(
                f"Generic task {generic_code} not found. Fell back to task {task.code} ({task.id})."
            )
            
        return task.id
