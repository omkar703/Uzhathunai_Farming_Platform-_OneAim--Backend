"""
Query API endpoints for Uzhathunai v2.0.

Endpoints for query management, responses, and schedule change proposals.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query as QueryParam
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.enums import QueryStatus
from app.services.query_service import QueryService
from app.services.query_response_service import QueryResponseService
from app.schemas.query import (
    QueryCreate,
    QueryUpdate,
    QueryStatusUpdate,
    QueryResponse,
    QueryListResponse,
    QueryResponseCreate,
    QueryResponseResponse as QueryResponseSchema,
    QueryPhotoCreate,
    QueryPhotoResponse,
    ScheduleChangeProposal
)
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/queries", tags=["Queries"])


@router.post("", response_model=QueryResponse, status_code=201)
def create_query(
    data: QueryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new query.
    
    Validates:
    - Work order exists and is ACTIVE
    - Farming organization has active work order with FSP
    
    Requirements: 12.1, 12.2, 12.5, 12.9
    """
    service = QueryService(db)
    
    query = service.create_query(
        farming_organization_id=data.farming_organization_id,
        fsp_organization_id=data.fsp_organization_id,
        work_order_id=data.work_order_id,
        title=data.title,
        description=data.description,
        user_id=current_user.id,
        farm_id=data.farm_id,
        plot_id=data.plot_id,
        crop_id=data.crop_id,
        priority=data.priority
    )
    
    return query


@router.get("", response_model=QueryListResponse)
def get_queries(
    farming_organization_id: Optional[UUID] = QueryParam(None),
    fsp_organization_id: Optional[UUID] = QueryParam(None),
    work_order_id: Optional[UUID] = QueryParam(None),
    status: Optional[QueryStatus] = QueryParam(None),
    priority: Optional[str] = QueryParam(None),
    crop_id: Optional[UUID] = QueryParam(None),
    page: int = QueryParam(1, ge=1),
    limit: int = QueryParam(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get queries with filtering and pagination.
    
    Supports filtering by:
    - farming_organization_id
    - fsp_organization_id
    - work_order_id
    - status
    - priority
    - crop_id
    
    Requirements: 12.9
    """
    service = QueryService(db)
    
    queries, total = service.get_queries(
        farming_organization_id=farming_organization_id,
        fsp_organization_id=fsp_organization_id,
        work_order_id=work_order_id,
        status=status,
        priority=priority,
        crop_id=crop_id,
        page=page,
        limit=limit
    )
    
    return {
        "items": queries,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/{query_id}", response_model=QueryResponse)
def get_query(
    query_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get query by ID.
    
    Requirements: 12.8
    """
    service = QueryService(db)
    query = service.get_query(query_id)
    return query


@router.put("/{query_id}/status", response_model=QueryResponse)
def update_query_status(
    query_id: UUID,
    data: QueryStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update query status.
    
    Supports status transitions:
    - OPEN → IN_PROGRESS
    - IN_PROGRESS → PENDING_CLARIFICATION
    - IN_PROGRESS → RESOLVED
    - RESOLVED → REOPEN
    - RESOLVED → CLOSED
    - CLOSED → REOPEN
    
    Requirements: 12.5, 13.9, 13.13, 13.14, 13.15
    """
    service = QueryService(db)
    
    query = service.update_query_status(
        query_id=query_id,
        status=data.status,
        user_id=current_user.id,
        resolved_by=data.resolved_by
    )
    
    return query


@router.post("/{query_id}/responses", response_model=QueryResponseSchema, status_code=201)
def create_query_response(
    query_id: UUID,
    data: QueryResponseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a response to a query.
    
    Supports back-and-forth conversation from both farming org and FSP.
    Updates query status to IN_PROGRESS if currently OPEN.
    
    Requirements: 13.1, 13.2, 13.3, 13.10, 13.11
    """
    service = QueryResponseService(db)
    
    response = service.create_response(
        query_id=query_id,
        response_text=data.response_text,
        user_id=current_user.id,
        has_recommendation=data.has_recommendation
    )
    
    return response


@router.get("/{query_id}/responses", response_model=list[QueryResponseSchema])
def get_query_responses(
    query_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all responses for a query in chronological order.
    
    Displays back-and-forth conversation with responder identification.
    
    Requirements: 13.11, 13.12
    """
    service = QueryResponseService(db)
    responses = service.get_query_conversation(query_id)
    return responses


@router.post("/{query_id}/propose-changes", response_model=dict, status_code=201)
def propose_schedule_changes(
    query_id: UUID,
    data: ScheduleChangeProposal,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Propose schedule changes as part of query response.
    
    Creates change log entries with trigger_type=QUERY and is_applied=false.
    Requires FSP to have write permission via work order.
    
    Requirements: 13.5, 13.6, 13.12
    """
    service = QueryResponseService(db)
    
    change_logs = service.propose_schedule_changes(
        query_id=query_id,
        schedule_id=data.schedule_id,
        changes=data.changes,
        user_id=current_user.id
    )
    
    return {
        "message": "Schedule changes proposed successfully",
        "changes_count": len(change_logs),
        "change_log_ids": [str(log.id) for log in change_logs]
    }


@router.post("/{query_id}/photos", response_model=QueryPhotoResponse, status_code=201)
def upload_query_photo(
    query_id: UUID,
    data: QueryPhotoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload photo to a query.
    
    Requirements: 12.7
    """
    service = QueryResponseService(db)
    
    photo = service.attach_photo_to_query(
        query_id=query_id,
        file_url=data.file_url,
        file_key=data.file_key,
        user_id=current_user.id,
        caption=data.caption
    )
    
    return photo


@router.post("/responses/{response_id}/photos", response_model=QueryPhotoResponse, status_code=201)
def upload_response_photo(
    response_id: UUID,
    data: QueryPhotoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload photo to a query response.
    
    Requirements: 13.4
    """
    service = QueryResponseService(db)
    
    photo = service.attach_photo_to_response(
        response_id=response_id,
        file_url=data.file_url,
        file_key=data.file_key,
        user_id=current_user.id,
        caption=data.caption
    )
    
    return photo
