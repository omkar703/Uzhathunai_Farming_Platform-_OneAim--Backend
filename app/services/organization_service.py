"""
Organization service for Uzhathunai v2.0.
Handles organization CRUD operations with FSP service management.
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import case, func, and_, or_
from sqlalchemy import case, func, and_, or_, desc, select
from uuid import UUID

from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.fsp_service import FSPServiceListing
from app.models.audit import Audit
from app.models.work_order import WorkOrder
from app.models.user import User
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
            # All new organizations are ACTIVE by default (Auto-approved)
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
            # Check for unique constraint violation manually if not caught by validation
            if "duplicate key value violates unique constraint" in str(e):
                 self.metrics.increment('organization.created', {
                    'type': data.organization_type.value,
                    'status': 'conflict'
                })
                 raise ConflictError(
                    message=f"Organization with name '{data.name}' already exists",
                    error_code="ORG_NAME_EXISTS",
                    details={"name": data.name}
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
    
    def get_marketplace_organizations(
        self,
        user_id: UUID,
        org_type: Optional[OrganizationType] = None,
        status: Optional[OrganizationStatus] = OrganizationStatus.ACTIVE,
        district: Optional[str] = None,
        state: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Organization], int]:
        """
        Get marketplace organizations for browsing.
        
        Returns approved/active organizations that the user is NOT a member of.
        Used by freelancers to discover organizations to join.
        
        Args:
            user_id: User ID (to exclude their organizations)
            org_type: Optional filter by organization type (FARMING or FSP)
            status: Optional filter by status (defaults to ACTIVE only)
            district: Optional filter by district
            state: Optional filter by state
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (organizations list, total count)
        """
        self.logger.info(
            "Fetching marketplace organizations",
            extra={
                "user_id": str(user_id),
                "org_type": org_type.value if org_type else None,
                "status": status.value if status else None,
                "district": district,
                "state": state,
                "page": page,
                "limit": limit
            }
        )
        
        # Build base query - get all organizations
        query = self.db.query(Organization)
        
        # Exclude organizations where user is already an ACTIVE member
        # Use LEFT JOIN to find organizations where user is NOT a member
        user_org_ids = self.db.query(OrgMember.organization_id).filter(
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).subquery()
        
        query = query.filter(~Organization.id.in_(user_org_ids))
        
        # Apply filters
        if status:
            if status == OrganizationStatus.ACTIVE:
                query = query.filter(Organization.status.in_([OrganizationStatus.ACTIVE, OrganizationStatus.IN_PROGRESS]))
            else:
                query = query.filter(Organization.status == status)
        
        if org_type:
            query = query.filter(Organization.organization_type == org_type)
        
        if district:
            query = query.filter(Organization.district.ilike(f"%{district}%"))
        
        if state:
            query = query.filter(Organization.state.ilike(f"%{state}%"))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        offset = (page - 1) * limit
        organizations = query.order_by(Organization.created_at.desc()).offset(offset).limit(limit).all()
        
        self.logger.info(
            "Marketplace organizations fetched",
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
        
        # Check if user is a member or super admin
        if self._is_super_admin(user_id):
            return org
            
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

    def get_organization_details(
        self,
        org_id: UUID,
        user_id: UUID
    ) -> dict:
        """
        Get comprehensive organization details including members, audits, and work orders.
        
        Args:
            org_id: Organization ID
            user_id: User ID (for access control)
        
        Returns:
            Dictionary with organization details and related data
        """
        # Reuse base get logic for permission check
        org = self.get_organization(org_id, user_id)
        
        # 1. Fetch Members
        members_query = self.db.query(
            OrgMember,
            User,
            Role.name.label('role_name')
        ).join(
            User, OrgMember.user_id == User.id
        ).join(
            OrgMemberRole, 
            and_(
                OrgMemberRole.organization_id == org_id,
                OrgMemberRole.user_id == User.id,
                OrgMemberRole.is_primary == True
            )
        ).join(
            Role, OrgMemberRole.role_id == Role.id
        ).filter(
            OrgMember.organization_id == org_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).all()
        
        members_data = []
        for member, user, role_name in members_query:
            members_data.append({
                "user_id": str(user.id),
                "full_name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "role": role_name,
                "status": member.status.value,
                "joined_at": member.joined_at
            })
            
        # 2. Fetch Recent Audits
        # Audits where this org is the Farming Organization (subject of audit)
        # OR audits where this org is FSP (conductor of audit)
        audit_filter = or_(
            Audit.farming_organization_id == org_id,
            Audit.fsp_organization_id == org_id
        )
        
        recent_audits = self.db.query(Audit).filter(
            audit_filter
        ).order_by(desc(Audit.created_at)).limit(5).all()
        
        audits_data = []
        for audit in recent_audits:
            # Determine auditor name (FSP name or internal user?)
            # Simplified for now
            audits_data.append({
                "id": str(audit.id),
                "template_name": audit.name, # Using audit name as template name proxy or fetch template? Audit.name is usually "Audit for X"
                "status": audit.status.value,
                "auditor_name": "Internal/External", # Placeholder, ideally fetch FSP name or creator
                "audit_date": audit.created_at, # Using created_at for now
                "score": None # Score logic if exists
            })
            
        # 3. Fetch Recent Work Orders
        wo_filter = or_(
            WorkOrder.farming_organization_id == org_id,
            WorkOrder.fsp_organization_id == org_id
        )
        
        recent_wos = self.db.query(WorkOrder).filter(
            wo_filter
        ).order_by(desc(WorkOrder.created_at)).limit(5).all()
        
        wos_data = []
        for wo in recent_wos:
            wos_data.append({
                "id": str(wo.id),
                "status": wo.status.value,
                "service_name": wo.title,
                "start_date": wo.start_date,
                "amount": float(wo.total_amount) if wo.total_amount else 0.0
            })
            
        # 4. Stats
        total_members = len(members_data)
        total_audits = self.db.query(func.count(Audit.id)).filter(audit_filter).scalar()
        
        from app.models.enums import WorkOrderStatus
        active_wos = self.db.query(func.count(WorkOrder.id)).filter(
            wo_filter,
            WorkOrder.status == WorkOrderStatus.ACTIVE
        ).scalar()
        
        completed_wos = self.db.query(func.count(WorkOrder.id)).filter(
            wo_filter,
            WorkOrder.status == WorkOrderStatus.COMPLETED
        ).scalar()
        
        stats = {
            "total_members": total_members,
            "total_audits": total_audits,
            "active_work_orders": active_wos,
            "completed_work_orders": completed_wos
        }
        
        # Combine into dict that matches OrganizationDetailResponse
        # Use Pydantic's .from_attributes logic? 
        # Since we return a dict, we need to map ORM attributes manually or 
        # relying on Pydantic to extract from dict.
        
        # We can return the Org object and attach these fields if Pydantic supports mixed?
        # But Org object is SQLAlchemy model. 
        # Safest is to convert Org to dict or use `__dict__` but relationships might issue.
        
        # Let's manual map standard org fields + new fields to be safe
        response_data = {
            "id": str(org.id),
            "name": org.name,
            "description": org.description,
            "logo_url": org.logo_url,
            "organization_type": org.organization_type,
            "status": org.status,
            "is_approved": org.is_approved,
            "registration_number": org.registration_number,
            "address": org.address,
            "district": org.district,
            "state": org.state,
            "pincode": org.pincode,
            "contact_email": org.contact_email,
            "contact_phone": org.contact_phone,
            "subscription_plan_id": str(org.subscription_plan_id) if org.subscription_plan_id else None,
            "subscription_start_date": org.subscription_start_date,
            "subscription_end_date": org.subscription_end_date,
            "created_at": org.created_at,
            "updated_at": org.updated_at,
            "created_by": str(org.created_by) if org.created_by else None,
            "updated_by": str(org.updated_by) if org.updated_by else None,
            # FSP services if applicable
            "services": org.fsp_services if org.organization_type == OrganizationType.FSP else None,
            # New fields
            "members": members_data,
            "recent_audits": audits_data,
            "recent_work_orders": wos_data,
            "stats": stats
        }
        
        return response_data

    def get_marketplace_provider_details(
        self,
        org_id: UUID
    ) -> Organization:
        """
        Get marketplace provider details (public access for authenticated users).
        
        Args:
            org_id: Organization (Provider) ID
            
        Returns:
            Organization
            
        Raises:
            NotFoundError: If organization not found or not active
        """
        self.logger.info(
            "Fetching marketplace provider details",
            extra={"org_id": str(org_id)}
        )
        
        # Get organization - must be FSP and (ACTIVE or IN_PROGRESS)
        org = self.db.query(Organization).filter(
            Organization.id == org_id,
            Organization.organization_type == OrganizationType.FSP,
            Organization.status.in_([OrganizationStatus.ACTIVE, OrganizationStatus.IN_PROGRESS])
        ).first()
        
        if not org:
            raise NotFoundError(
                message=f"Marketplace provider {org_id} not found",
                error_code="PROVIDER_NOT_FOUND"
            )
            
        # Optimization: Fetch and attach services directly
        if org.organization_type == OrganizationType.FSP:
            # Only ACTIVE services for the marketplace
            from app.models.enums import ServiceStatus
            services = self.db.query(FSPServiceListing).filter(
                FSPServiceListing.fsp_organization_id == org_id,
                FSPServiceListing.status == ServiceStatus.ACTIVE
            ).all()
            
            # Eagerly load the master service relationship for each listing
            for service in services:
                _ = service.service
                
            org.services = services
            
        return org
    
    def get_marketplace_explore(
        self,
        user_id: UUID
    ) -> List[dict]:
        """
        Get unified marketplace discovery view for Farmers.
        
        Logic:
        - Fetch all ACTIVE organizations of type FSP.
        - Include only FSPs that have at least one ACTIVE service listing.
        - Return unified structure with service_count.
        
        Args:
            user_id: Current user ID (for auditing/logging)
            
        Returns:
            List of FSP provider summaries
        """
        self.logger.info(
            "Fetching marketplace explore view",
            extra={"user_id": str(user_id)}
        )
        
        try:
            from app.models.fsp_service import FSPServiceListing
            from app.models.enums import ServiceStatus
            
            # Subquery to count active services per FSP
            service_counts = self.db.query(
                FSPServiceListing.fsp_organization_id,
                func.count(FSPServiceListing.id).label('service_count')
            ).filter(
                FSPServiceListing.status == ServiceStatus.ACTIVE
            ).group_by(FSPServiceListing.fsp_organization_id).subquery()
            
            # Final query joining organizations with service counts
            query = self.db.query(
                Organization,
                service_counts.c.service_count
            ).join(
                service_counts,
                Organization.id == service_counts.c.fsp_organization_id
            ).filter(
                Organization.organization_type == OrganizationType.FSP,
                Organization.status == OrganizationStatus.ACTIVE
            ).order_by(Organization.name.asc())
            
            results = query.all()
            
            explore_results = []
            for org, service_count in results:
                # Basic FSP summary with unified structure
                explore_results.append({
                    "id": str(org.id),
                    "name": org.name,
                    "description": org.description or "",
                    "specialization": "General Agriculture", # Default placeholder
                    "rating": 4.5, # Static placeholder as requested/expected
                    "is_verified": True if org.status == OrganizationStatus.ACTIVE else False,
                    "service_count": int(service_count or 0),
                    "logo_url": org.logo_url,
                    "district": org.district,
                    "state": org.state
                })
            
            self.logger.info(
                "Marketplace explore view fetched",
                extra={"user_id": str(user_id), "count": len(explore_results)}
            )
            
            return explore_results
            
        except Exception as e:
            self.logger.error(
                "Failed to fetch marketplace explore",
                extra={"user_id": str(user_id), "error": str(e)},
                exc_info=True
            )
            raise

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
        # Check global uniqueness of organization name
        existing = self.db.query(Organization).filter(
            Organization.name == name
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
        if self._is_super_admin(user_id):
            return
            
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
    def get_fsp_clients(
        self,
        fsp_org_id: UUID,
        user_id: UUID
    ) -> List[dict]:
        """
        Get list of clients (Farming Organizations) for an FSP.
        
        A client is any Farming Organization that has an active relationship 
        (PENDING, ACCEPTED, ACTIVE Work Order) with the FSP.
        
        Args:
            fsp_org_id: FSP Organization ID
            user_id: User ID (must be FSP_OWNER/FSP_ADMIN)
            
        Returns:
            List of client dictionaries ready for schema validation
        """
        self.logger.info(
            "Fetching FSP clients",
            extra={
                "fsp_org_id": str(fsp_org_id),
                "user_id": str(user_id)
            }
        )
        
        # Check permission
        self._check_admin_permission(fsp_org_id, user_id)
        
        try:
            from app.models.work_order import WorkOrder
            from app.models.enums import WorkOrderStatus
            
            # Find all unique farming organizations with relevant work orders
            # Use query with join to filter and group
            # We want organizations that have at least one non-cancelled work order
            
            # Subquery to get counts and status info
            stmt = self.db.query(
                WorkOrder.farming_organization_id,
                func.count(WorkOrder.id).label('total_orders'),
                func.sum(
                    case(
                        (WorkOrder.status == WorkOrderStatus.ACTIVE, 1),
                        else_=0
                    )
                ).label('active_orders')
            ).filter(
                WorkOrder.fsp_organization_id == fsp_org_id,
                WorkOrder.status.in_([
                    WorkOrderStatus.PENDING,
                    WorkOrderStatus.ACCEPTED,
                    WorkOrderStatus.ACTIVE
                ])
            ).group_by(WorkOrder.farming_organization_id).subquery()
            
            # Main query to fetch organization details
            results = self.db.query(
                Organization,
                stmt.c.total_orders,
                stmt.c.active_orders
            ).join(
                stmt,
                Organization.id == stmt.c.farming_organization_id
            ).all()
            
            clients = []
            for org, total_orders, active_orders in results:
                # Determine relationship status
                if active_orders > 0:
                    rel_status = "ACTIVE"
                else:
                    rel_status = "PENDING"
                    
                clients.append({
                    "id": str(org.id),
                    "name": org.name,
                    "type": org.organization_type,
                    "status": org.status,
                    "relationship_status": rel_status,
                    "contact_info": {
                        "email": org.contact_email,
                        "phone": org.contact_phone
                    },
                    "active_work_orders": int(active_orders)
                })
                
            self.logger.info(
                "FSP clients fetched",
                extra={
                    "fsp_org_id": str(fsp_org_id),
                    "count": len(clients)
                }
            )
            
            return clients
            
        except Exception as e:
            self.logger.error(
                "Failed to fetch FSP clients",
                extra={
                    "fsp_org_id": str(fsp_org_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise

    def get_farming_providers(
        self,
        farming_org_id: UUID,
        user_id: UUID
    ) -> List[dict]:
        """
        Get list of Service Providers (FSPs) for a Farmer.
        
        Args:
            farming_org_id: Farming Organization ID
            user_id: User ID (must be OWNER/ADMIN)
            
        Returns:
            List of provider dictionaries ready for schema validation
        """
        self.logger.info(
            "Fetching farming providers",
            extra={
                "farming_org_id": str(farming_org_id),
                "user_id": str(user_id)
            }
        )
        
        # Check permission
        self._check_admin_permission(farming_org_id, user_id)
        
        try:
            from app.models.work_order import WorkOrder
            from app.models.enums import WorkOrderStatus
            
            # Find all unique FSPs with relevant work orders
            # Subquery to get counts and stats
            stmt = self.db.query(
                WorkOrder.fsp_organization_id,
                func.count(WorkOrder.id).label('total_contracts'),
                func.sum(
                    case(
                        (WorkOrder.status == WorkOrderStatus.ACTIVE, 1),
                        else_=0
                    )
                ).label('active_contracts'),
                func.min(WorkOrder.created_at).label('first_contract_date')
            ).filter(
                WorkOrder.farming_organization_id == farming_org_id,
                # Consider all non-cancelled orders as history
                WorkOrder.status != WorkOrderStatus.CANCELLED
            ).group_by(WorkOrder.fsp_organization_id).subquery()
            
            # Main query to fetch organization details
            results = self.db.query(
                Organization,
                stmt.c.total_contracts,
                stmt.c.active_contracts,
                stmt.c.first_contract_date
            ).join(
                stmt,
                Organization.id == stmt.c.fsp_organization_id
            ).all()
            
            providers = []
            for org, total_contracts, active_contracts, first_date in results:
                # Try to get primary service category if available (optional)
                service_category = "General"
                # TODO: Implement service category lookup
                    
                providers.append({
                    "id": str(org.id),
                    "name": org.name,
                    "logo_url": org.logo_url,
                    "service_category": service_category,
                    "active_contracts_count": int(active_contracts or 0),
                    "total_contracts_history": int(total_contracts or 0),
                    "first_contract_date": first_date,
                    "contact": {
                        "email": org.contact_email,
                        "phone": org.contact_phone
                    }
                })
                
            self.logger.info(
                "Farming providers fetched",
                extra={
                    "farming_org_id": str(farming_org_id),
                    "count": len(providers)
                }
            )
            
            return providers
            
        except Exception as e:
            self.logger.error(
                "Failed to fetch farming providers",
                extra={
                    "farming_org_id": str(farming_org_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
            
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

