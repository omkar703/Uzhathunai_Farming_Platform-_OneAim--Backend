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
            
            # Get primary role for top-level display
            primary_role = next((mr for mr in member_roles if mr.is_primary), member_roles[0] if member_roles else None)
            
            # Check if user is owner (has OWNER or FSP_OWNER role)
            is_owner = any(mr.role.code in ['OWNER', 'FSP_OWNER'] for mr in member_roles)
            
            members_data.append({
                "id": str(member.id),
                "user_id": str(member.user_id),
                "organization_id": str(member.organization_id),
                "status": member.status.value,
                "roles": roles_data,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "user_name": user.full_name if user.full_name else None,
                "user_email": user.email,
                # Top-level role info for easy frontend access
                "role_id": str(primary_role.role_id) if primary_role else None,
                "role_name": primary_role.role.code if primary_role else None,
                "is_owner": is_owner
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

    def _is_super_admin(self, user_id: UUID) -> bool:
        """Check if user is a super admin."""
        # Avoid circular imports
        from app.models.organization import OrgMemberRole
        from app.models.rbac import Role
        
        return self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.user_id == user_id,
            Role.code == "SUPER_ADMIN"
        ).first() is not None

    def _check_membership(self, org_id: UUID, user_id: UUID):
        """
        Check if user is a member of organization.
        
        Args:
            org_id: Organization ID
            user_id: User ID
        
        Raises:
            PermissionError: If user is not a member
        """
        if self._is_super_admin(user_id):
            return

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
    
    def get_member_details(
        self,
        org_id: UUID,
        user_id: UUID,
        current_user_id: UUID
    ) -> dict:
        """
        Get enhanced member details including profile information.
        
        Args:
            org_id: Organization ID
            user_id: User ID to get details for
            current_user_id: Current user ID (for access control)
        
        Returns:
            Enhanced member details dictionary
        
        Raises:
            PermissionError: If current user is not a member
            NotFoundError: If member not found
        """
        self.logger.info(
            "Fetching member details",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id),
                "current_user_id": str(current_user_id)
            }
        )
        
        # Check if current user is a member
        self._check_membership(org_id, current_user_id)
        
        # Get member and user data
        result = self.db.query(OrgMember, User).join(
            User, OrgMember.user_id == User.id
        ).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == user_id
        ).first()
        
        if not result:
            raise NotFoundError(
                message="Member not found",
                error_code="MEMBER_NOT_FOUND",
                details={"user_id": str(user_id)}
            )
        
        member, user = result
        
        # Get all roles for this member
        member_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.user_id == user_id,
            OrgMemberRole.organization_id == org_id
        ).all()
        
        # Get primary role
        primary_role = next((mr for mr in member_roles if mr.is_primary), member_roles[0] if member_roles else None)
        
        # Check if user is owner
        is_owner = any(mr.role.code in ['OWNER', 'FSP_OWNER'] for mr in member_roles)
        
        details = {
            "id": str(member.id),
            "user_id": str(user.id),
            "user_name": user.full_name or "",
            "user_email": user.email,
            "phone": user.phone or "",
            "role_id": str(primary_role.role_id) if primary_role else "",
            "role_name": primary_role.role.code if primary_role else "",
            "is_owner": is_owner,
            "status": member.status.value,
            "joined_at": member.joined_at.isoformat() if member.joined_at else "",
            "bio": user.bio or "",
            "address": user.address or "",
            "profile_picture": user.profile_picture_url or ""
        }
        
        self.logger.info(
            "Member details fetched successfully",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        return details
    
    def get_member_work_history(
        self,
        org_id: UUID,
        user_id: UUID,
        current_user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[dict], int]:
        """
        Get member work history (activities within the organization).
        
        For now, returns mock data. In the future, this can pull from:
        - Work orders
        - Audits
        - Schedule tasks
        - Other activity logs
        
        Args:
            org_id: Organization ID
            user_id: User ID to get history for
            current_user_id: Current user ID (for access control)
            limit: Maximum items to return
            offset: Offset for pagination
        
        Returns:
            Tuple of (work history items, total count)
        
        Raises:
            PermissionError: If current user is not a member
            NotFoundError: If member not found
        """
        self.logger.info(
            "Fetching member work history",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id),
                "current_user_id": str(current_user_id),
                "limit": limit,
                "offset": offset
            }
        )
        
        # Check if current user is a member
        self._check_membership(org_id, current_user_id)
        
        # Check if target user is a member
        member = self.db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == user_id
        ).first()
        
        if not member:
            raise NotFoundError(
                message="Member not found",
                error_code="MEMBER_NOT_FOUND",
                details={"user_id": str(user_id)}
            )
        
        # Mock work history data
        # In the future, replace this with actual queries to work_orders, audits, etc.
        import uuid
        from datetime import datetime, timedelta
        
        mock_activities = [
            {
                "id": str(uuid.uuid4()),
                "activity_type": "TASK_COMPLETED",
                "title": "Completed soil testing",
                "description": "Tested 5 acres of land in North Field",
                "date": (datetime.utcnow() - timedelta(days=3)).isoformat() + "Z",
                "location": "North Field",
                "metadata": {
                    "task_id": str(uuid.uuid4()),
                    "farm_id": str(uuid.uuid4())
                }
            },
            {
                "id": str(uuid.uuid4()),
                "activity_type": "FARM_VISIT",
                "title": "Farm inspection",
                "description": "Routine inspection of irrigation system",
                "date": (datetime.utcnow() - timedelta(days=5)).isoformat() + "Z",
                "location": "Green Valley Farm",
                "metadata": None
            },
            {
                "id": str(uuid.uuid4()),
                "activity_type": "CONSULTATION",
                "title": "Pest management consultation",
                "description": "Advised on organic pest control methods",
                "date": (datetime.utcnow() - timedelta(days=8)).isoformat() + "Z",
                "location": None,
                "metadata": None
            },
            {
                "id": str(uuid.uuid4()),
                "activity_type": "REPORT_SUBMITTED",
                "title": "Monthly crop report",
                "description": "Submitted comprehensive crop health report",
                "date": (datetime.utcnow() - timedelta(days=10)).isoformat() + "Z",
                "location": "Office",
                "metadata": {
                    "report_id": str(uuid.uuid4())
                }
            },
            {
                "id": str(uuid.uuid4()),
                "activity_type": "TRAINING",
                "title": "Conducted drip irrigation training",
                "description": "Trained 10 workers on new drip irrigation system",
                "date": (datetime.utcnow() - timedelta(days=15)).isoformat() + "Z",
                "location": "Training Center",
                "metadata": None
            }
        ]
        
        total = len(mock_activities)
        
        # Apply pagination
        paginated_items = mock_activities[offset:offset + limit]
        
        self.logger.info(
            "Member work history fetched",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id),
                "count": len(paginated_items),
                "total": total
            }
        )
        
        return paginated_items, total
