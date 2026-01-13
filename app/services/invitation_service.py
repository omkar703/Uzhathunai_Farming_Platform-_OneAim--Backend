"""
Invitation service for Uzhathunai v2.0.
Handles organization member invitation workflow.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.invitation import OrgMemberInvitation
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.enums import InvitationStatus, MemberStatus
from app.schemas.invitation import InviteMemberRequest
from app.core.logging import get_logger
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ConflictError,
    PermissionError
)
from app.services.auth_service import AuthService

logger = get_logger(__name__)


class InvitationService:
    """Service for invitation management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
    
    def send_invitation(
        self,
        org_id: UUID,
        inviter_id: UUID,
        data: InviteMemberRequest
    ) -> OrgMemberInvitation:
        """
        Send invitation to join organization.
        
        Args:
            org_id: Organization ID
            inviter_id: User ID sending the invitation
            data: Invitation data
        
        Returns:
            Created invitation
        
        Raises:
            PermissionError: If inviter doesn't have permission
            ConflictError: If user is already a member or has pending invitation
            ValidationError: If validation fails
        """
        self.logger.info(
            "Sending invitation",
            extra={
                "org_id": str(org_id),
                "inviter_id": str(inviter_id),
                "invitee_email": data.invitee_email,
                "role_id": str(data.role_id)
            }
        )
        
        # Check if inviter has admin permission
        self._check_admin_permission(org_id, inviter_id)
        
        # Verify organization exists
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise NotFoundError(
                message="Organization not found",
                error_code="ORG_NOT_FOUND"
            )
        
        # Verify role exists
        role = self.db.query(Role).filter(Role.id == data.role_id).first()
        if not role:
            raise NotFoundError(
                message="Role not found",
                error_code="ROLE_NOT_FOUND"
            )
        
        # Check if email is already a member
        from app.models.user import User
        existing_user = self.db.query(User).filter(User.email == data.invitee_email).first()
        if existing_user:
            existing_member = self.db.query(OrgMember).filter(
                OrgMember.organization_id == org_id,
                OrgMember.user_id == existing_user.id
            ).first()
            
            if existing_member:
                raise ConflictError(
                    message="User is already a member of this organization",
                    error_code="ALREADY_MEMBER"
                )
        
        # Check for duplicate pending invitation
        existing_invitation = self.db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.organization_id == org_id,
            OrgMemberInvitation.invitee_email == data.invitee_email,
            OrgMemberInvitation.status == InvitationStatus.PENDING
        ).first()
        
        if existing_invitation:
            raise ConflictError(
                message="Pending invitation already exists for this email",
                error_code="DUPLICATE_INVITATION"
            )
        
        try:
            # Create invitation
            from datetime import timezone
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(days=data.expires_in_days)
            
            invitation = OrgMemberInvitation(
                organization_id=org_id,
                inviter_id=inviter_id,
                invitee_email=data.invitee_email,
                invitee_user_id=existing_user.id if existing_user else None,
                role_id=data.role_id,
                status=InvitationStatus.PENDING,
                invited_at=now,
                expires_at=expires_at,
                message=data.message
            )
            
            self.db.add(invitation)
            self.db.commit()
            self.db.refresh(invitation)
            
            # TODO: Send invitation email
            # This would be implemented in Phase 8 (Notifications)
            # For now, we just log it
            self.logger.info(
                "Invitation email would be sent",
                extra={
                    "invitation_id": str(invitation.id),
                    "invitee_email": data.invitee_email,
                    "org_name": org.name
                }
            )
            
            self.logger.info(
                "Invitation sent successfully",
                extra={
                    "invitation_id": str(invitation.id),
                    "org_id": str(org_id),
                    "inviter_id": str(inviter_id),
                    "invitee_email": data.invitee_email
                }
            )
            
            return invitation
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to send invitation",
                extra={
                    "org_id": str(org_id),
                    "inviter_id": str(inviter_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def get_organization_invitations(
        self,
        org_id: UUID,
        user_id: UUID,
        status_filter: Optional[InvitationStatus] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[OrgMemberInvitation], int]:
        """
        Get invitations for organization.
        
        Args:
            org_id: Organization ID
            user_id: User ID (for access control)
            status_filter: Optional filter by status
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (invitations list, total count)
        
        Raises:
            PermissionError: If user doesn't have permission
        """
        self.logger.info(
            "Fetching organization invitations",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id),
                "status_filter": status_filter.value if status_filter else None,
                "page": page,
                "limit": limit
            }
        )
        
        # Check if user has admin permission
        self._check_admin_permission(org_id, user_id)
        
        # Build query
        query = self.db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.organization_id == org_id
        )
        
        # Apply filters
        if status_filter:
            query = query.filter(OrgMemberInvitation.status == status_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        invitations = query.order_by(OrgMemberInvitation.invited_at.desc()).offset(offset).limit(limit).all()
        
        self.logger.info(
            "Organization invitations fetched",
            extra={
                "org_id": str(org_id),
                "count": len(invitations),
                "total": total
            }
        )
        
        return invitations, total
    
    def get_user_invitations(
        self,
        email: str,
        status_filter: Optional[InvitationStatus] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[OrgMemberInvitation], int]:
        """
        Get invitations for user's email.
        
        Args:
            email: User email
            status_filter: Optional filter by status
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (invitations list, total count)
        """
        self.logger.info(
            "Fetching user invitations",
            extra={
                "email": email,
                "status_filter": status_filter.value if status_filter else None,
                "page": page,
                "limit": limit
            }
        )
        
        # Build query
        query = self.db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.invitee_email == email
        )
        
        # Apply filters
        if status_filter:
            query = query.filter(OrgMemberInvitation.status == status_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        invitations = query.order_by(OrgMemberInvitation.invited_at.desc()).offset(offset).limit(limit).all()
        
        self.logger.info(
            "User invitations fetched",
            extra={
                "email": email,
                "count": len(invitations),
                "total": total
            }
        )
        
        return invitations, total
    
    def accept_invitation(
        self,
        invitation_id: UUID,
        user_id: UUID
    ) -> dict:
        """
        Accept organization invitation.
        
        Args:
            invitation_id: Invitation ID
            user_id: User ID accepting the invitation
        
        Returns:
            Result dictionary with membership info
        
        Raises:
            NotFoundError: If invitation not found
            ValidationError: If invitation is not pending or expired
        """
        self.logger.info(
            "Accepting invitation",
            extra={
                "invitation_id": str(invitation_id),
                "user_id": str(user_id)
            }
        )
        
        # Get invitation
        invitation = self.db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.id == invitation_id
        ).first()
        
        if not invitation:
            raise NotFoundError(
                message="Invitation not found",
                error_code="INVITATION_NOT_FOUND"
            )
        
        # Verify invitation is for this user
        from app.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.email != invitation.invitee_email:
            raise ValidationError(
                message="Invitation is not for this user",
                error_code="INVALID_INVITATION"
            )
        
        # Check if invitation is pending
        if invitation.status != InvitationStatus.PENDING:
            raise ValidationError(
                message=f"Invitation is {invitation.status.value}",
                error_code="INVITATION_NOT_PENDING"
            )
        
        # Check if invitation is expired
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if invitation.expires_at and invitation.expires_at < now:
            invitation.status = InvitationStatus.EXPIRED
            self.db.commit()
            raise ValidationError(
                message="Invitation has expired",
                error_code="INVITATION_EXPIRED"
            )
        
        try:
            # Remove FREELANCER role if user is a freelancer
            auth_service = AuthService(self.db)
            if auth_service.is_freelancer(user_id):
                auth_service.remove_freelancer_role(user_id)
                self.logger.info(
                    "FREELANCER role removed",
                    extra={
                        "user_id": str(user_id),
                        "reason": "accepting_invitation"
                    }
                )
            
            # Create membership
            from datetime import timezone
            now = datetime.now(timezone.utc)
            member = OrgMember(
                user_id=user_id,
                organization_id=invitation.organization_id,
                status=MemberStatus.ACTIVE,
                joined_at=now,
                invited_by=invitation.inviter_id,
                invitation_id=invitation.id
            )
            self.db.add(member)
            self.db.flush()
            
            # Create role assignment
            member_role = OrgMemberRole(
                user_id=user_id,
                organization_id=invitation.organization_id,
                role_id=invitation.role_id,
                is_primary=True,
                assigned_at=now,
                assigned_by=invitation.inviter_id
            )
            self.db.add(member_role)
            
            # Update invitation status
            invitation.status = InvitationStatus.ACCEPTED
            invitation.responded_at = now
            invitation.invitee_user_id = user_id
            
            self.db.commit()
            
            self.logger.info(
                "Invitation accepted successfully",
                extra={
                    "invitation_id": str(invitation_id),
                    "user_id": str(user_id),
                    "org_id": str(invitation.organization_id)
                }
            )
            
            return {
                "success": True,
                "message": "Invitation accepted successfully",
                "organization_id": str(invitation.organization_id),
                "member_id": str(member.id)
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to accept invitation",
                extra={
                    "invitation_id": str(invitation_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def reject_invitation(
        self,
        invitation_id: UUID,
        user_id: UUID
    ) -> dict:
        """
        Reject organization invitation.
        
        Args:
            invitation_id: Invitation ID
            user_id: User ID rejecting the invitation
        
        Returns:
            Result dictionary
        
        Raises:
            NotFoundError: If invitation not found
            ValidationError: If invitation is not pending
        """
        self.logger.info(
            "Rejecting invitation",
            extra={
                "invitation_id": str(invitation_id),
                "user_id": str(user_id)
            }
        )
        
        # Get invitation
        invitation = self.db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.id == invitation_id
        ).first()
        
        if not invitation:
            raise NotFoundError(
                message="Invitation not found",
                error_code="INVITATION_NOT_FOUND"
            )
        
        # Verify invitation is for this user
        from app.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.email != invitation.invitee_email:
            raise ValidationError(
                message="Invitation is not for this user",
                error_code="INVALID_INVITATION"
            )
        
        # Check if invitation is pending
        if invitation.status != InvitationStatus.PENDING:
            raise ValidationError(
                message=f"Invitation is {invitation.status.value}",
                error_code="INVITATION_NOT_PENDING"
            )
        
        try:
            # Update invitation status
            from datetime import timezone
            invitation.status = InvitationStatus.REJECTED
            invitation.responded_at = datetime.now(timezone.utc)
            invitation.invitee_user_id = user_id
            
            self.db.commit()
            
            self.logger.info(
                "Invitation rejected successfully",
                extra={
                    "invitation_id": str(invitation_id),
                    "user_id": str(user_id),
                    "org_id": str(invitation.organization_id)
                }
            )
            
            return {
                "success": True,
                "message": "Invitation rejected successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to reject invitation",
                extra={
                    "invitation_id": str(invitation_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def cancel_invitation(
        self,
        invitation_id: UUID,
        user_id: UUID
    ) -> dict:
        """
        Cancel pending invitation.
        
        Args:
            invitation_id: Invitation ID
            user_id: User ID canceling the invitation
        
        Returns:
            Result dictionary
        
        Raises:
            NotFoundError: If invitation not found
            PermissionError: If user doesn't have permission
            ValidationError: If invitation is not pending
        """
        self.logger.info(
            "Canceling invitation",
            extra={
                "invitation_id": str(invitation_id),
                "user_id": str(user_id)
            }
        )
        
        # Get invitation
        invitation = self.db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.id == invitation_id
        ).first()
        
        if not invitation:
            raise NotFoundError(
                message="Invitation not found",
                error_code="INVITATION_NOT_FOUND"
            )
        
        # Check if user has admin permission
        self._check_admin_permission(invitation.organization_id, user_id)
        
        # Check if invitation is pending
        if invitation.status != InvitationStatus.PENDING:
            raise ValidationError(
                message=f"Invitation is {invitation.status.value}",
                error_code="INVITATION_NOT_PENDING"
            )
        
        try:
            # Update invitation status
            from datetime import timezone
            invitation.status = InvitationStatus.CANCELLED
            invitation.responded_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            self.logger.info(
                "Invitation cancelled successfully",
                extra={
                    "invitation_id": str(invitation_id),
                    "user_id": str(user_id),
                    "org_id": str(invitation.organization_id)
                }
            )
            
            return {
                "success": True,
                "message": "Invitation cancelled successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to cancel invitation",
                extra={
                    "invitation_id": str(invitation_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
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
