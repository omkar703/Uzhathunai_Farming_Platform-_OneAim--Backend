"""
FSP Approval service for Uzhathunai v2.0.
Handles FSP organization approval workflow (SuperAdmin only).
"""
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.fsp_service import FSPApprovalDocument
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import OrganizationStatus, OrganizationType
from app.core.logging import get_logger
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    PermissionError
)

logger = get_logger(__name__)


class FSPApprovalService:
    """Service for FSP organization approval workflow."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
    
    def upload_approval_document(
        self,
        fsp_org_id: UUID,
        user_id: UUID,
        document_type: str,
        file_url: str,
        file_key: str,
        file_name: str
    ) -> FSPApprovalDocument:
        """
        Upload approval document for FSP organization.
        
        Args:
            fsp_org_id: FSP organization ID
            user_id: User ID (must be member of FSP org)
            document_type: Type of document
            file_url: URL of uploaded file
            file_key: Storage key of file
            file_name: Original file name
        
        Returns:
            Created approval document
        
        Raises:
            NotFoundError: If organization not found
            ValidationError: If organization is not FSP type
            PermissionError: If user is not a member
        """
        self.logger.info(
            "Uploading FSP approval document",
            extra={
                "fsp_org_id": str(fsp_org_id),
                "user_id": str(user_id),
                "document_type": document_type
            }
        )
        
        # Get organization
        org = self.db.query(Organization).filter(Organization.id == fsp_org_id).first()
        if not org:
            raise NotFoundError(
                message="Organization not found",
                error_code="ORG_NOT_FOUND"
            )
        
        # Verify organization is FSP type
        if org.organization_type != OrganizationType.FSP:
            raise ValidationError(
                message="Organization is not FSP type",
                error_code="NOT_FSP_ORG"
            )
        
        # Check if user is a member
        self._check_membership(fsp_org_id, user_id)
        
        try:
            # Create approval document
            document = FSPApprovalDocument(
                fsp_organization_id=fsp_org_id,
                document_type=document_type,
                file_url=file_url,
                file_key=file_key,
                file_name=file_name,
                uploaded_by=user_id
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            self.logger.info(
                "FSP approval document uploaded successfully",
                extra={
                    "document_id": str(document.id),
                    "fsp_org_id": str(fsp_org_id),
                    "user_id": str(user_id)
                }
            )
            
            return document
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to upload FSP approval document",
                extra={
                    "fsp_org_id": str(fsp_org_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def get_pending_approvals(
        self,
        user_id: UUID,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Organization], int]:
        """
        Get FSP organizations pending approval (SuperAdmin only).
        
        Args:
            user_id: User ID (must be SuperAdmin)
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (organizations, total count)
        
        Raises:
            PermissionError: If user is not SuperAdmin
        """
        self.logger.info(
            "Fetching pending FSP approvals",
            extra={
                "user_id": str(user_id),
                "page": page,
                "limit": limit
            }
        )
        
        # Check if user is SuperAdmin
        self._check_super_admin(user_id)
        
        # Query FSP organizations with NOT_STARTED or IN_PROGRESS status
        query = self.db.query(Organization).filter(
            Organization.organization_type == OrganizationType.FSP,
            Organization.status.in_([OrganizationStatus.NOT_STARTED, OrganizationStatus.IN_PROGRESS])
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        organizations = query.order_by(
            Organization.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        self.logger.info(
            "Pending FSP approvals fetched",
            extra={
                "count": len(organizations),
                "total": total,
                "page": page
            }
        )
        
        return organizations, total
    
    def review_fsp_organization(
        self,
        fsp_org_id: UUID,
        admin_user_id: UUID,
        approve: bool,
        notes: Optional[str] = None
    ) -> Organization:
        """
        Approve or reject FSP organization (SuperAdmin only).
        
        Args:
            fsp_org_id: FSP organization ID
            admin_user_id: SuperAdmin user ID
            approve: True to approve, False to reject
            notes: Optional review notes
        
        Returns:
            Updated organization
        
        Raises:
            NotFoundError: If organization not found
            ValidationError: If organization is not FSP type
            PermissionError: If user is not SuperAdmin
        """
        self.logger.info(
            "Reviewing FSP organization",
            extra={
                "fsp_org_id": str(fsp_org_id),
                "admin_user_id": str(admin_user_id),
                "approve": approve
            }
        )
        
        # Check if user is SuperAdmin
        self._check_super_admin(admin_user_id)
        
        # Get organization
        org = self.db.query(Organization).filter(Organization.id == fsp_org_id).first()
        if not org:
            raise NotFoundError(
                message="Organization not found",
                error_code="ORG_NOT_FOUND"
            )
        
        # Verify organization is FSP type
        if org.organization_type != OrganizationType.FSP:
            raise ValidationError(
                message="Organization is not FSP type",
                error_code="NOT_FSP_ORG"
            )
        
        try:
            # Update organization status
            if approve:
                # Requirement 14.4: SuperAdmin approves FSP organization
                org.status = OrganizationStatus.ACTIVE
                self.logger.info(
                    "FSP organization approved",
                    extra={
                        "fsp_org_id": str(fsp_org_id),
                        "admin_user_id": str(admin_user_id)
                    }
                )
            else:
                # Reject - set back to NOT_STARTED
                org.status = OrganizationStatus.NOT_STARTED
                self.logger.info(
                    "FSP organization rejected",
                    extra={
                        "fsp_org_id": str(fsp_org_id),
                        "admin_user_id": str(admin_user_id)
                    }
                )
            
            org.updated_by = admin_user_id
            org.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(org)
            
            self.logger.info(
                "FSP organization review completed",
                extra={
                    "fsp_org_id": str(fsp_org_id),
                    "new_status": org.status.value,
                    "admin_user_id": str(admin_user_id)
                }
            )
            
            return org
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to review FSP organization",
                extra={
                    "fsp_org_id": str(fsp_org_id),
                    "admin_user_id": str(admin_user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def get_organization_documents(
        self,
        fsp_org_id: UUID,
        user_id: UUID
    ) -> List[FSPApprovalDocument]:
        """
        Get approval documents for FSP organization.
        
        Args:
            fsp_org_id: FSP organization ID
            user_id: User ID (must be member or SuperAdmin)
        
        Returns:
            List of approval documents
        
        Raises:
            NotFoundError: If organization not found
            PermissionError: If user doesn't have access
        """
        self.logger.info(
            "Fetching FSP approval documents",
            extra={
                "fsp_org_id": str(fsp_org_id),
                "user_id": str(user_id)
            }
        )
        
        # Get organization
        org = self.db.query(Organization).filter(Organization.id == fsp_org_id).first()
        if not org:
            raise NotFoundError(
                message="Organization not found",
                error_code="ORG_NOT_FOUND"
            )
        
        # Check if user is SuperAdmin or member of organization
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        is_super_admin = self._is_super_admin(user_id)
        is_member = self._is_member(fsp_org_id, user_id)
        
        if not (is_super_admin or is_member):
            raise PermissionError(
                message="You don't have permission to view these documents",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
        
        # Get documents
        documents = self.db.query(FSPApprovalDocument).filter(
            FSPApprovalDocument.fsp_organization_id == fsp_org_id
        ).order_by(FSPApprovalDocument.uploaded_at.desc()).all()
        
        self.logger.info(
            "FSP approval documents fetched",
            extra={
                "fsp_org_id": str(fsp_org_id),
                "count": len(documents)
            }
        )
        
        return documents
    
    def _check_membership(self, org_id: UUID, user_id: UUID):
        """
        Check if user is a member of organization.
        
        Args:
            org_id: Organization ID
            user_id: User ID
        
        Raises:
            PermissionError: If user is not a member
        """
        from app.models.organization import OrgMember
        from app.models.enums import MemberStatus
        
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
    
    def _is_member(self, org_id: UUID, user_id: UUID) -> bool:
        """Check if user is a member of organization."""
        from app.models.organization import OrgMember
        from app.models.enums import MemberStatus
        
        member = self.db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        return member is not None
    
    def _check_super_admin(self, user_id: UUID):
        """
        Check if user is SuperAdmin.
        
        Args:
            user_id: User ID
        
        Raises:
            PermissionError: If user is not SuperAdmin
        """
        from app.models.rbac import Role
        from app.models.organization import OrgMemberRole
        
        # Check if user has SuperAdmin role (system-level role)
        super_admin_role = self.db.query(Role).filter(
            Role.code == 'SUPER_ADMIN'
        ).first()
        
        if not super_admin_role:
            raise PermissionError(
                message="SuperAdmin role not found in system",
                error_code="ROLE_NOT_FOUND"
            )
        
        # Check if user has this role
        has_role = self.db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == user_id,
            OrgMemberRole.role_id == super_admin_role.id
        ).first()
        
        if not has_role:
            raise PermissionError(
                message="SuperAdmin access required",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
    
    def _is_super_admin(self, user_id: UUID) -> bool:
        """Check if user is SuperAdmin."""
        from app.models.rbac import Role
        from app.models.organization import OrgMemberRole
        
        super_admin_role = self.db.query(Role).filter(
            Role.code == 'SUPER_ADMIN'
        ).first()
        
        if not super_admin_role:
            return False
        
        has_role = self.db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == user_id,
            OrgMemberRole.role_id == super_admin_role.id
        ).first()
        
        return has_role is not None
