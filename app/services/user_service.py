"""
User service for Uzhathunai v2.0.
Handles user search and management operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from uuid import UUID

from app.models.user import User
from app.models.organization import OrgMemberRole
from app.models.rbac import Role
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
    
    def search_freelancers(
        self,
        search_query: Optional[str] = None
    ) -> List[dict]:
        """
        Search for users who can be invited to organizations.
        
        Filters out users who are owners of any organization.
        
        Args:
            search_query: Optional search string for name or email
            
        Returns:
            List of user dictionaries
        """
        self.logger.info(
            "Searching for freelancers",
            extra={"search_query": search_query}
        )
        
        # Get user IDs who are owners
        owner_role_codes = ['OWNER', 'FSP_OWNER']
        owner_user_ids = self.db.query(OrgMemberRole.user_id).join(Role).filter(
            Role.code.in_(owner_role_codes)
        ).distinct().subquery()
        
        # Build base query filtering out owners
        query = self.db.query(User).filter(
            ~User.id.in_(owner_user_ids),
            User.is_active == True
        )
        
        # Apply search filter
        if search_query and search_query.strip():
            search_pattern = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.phone.ilike(search_pattern)
                )
            )
        
        users = query.order_by(User.created_at.desc()).limit(50).all()
        
        result = [
            {
                "id": str(user.id),
                "name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "specialization": user.specialization or "",
                "profile_picture": user.profile_picture_url or ""
            }
            for user in users
        ]
        
        self.logger.info(
            "Freelancers search completed",
            extra={"count": len(result), "search_query": search_query}
        )
        
        return result
