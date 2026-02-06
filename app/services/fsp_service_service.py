"""
FSP Service service for Uzhathunai v2.0.
Handles FSP service listing management and approval triggers.
"""
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID

from app.models.fsp_service import FSPServiceListing, MasterService
from app.models.organization import Organization, OrgMemberRole
from app.models.rbac import Role
from app.models.enums import ServiceStatus, OrganizationStatus, OrganizationType
from app.schemas.fsp_service import (
    FSPServiceListingCreate,
    FSPServiceListingUpdate
)
from app.core.logging import get_logger
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    PermissionError
)

logger = get_logger(__name__)


class FSPServiceService:
    """Service for FSP service listing management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
    
    def get_master_services(
        self,
        active_only: bool = True
    ) -> List[MasterService]:
        """
        Get all master services.
        
        Args:
            active_only: If True, return only active services
        
        Returns:
            List of master services
        """
        self.logger.info(
            "Fetching master services",
            extra={"active_only": active_only}
        )
        
        query = self.db.query(MasterService)
        
        if active_only:
            query = query.filter(MasterService.status == ServiceStatus.ACTIVE)
        
        services = query.order_by(MasterService.sort_order, MasterService.name).all()
        
        self.logger.info(
            "Master services fetched",
            extra={"count": len(services)}
        )
        
        return services
    
    def get_service_listings(
        self,
        fsp_organization_id: Optional[UUID] = None,
        service_type: Optional[UUID] = None,
        district: Optional[str] = None,
        pricing_model: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[FSPServiceListing], int]:
        """
        Get service listings from marketplace with filtering.
        Only returns listings from ACTIVE FSP organizations.
        
        Args:
            fsp_organization_id: Filter by FSP organization ID
            service_type: Filter by master service ID
            district: Filter by service area district
            pricing_model: Filter by pricing model
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (service listings, total count)
        """
        self.logger.info(
            "Fetching marketplace service listings",
            extra={
                "fsp_organization_id": str(fsp_organization_id) if fsp_organization_id else None,
                "service_type": str(service_type) if service_type else None,
                "district": district,
                "pricing_model": pricing_model,
                "page": page,
                "limit": limit
            }
        )
        
        # Base query - only ACTIVE listings from ACTIVE or IN_PROGRESS FSP organizations
        query = self.db.query(FSPServiceListing).join(
            Organization,
            FSPServiceListing.fsp_organization_id == Organization.id
        ).filter(
            FSPServiceListing.status == ServiceStatus.ACTIVE,
            Organization.status.in_([OrganizationStatus.ACTIVE, OrganizationStatus.IN_PROGRESS]),
            Organization.organization_type == OrganizationType.FSP
        )
        
        # Apply filters
        if fsp_organization_id:
            query = query.filter(FSPServiceListing.fsp_organization_id == fsp_organization_id)
            
        if service_type:
            query = query.filter(FSPServiceListing.service_id == service_type)
        
        if district:
            # Use PostgreSQL array contains operator
            query = query.filter(FSPServiceListing.service_area_districts.contains([district]))
        
        if pricing_model:
            query = query.filter(FSPServiceListing.pricing_model == pricing_model)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        services = query.order_by(
            FSPServiceListing.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Eagerly load the service relationship for response serialization
        for service_listing in services:
            _ = service_listing.service
        
        self.logger.info(
            "Marketplace service listings fetched",
            extra={
                "count": len(services),
                "total": total,
                "page": page
            }
        )
        
        return services, total
    
    def get_organization_services(
        self,
        org_id: UUID,
        user_id: UUID,
        active_only: bool = False
    ) -> List[FSPServiceListing]:
        """
        Get service listings for FSP organization.
        
        Args:
            org_id: Organization ID
            user_id: User ID (for access control)
            active_only: If True, return only active services
        
        Returns:
            List of service listings
        
        Raises:
            NotFoundError: If organization not found
            ValidationError: If organization is not FSP type
            PermissionError: If user is not a member
        """
        self.logger.info(
            "Fetching organization services",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id),
                "active_only": active_only
            }
        )
        
        # Get organization
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise NotFoundError(
                message="Organization not found",
                error_code="ORG_NOT_FOUND"
            )
        
        # Verify organization is FSP type
        if org.organization_type != OrganizationType.FSP:
            self.logger.warning(
                "Organization type mismatch in get_organization_services",
                extra={
                    "org_id": str(org_id),
                    "expected": OrganizationType.FSP,
                    "actual": org.organization_type,
                    "actual_type": str(type(org.organization_type))
                }
            )
            # Temporary fix/workaround if it's a string comparison issue
            if str(org.organization_type) == "FSP":
                self.logger.info("String comparison matched 'FSP', proceeding anyway")
            else:
                raise ValidationError(
                    message=f"Organization {org_id} is not FSP type (Actual: {org.organization_type})",
                    error_code="NOT_FSP_ORG"
                )
        
        # Check if user is a member
        self._check_membership(org_id, user_id)
        
        # Get service listings
        query = self.db.query(FSPServiceListing).filter(
            FSPServiceListing.fsp_organization_id == org_id
        )
        
        if active_only:
            query = query.filter(FSPServiceListing.status == ServiceStatus.ACTIVE)
        
        services = query.order_by(FSPServiceListing.created_at.desc()).all()
        
        # Eagerly load the service relationship for response serialization
        for service_listing in services:
            _ = service_listing.service
        
        return services
    
    def get_service_listing(
        self,
        service_id: UUID,
        user_id: UUID
    ) -> FSPServiceListing:
        """
        Get specific service listing.
        
        Args:
            service_id: Service listing ID
            user_id: User ID (for access control)
        
        Returns:
            Service listing
        
        Raises:
            NotFoundError: If service listing not found
            PermissionError: If user doesn't have permission
        """
        self.logger.info(
            "Fetching service listing",
            extra={
                "service_id": str(service_id),
                "user_id": str(user_id)
            }
        )
        
        # Get service listing
        service_listing = self.db.query(FSPServiceListing).filter(
            FSPServiceListing.id == service_id
        ).first()
        
        if not service_listing:
            raise NotFoundError(
                message="Service listing not found",
                error_code="SERVICE_LISTING_NOT_FOUND"
            )
        
        # Check if user is a member of the organization
        self._check_membership(service_listing.fsp_organization_id, user_id)
        
        # Eagerly load the service relationship
        _ = service_listing.service
        
        return service_listing
    def create_service_listing(
        self,
        org_id: UUID,
        user_id: UUID,
        data: FSPServiceListingCreate
    ) -> FSPServiceListing:
        """
        Create new service listing for FSP organization.
        Triggers approval process by setting org status to IN_PROGRESS.
        
        Args:
            org_id: Organization ID
            user_id: User ID (must be FSP_OWNER/FSP_ADMIN)
            data: Service listing data
        
        Returns:
            Created service listing
        
        Raises:
            NotFoundError: If organization or master service not found
            ValidationError: If organization is not FSP type
            PermissionError: If user doesn't have permission
        """
        self.logger.info(
            "Creating service listing",
            extra={
                "org_id": str(org_id),
                "user_id": str(user_id),
                "service_id": str(data.service_id)
            }
        )
        
        # Get organization
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise NotFoundError(
                message="Organization not found",
                error_code="ORG_NOT_FOUND"
            )
        
        # Verify organization is FSP type
        if org.organization_type != OrganizationType.FSP:
            self.logger.warning(
                "Organization type mismatch in create_service_listing",
                extra={
                    "org_id": str(org_id),
                    "expected": OrganizationType.FSP,
                    "actual": org.organization_type
                }
            )
            if str(org.organization_type) != "FSP":
                raise ValidationError(
                    message=f"Organization {org_id} is not FSP type (Actual: {org.organization_type})",
                    error_code="NOT_FSP_ORG"
                )
        
        # Validate FSP organization status - must be ACTIVE to create listings
        # Requirement 1.7: WHEN FSP organization is NOT_STARTED status THEN prevent creating service listings
        if org.status == OrganizationStatus.NOT_STARTED:
            raise PermissionError(
                message="Cannot create service listings until SuperAdmin approves organization to ACTIVE status",
                error_code="FSP_NOT_APPROVED",
                details={"org_status": org.status.value}
            )
        
        # Check if user has admin permission
        self._check_admin_permission(org_id, user_id)
        
        # Verify master service exists
        master_service = self.db.query(MasterService).filter(
            MasterService.id == data.service_id
        ).first()
        if not master_service:
            raise NotFoundError(
                message="Master service not found",
                error_code="SERVICE_NOT_FOUND"
            )
        
        try:
            # Create service listing
            service_listing = FSPServiceListing(
                fsp_organization_id=org_id,
                service_id=data.service_id,
                title=data.title,
                description=data.description,
                service_area_districts=data.service_area_districts,
                pricing_model=data.pricing_model,
                base_price=data.base_price,
                status=ServiceStatus.ACTIVE,
                created_by=user_id,
                updated_by=user_id
            )
            
            self.db.add(service_listing)
            
            # Trigger approval process
            if org.status == OrganizationStatus.ACTIVE:
                org.status = OrganizationStatus.IN_PROGRESS
                org.updated_by = user_id
                org.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(service_listing)
            
            # Eagerly load the service relationship for response serialization
            _ = service_listing.service
            
            self.logger.info(
                "Service listing created successfully",
                extra={
                    "service_listing_id": str(service_listing.id),
                    "org_id": str(org_id),
                    "user_id": str(user_id),
                    "org_status": org.status.value
                }
            )
            
            return service_listing
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to create service listing",
                extra={
                    "org_id": str(org_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def update_service_listing(
        self,
        service_id: UUID,
        user_id: UUID,
        data: FSPServiceListingUpdate
    ) -> FSPServiceListing:
        """
        Update service listing.
        Triggers approval process by setting org status to IN_PROGRESS.
        
        Args:
            service_id: Service listing ID
            user_id: User ID (must be FSP_OWNER/FSP_ADMIN)
            data: Update data
        
        Returns:
            Updated service listing
        
        Raises:
            NotFoundError: If service listing not found
            PermissionError: If user doesn't have permission
        """
        self.logger.info(
            "Updating service listing",
            extra={
                "service_id": str(service_id),
                "user_id": str(user_id)
            }
        )
        
        # Get service listing
        service_listing = self.db.query(FSPServiceListing).filter(
            FSPServiceListing.id == service_id
        ).first()
        if not service_listing:
            raise NotFoundError(
                message="Service listing not found",
                error_code="SERVICE_LISTING_NOT_FOUND"
            )
        
        # Check if user has admin permission
        self._check_admin_permission(service_listing.fsp_organization_id, user_id)
        
        try:
            # Update fields
            update_data = data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(service_listing, field, value)
            
            service_listing.updated_by = user_id
            service_listing.updated_at = datetime.utcnow()
            
            # Trigger approval process
            org = self.db.query(Organization).filter(
                Organization.id == service_listing.fsp_organization_id
            ).first()
            if org and org.status == OrganizationStatus.ACTIVE:
                org.status = OrganizationStatus.IN_PROGRESS
                org.updated_by = user_id
                org.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(service_listing)
            
            # Eagerly load the service relationship for response serialization
            _ = service_listing.service
            
            self.logger.info(
                "Service listing updated successfully",
                extra={
                    "service_id": str(service_id),
                    "user_id": str(user_id),
                    "updated_fields": list(update_data.keys()),
                    "org_status": org.status.value if org else None
                }
            )
            
            return service_listing
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to update service listing",
                extra={
                    "service_id": str(service_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def delete_service_listing(
        self,
        service_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete service listing with ownership validation.
        
        Args:
            service_id: Service listing ID
            user_id: User ID (must be FSP_OWNER/FSP_ADMIN of owning org)
        
        Raises:
            NotFoundError: If service listing not found
            PermissionError: If user doesn't have permission
        """
        self.logger.info(
            "Deleting service listing",
            extra={
                "service_id": str(service_id),
                "user_id": str(user_id)
            }
        )
        
        # Get service listing
        service_listing = self.db.query(FSPServiceListing).filter(
            FSPServiceListing.id == service_id
        ).first()
        if not service_listing:
            raise NotFoundError(
                message="Service listing not found",
                error_code="SERVICE_LISTING_NOT_FOUND"
            )
        
        # Validate ownership - user must be admin of the FSP organization that owns this listing
        self._check_admin_permission(service_listing.fsp_organization_id, user_id)
        
        try:
            self.db.delete(service_listing)
            self.db.commit()
            
            self.logger.info(
                "Service listing deleted successfully",
                extra={
                    "service_id": str(service_id),
                    "user_id": str(user_id),
                    "org_id": str(service_listing.fsp_organization_id)
                }
            )
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to delete service listing",
                extra={
                    "service_id": str(service_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def deactivate_service_listing(
        self,
        service_id: UUID,
        user_id: UUID
    ) -> FSPServiceListing:
        """
        Deactivate service listing.
        Does NOT trigger approval process.
        
        Args:
            service_id: Service listing ID
            user_id: User ID (must be FSP_OWNER/FSP_ADMIN)
        
        Returns:
            Updated service listing
        
        Raises:
            NotFoundError: If service listing not found
            PermissionError: If user doesn't have permission
        """
        self.logger.info(
            "Deactivating service listing",
            extra={
                "service_id": str(service_id),
                "user_id": str(user_id)
            }
        )
        
        # Get service listing
        service_listing = self.db.query(FSPServiceListing).filter(
            FSPServiceListing.id == service_id
        ).first()
        if not service_listing:
            raise NotFoundError(
                message="Service listing not found",
                error_code="SERVICE_LISTING_NOT_FOUND"
            )
        
        # Check if user has admin permission
        self._check_admin_permission(service_listing.fsp_organization_id, user_id)
        
        try:
            # Deactivate service
            service_listing.status = ServiceStatus.INACTIVE
            service_listing.updated_by = user_id
            service_listing.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(service_listing)
            
            self.logger.info(
                "Service listing deactivated successfully",
                extra={
                    "service_id": str(service_id),
                    "user_id": str(user_id)
                }
            )
            
            return service_listing
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to deactivate service listing",
                extra={
                    "service_id": str(service_id),
                    "user_id": str(user_id),
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
    
    def _check_admin_permission(self, org_id: UUID, user_id: UUID):
        """
        Check if user has admin permission (FSP_OWNER/FSP_ADMIN).
        
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
        
        # Check if user has FSP_OWNER or FSP_ADMIN role
        admin_roles = ['FSP_OWNER', 'FSP_ADMIN']
        has_admin = any(mr.role.code in admin_roles for mr in member_roles)
        
        if not has_admin:
            raise PermissionError(
                message="You don't have permission to perform this action",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={"org_id": str(org_id), "required_roles": admin_roles}
            )
