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
    
    def send_invitation_by_user_id(
        self,
        org_id: UUID,
        inviter_id: UUID,
        user_id: UUID,
        role_code: str
    ) -> OrgMemberInvitation:
        """
        Send invitation to specific user ID with specific role code.
        
        Args:
            org_id: Organization ID
            inviter_id: User ID sending the invitation
            user_id: User ID to invite
            role_code: Role code to assign (e.g., 'FSP_ADMIN')
            
        Returns:
            Created invitation
        """
        self.logger.info(
            "Sending invitation by user ID",
            extra={
                "org_id": str(org_id),
                "inviter_id": str(inviter_id),
                "user_id": str(user_id),
                "role_code": role_code
            }
        )
        
        # Check if inviter has admin permission
        self._check_admin_permission(org_id, inviter_id)
        
        # Verify user exists
        from app.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
            
        # Verify role exists by code
        role = self.db.query(Role).filter(Role.code == role_code).first()
        if not role:
            raise NotFoundError(
                message=f"Role with code '{role_code}' not found",
                error_code="ROLE_NOT_FOUND"
            )
            
        # Call send_invitation logic (adapted for user_id)
        data = InviteMemberRequest(
            invitee_email=user.email,
            role_id=role.id,
            message=f"Invitation to join organization with role {role_code}"
        )
        
        return self.send_invitation(org_id, inviter_id, data)
    
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
    
    def create_join_request(
        self,
        org_id: UUID,
        user_id: UUID
    ) -> OrgMemberInvitation:
        """
        Create a request to join an organization.
        
        Args:
            org_id: Organization ID
            user_id: User ID requesting to join
        
        Returns:
            Created invitation (join request)
        
        Raises:
            NotFoundError: If organization not found
            ConflictError: If user is already member or owner of another org
            ValidationError: If validation fails
        """
        self.logger.info(
            "Creating join request",
            extra= {
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        # Verify organization exists
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise NotFoundError(
                message="Organization not found",
                error_code="ORG_NOT_FOUND"
            )
        
        # Check if user is already a member
        existing_member = self.db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        if existing_member:
            raise ConflictError(
                message="You are already a member of this organization",
                error_code="ALREADY_MEMBER"
            )
            
        # Check if user has pending Join Request
        pending_request = self.db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.organization_id == org_id,
            OrgMemberInvitation.inviter_id == user_id,
            OrgMemberInvitation.invitee_user_id == user_id,
            OrgMemberInvitation.status == InvitationStatus.PENDING
        ).first()
        
        if pending_request:
            raise ConflictError(
                message="You already have a pending request for this organization",
                error_code="DUPLICATE_REQUEST"
            )

        # Verify user is not an Owner of another organization
        # Check for OWNER or FSP_OWNER roles in any organization
        owner_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.user_id == user_id,
            Role.code.in_(['OWNER', 'FSP_OWNER'])
        ).first()
        
        if owner_roles:
            raise PermissionError(
                message="Organization owners cannot join other organizations as freelancers",
                error_code="OWNER_RESTRICTION"
            )
            
        # Get WORKER role
        role = self.db.query(Role).filter(Role.code == 'WORKER').first()
        if not role:
            # Fallback to MEMBER if WORKER not found
            role = self.db.query(Role).filter(Role.code == 'MEMBER').first()
            
        if not role:
            raise NotFoundError(
                message="Default role for members not found",
                error_code="ROLE_NOT_FOUND"
            )
            
        # Get user email
        from app.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        
        try:
            # Create Join Request (Self-Invitation)
            # inviter_id == invitee_user_id
            from datetime import timezone
            now = datetime.now(timezone.utc)
            # Default expiration 30 days
            expires_at = now + timedelta(days=30)
            
            invitation = OrgMemberInvitation(
                organization_id=org_id,
                inviter_id=user_id,
                invitee_email=user.email,
                invitee_user_id=user_id,
                role_id=role.id,
                status=InvitationStatus.PENDING,
                invited_at=now,
                expires_at=expires_at,
                message="Request to join organization"
            )
            
            self.db.add(invitation)
            self.db.commit()
            self.db.refresh(invitation)
            
            self.logger.info(
                "Join request created successfully",
                extra={
                    "invitation_id": str(invitation.id),
                    "org_id": str(org_id),
                    "user_id": str(user_id)
                }
            )
            
            return invitation
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to create join request",
                extra={"user_id": str(user_id), "error": str(e)},
                exc_info=True
            )
            raise

    def get_join_requests(
        self,
        org_id: UUID,
        user_id: UUID
    ) -> List[dict]:
        """
        Get pending join requests for an organization.
        
        Args:
            org_id: Organization ID
            user_id: User ID (Admin/Owner) requesting list
            
        Returns:
            List of join request data dictionaries
        """
        # Check admin permission
        self._check_admin_permission(org_id, user_id)
        
        # Query for join requests: inviter_id == invitee_user_id AND PENDING
        requests = self.db.query(OrgMemberInvitation).join(Role).filter(
            OrgMemberInvitation.organization_id == org_id,
            OrgMemberInvitation.status == InvitationStatus.PENDING,
            OrgMemberInvitation.inviter_id == OrgMemberInvitation.invitee_user_id
        ).all()
        
        # Format response
        result = []
        from app.models.user import User
        
        for req in requests:
            # Fetch user name 
            # (In a real app, join User to query to optimize, but this is consistent)
            user = self.db.query(User).filter(User.id == req.inviter_id).first()
            inviter_name = f"{user.first_name} {user.last_name}" if user else "Unknown"
            
            result.append({
                "id": str(req.id),
                "inviter_name": inviter_name,
                "role": req.role.code,
                "status": req.status.value,
                "created_at": req.invited_at.isoformat() if req.invited_at else None,
                "user_id": str(req.inviter_id)
            })
            
        return result

    def accept_invitation(
        self,
        invitation_id: UUID,
        user_id: UUID,
        role_id: Optional[UUID] = None
    ) -> dict:
        """
        Accept organization invitation OR Approve join request.
        
        Handles two scenarios:
        1. Standard Invitation: User accepts invitation to join org.
        2. Join Request: Org Admin approves user's request to join.
        
        Args:
            invitation_id: Invitation ID
            user_id: User ID (Invitee OR Org Admin)
            role_id: Optional role ID to override invitation's default role
        
        Returns:
            Result dictionary
            
        Raises:
            ValidationError: If permissions invalid or invitation not pending
        """
        self.logger.info(
            "Accepting/Approving invitation",
            extra={
                "invitation_id": str(invitation_id),
                "user_id": str(user_id)
            }
        )
        
        invitation = self.db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.id == invitation_id
        ).first()
        
        if not invitation:
            raise NotFoundError(message="Invitation not found", error_code="INV_NOT_FOUND")
            
        if invitation.status != InvitationStatus.PENDING:
            raise ValidationError(message="Invitation is not PENDING", error_code="INVALID_STATUS")

        # Determine if this is a Join Request (Self-Invite)
        is_join_request = (invitation.inviter_id == invitation.invitee_user_id)
        
        target_user_id = invitation.invitee_user_id
        
        if is_join_request:
            # Scenario 2: Join Request -> Requires Org Admin Approval
            self._check_admin_permission(invitation.organization_id, user_id)
            # target_user_id is the user joining (inviter/invitee)
        else:
            # Scenario 1: Standard Invite -> Requires Invitee Acceptance
            if user_id != invitation.invitee_user_id:
                # Fallback: Check email if user_id mapping wasn't set (though logic sets it)
                from app.models.user import User
                user = self.db.query(User).filter(User.id == user_id).first()
                if not user or user.email != invitation.invitee_email:
                    raise PermissionError(
                        message="This invitation is not for you",
                        error_code="INVALID_USER"
                    )
        
        # Common Logic: Create Membership
        try:
             # Remove FREELANCER role if user is joining
            auth_service = AuthService(self.db)
            if auth_service.is_freelancer(target_user_id):
                auth_service.remove_freelancer_role(target_user_id)
            
            from datetime import timezone
            now = datetime.now(timezone.utc)
            
            # Create member
            member = OrgMember(
                user_id=target_user_id,
                organization_id=invitation.organization_id,
                status=MemberStatus.ACTIVE,
                joined_at=now,
                invited_by=invitation.inviter_id, # Could be self
                invitation_id=invitation.id
            )
            self.db.add(member)
            self.db.flush()
            
            # Determine which role to assign
            # If role_id is provided (admin overriding), use it
            # Otherwise use invitation's default role_id
            assigned_role_id = role_id if role_id else invitation.role_id
            
            # Validate role exists if custom role provided
            if role_id:
                role_check = self.db.query(Role).filter(Role.id == role_id).first()
                if not role_check:
                    raise NotFoundError(
                        message="Specified role not found",
                        error_code="ROLE_NOT_FOUND"
                    )
            
            # Assign Role
            member_role = OrgMemberRole(
                user_id=target_user_id,
                organization_id=invitation.organization_id,
                role_id=assigned_role_id,
                is_primary=True,
                assigned_at=now,
                assigned_by=user_id # Who approved/accepted
            )
            self.db.add(member_role)
            
            # Update Invitation
            invitation.status = InvitationStatus.ACCEPTED
            invitation.responded_at = now
            # invitee_user_id is already set for join/standard usually, but ensure it
            invitation.invitee_user_id = target_user_id 
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Invitation accepted" if not is_join_request else "Request approved",
                "member_id": str(member.id)
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error("Failed to accept invitation", exc_info=True)
            raise

    def reject_invitation(
        self,
        invitation_id: UUID,
        user_id: UUID
    ) -> dict:
        """
        Reject organization invitation OR Decline join request.
        
        Args:
            invitation_id: Invitation ID
            user_id: User ID rejecting/declining
            
        Returns:
            Result dictionary
        """
        invitation = self.db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.id == invitation_id
        ).first()
        
        if not invitation:
             raise NotFoundError(message="Invitation not found")
             
        if invitation.status != InvitationStatus.PENDING:
             raise ValidationError(message="Invitation is not PENDING")
             
        is_join_request = (invitation.inviter_id == invitation.invitee_user_id)
        
        if is_join_request:
            # Org Admin rejecting the join request
            self._check_admin_permission(invitation.organization_id, user_id)
        else:
            # Invitee rejecting the invite
            if user_id != invitation.invitee_user_id:
                 # Check email check fall back...
                 # Simplification for now:
                 from app.models.user import User
                 user = self.db.query(User).filter(User.id == user_id).first()
                 if not user or user.email != invitation.invitee_email:
                     raise PermissionError(message="Not authorized")

        try:
            from datetime import timezone
            invitation.status = InvitationStatus.REJECTED
            invitation.responded_at = datetime.now(timezone.utc)
            self.db.commit()
            
            return {
                "success": True,
                "message": "Invitation rejected" if not is_join_request else "Request rejected"
            }
        except Exception as e:
            self.db.rollback()
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
