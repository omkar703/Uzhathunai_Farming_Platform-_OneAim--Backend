"""
Section service for managing sections with ownership validation.
Supports system-defined and organization-specific sections for Farm Audit Management.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, PermissionError, ValidationError
from app.models.section import Section, SectionTranslation
from app.schemas.section import (
    SectionCreate, SectionUpdate, SectionResponse, SectionDetailResponse,
    SectionTranslationResponse
)

logger = get_logger(__name__)


class SectionService:
    """Service for section operations with ownership validation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_sections(
        self,
        org_id: Optional[UUID],
        language: str = "en",
        include_system: bool = True,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[SectionResponse], int]:
        """
        Get sections (system-defined and org-specific).
        
        Args:
            org_id: Organization ID
            language: Language code for translations (default: en)
            include_system: Include system-defined sections (default: True)
            
        Returns:
            List of sections
        """
        from sqlalchemy.orm import joinedload
        
        query = self.db.query(Section).filter(
            Section.is_active == True
        ).options(
            joinedload(Section.translations)
        )
        
        # Filter by ownership
        if include_system:
            # Include both system-defined and org-specific
            if org_id:
                query = query.filter(
                    or_(
                        Section.is_system_defined == True,
                        Section.owner_org_id == org_id
                    )
                )
            # If org_id is None (Systems Admin), no need to filter further as we want everything
            # or maybe just system defined? Usually admin sees all.
            # But based on the request, let's keep it simple.
        else:
            # Only org-specific
            if org_id:
                query = query.filter(
                    and_(
                        Section.is_system_defined == False,
                        Section.owner_org_id == org_id
                    )
                )
            else:
                 # If org_id is None (Systems Admin) and include_system=False, 
                 # this case might be weird, but let's just return all non-system
                 query = query.filter(Section.is_system_defined == False)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        sections = query.order_by(Section.code).offset(offset).limit(limit).all()
        
        logger.info(
            "Retrieved sections",
            extra={
                "org_id": str(org_id),
                "count": len(sections),
                "total": total,
                "include_system": include_system,
                "language": language,
                "page": page,
                "limit": limit
            }
        )
        
        return [self._to_section_response(section, language) for section in sections], total
    
    def get_section(
        self,
        section_id: UUID,
        org_id: Optional[UUID],
        language: str = "en"
    ) -> SectionDetailResponse:
        """
        Get section by ID with all translations.
        
        Args:
            section_id: Section ID
            org_id: Organization ID
            language: Language code for translations (default: en)
            
        Returns:
            Section with all translations
            
        Raises:
            NotFoundError: If section not found
            PermissionError: If section is not accessible by organization
        """
        from sqlalchemy.orm import joinedload
        
        section = self.db.query(Section).filter(
            Section.id == section_id
        ).options(
            joinedload(Section.translations)
        ).first()
        
        if not section:
            raise NotFoundError(
                message=f"Section {section_id} not found",
                error_code="SECTION_NOT_FOUND",
                details={"section_id": str(section_id)}
            )
        
        # Validate access
        # If org_id is None (Super Admin), allow access
        if org_id:
            if not section.is_system_defined and section.owner_org_id != org_id:
                raise PermissionError(
                    message="Cannot access section owned by another organization",
                    error_code="INSUFFICIENT_PERMISSIONS",
                    details={
                        "section_id": str(section_id),
                        "owner_org_id": str(section.owner_org_id),
                        "requesting_org_id": str(org_id)
                    }
                )
        
        logger.info(
            "Retrieved section",
            extra={
                "section_id": str(section_id),
                "org_id": str(org_id),
                "language": language
            }
        )
        
        return self._to_section_detail_response(section, language)
    
    def create_org_section(
        self,
        data: SectionCreate,
        org_id: Optional[UUID],
        user_id: UUID
    ) -> SectionDetailResponse:
        """
        Create organization-specific section.
        
        Args:
            data: Section creation data
            org_id: Organization ID
            user_id: User ID creating the section
            
        Returns:
            Created section
            
        Raises:
            ValidationError: If section code already exists for organization
        """
        # Check if section code already exists for this org
        if org_id:
            # Org specific duplicate check
            existing = self.db.query(Section).filter(
                and_(
                    Section.code == data.code,
                    Section.owner_org_id == org_id,
                    Section.is_active == True
                )
            ).first()
        else:
            # System defined duplicate check
            existing = self.db.query(Section).filter(
                and_(
                    Section.code == data.code,
                    Section.is_system_defined == True,
                    Section.is_active == True
                )
            ).first()
        
        if existing:
            raise ValidationError(
                message=f"Section with code '{data.code}' already exists",
                error_code="DUPLICATE_SECTION_CODE",
                details={"code": data.code}
            )
        
        # Create section
        is_system = org_id is None
        
        section = Section(
            code=data.code,
            is_system_defined=is_system,
            owner_org_id=org_id,
            is_active=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(section)
        self.db.flush()
        
        # Create translations
        for trans_data in data.translations:
            translation = SectionTranslation(
                section_id=section.id,
                language_code=trans_data['language_code'],
                name=trans_data['name'],
                description=trans_data.get('description')
            )
            self.db.add(translation)
        
        self.db.commit()
        self.db.refresh(section)
        
        logger.info(
            "Created organization-specific section",
            extra={
                "section_id": str(section.id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "code": data.code,
                "translations_count": len(data.translations)
            }
        )
        
        return self._to_section_detail_response(section, "en")
    
    def update_org_section(
        self,
        section_id: UUID,
        data: SectionUpdate,
        org_id: Optional[UUID],
        user_id: UUID
    ) -> SectionDetailResponse:
        """
        Update organization-specific section.
        
        Args:
            section_id: Section ID
            data: Section update data
            org_id: Organization ID
            user_id: User ID updating the section
            
        Returns:
            Updated section
            
        Raises:
            NotFoundError: If section not found
            PermissionError: If section is system-defined or owned by another org
        """
        section = self.db.query(Section).filter(
            Section.id == section_id
        ).first()
        
        if not section:
            raise NotFoundError(
                message=f"Section {section_id} not found",
                error_code="SECTION_NOT_FOUND",
                details={"section_id": str(section_id)}
            )
        
        # Validate ownership
        self._validate_ownership(section, org_id, "update")
        
        # Update fields
        if data.is_active is not None:
            section.is_active = data.is_active
        
        # Update translations
        if data.translations:
            for trans_data in data.translations:
                lang = trans_data['language_code']
                translation = self.db.query(SectionTranslation).filter(
                    and_(
                        SectionTranslation.section_id == section_id,
                        SectionTranslation.language_code == lang
                    )
                ).first()
                
                if translation:
                    translation.name = trans_data['name']
                    if 'description' in trans_data:
                        translation.description = trans_data['description']
                else:
                    translation = SectionTranslation(
                        section_id=section_id,
                        language_code=lang,
                        name=trans_data['name'],
                        description=trans_data.get('description')
                    )
                    self.db.add(translation)
        
        section.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(section)
        
        logger.info(
            "Updated organization-specific section",
            extra={
                "section_id": str(section_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return self._to_section_detail_response(section, "en")
    
    def delete_org_section(
        self,
        section_id: UUID,
        org_id: Optional[UUID],
        user_id: UUID
    ) -> None:
        """
        Delete (soft delete) organization-specific section.
        
        Args:
            section_id: Section ID
            org_id: Organization ID
            user_id: User ID deleting the section
            
        Raises:
            NotFoundError: If section not found
            PermissionError: If section is system-defined or owned by another org
        """
        section = self.db.query(Section).filter(
            Section.id == section_id
        ).first()
        
        if not section:
            raise NotFoundError(
                message=f"Section {section_id} not found",
                error_code="SECTION_NOT_FOUND",
                details={"section_id": str(section_id)}
            )
        
        # Validate ownership
        self._validate_ownership(section, org_id, "delete")
        
        # Soft delete
        section.is_active = False
        section.updated_by = user_id
        
        self.db.commit()
        
        logger.info(
            "Deleted organization-specific section",
            extra={
                "section_id": str(section_id),
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
    
    def _validate_ownership(
        self,
        section: Section,
        org_id: Optional[UUID],
        operation: str
    ) -> None:
        """
        Validate section ownership for modification operations.
        
        Args:
            section: Section to validate
            org_id: Organization ID attempting the operation
            operation: Operation being performed (update/delete)
            
        Raises:
            PermissionError: If section is system-defined or owned by another org
        """
        if org_id is None:
             # System Admin can do anything!
             # Except maybe modifying other org's sections? 
             # Requirement says "Enable System Admin to Create Audit Sections", implies managing system sections.
             # If system admin tries to edit org section, let's allow it for now or check logic.
             # But if they are editing a system section:
             if section.is_system_defined:
                 return # Allow
             
             # If they try to edit org section, they are super admin, so they can.
             return

        if section.is_system_defined:
             raise PermissionError(
                message=f"Cannot {operation} system-defined section",
                error_code="SYSTEM_DEFINED_IMMUTABLE",
                details={
                    "section_id": str(section.id),
                    "operation": operation
                }
            )
        
        if section.owner_org_id != org_id:
            raise PermissionError(
                message=f"Cannot {operation} section owned by another organization",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "section_id": str(section.id),
                    "owner_org_id": str(section.owner_org_id),
                    "requesting_org_id": str(org_id),
                    "operation": operation
                }
            )
    
    def _to_section_response(
        self,
        section: Section,
        language: str
    ) -> SectionResponse:
        """Convert section model to response schema."""
        # Extract translated name and description for requested language
        name = None
        description = None
        
        for t in section.translations:
            if t.language_code == language:
                name = t.name
                description = t.description
                break
        
        # Fallback to English if requested language not found
        if not name:
            for t in section.translations:
                if t.language_code == 'en':
                    name = t.name
                    description = t.description
                    break
        
        # Fallback to code if no translation found
        if not name:
            name = section.code
        
        return SectionResponse(
            id=section.id,
            code=section.code,
            is_system_defined=section.is_system_defined,
            owner_org_id=section.owner_org_id,
            is_active=section.is_active,
            created_at=section.created_at,
            updated_at=section.updated_at,
            created_by=section.created_by,
            updated_by=section.updated_by,
            name=name,
            description=description
        )
    
    def _to_section_detail_response(
        self,
        section: Section,
        language: str
    ) -> SectionDetailResponse:
        """Convert section model to detailed response schema with all translations."""
        # Convert all translations
        translations_list = [
            SectionTranslationResponse(
                id=t.id,
                section_id=t.section_id,
                language_code=t.language_code,
                name=t.name,
                description=t.description,
                created_at=t.created_at
            )
            for t in section.translations
        ]
        
        # Extract translated name and description for requested language
        name = None
        description = None
        
        for t in section.translations:
            if t.language_code == language:
                name = t.name
                description = t.description
                break
        
        # Fallback to English if requested language not found
        if not name:
            for t in section.translations:
                if t.language_code == 'en':
                    name = t.name
                    description = t.description
                    break
        
        # Fallback to code if no translation found
        if not name:
            name = section.code
        
        return SectionDetailResponse(
            id=section.id,
            code=section.code,
            is_system_defined=section.is_system_defined,
            owner_org_id=section.owner_org_id,
            is_active=section.is_active,
            created_at=section.created_at,
            updated_at=section.updated_at,
            created_by=section.created_by,
            updated_by=section.updated_by,
            name=name,
            description=description,
            translations=translations_list
        )
