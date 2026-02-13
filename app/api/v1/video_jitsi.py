"""
Jitsi Meet video calling API endpoints.
Simplified video session management using Jitsi Meet rooms.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import hashlib
import time

from app.core.database import get_db
from app.core.auth import get_current_active_user as get_current_user
from app.models.user import User
from app.models.work_order import WorkOrder
from app.models.organization import OrgMember, Organization
from app.models.video_session import VideoSession, VideoSessionStatus
from app.models.enums import OrganizationStatus

router = APIRouter()

class ScheduleMeetingRequest(BaseModel):
    work_order_id: UUID
    topic: str
    start_time: Optional[datetime] = None
    duration: int = 45  # Default 45 mins

def generate_jitsi_room_name(work_order_id: UUID) -> str:
    """
    Generate a unique Jitsi room name.
    Format: agro-{short_hash}-{timestamp}
    """
    # Create a short hash from work order ID for uniqueness
    hash_obj = hashlib.md5(str(work_order_id).encode())
    short_hash = hash_obj.hexdigest()[:8]
    timestamp = int(time.time())
    
    return f"agro-{short_hash}-{timestamp}"

@router.post("/schedule", status_code=status.HTTP_201_CREATED)
async def schedule_meeting(
    request: ScheduleMeetingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Schedule a Jitsi Meet video session for a Work Order.
    Returns immediately with session details (no async background task needed).
    """
    # 1. Verify Work Order exists
    work_order = db.query(WorkOrder).filter(WorkOrder.id == request.work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work Order not found")
        
    # 2. Authorization & Validation
    start_time = request.start_time or datetime.utcnow()
    
    # Check if organizations are active
    fsp_org = db.query(Organization).filter(Organization.id == work_order.fsp_organization_id).first()
    farm_org = db.query(Organization).filter(Organization.id == work_order.farming_organization_id).first()
    
    allowed_statuses = [OrganizationStatus.ACTIVE, OrganizationStatus.IN_PROGRESS]
    if (not fsp_org or fsp_org.status not in allowed_statuses) or (not farm_org or farm_org.status not in allowed_statuses):
        raise HTTPException(
            status_code=403, 
            detail={
                "message": "Your organization is awaiting approval.",
                "error_code": "ORG_NOT_APPROVED"
            }
        )

    # 3. Generate Jitsi room details
    room_name = generate_jitsi_room_name(request.work_order_id)
    # Using Jitsi Meet public server - users may need to click "Join in browser"
    join_url = f"https://meet.jit.si/{room_name}"
    
    # 4. Create ACTIVE Session (no background processing needed)
    video_session = VideoSession(
        work_order_id=request.work_order_id,
        topic=request.topic,
        start_time=start_time,
        duration=request.duration,
        room_name=room_name,
        join_url=join_url,
        status=VideoSessionStatus.ACTIVE,  # Immediately active
        created_by=current_user.id
    )
    db.add(video_session)
    db.commit()
    db.refresh(video_session)
    
    # 5. Create notification for recipient
    try:
        from app.models.notification import Notification
        
        print(f"[DEBUG] Starting notification creation for video call")
        
        # Determine recipient: if current user is in FSP org, notify farmer; otherwise notify FSP
        current_user_orgs = db.query(OrgMember).filter(
            OrgMember.user_id == current_user.id,
            OrgMember.status == 'ACTIVE'
        ).all()
        current_org_ids = [org.organization_id for org in current_user_orgs]
        
        print(f"[DEBUG] Current user orgs: {current_org_ids}")
        print(f"[DEBUG] Work order FSP org: {work_order.fsp_organization_id}")
        print(f"[DEBUG] Work order Farmer org: {work_order.farming_organization_id}")
        
        # Check if current user is FSP or Farmer
        is_fsp_calling = work_order.fsp_organization_id in current_org_ids
        
        print(f"[DEBUG] Is FSP calling: {is_fsp_calling}")
        
        if is_fsp_calling:
            # FSP is calling farmer - notify farmer org members
            recipient_org_id = work_order.farming_organization_id
            caller_org = db.query(Organization).filter(Organization.id == work_order.fsp_organization_id).first()
            caller_name = caller_org.name if caller_org else "FSP"
        else:
            # Farmer is calling FSP - notify FSP org members
            recipient_org_id = work_order.fsp_organization_id
            caller_org = db.query(Organization).filter(Organization.id == work_order.farming_organization_id).first()
            caller_name = caller_org.name if caller_org else "Farmer"
        
        print(f"[DEBUG] Recipient org ID: {recipient_org_id}")
        print(f"[DEBUG] Caller name: {caller_name}")
        
        # Get all active members of recipient organization
        recipient_members = db.query(OrgMember).filter(
            OrgMember.organization_id == recipient_org_id,
            OrgMember.status == 'ACTIVE'
        ).all()
        
        print(f"[DEBUG] Found {len(recipient_members)} recipient members")
        
        # Create notification for each recipient
        for member in recipient_members:
            print(f"[DEBUG] Creating notification for user: {member.user_id}")
            notification = Notification(
                user_id=member.user_id,
                type='VIDEO_CALL',
                title='Video Call Invitation',
                message=f'{caller_name} has started a video consultation. Join now!',
                data={
                    'session_id': str(video_session.id),
                    'join_url': join_url,
                    'room_name': room_name,
                    'work_order_id': str(work_order.id),
                    'caller_name': caller_name
                },
                is_read=False
            )
            db.add(notification)
        
        db.commit()
        print(f"[DEBUG] Successfully created {len(recipient_members)} notifications")
    except Exception as e:
        # Non-blocking - log but don't fail the meeting creation
        import traceback
        print(f"[WARNING] Failed to create notification: {e}")
        print(f"[WARNING] Traceback: {traceback.format_exc()}")
    
    
    # 6. Send chat notification to farmer (legacy support)
    try:
        from app.api.v1.chat import create_channel, send_message
        from app.schemas.chat import ChannelCreate, MessageCreate
        
        # Create/get channel for this work order
        channel_data = ChannelCreate(
            participant_org_id=work_order.farming_organization_id,
            context_type="WORK_ORDER",
            context_id=str(work_order.id)
        )
        channel_response = await create_channel(channel_data, db, current_user)
        
        if channel_response.get("success") and channel_response.get("data"):
            channel_id = channel_response["data"].get("id") or channel_response["data"].get("channel_id")
            
            # Send VIDEO_CALL_JOIN message
            message_data = MessageCreate(content=f"VIDEO_CALL_JOIN:{join_url}")
            await send_message(channel_id, message_data, db, current_user)
    except Exception as e:
        # Non-blocking - log but don't fail the meeting creation
        print(f"[WARNING] Failed to send chat notification: {e}")
    
    return {
        "success": True,
        "message": "Meeting scheduled successfully",
        "data": {
            "session_id": str(video_session.id),
            "room_name": room_name,
            "join_url": join_url
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
    Get the Join URL for a Jitsi meeting.
    All participants use the same URL (no separate host/participant URLs).
    """
    session = db.query(VideoSession).filter(VideoSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Permission Check
    wo = db.query(WorkOrder).filter(WorkOrder.id == session.work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
        
    # Check if user is member of either organization
    is_member = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.organization_id.in_([wo.farming_organization_id, wo.fsp_organization_id]),
        OrgMember.status == 'ACTIVE'
    ).first()
    
    if not is_member and session.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to join this meeting")

    # Status Check
    if session.status != VideoSessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Meeting is not active yet")

    # Return same URL for everyone (Jitsi handles roles internally)
    return {
        "success": True,
        "message": "Join URL retrieved successfully",
        "data": {
            "url": session.join_url,
            "room_name": session.room_name,
            "role": "participant"  # Jitsi auto-assigns first joiner as moderator
        },
        "error_code": None
    }

@router.get("/my-active-calls")
async def get_my_active_calls(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active video calls for the current user (farmer side).
    Returns calls where the user is a member of the farming organization.
    """
    # Find user's farming organizations
    farmer_orgs = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == 'ACTIVE'
    ).all()
    
    if not farmer_orgs:
        return {
            "success": True,
            "message": "No active calls",
            "data": [],
            "error_code": None
        }
    
    org_ids = [org.organization_id for org in farmer_orgs]
    
    # Find active video sessions for work orders involving these orgs
    active_sessions = db.query(VideoSession).join(
        WorkOrder, VideoSession.work_order_id == WorkOrder.id
    ).filter(
        VideoSession.status == VideoSessionStatus.ACTIVE,
        WorkOrder.farming_organization_id.in_(org_ids)
    ).all()
    
    result = []
    for session in active_sessions:
        wo = db.query(WorkOrder).filter(WorkOrder.id == session.work_order_id).first()
        fsp_org = db.query(Organization).filter(Organization.id == wo.fsp_organization_id).first() if wo else None
        
        result.append({
            "session_id": str(session.id),
            "topic": session.topic,
            "join_url": session.join_url,
            "room_name": session.room_name,
            "start_time": session.start_time.isoformat() if session.start_time else None,
            "created_at": session.created_at.isoformat(),
            "fsp_name": fsp_org.name if fsp_org else "FSP",
            "work_order_id": str(wo.id) if wo else None
        })
    
    return {
        "success": True,
        "message": f"Found {len(result)} active call(s)",
        "data": result,
        "error_code": None
    }

