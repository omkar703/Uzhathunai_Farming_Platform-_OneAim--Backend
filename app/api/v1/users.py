"""
User API endpoints for Uzhathunai v2.0.
Handles user search and related operations.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, status, Query, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.response import BaseResponse
from app.schemas.user import FreelancerResponse

router = APIRouter()


@router.get(
    "/freelancers",
    response_model=BaseResponse[list[FreelancerResponse]],
    status_code=status.HTTP_200_OK,
    summary="Search freelancers",
    description="Search for users who can be invited to organizations"
)
def search_freelancers(
    q: Optional[str] = Query(None, description="Search query for name or email"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Search for freelancers (users who can be invited to organizations).
    
    Returns users who:
    - Are NOT owners of any organization
    - Match the search query (if provided)
    - Are active users
    
    Search is case-insensitive and matches against:
    - First name
    - Last name
    - Email
    
    Returns up to 50 matching users.
    """
    service = UserService(db)
    users = service.search_freelancers(search_query=q)
    
    return {
        "success": True,
        "message": "Freelancers retrieved successfully",
        "data": users
    }


@router.post(
    "/profile-picture",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Upload profile picture",
    description="Upload a new profile picture for the current user"
)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new profile picture.
    
    This is a mock implementation that returns a static URL.
    In a real app, this would upload to S3/GCS and update the user's profile_picture_url.
    """
    # Simulate file upload and URL generation
    mock_url = f"https://storage.uzhathunai.com/profiles/{current_user.id}/{file.filename}"
    
    # Update user model
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    from app.schemas.user import UserUpdate
    auth_service.update_profile(str(current_user.id), UserUpdate(profile_picture_url=mock_url))
    
    return {
        "success": True,
        "message": "Profile picture uploaded successfully",
        "data": {
            "profile_picture_url": mock_url
        }
    }
