"""
Organization service for Uzhathunai v2.0.
Handles organization CRUD operations with FSP service management.
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.fsp_service import FSPServiceListing
from app.models.subscription import SubscriptionPlan
from app.models.rbac import Role
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus
)
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse
)
from app.core.logging import get_logger
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ConflictError,
    PermissionError
)
from app.services.auth_service import AuthService

logger = get_logger(__name__)


class MetricsCollector:
    """Simple metrics collector for tracking operations."""
    
    @staticmethod
    def increment(metric_name: str, tags: dict = None):
        """Increment a metric counter."""
        # In production, this would send to a metrics service
        logger.info(
            "metric_increment",
            metric=metric_name,
            tags=tags or {}
        )


class OrganizationService:
    """Service for organization management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
        self.metrics = MetricsCollector()
    
    def create_organization(
        self,
        data: OrganizationCreate,
        user_id: UUID
    ) -> Organization:
        """
        Create new organization with fresh implementation.
        
        Args:
            data: Organization creation data
            user_id: ID of user creating the organization
        
        Returns:
            Created organization
        
        Raises:
            ConflictError: If organization name already exists for user
            ValidationError: If validation fails
        """
        self.logger.info(
            "Creating organization",
            extra={
                "user_id": str(user_id),
                "org_type": data.organization_type.value,
                "org_name": data.name
            }
        )
        
        try:
            # Validation
            self._validate_organization_name(data.name, user_id)
            
            # Determine initial status
            if data.organization_type == OrganizationType.FSP and data.services:
                status = OrganizationStatus.NOT_STARTED  # Pending approval
            else:
                status = OrganizationStatus.ACTIVE
            
            # Create organization
            org = Organization(
                name=data.name,
                organization_type=data.organization_type,
                status=status,
                description=data.description,
                logo_url=data.logo_url,
                address=data.address,
                district=data.district,
                pincode=data.pincode,
                contact_email=data.contact_email,
                contact_phone=data.contact_phone,
                created_by=user_id,
                updated_by=user_id
            )
            
            self.db.add(org)
            self.db.flush()  # Get org.id
            
            # Create FSP service listings if FSP
            if data.organization_type == OrganizationType.FSP and data.services:
                for service_data in data.services:
                    service_listing = FSPServiceListing(
                        fsp_organization_id=org.id,
                        service_id=service_data.service_id,
                        title=service_data.title,
                        description=service_data.description,
                        service_area_districts=service_data.service_area_districts,
                        pricing_model=service_data.pricing_model,
                        base_price=service_data.base_price,
                        created_by=user_id,
                        updated_by=user_id
                    )
                    self.db.add(service_listing)
            
            # Assign default subscription plan
            self._assign_default_subscription(org)
            
            # Create owner membership
            self._create_owner_membership(org.id, user_id, data.organization_type)
            
            self.db.commit()
            self.db.refresh(org)
            
            # Metrics
            self.metrics.increment('organization.created', {
                'type': data.organization_type.value,
                'status': 'success'
            })
            
            self.logger.info(
                "Organization created successfully",
                extra={
                    "org_id": str(org.id),
                    "user_id": str(user_id),
                    "org_type": data.organization_type.value,
                    "status": status.value
                }
            )
            
            return org
            
        except ConflictError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to create organization",
                extra={"user_id": str(user_id), "error": str(e)},
                exc_info=True
            )
            self.metrics.increment('organization.created', {
                'type': data.organization_type.value,
                'status': 'failure'
            })
            raise
    
    def get_user_organizations(
        self,
        user_id: UUID,
        org_type: Optional[OrganizationType] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Organization], int]:
        """
        Get all organizations user belongs to.
        
        Args:
            user_id: User ID
            org_type: Optional filter by organization type
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (organizations list, total count)
        """
        self.logger.info(
            "Fetching user organizations",
            extra={
                "user_id": str(user_id),
                "org_type": org_type.value if org_type else None,
                "page": page,
                "limit": limit
            }
        )
        
        # Build query
        query = self.db.query(Organization).join(OrgMember).filter(
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        )
        
        # Apply filters
        if org_type:
            query = query.filter(Organization.organization_type == org_type)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        organizations = query.order_by(Organization.created_at.desc()).offset(offset).limit(limit).all()
        
        self.logger.info(
            "User organizations fetched",
            extra={
                "user_id": str(user_id),
                "count": len(organizations),
                "total": total
            }
        )
        
        return organizations, total
    
    def get_organization(
        self,
        org_id: UUID,
        user_id: UUID
    ) -> Organization:
        """
        Get organization details.
        
        Args:
            org_id: Organization ID
            user_id: User ID (for access control)
        
        Returns:
            Organization
        
        Raises:
            NotFoundError: If organization not found
            PermissionError: If user is not a member
        """
        self.logger.info(
            "Fetching organization",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        # Get organization
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise NotFoundError(
                message=f"Organization {org_id} not found",
                error_code="ORG_NOT_FOUND",
                details={"org_id": str(org_id)}
            )
        
        # Check if user is a member
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
        
        return org
    
    def update_organization(
        self,
        org_id: UUID,
        user_id: UUID,
        data: OrganizationUpdate
    ) -> Organization:
        """
        Update organization details.
        
        Args:
            org_id: Organization ID
            user_id: User ID (must be OWNER/ADMIN)
            data: Update data
        
        Returns:
            Updated organization
        
        Raises:
            NotFoundError: If organization not found
            PermissionError: If user doesn't have permission
        """
        self.logger.info(
            "Updating organization",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id)
            }
        )
        
        # Get organization
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise NotFoundError(
                message=f"Organization {org_id} not found",
                error_code="ORG_NOT_FOUND",
                details={"org_id": str(org_id)}
            )
        
        # Check if user has permission (OWNER/ADMIN)
        self._check_admin_permission(org_id, user_id)
        
        try:
            # Update fields
            update_data = data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(org, field, value)
            
            org.updated_by = user_id
            org.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(org)
            
            self.logger.info(
                "Organization updated successfully",
                extra={
                    "org_id": str(org_id),
                    "user_id": str(user_id),
                    "updated_fields": list(update_data.keys())
                }
            )
            
            return org
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to update organization",
                extra={"org_id": str(org_id), "user_id": str(user_id), "error": str(e)},
                exc_info=True
            )
            raise
    
    def _validate_organization_name(self, name: str, user_id: UUID):
        """
        Validate organization name uniqueness per user.
        
        Args:
            name: Organization name
            user_id: User ID
        
        Raises:
            ConflictError: If name already exists for user
        """
        existing = self.db.query(Organization).join(OrgMember).filter(
            Organization.name == name,
            OrgMember.user_id == user_id
        ).first()
        
        if existing:
            raise ConflictError(
                message=f"Organization with name '{name}' already exists",
                error_code="ORG_NAME_EXISTS",
                details={"name": name}
            )
    
    def _assign_default_subscription(self, org: Organization):
        """
        Assign default subscription plan to organization.
        
        Args:
            org: Organization to assign subscription to
        """
        # Get FREE plan as default for all new organizations
        default_plan = self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == 'FREE',
            SubscriptionPlan.is_active == True
        ).first()
        
        if default_plan:
            org.subscription_plan_id = default_plan.id
            org.subscription_start_date = date.today()
            # Default to 30 days trial
            from datetime import timedelta
            org.subscription_end_date = date.today() + timedelta(days=30)
            
            self.logger.info(
                "Default subscription assigned",
                extra={
                    "org_id": str(org.id),
                    "plan_name": 'FREE'
                }
            )
    
    def _create_owner_membership(
        self,
        org_id: UUID,
        user_id: UUID,
        org_type: OrganizationType
    ):
        """
        Create owner membership and role.
        
        Removes FREELANCER role if user is a freelancer.
        
        Args:
            org_id: Organization ID
            user_id: User ID
            org_type: Organization type
        """
        # Remove FREELANCER role if user is a freelancer
        auth_service = AuthService(self.db)
        if auth_service.is_freelancer(user_id):
            auth_service.remove_freelancer_role(user_id)
            self.logger.info(
                "FREELANCER role removed",
                extra={
                    "user_id": str(user_id),
                    "reason": "creating_organization"
                }
            )
        
        # Determine owner role
        role_code = 'OWNER' if org_type == OrganizationType.FARMING else 'FSP_OWNER'
        role = self.db.query(Role).filter(Role.code == role_code).first()
        
        if not role:
            raise NotFoundError(
                message=f"Role {role_code} not found",
                error_code="ROLE_NOT_FOUND",
                details={"role_code": role_code}
            )
        
        # Create membership
        member = OrgMember(
            user_id=user_id,
            organization_id=org_id,
            status=MemberStatus.ACTIVE,
            joined_at=datetime.utcnow()
        )
        self.db.add(member)
        self.db.flush()
        
        # Create role assignment
        member_role = OrgMemberRole(
            user_id=user_id,
            organization_id=org_id,
            role_id=role.id,
            is_primary=True,
            assigned_at=datetime.utcnow(),
            assigned_by=user_id
        )
        self.db.add(member_role)
        
        self.logger.info(
            "Owner membership created",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id),
                "role_code": role_code
            }
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
