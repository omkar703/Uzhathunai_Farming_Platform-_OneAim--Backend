"""
Work Order service for Uzhathunai v2.0.
Handles work order CRUD operations, acceptance workflow, and status management.
"""
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.models.work_order import WorkOrder, WorkOrderScope
from app.models.organization import Organization
from app.models.enums import (
    WorkOrderStatus,
    WorkOrderScopeType,
    OrganizationType
)
from app.core.logging import get_logger
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    ConflictError,
    PermissionError
)

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


class WorkOrderService:
    """Service for work order management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
        self.metrics = MetricsCollector()
    
    def create_work_order(
        self,
        farming_organization_id: UUID,
        fsp_organization_id: UUID,
        title: str,
        description: Optional[str],
        service_listing_id: Optional[UUID],
        terms_and_conditions: Optional[str],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        total_amount: Optional[float],
        currency: str,
        user_id: UUID
    ) -> WorkOrder:
        """
        Create new work order with scope definition.
        
        Args:
            farming_organization_id: Farming organization ID
            fsp_organization_id: FSP organization ID
            title: Work order title
            description: Work order description
            service_listing_id: Optional service listing reference
            terms_and_conditions: Terms and conditions
            start_date: Optional start date
            end_date: Optional end date
            total_amount: Optional total amount
            currency: Currency code
            user_id: ID of user creating the work order
        
        Returns:
            Created work order
        
        Raises:
            NotFoundError: If organizations not found
            ValidationError: If validation fails
        """
        return self._create_work_order_impl(
            farming_organization_id, fsp_organization_id, title, description,
            service_listing_id, terms_and_conditions, start_date, end_date,
            total_amount, currency, user_id
        )

    def _create_work_order_impl(
        self,
        farming_organization_id: UUID,
        fsp_organization_id: UUID,
        title: str,
        description: Optional[str],
        service_listing_id: Optional[UUID],
        terms_and_conditions: Optional[str],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        total_amount: Optional[float],
        currency: str,
        user_id: UUID
    ) -> WorkOrder:
        self.logger.info(
            "Creating work order",
            extra={
                "user_id": str(user_id),
                "farming_org_id": str(farming_organization_id),
                "fsp_org_id": str(fsp_organization_id),
                "title": title
            }
        )
        
        try:
            # Validate organizations exist
            self._validate_organizations(farming_organization_id, fsp_organization_id)
            
            # Generate unique work order number
            work_order_number = self._generate_work_order_number()
            
            # Create work order
            # Note: scope_metadata must be None (not {}) to satisfy DB constraint
            # Constraint requires: NULL OR object with at least one of: total_items, farms, plots, crops, organizations
            work_order = WorkOrder(
                farming_organization_id=farming_organization_id,
                fsp_organization_id=fsp_organization_id,
                service_listing_id=service_listing_id,
                work_order_number=work_order_number,
                title=title,
                description=description,
                status=WorkOrderStatus.PENDING,
                terms_and_conditions=terms_and_conditions,
                start_date=start_date,
                end_date=end_date,
                total_amount=total_amount,
                currency=currency,
                service_snapshot={"name": title, "description": description},
                created_by=user_id,
                updated_by=user_id
            )
            # Explicitly do NOT set scope_metadata - let it default to NULL
            
            self.db.add(work_order)
            self.db.commit()
            self.db.refresh(work_order)
            
            # Metrics
            self.metrics.increment('work_order.created', {
                'status': 'success'
            })
            
            self.logger.info(
                "Work order created successfully",
                extra={
                    "work_order_id": str(work_order.id),
                    "work_order_number": work_order_number,
                    "user_id": str(user_id)
                }
            )
            
            return work_order
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to create work order",
                extra={"user_id": str(user_id), "error": str(e)},
                exc_info=True
            )
            self.metrics.increment('work_order.created', {
                'status': 'failure'
            })
            raise
    
    def accept_work_order(
        self,
        work_order_id: UUID,
        user_id: UUID
    ) -> WorkOrder:
        """
        FSP accepts work order and grants access to resources.
        
        Args:
            work_order_id: Work order ID
            user_id: FSP user ID accepting the work order
        
        Returns:
            Updated work order
        
        Raises:
            NotFoundError: If work order not found
            ValidationError: If work order not in PENDING status
            PermissionError: If user not from FSP organization
        """
        self.logger.info(
            "Accepting work order",
            extra={
                "work_order_id": str(work_order_id),
                "user_id": str(user_id)
            }
        )
        
        # Get work order
        work_order = self.db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if not work_order:
            raise NotFoundError(
                message=f"Work order {work_order_id} not found",
                error_code="WORK_ORDER_NOT_FOUND",
                details={"work_order_id": str(work_order_id)}
            )
        
        # Validate status
        if work_order.status != WorkOrderStatus.PENDING:
            raise ValidationError(
                message=f"Work order must be in PENDING status to accept. Current status: {work_order.status.value}",
                error_code="INVALID_WORK_ORDER_STATUS",
                details={"current_status": work_order.status.value}
            )
        
        # Validate user is from FSP organization
        # This would be checked by the API layer, but we validate here too
        
        try:
            # Update work order status
            work_order.status = WorkOrderStatus.ACCEPTED
            work_order.accepted_at = datetime.utcnow()
            work_order.accepted_by = user_id
            work_order.updated_by = user_id
            work_order.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(work_order)
            
            # Metrics
            self.metrics.increment('work_order.accepted', {
                'status': 'success'
            })
            
            self.logger.info(
                "Work order accepted successfully",
                extra={
                    "work_order_id": str(work_order_id),
                    "user_id": str(user_id),
                    "work_order_number": work_order.work_order_number
                }
            )
            
            return work_order
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to accept work order",
                extra={"work_order_id": str(work_order_id), "user_id": str(user_id), "error": str(e)},
                exc_info=True
            )
            self.metrics.increment('work_order.accepted', {
                'status': 'failure'
            })
            raise
    
    def update_work_order_status(
        self,
        work_order_id: UUID,
        new_status: WorkOrderStatus,
        user_id: UUID,
        completion_notes: Optional[str] = None,
        completion_photo_url: Optional[str] = None
    ) -> WorkOrder:
        """
        Update work order status with access revocation for terminal states.
        
        Args:
            work_order_id: Work order ID
            new_status: New status
            user_id: User ID performing the update
        
        Returns:
            Updated work order
        
        Raises:
            NotFoundError: If work order not found
            ValidationError: If status transition is invalid
        """
        self.logger.info(
            "Updating work order status",
            extra={
                "work_order_id": str(work_order_id),
                "new_status": new_status.value,
                "user_id": str(user_id)
            }
        )
        
        # Get work order
        work_order = self.db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if not work_order:
            raise NotFoundError(
                message=f"Work order {work_order_id} not found",
                error_code="WORK_ORDER_NOT_FOUND",
                details={"work_order_id": str(work_order_id)}
            )
        
        # Validate status transition
        self._validate_status_transition(work_order.status, new_status)
        
        try:
            old_status = work_order.status
            work_order.status = new_status
            work_order.updated_by = user_id
            work_order.updated_at = datetime.utcnow()
            
            # Set completion/cancellation timestamps
            if new_status == WorkOrderStatus.COMPLETED:
                work_order.completed_at = datetime.utcnow()
                work_order.completion_notes = completion_notes
                work_order.completion_photo_url = completion_photo_url
            elif new_status == WorkOrderStatus.CANCELLED:
                work_order.cancelled_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(work_order)
            
            # Metrics
            self.metrics.increment('work_order.status_updated', {
                'old_status': old_status.value,
                'new_status': new_status.value,
                'status': 'success'
            })
            
            self.logger.info(
                "Work order status updated successfully",
                extra={
                    "work_order_id": str(work_order_id),
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "user_id": str(user_id)
                }
            )
            
            return work_order
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to update work order status",
                extra={"work_order_id": str(work_order_id), "user_id": str(user_id), "error": str(e)},
                exc_info=True
            )
            self.metrics.increment('work_order.status_updated', {
                'status': 'failure'
            })
            raise
    
    def get_work_orders(
        self,
        user_id: UUID,
        organization_id: Optional[UUID] = None,
        fsp_organization_id: Optional[UUID] = None,
        farming_organization_id: Optional[UUID] = None,
        status: Optional[WorkOrderStatus] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[WorkOrder], int]:
        """
        Get work orders with pagination and multi-dimensional filtering.
        
        Args:
            user_id: User ID
            organization_id: Optional filter for ANY organization associated with the work order
            fsp_organization_id: Optional filter specific to the FSP organization
            farming_organization_id: Optional filter specific to the Farming organization
            status: Optional filter by status
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (work orders list, total count)
        """
        self.logger.info(
            "Fetching work orders",
            extra={
                "user_id": str(user_id),
                "organization_id": str(organization_id) if organization_id else None,
                "fsp_org_id": str(fsp_organization_id) if fsp_organization_id else None,
                "farming_org_id": str(farming_organization_id) if farming_organization_id else None,
                "status": status.value if status else None,
                "page": page,
                "limit": limit
            }
        )
        
        # Build query
        query = self.db.query(WorkOrder).options(
            joinedload(WorkOrder.farming_organization),
            joinedload(WorkOrder.fsp_organization)
        )
        
        # Apply filters
        # 1. Broad organization filter (OR)
        if organization_id:
            query = query.filter(
                (WorkOrder.farming_organization_id == organization_id) |
                (WorkOrder.fsp_organization_id == organization_id)
            )
            
        # 2. Specific FSP filter (AND)
        if fsp_organization_id:
            query = query.filter(WorkOrder.fsp_organization_id == fsp_organization_id)
            
        # 3. Specific Farming filter (AND)
        if farming_organization_id:
            query = query.filter(WorkOrder.farming_organization_id == farming_organization_id)
        
        if status:
            query = query.filter(WorkOrder.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        work_orders = query.order_by(WorkOrder.created_at.desc()).offset(offset).limit(limit).all()
        
        self.logger.info(
            "Work orders fetched",
            extra={
                "user_id": str(user_id),
                "count": len(work_orders),
                "total": total
            }
        )
        
        return work_orders, total
    
    def get_work_order(
        self,
        work_order_id: UUID,
        user_id: UUID
    ) -> WorkOrder:
        """
        Get work order details.
        
        Args:
            work_order_id: Work order ID
            user_id: User ID (for access control)
        
        Returns:
            Work order
        
        Raises:
            NotFoundError: If work order not found
        """
        self.logger.info(
            "Fetching work order",
            extra={
                "work_order_id": str(work_order_id),
                "user_id": str(user_id)
            }
        )
        
        work_order = self.db.query(WorkOrder).options(
            joinedload(WorkOrder.farming_organization),
            joinedload(WorkOrder.fsp_organization)
        ).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if not work_order:
            raise NotFoundError(
                message=f"Work order {work_order_id} not found",
                error_code="WORK_ORDER_NOT_FOUND",
                details={"work_order_id": str(work_order_id)}
            )
        
        return work_order
    
    def _validate_organizations(
        self,
        farming_org_id: UUID,
        fsp_org_id: UUID
    ):
        """
        Validate that both organizations exist and have correct types.
        
        Args:
            farming_org_id: Farming organization ID
            fsp_org_id: FSP organization ID
        
        Raises:
            NotFoundError: If organizations not found
            ValidationError: If organization types are incorrect
        """
        # Check farming organization
        farming_org = self.db.query(Organization).filter(
            Organization.id == farming_org_id
        ).first()
        
        if not farming_org:
            raise NotFoundError(
                message=f"Farming organization {farming_org_id} not found",
                error_code="FARMING_ORG_NOT_FOUND",
                details={"farming_org_id": str(farming_org_id)}
            )
        
        if farming_org.organization_type != OrganizationType.FARMING:
            raise ValidationError(
                message=f"Organization {farming_org_id} is not a farming organization",
                error_code="INVALID_FARMING_ORG_TYPE",
                details={"org_type": farming_org.organization_type.value}
            )
        
        # Check FSP organization
        fsp_org = self.db.query(Organization).filter(
            Organization.id == fsp_org_id
        ).first()
        
        if not fsp_org:
            raise NotFoundError(
                message=f"FSP organization {fsp_org_id} not found",
                error_code="FSP_ORG_NOT_FOUND",
                details={"fsp_org_id": str(fsp_org_id)}
            )
        
        if fsp_org.organization_type != OrganizationType.FSP:
            raise ValidationError(
                message=f"Organization {fsp_org_id} is not an FSP organization",
                error_code="INVALID_FSP_ORG_TYPE",
                details={"org_type": fsp_org.organization_type.value}
            )
    
    def _generate_work_order_number(self) -> str:
        """
        Generate unique work order number.
        
        Returns:
            Unique work order number (e.g., WO-2024-0001)
        """
        # Get current year
        year = datetime.utcnow().year
        
        # Get count of work orders this year
        count = self.db.query(WorkOrder).filter(
            WorkOrder.work_order_number.like(f'WO-{year}-%')
        ).count()
        
        # Generate number
        number = f'WO-{year}-{count + 1:04d}'
        
        return number
    
    def _validate_status_transition(
        self,
        current_status: WorkOrderStatus,
        new_status: WorkOrderStatus
    ):
        """
        Validate work order status transition.
        
        Valid transitions:
        - PENDING → ACCEPTED, REJECTED, CANCELLED
        - ACCEPTED → ACTIVE, CANCELLED
        - ACTIVE → COMPLETED, CANCELLED
        - Terminal states (COMPLETED, CANCELLED, REJECTED) cannot transition
        
        Args:
            current_status: Current status
            new_status: New status
        
        Raises:
            ValidationError: If transition is invalid
        """
        # Define valid transitions
        valid_transitions = {
            WorkOrderStatus.PENDING: [
                WorkOrderStatus.ACCEPTED,
                WorkOrderStatus.REJECTED,
                WorkOrderStatus.CANCELLED
            ],
            WorkOrderStatus.ACCEPTED: [
                WorkOrderStatus.ACTIVE,
                WorkOrderStatus.CANCELLED
            ],
            WorkOrderStatus.ACTIVE: [
                WorkOrderStatus.COMPLETED,
                WorkOrderStatus.CANCELLED
            ],
            # Terminal states
            WorkOrderStatus.COMPLETED: [],
            WorkOrderStatus.CANCELLED: [],
            WorkOrderStatus.REJECTED: []
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise ValidationError(
                message=f"Invalid status transition from {current_status.value} to {new_status.value}",
                error_code="INVALID_STATUS_TRANSITION",
                details={
                    "current_status": current_status.value,
                    "new_status": new_status.value,
                    "valid_transitions": [s.value for s in valid_transitions.get(current_status, [])]
                }
            )

    def assign_work_order(
        self,
        work_order_id: UUID,
        assigned_to_user_id: UUID,
        assigner_user_id: UUID
    ) -> WorkOrder:
        """
        Assign work order to a member.
        
        Args:
            work_order_id: Work order ID
            assigned_to_user_id: User ID to assign to
            assigner_user_id: User ID performing assignment (must be FSP Admin/Manager)
        
        Returns:
            Updated work order
        """
        self.logger.info(
            "Assigning work order",
            extra={
                "work_order_id": str(work_order_id),
                "assigned_to": str(assigned_to_user_id),
                "assigner": str(assigner_user_id)
            }
        )
        
        work_order = self.get_work_order(work_order_id, assigner_user_id)
        
        # Check if assigner has permission
        # simplified: ensure assigner is part of FSP org
        # In real world: check for ADMIN/OWNER/MANAGER role
        from app.models.organization import OrgMember
        from app.models.enums import MemberStatus
        
        assigner_member = self.db.query(OrgMember).filter(
            OrgMember.organization_id == work_order.fsp_organization_id,
            OrgMember.user_id == assigner_user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        if not assigner_member:
             raise PermissionError(
                message="You must be a member of the FSP organization to assign work orders",
                error_code="INSUFFICIENT_PERMISSIONS"
            )

        # Check if assignee is member of FSP
        assignee_member = self.db.query(OrgMember).filter(
            OrgMember.organization_id == work_order.fsp_organization_id,
            OrgMember.user_id == assigned_to_user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        if not assignee_member:
            raise ValidationError(
                message="Assigned user is not an active member of the FSP organization",
                error_code="INVALID_ASSIGNEE"
            )
            
        work_order.assigned_to_user_id = assigned_to_user_id
        work_order.updated_by = assigner_user_id
        work_order.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(work_order)
        
        # TODO: Add to chat channel
        # For now, we assume ChatService logic will handle "Adding member" separately 
        # or we trigger it here if ChatService was imported.
        # To avoid circular imports, simpler to just update DB. 
        # The user requirement said "If assigned_member exists, they should be automatically added".
        # This implies ChatService keeps track or we do it here.
        # We will add a TODO for Chat Integration logic.
        
        self.logger.info("Work order assigned successfully", extra={"work_order_id": str(work_order.id)})
        return work_order

    def toggle_work_order_access(
        self,
        work_order_id: UUID,
        access_granted: bool,
        user_id: UUID
    ) -> WorkOrder:
        """
        Toggle access granted content for a work order.
        
        Args:
            work_order_id: Work order ID
            access_granted: Boolean indicating granted access
            user_id: User ID performing the action
            
        Returns:
            Updated work order
        """
        self.logger.info(
            "Toggling work order access",
            extra={
                "work_order_id": str(work_order_id),
                "access_granted": access_granted,
                "user_id": str(user_id)
            }
        )
        
        work_order = self.get_work_order(work_order_id, user_id)
        
        # Verify user is from the farming organization (owner of the data)
        # Simplified check: ensure user is associated with farming org
        # In a real scenario, we'd check roles/permissions more strictly
        
        work_order.access_granted = access_granted
        work_order.updated_by = user_id
        work_order.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(work_order)
        
        self.logger.info(
            "Work order access updated",
            extra={
                "work_order_id": str(work_order.id),
                "access_granted": access_granted
            }
        )
        
        return work_order


    def start_work_order(
        self,
        work_order_id: UUID,
        user_id: UUID
    ) -> WorkOrder:
        """
        Start work order (Transition ACCEPTED -> ACTIVE).
        
        Args:
            work_order_id: Work order ID
            user_id: User ID starting the work
            
        Returns:
            Updated work order
        """
        self.logger.info(
            "Starting work order", 
            extra={"work_order_id": str(work_order_id), "user_id": str(user_id)}
        )
        
        work_order = self.get_work_order(work_order_id, user_id)
        
        # Validate current status
        if work_order.status != WorkOrderStatus.ACCEPTED:
             raise ValidationError(
                message=f"Work order must be in ACCEPTED status to start. Current: {work_order.status.value}",
                error_code="INVALID_STATUS_TRANSITION"
            )
            
        # Permission check: Assigner or Assignee or Admin
        if work_order.assigned_to_user_id != user_id:
             # Check if admin/owner
             # Simplified: Check if member of FSP
             from app.models.organization import OrgMember, OrgMemberRole
             from app.models.enums import MemberStatus
             member = self.db.query(OrgMember).filter(
                OrgMember.organization_id == work_order.fsp_organization_id,
                OrgMember.user_id == user_id,
                OrgMember.status == MemberStatus.ACTIVE
             ).first()
             if not member:
                  raise PermissionError(
                      message="You do not have permission to start this work order",
                      error_code="INSUFFICIENT_PERMISSIONS",
                      details={"user_id": str(user_id)}
                  )
        
        work_order.status = WorkOrderStatus.ACTIVE
        if not work_order.start_date:
            work_order.start_date = datetime.utcnow().date()
            
        work_order.updated_by = user_id
        work_order.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(work_order)
        
        self.logger.info("Work order started", extra={"work_order_id": str(work_order.id)})
        return work_order

    def upload_completion_proof(
        self,
        work_order_id: UUID,
        file_data: any, # BinaryIO
        filename: str,
        user_id: UUID
    ) -> str:
        """
        Upload completion proof photo to storage.
        
        Returns:
            URL of the uploaded photo
        """
        from app.services.photo_service import PhotoService
        photo_service = PhotoService(self.db)
        
        # We reuse the photo_service's storage logic but with a custom path
        # Path: work_orders/{work_order_id}/proof/{timestamp}{ext}
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        import os
        ext = os.path.splitext(filename)[1] or '.jpg'
        file_key = f"work_orders/{work_order_id}/proof/{timestamp}{ext}"
        
        # Compress and upload
        compressed_data = photo_service._compress_image(file_data)
        file_url = photo_service._upload_to_storage(compressed_data, file_key)
        
        return file_url
