"""
Audit ownership validation utilities for Farm Audit Management System.
Enforces system vs organization ownership rules.
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.exceptions import PermissionError
from app.models.user import User


def validate_system_entity_modification(
    is_system_defined: bool,
    user: User,
    entity_type: str
) -> None:
    """
    Validate that system-defined entities cannot be modified by org users.
    
    Requirement 19.1: Prevent modification of system-defined entities by organization users
    
    Args:
        is_system_defined: Whether entity is system-defined
        user: Current user
        entity_type: Type of entity (e.g., "template", "parameter", "section")
    
    Raises:
        PermissionError: If org user attempts to modify system entity
    """
    if is_system_defined and not is_system_user(user):
        raise PermissionError(
            message=f"Cannot modify system-defined {entity_type}. System entities are read-only for organization users.",
            error_code="SYSTEM_ENTITY_MODIFICATION_DENIED",
            details={
                "entity_type": entity_type,
                "user_id": str(user.id),
                "is_system_defined": True
            }
        )


def validate_organization_ownership(
    owner_org_id: Optional[UUID],
    user_org_id: UUID,
    entity_type: str,
    entity_id: UUID
) -> None:
    """
    Validate that user can only modify entities owned by their organization.
    
    Requirement 19.3: Prevent cross-organization modifications
    
    Args:
        owner_org_id: Organization that owns the entity
        user_org_id: User's organization
        entity_type: Type of entity (e.g., "template", "parameter", "section")
        entity_id: Entity ID
    
    Raises:
        PermissionError: If user attempts to modify another org's entity
    """
    if owner_org_id and owner_org_id != user_org_id:
        raise PermissionError(
            message=f"Cannot modify {entity_type} owned by another organization",
            error_code="CROSS_ORGANIZATION_MODIFICATION_DENIED",
            details={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "owner_org_id": str(owner_org_id),
                "user_org_id": str(user_org_id)
            }
        )


def validate_entity_modification(
    is_system_defined: bool,
    owner_org_id: Optional[UUID],
    user: User,
    user_org_id: UUID,
    entity_type: str,
    entity_id: UUID
) -> None:
    """
    Comprehensive validation for entity modification.
    Combines system entity and ownership checks.
    
    Requirements:
    - 19.1: Prevent modification of system-defined entities by org users
    - 19.2: Allow system users to modify any entity
    - 19.3: Prevent cross-organization modifications
    
    Args:
        is_system_defined: Whether entity is system-defined
        owner_org_id: Organization that owns the entity
        user: Current user
        user_org_id: User's organization
        entity_type: Type of entity
        entity_id: Entity ID
    
    Raises:
        PermissionError: If modification is not allowed
    """
    # System users can modify anything (Requirement 19.2)
    if is_system_user(user):
        return
    
    # Check system entity modification (Requirement 19.1)
    validate_system_entity_modification(is_system_defined, user, entity_type)
    
    # Check organization ownership (Requirement 19.3)
    validate_organization_ownership(owner_org_id, user_org_id, entity_type, entity_id)


def validate_copy_permission(
    source_is_system: bool,
    source_owner_org_id: Optional[UUID],
    user: User,
    user_org_id: UUID,
    has_consultancy: bool,
    entity_type: str
) -> None:
    """
    Validate permission to copy entity.
    
    Requirements:
    - System users can copy any entity
    - Org users with consultancy can copy only their own org's entities
    - Regular org users cannot copy
    
    Args:
        source_is_system: Whether source entity is system-defined
        source_owner_org_id: Organization that owns source entity
        user: Current user
        user_org_id: User's organization
        has_consultancy: Whether user's org has consultancy service
        entity_type: Type of entity
    
    Raises:
        PermissionError: If copy is not allowed
    """
    # System users can copy anything
    if is_system_user(user):
        return
    
    # Org users with consultancy service
    if has_consultancy:
        # Can only copy from own organization
        if source_owner_org_id and source_owner_org_id != user_org_id:
            raise PermissionError(
                message=f"Can only copy {entity_type} from your own organization",
                error_code="CROSS_ORGANIZATION_COPY_DENIED",
                details={
                    "entity_type": entity_type,
                    "source_owner_org_id": str(source_owner_org_id),
                    "user_org_id": str(user_org_id)
                }
            )
        return
    
    # Regular org users cannot copy
    raise PermissionError(
        message=f"Insufficient permissions to copy {entity_type}. Consultancy service required.",
        error_code="COPY_PERMISSION_DENIED",
        details={
            "entity_type": entity_type,
            "user_org_id": str(user_org_id),
            "has_consultancy": False
        }
    )


def is_system_user(user: User) -> bool:
    """
    Check if user is a system user (SUPER_ADMIN).
    
    Args:
        user: Current user
    
    Returns:
        True if user is system user, False otherwise
    """
    # Check if user has is_superuser attribute
    return getattr(user, 'is_superuser', False)


def get_user_organization_type(db: Session, organization_id: UUID) -> str:
    """
    Get organization type (FARMING or FSP).
    
    Args:
        db: Database session
        organization_id: Organization ID
    
    Returns:
        Organization type
    """
    from app.models.organization import Organization
    
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise PermissionError(
            message="Organization not found",
            error_code="ORGANIZATION_NOT_FOUND",
            details={"organization_id": str(organization_id)}
        )
    
    return org.organization_type.value


def check_consultancy_service(db: Session, organization_id: UUID) -> bool:
    """
    Check if organization has consultancy service enabled.
    
    Args:
        db: Database session
        organization_id: Organization ID
    
    Returns:
        True if consultancy service is enabled, False otherwise
    """
    from app.models.fsp_service import FSPService
    from app.models.enums import ServiceStatus
    
    # Check if organization has active consultancy service
    service = db.query(FSPService).filter(
        FSPService.fsp_organization_id == organization_id,
        FSPService.status == ServiceStatus.ACTIVE
    ).first()
    
    # For now, we'll assume any active FSP service includes consultancy
    # In production, you might want to check specific service types
    return service is not None


def validate_audit_access(
    db: Session,
    audit_fsp_org_id: UUID,
    audit_farming_org_id: UUID,
    user: User,
    user_org_id: UUID
) -> None:
    """
    Validate that user has access to audit.
    
    Args:
        db: Database session
        audit_fsp_org_id: FSP organization that created the audit
        audit_farming_org_id: Farming organization being audited
        user: Current user
        user_org_id: User's organization
    
    Raises:
        PermissionError: If user doesn't have access to audit
    """
    # System users have access to all audits
    if is_system_user(user):
        return
    
    # User must be from either FSP org or farming org
    if user_org_id not in [audit_fsp_org_id, audit_farming_org_id]:
        raise PermissionError(
            message="User does not have access to this audit",
            error_code="AUDIT_ACCESS_DENIED",
            details={
                "user_id": str(user.id),
                "user_org_id": str(user_org_id),
                "audit_fsp_org_id": str(audit_fsp_org_id),
                "audit_farming_org_id": str(audit_farming_org_id)
            }
        )
