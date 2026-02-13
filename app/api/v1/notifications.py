"""
Notification endpoints for user notifications.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from uuid import UUID
from datetime import datetime

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
def get_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    unread_only: bool = False
) -> Dict:
    """
    Get all notifications for the current user.
    """
    logger.info(
        "Fetching notifications",
        extra={
            "user_id": str(current_user.id),
            "unread_only": unread_only
        }
    )
    
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).all()
    
    result = []
    for notif in notifications:
        result.append({
            "id": str(notif.id),
            "type": notif.type,
            "title": notif.title,
            "message": notif.message,
            "data": notif.data,
            "is_read": notif.is_read,
            "created_at": notif.created_at.isoformat(),
            "read_at": notif.read_at.isoformat() if notif.read_at else None
        })
    
    return {
        "success": True,
        "data": result,
        "error_code": None
    }


@router.post("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Mark a notification as read.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Notification marked as read",
        "error_code": None
    }


@router.get("/unread-count")
def get_unread_notification_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, int]:
    """
    Get count of unread notifications for the current user.
    """
    logger.info(
        "Fetching unread notification count",
        extra={
            "user_id": str(current_user.id),
            "action": "get_unread_count"
        }
    )
    
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {'count': count}
