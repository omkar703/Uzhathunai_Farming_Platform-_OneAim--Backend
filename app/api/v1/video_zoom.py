from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_active_user as get_current_user
from app.models.user import User
from app.models.work_order import WorkOrder
from app.models.organization import OrgMember
from app.models.video_session import VideoSession, VideoSessionStatus
from app.services.zoom_service import zoom_service

router = APIRouter()

from typing import Optional

class ScheduleMeetingRequest(BaseModel):
    work_order_id: UUID
    topic: str
    start_time: Optional[datetime] = None
    duration: int = 45 # Default 45 mins

class MeetingResponse(BaseModel):
    message: str
    status: str

async def create_zoom_meeting_task(session_id: UUID, topic: str, start_time: datetime, duration: int, db: Session):
    """
    Background task to create zoom meeting and update DB.
    """
    try:
        # 1. Reuse DB session or create new one? 
        # Typically background tasks should handle their own transactions if they are long running, 
        # but here we pass the session or re-instantiate. 
        # Passing db session from request is risky if request finishes. 
        # Better to query fresh if possible, but for now we follow standard pattern or assume db scope is safe?
        # Actually, FastAPI BackgroundTasks runs AFTER response. The dependency session might be closed.
        # SAFE PATTERN: Create new session manually or use a thread-local scoped session if available.
        # But `get_db` is a generator. We'll rely on the fact that we can't easily inject a new session here without 
        # manual session maker usage. 
        # FIX: We will just do the Zoom Call first (async), then update DB.
        # Actually safer: Request -> Create PENDING DB Record -> Return 202 -> Background: Create Zoom -> Update DB.
        # For the background update, we need a fresh DB session.
        pass 
        # Implementing logic inside the wrapper below for simplicity with manual session management if needed, 
        # or just import SessionLocal from database.py
    except Exception as e:
        print(f"Error in background task: {e}")

from app.core.database import SessionLocal

async def process_zoom_meeting(session_id: UUID, topic: str, start_time: datetime, duration: int):
    db = SessionLocal()
    try:
        # Get session
        video_session = db.query(VideoSession).filter(VideoSession.id == session_id).first()
        if not video_session:
            return

        # Create Zoom Meeting
        try:
            zoom_data = await zoom_service.create_meeting(topic, start_time, duration)
            
            # Update DB
            video_session.zoom_meeting_id = str(zoom_data.get("id"))
            video_session.join_url = zoom_data.get("join_url")
            video_session.start_url = zoom_data.get("start_url")
            video_session.password = zoom_data.get("password")
            video_session.status = VideoSessionStatus.ACTIVE
            
            db.commit()
        except Exception as e:
            print(f"Zoom creation failed: {e}")
            video_session.status = VideoSessionStatus.CANCELLED
            db.commit()
            
    finally:
        db.close()

@router.post("/schedule", status_code=status.HTTP_202_ACCEPTED)
async def schedule_meeting(
    request: ScheduleMeetingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Schedule a Zoom meeting for a Work Order.
    """
    # 1. Verify Work Order exists
    work_order = db.query(WorkOrder).filter(WorkOrder.id == request.work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work Order not found")
        
    # 2. Authorization & Validation
    start_time = request.start_time or datetime.utcnow()
    
    # Check if organizations are approved to prevent 403s later in Zoom
    from app.models.organization import Organization
    fsp_org = db.query(Organization).filter(Organization.id == work_order.fsp_organization_id).first()
    farm_org = db.query(Organization).filter(Organization.id == work_order.farming_organization_id).first()
    
    if not (fsp_org and fsp_org.is_approved) or not (farm_org and farm_org.is_approved):
         raise HTTPException(
             status_code=403, 
             detail={
                 "message": "Your organization is awaiting approval.",
                 "error_code": "ORG_NOT_APPROVED"
             }
         )

    # 3. Create PENDING Session
    video_session = VideoSession(
        work_order_id=request.work_order_id,
        topic=request.topic,
        start_time=start_time,
        duration=request.duration,
        status=VideoSessionStatus.PENDING,
        created_by=current_user.id
    )
    db.add(video_session)
    db.commit()
    db.refresh(video_session)
    
    # 4. Trigger Background Task
    background_tasks.add_task(
        process_zoom_meeting, 
        video_session.id, 
        request.topic, 
        start_time, 
        request.duration
    )
    
    return {
        "success": True,
        "message": "Meeting scheduling started",
        "data": {
            "session_id": str(video_session.id)
        },
        "error_code": None
    }

@router.get("/{session_id}/join-url")
async def get_join_url(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the Join URL for a meeting.
    Returns start_url for Host, join_url for others.
    """
    session = db.query(VideoSession).filter(VideoSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Permission Check
    url_data = {}
    if session.created_by == current_user.id:
        role = "host"
    else:
        # Check if user is member of Farming Org or FSP Org linked to Work Order
        wo = db.query(WorkOrder).filter(WorkOrder.id == session.work_order_id).first()
        if not wo:
             raise HTTPException(status_code=404, detail="Work Order not found")
             
        is_member = db.query(OrgMember).filter(
            OrgMember.user_id == current_user.id,
            OrgMember.organization_id.in_([wo.farming_organization_id, wo.fsp_organization_id]),
            OrgMember.status == 'ACTIVE' # Assuming enum but string check for speed or import enum
        ).first()
        
        if not is_member:
             raise HTTPException(status_code=403, detail="You are not authorized to join this meeting")
             
        role = "participant"

    # Status Check
    if session.status != VideoSessionStatus.ACTIVE:
         # If user is host/creator, and status is PENDING, they might need start_url? 
         # But in this flow, we only update URLs *after* Zoom creation (ACTIVE).
         # So if PENDING, URLs are null.
         raise HTTPException(status_code=400, detail="Meeting is not active yet")

    if role == "host":
        url_data = {"url": session.start_url, "role": "host"}
    else:
        url_data = {"url": session.join_url, "role": "participant"}
        
    return {
        "success": True,
        "message": "Join URL retrieved successfully",
        "data": url_data,
        "error_code": None
    }
