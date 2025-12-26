"""
Work Order Scope service for Uzhathunai v2.0.
Handles work order scope management, permissions, and FSP access validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.models.work_order import WorkOrder, WorkOrderScope
from app.models.organization import Organization
from app.models.farm import Farm
from app.models.plot import Plot
from app.models.crop import Crop
from app.models.enums import (
    WorkOrderStatus,
    WorkOrderScopeType
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


class WorkOrderScopeService:
    """Service for work order scope management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
        self.metrics = MetricsCollector()
    
    def add_work_order_scope(
        self,
        work_order_id: UUID,
        scope_items: List[Dict[str, Any]],
        user_id: UUID
    ) -> List[WorkOrderScope]:
        """
        Add scope items to work order with mixed scope support.
        
        Args:
            work_order_id: Work order ID
            scope_items: List of scope items with structure:
                {
                    "scope": "FARM" | "PLOT" | "CROP" | "ORGANIZATION",
                    "scope_id": UUID,
                    "access_permissions": {
                        "read": bool,
                        "write": bool,
                        "track": bool
                    },
                    "sort_order": int (optional)
                }
            user_id: User ID adding the scope
        
        Returns:
            List of created scope items
        
        Raises:
            NotFoundError: If work order or resources not found
            ValidationError: If validation fails
            ConflictError: If scope item already exists
        """
        self.logger.info(
            "Adding work order scope items",
            extra={
                "work_order_id": str(work_order_id),
                "scope_items_count": len(scope_items),
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
        
        try:
            created_items = []
            
            for item in scope_items:
                # Validate resource exists
                self._validate_scope_resource(
                    item['scope'],
                    item['scope_id'],
                    work_order.farming_organization_id
                )
                
                # Set default permissions if not provided
                permissions = item.get('access_permissions', {
                    'read': True,
                    'write': False,
                    'track': False
                })
                
                # Create scope item
                scope_item = WorkOrderScope(
                    work_order_id=work_order_id,
                    scope=WorkOrderScopeType(item['scope']),
                    scope_id=item['scope_id'],
                    access_permissions=permissions,
                    sort_order=item.get('sort_order', 0),
                    created_by=user_id
                )
                
                self.db.add(scope_item)
                created_items.append(scope_item)
            
            # Update scope metadata
            self._update_scope_metadata(work_order_id)
            
            self.db.commit()
            
            # Refresh items
            for item in created_items:
                self.db.refresh(item)
            
            # Metrics
            self.metrics.increment('work_order_scope.added', {
                'count': len(created_items),
                'status': 'success'
            })
            
            self.logger.info(
                "Work order scope items added successfully",
                extra={
                    "work_order_id": str(work_order_id),
                    "items_count": len(created_items),
                    "user_id": str(user_id)
                }
            )
            
            return created_items
            
        except IntegrityError as e:
            self.db.rollback()
            self.logger.error(
                "Duplicate scope item",
                extra={"work_order_id": str(work_order_id), "error": str(e)},
                exc_info=True
            )
            raise ConflictError(
                message="Scope item already exists for this work order",
                error_code="DUPLICATE_SCOPE_ITEM",
                details={"work_order_id": str(work_order_id)}
            )
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to add work order scope items",
                extra={"work_order_id": str(work_order_id), "user_id": str(user_id), "error": str(e)},
                exc_info=True
            )
            self.metrics.increment('work_order_scope.added', {
                'status': 'failure'
            })
            raise
    
    def calculate_scope_metadata(
        self,
        work_order_id: UUID
    ) -> Dict[str, int]:
        """
        Calculate scope metadata summary.
        
        Args:
            work_order_id: Work order ID
        
        Returns:
            Dictionary with counts: {
                "organizations": int,
                "farms": int,
                "plots": int,
                "crops": int,
                "total_items": int
            }
        """
        self.logger.info(
            "Calculating scope metadata",
            extra={"work_order_id": str(work_order_id)}
        )
        
        # Get all scope items
        scope_items = self.db.query(WorkOrderScope).filter(
            WorkOrderScope.work_order_id == work_order_id
        ).all()
        
        # Count by scope type
        metadata = {
            "organizations": 0,
            "farms": 0,
            "plots": 0,
            "crops": 0,
            "total_items": len(scope_items)
        }
        
        for item in scope_items:
            if item.scope == WorkOrderScopeType.ORGANIZATION:
                metadata["organizations"] += 1
            elif item.scope == WorkOrderScopeType.FARM:
                metadata["farms"] += 1
            elif item.scope == WorkOrderScopeType.PLOT:
                metadata["plots"] += 1
            elif item.scope == WorkOrderScopeType.CROP:
                metadata["crops"] += 1
        
        return metadata
    
    def update_scope_permissions(
        self,
        scope_id: UUID,
        permissions: Dict[str, bool],
        user_id: UUID
    ) -> WorkOrderScope:
        """
        Update access permissions for a scope item.
        
        Args:
            scope_id: Scope item ID
            permissions: New permissions dict with read, write, track
            user_id: User ID performing the update
        
        Returns:
            Updated scope item
        
        Raises:
            NotFoundError: If scope item not found
            ValidationError: If work order already accepted
        """
        self.logger.info(
            "Updating scope permissions",
            extra={
                "scope_id": str(scope_id),
                "permissions": permissions,
                "user_id": str(user_id)
            }
        )
        
        # Get scope item
        scope_item = self.db.query(WorkOrderScope).filter(
            WorkOrderScope.id == scope_id
        ).first()
        
        if not scope_item:
            raise NotFoundError(
                message=f"Scope item {scope_id} not found",
                error_code="SCOPE_ITEM_NOT_FOUND",
                details={"scope_id": str(scope_id)}
            )
        
        # Get work order to check status
        work_order = self.db.query(WorkOrder).filter(
            WorkOrder.id == scope_item.work_order_id
        ).first()
        
        # Allow permission updates even after acceptance (per requirements)
        # But log a warning if work order is already active
        if work_order.status in [WorkOrderStatus.ACTIVE, WorkOrderStatus.COMPLETED]:
            self.logger.warning(
                "Updating permissions on active/completed work order",
                extra={
                    "work_order_id": str(work_order.id),
                    "work_order_status": work_order.status.value
                }
            )
        
        try:
            # Update permissions
            scope_item.access_permissions = permissions
            
            self.db.commit()
            self.db.refresh(scope_item)
            
            # Metrics
            self.metrics.increment('work_order_scope.permissions_updated', {
                'status': 'success'
            })
            
            self.logger.info(
                "Scope permissions updated successfully",
                extra={
                    "scope_id": str(scope_id),
                    "user_id": str(user_id)
                }
            )
            
            return scope_item
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to update scope permissions",
                extra={"scope_id": str(scope_id), "user_id": str(user_id), "error": str(e)},
                exc_info=True
            )
            self.metrics.increment('work_order_scope.permissions_updated', {
                'status': 'failure'
            })
            raise
    
    def validate_fsp_access(
        self,
        fsp_organization_id: UUID,
        resource_type: WorkOrderScopeType,
        resource_id: UUID,
        required_permission: str
    ) -> bool:
        """
        Validate FSP has access to resource via active work order with hierarchical checking.
        
        Hierarchy:
        - ORGANIZATION scope grants access to all farms, plots, crops
        - FARM scope grants access to all plots and crops in that farm
        - PLOT scope grants access to all crops in that plot
        - CROP scope grants access to that specific crop only
        
        Args:
            fsp_organization_id: FSP organization ID
            resource_type: Type of resource (FARM, PLOT, CROP, ORGANIZATION)
            resource_id: Resource ID
            required_permission: Permission required (read, write, track)
        
        Returns:
            True if access granted
        
        Raises:
            PermissionError: If access not granted
        """
        self.logger.info(
            "Validating FSP access",
            extra={
                "fsp_org_id": str(fsp_organization_id),
                "resource_type": resource_type.value,
                "resource_id": str(resource_id),
                "required_permission": required_permission
            }
        )
        
        # Find active work orders for FSP
        active_work_orders = self.db.query(WorkOrder).filter(
            WorkOrder.fsp_organization_id == fsp_organization_id,
            WorkOrder.status == WorkOrderStatus.ACTIVE
        ).all()
        
        if not active_work_orders:
            raise PermissionError(
                message="No active work orders found for FSP organization",
                error_code="NO_ACTIVE_WORK_ORDER",
                details={"fsp_org_id": str(fsp_organization_id)}
            )
        
        # Check each work order for access
        for work_order in active_work_orders:
            # Direct scope match
            scope_item = self.db.query(WorkOrderScope).filter(
                WorkOrderScope.work_order_id == work_order.id,
                WorkOrderScope.scope == resource_type,
                WorkOrderScope.scope_id == resource_id
            ).first()
            
            if scope_item and scope_item.access_permissions.get(required_permission):
                self.logger.info(
                    "FSP access granted (direct match)",
                    extra={
                        "work_order_id": str(work_order.id),
                        "scope_type": resource_type.value
                    }
                )
                return True
            
            # Hierarchical check
            if self._check_hierarchical_access(
                work_order.id,
                resource_type,
                resource_id,
                required_permission
            ):
                return True
        
        # No access found
        raise PermissionError(
            message=f"FSP does not have '{required_permission}' access to {resource_type.value} {resource_id}",
            error_code="FSP_ACCESS_DENIED",
            details={
                "fsp_org_id": str(fsp_organization_id),
                "resource_type": resource_type.value,
                "resource_id": str(resource_id),
                "required_permission": required_permission
            }
        )
    
    def get_work_order_scope(
        self,
        work_order_id: UUID
    ) -> List[WorkOrderScope]:
        """
        Get all scope items for a work order.
        
        Args:
            work_order_id: Work order ID
        
        Returns:
            List of scope items
        """
        self.logger.info(
            "Fetching work order scope",
            extra={"work_order_id": str(work_order_id)}
        )
        
        scope_items = self.db.query(WorkOrderScope).filter(
            WorkOrderScope.work_order_id == work_order_id
        ).order_by(WorkOrderScope.sort_order).all()
        
        return scope_items
    
    def _validate_scope_resource(
        self,
        scope_type: str,
        scope_id: UUID,
        farming_org_id: UUID
    ):
        """
        Validate that scope resource exists and belongs to farming organization.
        
        Args:
            scope_type: Scope type (ORGANIZATION, FARM, PLOT, CROP)
            scope_id: Resource ID
            farming_org_id: Farming organization ID
        
        Raises:
            NotFoundError: If resource not found
            ValidationError: If resource doesn't belong to farming organization
        """
        scope_enum = WorkOrderScopeType(scope_type)
        
        if scope_enum == WorkOrderScopeType.ORGANIZATION:
            # Validate organization
            org = self.db.query(Organization).filter(
                Organization.id == scope_id
            ).first()
            
            if not org:
                raise NotFoundError(
                    message=f"Organization {scope_id} not found",
                    error_code="ORGANIZATION_NOT_FOUND",
                    details={"scope_id": str(scope_id)}
                )
            
            if org.id != farming_org_id:
                raise ValidationError(
                    message="Organization must match farming organization",
                    error_code="INVALID_ORGANIZATION_SCOPE",
                    details={"scope_id": str(scope_id)}
                )
        
        elif scope_enum == WorkOrderScopeType.FARM:
            # Validate farm
            farm = self.db.query(Farm).filter(
                Farm.id == scope_id
            ).first()
            
            if not farm:
                raise NotFoundError(
                    message=f"Farm {scope_id} not found",
                    error_code="FARM_NOT_FOUND",
                    details={"scope_id": str(scope_id)}
                )
            
            if farm.organization_id != farming_org_id:
                raise ValidationError(
                    message="Farm must belong to farming organization",
                    error_code="INVALID_FARM_SCOPE",
                    details={"scope_id": str(scope_id), "farm_org_id": str(farm.organization_id)}
                )
        
        elif scope_enum == WorkOrderScopeType.PLOT:
            # Validate plot
            plot = self.db.query(Plot).filter(
                Plot.id == scope_id
            ).first()
            
            if not plot:
                raise NotFoundError(
                    message=f"Plot {scope_id} not found",
                    error_code="PLOT_NOT_FOUND",
                    details={"scope_id": str(scope_id)}
                )
            
            # Check plot's farm belongs to farming organization
            farm = self.db.query(Farm).filter(
                Farm.id == plot.farm_id
            ).first()
            
            if not farm or farm.organization_id != farming_org_id:
                raise ValidationError(
                    message="Plot must belong to farming organization",
                    error_code="INVALID_PLOT_SCOPE",
                    details={"scope_id": str(scope_id)}
                )
        
        elif scope_enum == WorkOrderScopeType.CROP:
            # Validate crop
            crop = self.db.query(Crop).filter(
                Crop.id == scope_id
            ).first()
            
            if not crop:
                raise NotFoundError(
                    message=f"Crop {scope_id} not found",
                    error_code="CROP_NOT_FOUND",
                    details={"scope_id": str(scope_id)}
                )
            
            # Check crop's plot's farm belongs to farming organization
            plot = self.db.query(Plot).filter(
                Plot.id == crop.plot_id
            ).first()
            
            if plot:
                farm = self.db.query(Farm).filter(
                    Farm.id == plot.farm_id
                ).first()
                
                if not farm or farm.organization_id != farming_org_id:
                    raise ValidationError(
                        message="Crop must belong to farming organization",
                        error_code="INVALID_CROP_SCOPE",
                        details={"scope_id": str(scope_id)}
                    )
    
    def _update_scope_metadata(self, work_order_id: UUID):
        """
        Update work order scope metadata.
        
        Args:
            work_order_id: Work order ID
        """
        metadata = self.calculate_scope_metadata(work_order_id)
        
        work_order = self.db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if work_order:
            work_order.scope_metadata = metadata
    
    def _check_hierarchical_access(
        self,
        work_order_id: UUID,
        resource_type: WorkOrderScopeType,
        resource_id: UUID,
        required_permission: str
    ) -> bool:
        """
        Check hierarchical access for resource.
        
        Args:
            work_order_id: Work order ID
            resource_type: Resource type
            resource_id: Resource ID
            required_permission: Required permission
        
        Returns:
            True if hierarchical access granted
        """
        # Check ORGANIZATION scope (grants access to everything)
        if resource_type in [WorkOrderScopeType.FARM, WorkOrderScopeType.PLOT, WorkOrderScopeType.CROP]:
            # Get farming organization for this resource
            farming_org_id = self._get_farming_org_for_resource(resource_type, resource_id)
            
            if farming_org_id:
                org_scope = self.db.query(WorkOrderScope).filter(
                    WorkOrderScope.work_order_id == work_order_id,
                    WorkOrderScope.scope == WorkOrderScopeType.ORGANIZATION,
                    WorkOrderScope.scope_id == farming_org_id
                ).first()
                
                if org_scope and org_scope.access_permissions.get(required_permission):
                    self.logger.info(
                        "FSP access granted (organization scope)",
                        extra={"work_order_id": str(work_order_id)}
                    )
                    return True
        
        # Check FARM scope (grants access to plots and crops in that farm)
        if resource_type in [WorkOrderScopeType.PLOT, WorkOrderScopeType.CROP]:
            farm_id = self._get_farm_for_resource(resource_type, resource_id)
            
            if farm_id:
                farm_scope = self.db.query(WorkOrderScope).filter(
                    WorkOrderScope.work_order_id == work_order_id,
                    WorkOrderScope.scope == WorkOrderScopeType.FARM,
                    WorkOrderScope.scope_id == farm_id
                ).first()
                
                if farm_scope and farm_scope.access_permissions.get(required_permission):
                    self.logger.info(
                        "FSP access granted (farm scope)",
                        extra={"work_order_id": str(work_order_id)}
                    )
                    return True
        
        # Check PLOT scope (grants access to crops in that plot)
        if resource_type == WorkOrderScopeType.CROP:
            crop = self.db.query(Crop).filter(Crop.id == resource_id).first()
            
            if crop:
                plot_scope = self.db.query(WorkOrderScope).filter(
                    WorkOrderScope.work_order_id == work_order_id,
                    WorkOrderScope.scope == WorkOrderScopeType.PLOT,
                    WorkOrderScope.scope_id == crop.plot_id
                ).first()
                
                if plot_scope and plot_scope.access_permissions.get(required_permission):
                    self.logger.info(
                        "FSP access granted (plot scope)",
                        extra={"work_order_id": str(work_order_id)}
                    )
                    return True
        
        return False
    
    def _get_farming_org_for_resource(
        self,
        resource_type: WorkOrderScopeType,
        resource_id: UUID
    ) -> Optional[UUID]:
        """Get farming organization ID for a resource."""
        if resource_type == WorkOrderScopeType.FARM:
            farm = self.db.query(Farm).filter(Farm.id == resource_id).first()
            return farm.organization_id if farm else None
        
        elif resource_type == WorkOrderScopeType.PLOT:
            plot = self.db.query(Plot).filter(Plot.id == resource_id).first()
            if plot:
                farm = self.db.query(Farm).filter(Farm.id == plot.farm_id).first()
                return farm.organization_id if farm else None
        
        elif resource_type == WorkOrderScopeType.CROP:
            crop = self.db.query(Crop).filter(Crop.id == resource_id).first()
            if crop:
                plot = self.db.query(Plot).filter(Plot.id == crop.plot_id).first()
                if plot:
                    farm = self.db.query(Farm).filter(Farm.id == plot.farm_id).first()
                    return farm.organization_id if farm else None
        
        return None
    
    def _get_farm_for_resource(
        self,
        resource_type: WorkOrderScopeType,
        resource_id: UUID
    ) -> Optional[UUID]:
        """Get farm ID for a resource."""
        if resource_type == WorkOrderScopeType.PLOT:
            plot = self.db.query(Plot).filter(Plot.id == resource_id).first()
            return plot.farm_id if plot else None
        
        elif resource_type == WorkOrderScopeType.CROP:
            crop = self.db.query(Crop).filter(Crop.id == resource_id).first()
            if crop:
                plot = self.db.query(Plot).filter(Plot.id == crop.plot_id).first()
                return plot.farm_id if plot else None
        
        return None
