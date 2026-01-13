"""
Role service for Uzhathunai v2.0.
Handles role retrieval and filtering by organization type.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.rbac import Role
from app.models.enums import OrganizationType
from app.core.logging import get_logger
from app.core.exceptions import NotFoundError

logger = get_logger(__name__)


class RoleService:
    """Service for role management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
    
    def get_roles(self, org_type: Optional[OrganizationType] = None) -> List[Role]:
        """
        Get roles filtered by organization type.
        Used for populating role selectors in UI.
        
        Args:
            org_type: Optional organization type to filter roles
        
        Returns:
            List of roles
        """
        self.logger.info(
            "Fetching roles",
            extra={
                "org_type": org_type.value if org_type else None
            }
        )
        
        query = self.db.query(Role).filter(Role.is_active == True)
        
        if org_type == OrganizationType.FARMING:
            # FARMING roles: OWNER, ADMIN, SUPERVISOR, MEMBER
            query = query.filter(Role.code.in_(['OWNER', 'ADMIN', 'SUPERVISOR', 'MEMBER']))
        elif org_type == OrganizationType.FSP:
            # FSP roles: FSP_OWNER, FSP_ADMIN, FSP_CONSULTANT
            query = query.filter(Role.code.in_(['FSP_OWNER', 'FSP_ADMIN', 'FSP_CONSULTANT']))
        
        roles = query.order_by(Role.name).all()
        
        self.logger.info(
            "Roles fetched",
            extra={
                "org_type": org_type.value if org_type else None,
                "count": len(roles)
            }
        )
        
        return roles
    
    def get_role(self, role_id: UUID) -> Role:
        """
        Get role by ID.
        
        Args:
            role_id: Role ID
        
        Returns:
            Role
        
        Raises:
            NotFoundError: If role not found
        """
        self.logger.info(
            "Fetching role",
            extra={"role_id": str(role_id)}
        )
        
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise NotFoundError(
                message=f"Role {role_id} not found",
                error_code="ROLE_NOT_FOUND",
                details={"role_id": str(role_id)}
            )
        
        return role
