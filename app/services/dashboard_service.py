"""
Dashboard service for aggregating data from multiple sources.
Implements BFF pattern for optimized dashboard loading.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Dict, List, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta

from app.core.logging import get_logger
from app.core.exceptions import PermissionError
from app.models import (
    Farm,
    Plot,
    Crop,
    Schedule,
    WorkOrder,
    Query,
    OrgMember,
    Audit,
    ScheduleTask,
    TaskActual,
    Organization
)
from app.models.enums import (
    MemberStatus,
    WorkOrderStatus,
    QueryStatus,
    AuditStatus,
    TaskStatus,
    CropLifecycle,
    OrganizationType
)

logger = get_logger(__name__)


class DashboardService:
    """Service for dashboard data aggregation."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    def get_farming_dashboard(self, user_id: UUID, org_id: UUID) -> Dict[str, Any]:
        """
        Get aggregated dashboard data for farming organization.
        
        Args:
            user_id: Current user ID
            org_id: Organization ID
            
        Returns:
            Dictionary containing stats, action items, and recent activity
        """
        # Validate organization membership
        self._validate_org_membership(user_id, org_id)
        
        # Log operation
        self.logger.info(
            "Fetching farming dashboard",
            extra={
                "user_id": str(user_id),
                "organization_id": str(org_id),
                "action": "get_dashboard"
            }
        )
        
        try:
            # Get stats
            stats = {
                'farms': self._count_farms(org_id),
                'activeCrops': self._count_active_crops(org_id),
                'activeSchedules': self._count_active_schedules(org_id),
                'activeServices': self._count_active_work_orders(org_id),
                'openIssues': self._count_open_queries(org_id),
                'activeUsers': self._count_active_users(org_id)
            }
            
            # Get action required items
            action_required = {
                'pendingRecommendations': self._get_pending_recommendations(org_id),
                'unansweredQueries': self._get_unanswered_queries(org_id),
                'pendingWorkOrders': self._get_pending_work_orders(org_id),
                'unresolvedIssues': self._get_unresolved_issues(org_id),
                'overdueTasks': self._get_overdue_tasks(org_id)
            }
            
            # Get recent activity
            recent_activity = self._get_recent_activity(org_id, limit=5)
            
            self.logger.info(
                "Farming dashboard fetched successfully",
                extra={
                    "user_id": str(user_id),
                    "organization_id": str(org_id),
                    "stats": stats
                }
            )
            
            return {
                'stats': stats,
                'actionRequired': action_required,
                'recentActivity': recent_activity
            }
            
        except Exception as e:
            self.logger.error(
                "Failed to fetch farming dashboard",
                extra={
                    "user_id": str(user_id),
                    "organization_id": str(org_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def get_fsp_dashboard(self, user_id: UUID, org_id: UUID) -> Dict[str, Any]:
        """
        Get aggregated dashboard data for FSP organization.
        
        Args:
            user_id: Current user ID
            org_id: Organization ID
            
        Returns:
            Dictionary containing stats, action items, and recent activity
        """
        # Validate organization membership
        self._validate_org_membership(user_id, org_id)
        
        # Log operation
        self.logger.info(
            "Fetching FSP dashboard",
            extra={
                "user_id": str(user_id),
                "organization_id": str(org_id),
                "action": "get_dashboard"
            }
        )
        
        try:
            # Get stats
            stats = {
                'activeClients': self._count_fsp_clients(org_id),
                'activeOrders': self._count_fsp_work_orders(org_id),
                'auditsInProgress': self._count_audits_in_progress(org_id),
                'pendingRecommendations': self._count_pending_recommendations(org_id),
                'pendingQueries': self._count_pending_queries(org_id),
                'activeTeam': self._count_active_users(org_id)
            }
            
            # Get action required items
            action_required = {
                'newWorkOrderRequests': self._get_new_work_order_requests(org_id),
                'auditsToFinalize': self._get_audits_to_finalize(org_id),
                'clientQueries': self._get_client_queries(org_id),
                'recommendationsAwaitingResponse': self._get_recommendations_awaiting_response(org_id),
                'marketplaceInquiries': []  # Placeholder for future implementation
            }
            
            # Get recent activity
            recent_activity = self._get_recent_activity(org_id, limit=5)
            
            self.logger.info(
                "FSP dashboard fetched successfully",
                extra={
                    "user_id": str(user_id),
                    "organization_id": str(org_id),
                    "stats": stats
                }
            )
            
            return {
                'stats': stats,
                'actionRequired': action_required,
                'recentActivity': recent_activity
            }
            
        except Exception as e:
            self.logger.error(
                "Failed to fetch FSP dashboard",
                extra={
                    "user_id": str(user_id),
                    "organization_id": str(org_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def _validate_org_membership(self, user_id: UUID, org_id: UUID) -> None:
        """Validate user is a member of the organization."""
        member = self.db.query(OrgMember).filter(
            OrgMember.user_id == user_id,
            OrgMember.organization_id == org_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        if not member:
            raise PermissionError(
                message="User is not a member of this organization",
                error_code="NOT_A_MEMBER",
                details={"user_id": str(user_id), "organization_id": str(org_id)}
            )
    
    # Farming Organization Stats Methods
    
    def _count_farms(self, org_id: UUID) -> int:
        """Count total farms for organization."""
        return self.db.query(Farm).filter(
            Farm.organization_id == org_id
        ).count()
    
    def _count_active_crops(self, org_id: UUID) -> int:
        """Count active crops (not harvested/closed) for organization."""
        return self.db.query(Crop).join(Plot, Crop.plot_id == Plot.id).join(Farm, Plot.farm_id == Farm.id).filter(
            Farm.organization_id == org_id,
            Crop.lifecycle.notin_([CropLifecycle.COMPLETED, CropLifecycle.TERMINATED, CropLifecycle.CLOSED])
        ).count()
    
    def _count_active_schedules(self, org_id: UUID) -> int:
        """Count active schedules for organization."""
        return self.db.query(Schedule).join(Crop, Schedule.crop_id == Crop.id).join(Plot, Crop.plot_id == Plot.id).join(Farm, Plot.farm_id == Farm.id).filter(
            Farm.organization_id == org_id,
            Schedule.is_active == True
        ).count()
    
    def _count_active_work_orders(self, org_id: UUID) -> int:
        """Count active work orders for organization."""
        return self.db.query(WorkOrder).filter(
            WorkOrder.farming_organization_id == org_id,
            WorkOrder.status.in_([
                WorkOrderStatus.PENDING,
                WorkOrderStatus.ACCEPTED,
                WorkOrderStatus.ACTIVE
            ])
        ).count()
    
    def _count_open_queries(self, org_id: UUID) -> int:
        """Count open queries for organization."""
        return self.db.query(Query).filter(
            Query.farming_organization_id == org_id,
            Query.status.in_([QueryStatus.OPEN, QueryStatus.IN_PROGRESS])
        ).count()
    
    def _count_active_users(self, org_id: UUID) -> int:
        """Count active users in organization."""
        return self.db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).count()
    
    # FSP Organization Stats Methods
    
    def _count_fsp_clients(self, org_id: UUID) -> int:
        """Count active clients for FSP."""
        # Count unique client organizations from work orders
        return self.db.query(func.count(func.distinct(WorkOrder.farming_organization_id))).filter(
            WorkOrder.fsp_organization_id == org_id,
            WorkOrder.status != WorkOrderStatus.CANCELLED
        ).scalar() or 0
    
    def _count_fsp_work_orders(self, org_id: UUID) -> int:
        """Count active work orders for FSP."""
        return self.db.query(WorkOrder).filter(
            WorkOrder.fsp_organization_id == org_id,
            WorkOrder.status.in_([
                WorkOrderStatus.PENDING,
                WorkOrderStatus.ACCEPTED,
                WorkOrderStatus.ACTIVE
            ])
        ).count()
    
    def _count_audits_in_progress(self, org_id: UUID) -> int:
        """Count audits in progress for FSP."""
        return self.db.query(Audit).filter(
            Audit.fsp_organization_id == org_id,
            Audit.status == AuditStatus.IN_PROGRESS
        ).count()
    
    def _count_pending_recommendations(self, org_id: UUID) -> int:
        """Count pending recommendations for FSP."""
        # Placeholder - implement when recommendation model is available
        return 0
    
    def _count_pending_queries(self, org_id: UUID) -> int:
        """Count pending queries for FSP."""
        return self.db.query(Query).filter(
            Query.fsp_organization_id == org_id,
            Query.status.in_([QueryStatus.OPEN, QueryStatus.IN_PROGRESS])
        ).count()
    
    # Action Required Methods
    
    def _get_pending_recommendations(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get pending recommendations requiring action."""
        # Placeholder - implement when recommendation model is available
        return []
    
    def _get_unanswered_queries(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get unanswered queries."""
        queries = self.db.query(Query).filter(
            Query.farming_organization_id == org_id,
            Query.status == QueryStatus.OPEN
        ).order_by(Query.created_at.desc()).limit(5).all()
        
        return [
            {
                'id': str(query.id),
                'type': 'query',
                'title': f"Query about {query.title or 'farming'}",
                'count': 1,
                'urgency': 'pending',
                'timestamp': query.created_at.isoformat()
            }
            for query in queries
        ]
    
    def _get_pending_work_orders(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get pending work orders."""
        work_orders = self.db.query(WorkOrder).filter(
            WorkOrder.farming_organization_id == org_id,
            WorkOrder.status == WorkOrderStatus.PENDING
        ).order_by(WorkOrder.created_at.desc()).limit(5).all()
        
        return [
            {
                'id': str(wo.id),
                'type': 'work_order',
                'title': f"Work Order #{wo.id}",
                'count': 1,
                'urgency': 'pending',
                'timestamp': wo.created_at.isoformat()
            }
            for wo in work_orders
        ]
    
    def _get_unresolved_issues(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get unresolved issues (open queries)."""
        return self._get_unanswered_queries(org_id)
    
    def _get_overdue_tasks(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get overdue tasks."""
        today = datetime.now().date()
        
        # Get overdue schedule tasks
        overdue_tasks = self.db.query(ScheduleTask).join(Schedule, ScheduleTask.schedule_id == Schedule.id).join(Crop, Schedule.crop_id == Crop.id).join(Plot, Crop.plot_id == Plot.id).join(Farm, Plot.farm_id == Farm.id).filter(
            Farm.organization_id == org_id,
            ScheduleTask.due_date < today,
            ScheduleTask.status != TaskStatus.COMPLETED
        ).order_by(ScheduleTask.due_date).limit(5).all()
        
        return [
            {
                'id': str(task.id),
                'type': 'task',
                'title': f"Overdue task",
                'count': 1,
                'urgency': 'urgent',
                'timestamp': task.due_date.isoformat()
            }
            for task in overdue_tasks
        ]
    
    # FSP Action Required Methods
    
    def _get_new_work_order_requests(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get new work order requests for FSP."""
        work_orders = self.db.query(WorkOrder).filter(
            WorkOrder.fsp_organization_id == org_id,
            WorkOrder.status == WorkOrderStatus.PENDING
        ).order_by(WorkOrder.created_at.desc()).limit(5).all()
        
        return [
            {
                'id': str(wo.id),
                'type': 'work_order',
                'title': f"New Work Order Request",
                'count': 1,
                'urgency': 'pending',
                'timestamp': wo.created_at.isoformat()
            }
            for wo in work_orders
        ]
    
    def _get_audits_to_finalize(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get audits that need to be finalized."""
        audits = self.db.query(Audit).filter(
            Audit.fsp_organization_id == org_id,
            Audit.status == AuditStatus.IN_PROGRESS
        ).order_by(Audit.created_at.desc()).limit(5).all()
        
        return [
            {
                'id': str(audit.id),
                'type': 'audit',
                'title': f"Audit to finalize",
                'count': 1,
                'urgency': 'pending',
                'timestamp': audit.created_at.isoformat()
            }
            for audit in audits
        ]
    
    def _get_client_queries(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get client queries for FSP."""
        queries = self.db.query(Query).filter(
            Query.fsp_organization_id == org_id,
            Query.status == QueryStatus.OPEN
        ).order_by(Query.created_at.desc()).limit(5).all()
        
        return [
            {
                'id': str(query.id),
                'type': 'query',
                'title': f"Client Query",
                'count': 1,
                'urgency': 'pending',
                'timestamp': query.created_at.isoformat()
            }
            for query in queries
        ]
    
    def _get_recommendations_awaiting_response(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get recommendations awaiting response."""
        # Placeholder - implement when recommendation model is available
        return []
    
    # Recent Activity Methods
    
    def _get_recent_activity(self, org_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent activity for organization."""
        activities = []
        
        # Get recent farms
        recent_farms = self.db.query(Farm).filter(
            Farm.organization_id == org_id
        ).order_by(Farm.created_at.desc()).limit(2).all()
        
        for farm in recent_farms:
            activities.append({
                'id': str(farm.id),
                'icon': 'barn',
                'description': f"Farm '{farm.name}' was created",
                'timestamp': farm.created_at.isoformat(),
                'relatedEntity': 'farm',
                'relatedEntityId': str(farm.id)
            })
        
        # Get recent crops
        recent_crops = self.db.query(Crop).join(Plot, Crop.plot_id == Plot.id).join(Farm, Plot.farm_id == Farm.id).filter(
            Farm.organization_id == org_id
        ).order_by(Crop.created_at.desc()).limit(2).all()
        
        for crop in recent_crops:
            activities.append({
                'id': str(crop.id),
                'icon': 'sprout',
                'description': f"Crop was planted",
                'timestamp': crop.created_at.isoformat(),
                'relatedEntity': 'crop',
                'relatedEntityId': str(crop.id)
            })
        
        # Get recent work orders
        recent_work_orders = self.db.query(WorkOrder).filter(
            or_(
                WorkOrder.farming_organization_id == org_id,
                WorkOrder.fsp_organization_id == org_id
            )
        ).order_by(WorkOrder.created_at.desc()).limit(1).all()
        
        for wo in recent_work_orders:
            activities.append({
                'id': str(wo.id),
                'icon': 'briefcase',
                'description': f"Work order was created",
                'timestamp': wo.created_at.isoformat(),
                'relatedEntity': 'work_order',
                'relatedEntityId': str(wo.id)
            })
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
