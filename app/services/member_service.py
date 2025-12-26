"""
Member service for Uzhathunai v2.0.
Handles organization member management including multiple roles support.
"""
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.organization import OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.user import User
from app.models.enums import MemberStatus
from app.schemas.member import UpdateMemberRolesRequest, MemberResponse
from app.core.logging import get_logger
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    PermissionError
)

logger = get_logger(__name__)


class MemberService:
    """Service for member management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
    
    def get_members(
        self,
        org_id: UUID,
        user_id: UUID,
        role_filter: Optional[UUID] = None,
        status_filter: Optional[MemberStatus] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[dict], int]:
        """
        Get organization members with filtering and pagination.
        
        Args:
            org_id: Organization ID
            user_id: User ID (for access control)
            role_filter: Optional filter by role ID
            status_filter: Optional filter by member status
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (members list, total count)
        
        Raises:
            PermissionError: If user is not a member
        """
        self.logger.info(
            "Fetching organization members",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id),
                "role_filter": str(role_filter) if role_filter else None,
                "status_filter": status_filter.value if status_filter else None,
                "page": page,
                "limit": limit
            }
        )
        
        # Check if user is a member
        self._check_membership(org_id, user_id)
        
        # Build query with User join
        query = self.db.query(OrgMember, User).join(
            User, OrgMember.user_id == User.id
        ).filter(
            OrgMember.organization_id == org_id
        )
        
        # Apply filters
        if status_filter:
            query = query.filter(OrgMember.status == status_filter)
        
        if role_filter:
            query = query.join(OrgMemberRole).filter(
                OrgMemberRole.role_id == role_filter
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        results = query.order_by(OrgMember.joined_at.desc()).offset(offset).limit(limit).all()
        
        # Format response with roles and user details
        members_data = []
        for member, user in results:
            # Get all roles for this member
            member_roles = self.db.query(OrgMemberRole).join(Role).filter(
                OrgMemberRole.user_id == member.user_id,
                OrgMemberRole.organization_id == org_id
            ).all()
            
            roles_data = [
                {
                    "role_id": str(mr.role_id),
                    "role_name": mr.role.name,
                    "role_code": mr.role.code,
                    "is_primary": mr.is_primary
                }
                for mr in member_roles
            ]
            
            members_data.append({
                "id": str(member.id),
                "user_id": str(member.user_id),
                "organization_id": str(member.organization_id),
                "status": member.status.value,
                "roles": roles_data,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "user_name": user.full_name if user.full_name else None,
                "user_email": user.email
            })
        
        self.logger.info(
            "Organization members fetched",
            extra={
                "org_id": str(org_id),
                "count": len(members_data),
                "total": total
            }
        )
        
        return members_data, total
    
    def update_member_roles(
        self,
        org_id: UUID,
        current_user_id: UUID,
        target_user_id: UUID,
        data: UpdateMemberRolesRequest
    ) -> dict:
        """
        Update member roles (supports multiple roles).
        
        Args:
            org_id: Organization ID
            current_user_id: User ID performing the update
            target_user_id: User ID whose roles are being updated
            data: Role update data
        
        Returns:
            Updated member data
        
        Raises:
            PermissionError: If user doesn't have permission
            ValidationError: If trying to change OWNER role or own role
        """
        self.logger.info(
            "Updating member roles",
            extra={
                "org_id": str(org_id),
                "current_user_id": str(current_user_id),
                "target_user_id": str(target_user_id),
                "new_roles_count": len(data.roles)
            }
        )
        
        # Check if current user has admin permission
        self._check_admin_permission(org_id, current_user_id)
        
        # Cannot change own role
        if current_user_id == target_user_id:
            raise ValidationError(
                message="Cannot change your own role",
                error_code="CANNOT_CHANGE_OWN_ROLE"
            )
        
        # Get target member
        member = self.db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == target_user_id
        ).first()
        
        if not member:
            raise NotFoundError(
                message="Member not found",
                error_code="MEMBER_NOT_FOUND",
                details={"user_id": str(target_user_id)}
            )
        
        # Get current roles
        current_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.organization_id == org_id,
            OrgMemberRole.user_id == target_user_id
        ).all()
        
        # Check if trying to change OWNER/FSP_OWNER role
        owner_roles = ['OWNER', 'FSP_OWNER']
        has_owner_role = any(mr.role.code in owner_roles for mr in current_roles)
        
        if has_owner_role:
            raise ValidationError(
                message="Cannot change OWNER role",
                error_code="CANNOT_CHANGE_OWNER_ROLE"
            )
        
        try:
            # Delete existing roles
            for role in current_roles:
                self.db.delete(role)
            
            # Flush to ensure deletions are committed before inserts
            # This prevents unique constraint violations when updating roles
            self.db.flush()
            
            # Create new roles
            for role_data in data.roles:
                # Verify role exists
                role = self.db.query(Role).filter(Role.id == role_data.role_id).first()
                if not role:
                    raise NotFoundError(
                        message=f"Role {role_data.role_id} not found",
                        error_code="ROLE_NOT_FOUND"
                    )
                
                # Cannot assign OWNER/FSP_OWNER role
                if role.code in owner_roles:
                    raise ValidationError(
                        message="Cannot assign OWNER role",
                        error_code="CANNOT_ASSIGN_OWNER_ROLE"
                    )
                
                member_role = OrgMemberRole(
                    user_id=target_user_id,
                    organization_id=org_id,
                    role_id=role_data.role_id,
                    is_primary=role_data.is_primary,
                    assigned_at=datetime.utcnow(),
                    assigned_by=current_user_id
                )
                self.db.add(member_role)
            
            self.db.commit()
            
            self.logger.info(
                "Member roles updated successfully",
                extra={
                    "org_id": str(org_id),
                    "target_user_id": str(target_user_id),
                    "updated_by": str(current_user_id),
                    "new_roles_count": len(data.roles),
                    "reason": data.reason
                }
            )
            
            # Return updated member data
            return self._get_member_data(org_id, target_user_id)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to update member roles",
                extra={
                    "org_id": str(org_id),
                    "target_user_id": str(target_user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def update_member_status(
        self,
        org_id: UUID,
        current_user_id: UUID,
        target_user_id: UUID,
        status: MemberStatus,
        reason: Optional[str] = None
    ) -> dict:
        """
        Update member status.
        
        Args:
            org_id: Organization ID
            current_user_id: User ID performing the update
            target_user_id: User ID whose status is being updated
            status: New status
            reason: Optional reason for status change
        
        Returns:
            Updated member data
        
        Raises:
            PermissionError: If user doesn't have permission
            ValidationError: If trying to change OWNER status or own status
        """
        self.logger.info(
            "Updating member status",
            extra={
                "org_id": str(org_id),
                "current_user_id": str(current_user_id),
                "target_user_id": str(target_user_id),
                "new_status": status.value,
                "reason": reason
            }
        )
        
        # Check if current user has admin permission
        self._check_admin_permission(org_id, current_user_id)
        
        # Cannot change own status
        if current_user_id == target_user_id:
            raise ValidationError(
                message="Cannot change your own status",
                error_code="CANNOT_CHANGE_OWN_STATUS"
            )
        
        # Get target member
        member = self.db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == target_user_id
        ).first()
        
        if not member:
            raise NotFoundError(
                message="Member not found",
                error_code="MEMBER_NOT_FOUND",
                details={"user_id": str(target_user_id)}
            )
        
        # Check if member has OWNER role
        member_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.organization_id == org_id,
            OrgMemberRole.user_id == target_user_id
        ).all()
        
        owner_roles = ['OWNER', 'FSP_OWNER']
        has_owner_role = any(mr.role.code in owner_roles for mr in member_roles)
        
        if has_owner_role:
            raise ValidationError(
                message="Cannot change OWNER status",
                error_code="CANNOT_CHANGE_OWNER_STATUS"
            )
        
        try:
            # Update status
            member.status = status
            
            self.db.commit()
            
            self.logger.info(
                "Member status updated successfully",
                extra={
                    "org_id": str(org_id),
                    "target_user_id": str(target_user_id),
                    "updated_by": str(current_user_id),
                    "new_status": status.value,
                    "reason": reason
                }
            )
            
            # Return updated member data
            return self._get_member_data(org_id, target_user_id)
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to update member status",
                extra={
                    "org_id": str(org_id),
                    "target_user_id": str(target_user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def remove_member(
        self,
        org_id: UUID,
        current_user_id: UUID,
        target_user_id: UUID,
        reason: Optional[str] = None
    ) -> bool:
        """
        Remove member from organization.
        
        Args:
            org_id: Organization ID
            current_user_id: User ID performing the removal
            target_user_id: User ID to remove
            reason: Optional reason for removal
        
        Returns:
            True if successful
        
        Raises:
            PermissionError: If user doesn't have permission
            ValidationError: If trying to remove OWNER or self
        """
        self.logger.info(
            "Removing member",
            extra={
                "org_id": str(org_id),
                "current_user_id": str(current_user_id),
                "target_user_id": str(target_user_id),
                "reason": reason
            }
        )
        
        # Check if current user has admin permission
        self._check_admin_permission(org_id, current_user_id)
        
        # Cannot remove self
        if current_user_id == target_user_id:
            raise ValidationError(
                message="Cannot remove yourself",
                error_code="CANNOT_REMOVE_SELF"
            )
        
        # Get target member
        member = self.db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == target_user_id
        ).first()
        
        if not member:
            raise NotFoundError(
                message="Member not found",
                error_code="MEMBER_NOT_FOUND",
                details={"user_id": str(target_user_id)}
            )
        
        # Check if member has OWNER role
        member_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.organization_id == org_id,
            OrgMemberRole.user_id == target_user_id
        ).all()
        
        owner_roles = ['OWNER', 'FSP_OWNER']
        has_owner_role = any(mr.role.code in owner_roles for mr in member_roles)
        
        if has_owner_role:
            raise ValidationError(
                message="Cannot remove OWNER",
                error_code="CANNOT_REMOVE_OWNER"
            )
        
        try:
            # Delete member roles
            for role in member_roles:
                self.db.delete(role)
            
            # Delete member
            self.db.delete(member)
            
            self.db.commit()
            
            self.logger.info(
                "Member removed successfully",
                extra={
                    "org_id": str(org_id),
                    "target_user_id": str(target_user_id),
                    "removed_by": str(current_user_id),
                    "reason": reason
                }
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to remove member",
                extra={
                    "org_id": str(org_id),
                    "target_user_id": str(target_user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def _check_membership(self, org_id: UUID, user_id: UUID):
        """
        Check if user is a member of organization.
        
        Args:
            org_id: Organization ID
            user_id: User ID
        
        Raises:
            PermissionError: If user is not a member
        """
        member = self.db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        if not member:
            raise PermissionError(
                message="You are not a member of this organization",
                error_code="NOT_A_MEMBER",
                details={"org_id": str(org_id)}
            )
    
    def _check_admin_permission(self, org_id: UUID, user_id: UUID):
        """
        Check if user has admin permission (OWNER/ADMIN).
        
        Args:
            org_id: Organization ID
            user_id: User ID
        
        Raises:
            PermissionError: If user doesn't have permission
        """
        # Get user's roles in organization
        member_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.organization_id == org_id,
            OrgMemberRole.user_id == user_id
        ).all()
        
        if not member_roles:
            raise PermissionError(
                message="You are not a member of this organization",
                error_code="NOT_A_MEMBER",
                details={"org_id": str(org_id)}
            )
        
        # Check if user has OWNER or ADMIN role
        admin_roles = ['OWNER', 'ADMIN', 'FSP_OWNER', 'FSP_ADMIN']
        has_admin = any(mr.role.code in admin_roles for mr in member_roles)
        
        if not has_admin:
            raise PermissionError(
                message="You don't have permission to perform this action",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={"org_id": str(org_id), "required_roles": admin_roles}
            )
    
    def _get_member_data(self, org_id: UUID, user_id: UUID) -> dict:
        """
        Get member data with roles and user details.
        
        Args:
            org_id: Organization ID
            user_id: User ID
        
        Returns:
            Member data dictionary
        """
        result = self.db.query(OrgMember, User).join(
            User, OrgMember.user_id == User.id
        ).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == user_id
        ).first()
        
        if not result:
            raise NotFoundError(
                message="Member not found",
                error_code="MEMBER_NOT_FOUND"
            )
        
        member, user = result
        
        # Get all roles for this member
        member_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.user_id == user_id,
            OrgMemberRole.organization_id == org_id
        ).all()
        
        roles_data = [
            {
                "role_id": str(mr.role_id),
                "role_name": mr.role.name,
                "role_code": mr.role.code,
                "is_primary": mr.is_primary
            }
            for mr in member_roles
        ]
        
        return {
            "id": str(member.id),
            "user_id": str(member.user_id),
            "organization_id": str(member.organization_id),
            "status": member.status.value,
            "roles": roles_data,
            "joined_at": member.joined_at.isoformat() if member.joined_at else None,
            "user_name": user.full_name if user.full_name else None,
            "user_email": user.email
        }
