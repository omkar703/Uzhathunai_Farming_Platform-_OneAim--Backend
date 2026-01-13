"""
Query service for Uzhathunai v2.0.

Handles query creation, status updates, and filtering.
Validates active work order requirements.
"""
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.query import Query
from app.models.work_order import WorkOrder
from app.models.enums import QueryStatus, WorkOrderStatus
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.core.logging import get_logger

logger = get_logger(__name__)


class QueryService:
    """Service for managing queries."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_query(
        self,
        farming_organization_id: UUID,
        fsp_organization_id: UUID,
        work_order_id: UUID,
        title: str,
        description: str,
        user_id: UUID,
        farm_id: Optional[UUID] = None,
        plot_id: Optional[UUID] = None,
        crop_id: Optional[UUID] = None,
        priority: str = 'MEDIUM'
    ) -> Query:
        """
        Create a new query.
        
        Validates:
        - Work order exists and is ACTIVE
        - Farming organization has active work order with FSP
        
        Requirements: 12.1, 12.2, 12.5, 12.9
        """
        # Validate work order exists
        work_order = self.db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if not work_order:
            raise NotFoundError(
                message=f"Work order {work_order_id} not found",
                error_code="WORK_ORDER_NOT_FOUND",
                details={"work_order_id": str(work_order_id)}
            )
        
        # Validate work order is ACTIVE (Requirement 12.2)
        if work_order.status != WorkOrderStatus.ACTIVE:
            raise ValidationError(
                message=f"Cannot create query for work order with status {work_order.status}. Work order must be ACTIVE.",
                error_code="WORK_ORDER_NOT_ACTIVE",
                details={
                    "work_order_id": str(work_order_id),
                    "work_order_status": work_order.status.value,
                    "required_status": "ACTIVE"
                }
            )
        
        # Validate work order matches organizations
        if work_order.farming_organization_id != farming_organization_id:
            raise ValidationError(
                message="Work order does not belong to farming organization",
                error_code="WORK_ORDER_ORG_MISMATCH",
                details={
                    "work_order_id": str(work_order_id),
                    "expected_farming_org": str(farming_organization_id),
                    "actual_farming_org": str(work_order.farming_organization_id)
                }
            )
        
        if work_order.fsp_organization_id != fsp_organization_id:
            raise ValidationError(
                message="Work order does not belong to FSP organization",
                error_code="WORK_ORDER_FSP_MISMATCH",
                details={
                    "work_order_id": str(work_order_id),
                    "expected_fsp_org": str(fsp_organization_id),
                    "actual_fsp_org": str(work_order.fsp_organization_id)
                }
            )
        
        # Validate priority level (Requirement 12.6)
        valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
        if priority not in valid_priorities:
            raise ValidationError(
                message=f"Invalid priority level. Must be one of: {', '.join(valid_priorities)}",
                error_code="INVALID_PRIORITY",
                details={"priority": priority, "valid_priorities": valid_priorities}
            )
        
        # Generate query number (Requirement 12.4)
        query_number = self._generate_query_number()
        
        # Create query (Requirement 12.1)
        query = Query(
            farming_organization_id=farming_organization_id,
            fsp_organization_id=fsp_organization_id,
            work_order_id=work_order_id,
            query_number=query_number,
            title=title,
            description=description,
            farm_id=farm_id,
            plot_id=plot_id,
            crop_id=crop_id,
            status=QueryStatus.OPEN,  # Requirement 12.5
            priority=priority,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(query)
        self.db.commit()
        self.db.refresh(query)
        
        logger.info(
            "Query created",
            extra={
                "query_id": str(query.id),
                "query_number": query_number,
                "farming_org_id": str(farming_organization_id),
                "fsp_org_id": str(fsp_organization_id),
                "work_order_id": str(work_order_id),
                "priority": priority,
                "created_by": str(user_id)
            }
        )
        
        return query
    
    def update_query_status(
        self,
        query_id: UUID,
        status: QueryStatus,
        user_id: UUID,
        resolved_by: Optional[UUID] = None
    ) -> Query:
        """
        Update query status.
        
        Requirements: 12.5, 13.9, 13.13, 13.14, 13.15
        """
        query = self.db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            raise NotFoundError(
                message=f"Query {query_id} not found",
                error_code="QUERY_NOT_FOUND",
                details={"query_id": str(query_id)}
            )
        
        old_status = query.status
        query.status = status
        query.updated_by = user_id
        
        # Handle status-specific updates
        if status == QueryStatus.RESOLVED and resolved_by:
            query.resolved_at = datetime.utcnow()
            query.resolved_by = resolved_by
        elif status == QueryStatus.CLOSED:
            query.closed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(query)
        
        logger.info(
            "Query status updated",
            extra={
                "query_id": str(query_id),
                "query_number": query.query_number,
                "old_status": old_status.value,
                "new_status": status.value,
                "updated_by": str(user_id)
            }
        )
        
        return query
    
    def get_queries(
        self,
        farming_organization_id: Optional[UUID] = None,
        fsp_organization_id: Optional[UUID] = None,
        work_order_id: Optional[UUID] = None,
        status: Optional[QueryStatus] = None,
        priority: Optional[str] = None,
        crop_id: Optional[UUID] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Query], int]:
        """
        Get queries with filtering and pagination.
        
        Requirements: 12.9
        """
        query = self.db.query(Query)
        
        # Apply filters
        if farming_organization_id:
            query = query.filter(Query.farming_organization_id == farming_organization_id)
        
        if fsp_organization_id:
            query = query.filter(Query.fsp_organization_id == fsp_organization_id)
        
        if work_order_id:
            query = query.filter(Query.work_order_id == work_order_id)
        
        if status:
            query = query.filter(Query.status == status)
        
        if priority:
            query = query.filter(Query.priority == priority)
        
        if crop_id:
            query = query.filter(Query.crop_id == crop_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        queries = query.order_by(Query.created_at.desc()).offset(offset).limit(limit).all()
        
        logger.info(
            "Queries retrieved",
            extra={
                "total": total,
                "page": page,
                "limit": limit,
                "farming_org_id": str(farming_organization_id) if farming_organization_id else None,
                "fsp_org_id": str(fsp_organization_id) if fsp_organization_id else None,
                "status": status.value if status else None
            }
        )
        
        return queries, total
    
    def get_query(self, query_id: UUID) -> Query:
        """Get query by ID."""
        query = self.db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            raise NotFoundError(
                message=f"Query {query_id} not found",
                error_code="QUERY_NOT_FOUND",
                details={"query_id": str(query_id)}
            )
        
        return query
    
    def _generate_query_number(self) -> str:
        """Generate unique query number."""
        # Get count of existing queries
        count = self.db.query(Query).count()
        
        # Generate number with format Q-YYYYMMDD-XXXX
        date_str = datetime.utcnow().strftime("%Y%m%d")
        number = f"Q-{date_str}-{count + 1:04d}"
        
        # Ensure uniqueness
        while self.db.query(Query).filter(Query.query_number == number).first():
            count += 1
            number = f"Q-{date_str}-{count + 1:04d}"
        
        return number
