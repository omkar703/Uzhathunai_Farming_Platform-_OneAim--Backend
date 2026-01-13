"""
BFF endpoint for farming organization dashboard.
Aggregates data from multiple services in a single call.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/farming/dashboard")
def get_farming_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    BFF endpoint: Get farming organization dashboard data.
    Aggregates data from multiple services in one call to reduce network round trips.
    
    Returns:
        Dashboard data including:
        - stats: Quick stats (farms, crops, schedules, services, issues, users)
        - actionRequired: Items requiring user attention
        - recentActivity: Recent activity feed
    """
    service = DashboardService(db)
    
    # Get current organization from user context
    # Assuming user has current_organization_id set
    if not hasattr(current_user, 'current_organization_id') or not current_user.current_organization_id:
        # Fallback: get first active organization membership
        from app.models import OrgMember, MemberStatus
        member = db.query(OrgMember).filter(
            OrgMember.user_id == current_user.id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        if not member:
            return {
                'stats': {
                    'farms': 0,
                    'activeCrops': 0,
                    'activeSchedules': 0,
                    'activeServices': 0,
                    'openIssues': 0,
                    'activeUsers': 0
                },
                'actionRequired': {
                    'pendingRecommendations': [],
                    'unansweredQueries': [],
                    'pendingWorkOrders': [],
                    'unresolvedIssues': [],
                    'overdueTasks': []
                },
                'recentActivity': []
            }
        
        org_id = member.organization_id
    else:
        org_id = current_user.current_organization_id
    
    return service.get_farming_dashboard(
        user_id=current_user.id,
        org_id=org_id
    )
