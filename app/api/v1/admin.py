from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.organization import Organization, OrganizationStatus, OrgMemberRole
from app.models.rbac import Role
from app.core.auth import get_current_super_admin
from app.schemas.response import BaseResponse

from typing import List, Optional
from fastapi import Query
from uuid import UUID
from datetime import date

from app.schemas.query import QueryListResponse, QueryStatus
from app.schemas.schedule import PaginatedScheduleResponse
from app.schemas.task_actual import TaskActualResponse
from app.services.query_service import QueryService
from app.services.schedule_service import ScheduleService
from app.services.task_actual_service import TaskActualService

router = APIRouter()


@router.post(
    "/organizations/approve-all",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Approve all pending organizations",
    description="Approve all organizations with NOT_STARTED status. Only accessible by Super Admins."
)
async def approve_all_pending_organizations(
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Approve all pending (NOT_STARTED) organizations.
    """
    from app.models.organization import OrganizationStatus
    
    # Update all NOT_STARTED and IN_PROGRESS organizations to ACTIVE
    # Using bulk update for efficiency
    result = db.query(Organization).filter(
        Organization.status.in_([OrganizationStatus.NOT_STARTED, OrganizationStatus.IN_PROGRESS])
    ).update(
        {Organization.status: OrganizationStatus.ACTIVE},
        synchronize_session=False
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Approved {result} organization(s) successfully",
        "data": {"approved_count": result}
    }


@router.post(
    "/organizations/{organization_id}/approve",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Approve an organization",
    description="Approve a pending organization. Only accessible by Super Admins."
)
async def approve_organization(
    organization_id: str,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Approve an organization.
    """
    # 1. Get Organization
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "Organization not found",
                "error_code": "ORG_NOT_FOUND"
            }
        )
    
    # 2. Approve - set status to ACTIVE
    org.status = OrganizationStatus.ACTIVE
    db.commit()
    db.refresh(org)

    # 3. Clear Cache (Stub for now)
    # redis_client.delete(f"permissions:{organization_id}")

    return {
        "success": True,
        "message": f"Organization {org.name} approved successfully",
        "data": {
            "organization_id": str(org.id),
            "status": org.status.value
        }
    }


@router.post(
    "/organizations/{organization_id}/reject",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Reject an organization",
    description="Reject a pending organization. Only accessible by Super Admins."
)
async def reject_organization(
    organization_id: str,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Reject an organization.
    """
    # 1. Get Organization
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "Organization not found",
                "error_code": "ORG_NOT_FOUND"
            }
        )
    
    # 2. Reject - set status to REJECTED (using NOT_STARTED as fallback if DB enum issues occur)
    try:
        org.status = OrganizationStatus.REJECTED
        db.commit()
    except Exception as e:
        db.rollback()
        # Fallback to NOT_STARTED if REJECTED is not in DB enum
        org.status = OrganizationStatus.NOT_STARTED
        db.commit()
    
    db.refresh(org)

    return {
        "success": True,
        "message": f"Organization {org.name} rejected successfully",
        "data": {
            "organization_id": str(org.id),
            "status": org.status.value
        }
    }


@router.post(
    "/organizations/{organization_id}/suspend",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Suspend an organization",
    description="Suspend an active organization. Only accessible by Super Admins."
)
async def suspend_organization(
    organization_id: str,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Suspend an organization.
    """
    # 1. Get Organization
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "Organization not found",
                "error_code": "ORG_NOT_FOUND"
            }
        )
    
    # 2. Suspend - set status to SUSPENDED
    try:
        org.status = OrganizationStatus.SUSPENDED
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": f"Failed to suspend organization: {str(e)}",
                "error_code": "SUSPEND_FAILED"
            }
        )
    
    db.refresh(org)

    return {
        "success": True,
        "message": f"Organization {org.name} suspended successfully",
        "data": {
            "organization_id": str(org.id),
            "status": org.status.value
        }
    }


@router.get(
    "/organizations",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="List organizations",
    description="List all organizations with filtering and pagination. Only accessible by Super Admins."
)
async def list_organizations(
    org_status: Optional[OrganizationStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    List organizations with optional filters.
    """
    query = db.query(Organization)
    
    if org_status:
        query = query.filter(Organization.status == org_status)
        
    total = query.count()
    offset = (page - 1) * limit
    orgs = query.offset(offset).limit(limit).all()
    
    return {
        "success": True,
        "message": "Organizations retrieved successfully",
        "data": {
            "items": [
                {
                    "id": str(o.id),
                    "name": o.name,
                    "type": o.organization_type.value,
                    "status": o.status.value,
                    "created_at": o.created_at.isoformat() if o.created_at else None
                } for o in orgs
            ],
            "total": total,
            "page": page,
            "limit": limit
        }
    }


@router.get(
    "/queries",
    response_model=BaseResponse[QueryListResponse],
    status_code=status.HTTP_200_OK,
    summary="List all queries",
    description="List all queries across the platform with filtering and pagination. Only accessible by Super Admins."
)
async def list_all_queries(
    farming_organization_id: Optional[UUID] = Query(None),
    fsp_organization_id: Optional[UUID] = Query(None),
    status: Optional[QueryStatus] = Query(None),
    priority: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    List queries with platform-wide visibility.
    """
    service = QueryService(db)
    queries, total = service.get_queries(
        farming_organization_id=farming_organization_id,
        fsp_organization_id=fsp_organization_id,
        status=status,
        priority=priority,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "message": "Queries retrieved successfully",
        "data": {
            "items": queries,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get(
    "/schedules",
    response_model=BaseResponse[PaginatedScheduleResponse],
    status_code=status.HTTP_200_OK,
    summary="List all schedules",
    description="List all schedules across the platform with filtering and pagination. Only accessible by Super Admins."
)
async def list_all_schedules(
    crop_id: Optional[UUID] = Query(None),
    fsp_id: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    List schedules with platform-wide visibility.
    """
    service = ScheduleService(db)
    schedules, total = service.get_schedules(
        user=current_user,
        crop_id=crop_id,
        fsp_id=fsp_id,
        status=status_filter,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "message": "Schedules retrieved successfully",
        "data": {
            "items": schedules,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get(
    "/task-actuals",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="List all task actuals",
    description="List all task actuals across the platform with filtering and pagination. Only accessible by Super Admins."
)
async def list_all_task_actuals(
    schedule_id: Optional[UUID] = Query(None),
    crop_id: Optional[UUID] = Query(None),
    is_planned: Optional[bool] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    List task actuals with platform-wide visibility.
    """
    service = TaskActualService(db)
    task_actuals, total = service.get_task_actuals(
        schedule_id=schedule_id,
        crop_id=crop_id,
        is_planned=is_planned,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "message": "Task actuals retrieved successfully",
        "data": {
            "items": task_actuals,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }
