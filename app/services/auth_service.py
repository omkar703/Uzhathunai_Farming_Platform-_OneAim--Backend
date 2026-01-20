"""
Authentication service for Uzhathunai v2.0.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.models.user import User, RefreshToken
from app.models.organization import OrgMemberRole
from app.models.rbac import Role
from app.schemas.auth import UserRegister, UserLogin, ChangePassword
from app.schemas.user import UserUpdate
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_access_token_with_context,
    create_refresh_token,
    verify_refresh_token,
    get_token_hash
)
from app.core.config import settings
from app.core.exceptions import (
    ConflictError,
    AuthenticationError,
    NotFoundError
)
from app.core.logging import auth_logger


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(
        self,
        user_data: UserRegister,
        device_info: Optional[Dict[str, Any]] = None
    ) -> Tuple[User, str, str]:
        """
        Register a new user with FREELANCER role by default.
        
        Args:
            user_data: User registration data
            device_info: Optional device information
        
        Returns:
            Tuple of (User, access_token, refresh_token)
        
        Raises:
            HTTPException: If email already exists or validation fails
        """
        # Check if email already exists
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            auth_logger.log_registration_attempt(
                email=user_data.email,
                success=False,
                error="Email already registered"
            )
            raise ConflictError(
                message="Email already registered",
                error_code="EMAIL_EXISTS"
            )
        
        try:
            # Hash password
            password_hash = get_password_hash(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email,
                password_hash=password_hash,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone=user_data.phone,
                preferred_language=user_data.preferred_language or 'en',
                is_active=True,
                is_verified=False
            )
            
            self.db.add(user)
            self.db.flush()  # Flush to get user.id
            
            # Assign FREELANCER role by default
            self._assign_freelancer_role(user.id)
            
            self.db.commit()
            self.db.refresh(user)
            
            # Create tokens
            access_token = create_access_token(data={"sub": str(user.id)})
            refresh_token = create_refresh_token(
                user_id=str(user.id),
                db=self.db,
                remember_me=False,
                device_info=device_info
            )
            
            auth_logger.log_registration_attempt(
                email=user_data.email,
                success=True
            )
            
            return user, access_token, refresh_token
            
        except IntegrityError as e:
            self.db.rollback()
            auth_logger.log_registration_attempt(
                email=user_data.email,
                success=False,
                error=str(e)
            )
            raise ConflictError(
                message="Email already registered",
                error_code="EMAIL_EXISTS"
            )
        except Exception as e:
            self.db.rollback()
            auth_logger.log_registration_attempt(
                email=user_data.email,
                success=False,
                error=str(e)
            )
            raise
    
    def login_user(
        self,
        login_data: UserLogin,
        device_info: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[User, str, str]:
        """
        Authenticate user and return tokens.
        
        Args:
            login_data: User login credentials
            device_info: Optional device information
            ip_address: Optional IP address
            user_agent: Optional user agent
        
        Returns:
            Tuple of (User, access_token, refresh_token)
        
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = self.get_user_by_email(login_data.email)
        if not user:
            auth_logger.log_login_attempt(
                email=login_data.email,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error="User not found"
            )
            raise AuthenticationError(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS"
            )
        
        # Verify password
        if not user.verify_password(login_data.password):
            auth_logger.log_login_attempt(
                email=login_data.email,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error="Invalid password"
            )
            raise AuthenticationError(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS"
            )
        
        # Check if user is active
        if not user.is_active:
            auth_logger.log_login_attempt(
                email=login_data.email,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error="User inactive"
            )
            raise AuthenticationError(
                message="User account is inactive",
                error_code="INACTIVE_USER"
            )
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        self.db.commit()
        
        # Determine organization for token context
        from app.models.organization import OrgMember, MemberStatus
        
        organization_id_for_token = None
        
        # Get user's active organization memberships
        active_memberships = self.db.query(OrgMember).filter(
            OrgMember.user_id == user.id,
            OrgMember.status == MemberStatus.ACTIVE
        ).all()
        
        if login_data.organization_id:
            # User specified an organization - verify they have access
            specified_membership = next(
                (m for m in active_memberships if m.organization_id == login_data.organization_id),
                None
            )
            if not specified_membership:
                raise AuthenticationError(
                    message="You do not have access to the specified organization",
                    error_code="INVALID_ORGANIZATION"
                )
            organization_id_for_token = login_data.organization_id
        elif len(active_memberships) == 1:
            # Auto-select if user has only one organization
            organization_id_for_token = active_memberships[0].organization_id
        elif len(active_memberships) > 1:
            # User has multiple organizations but didn't specify - use first one
            # Frontend should handle organization selection
            organization_id_for_token = active_memberships[0].organization_id
        # else: user is a freelancer (no organizations), organization_id_for_token remains None
        
        # Create tokens with organization context
        if organization_id_for_token:
            access_token = create_access_token_with_context(
                user_id=str(user.id),
                db=self.db,
                organization_id=str(organization_id_for_token)
            )
        else:
            # Freelancer - no organization context
            access_token = create_access_token(data={"sub": str(user.id)})
        
        refresh_token = create_refresh_token(
            user_id=str(user.id),
            db=self.db,
            remember_me=login_data.remember_me,
            device_info=device_info
        )
        
        auth_logger.log_login_attempt(
            email=login_data.email,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return user, access_token, refresh_token
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            New access token
        
        Raises:
            HTTPException: If refresh token is invalid
        """
        # Verify refresh token
        payload = verify_refresh_token(refresh_token, self.db)
        if not payload:
            auth_logger.log_token_operation(
                operation="refresh",
                user_id="unknown",
                success=False,
                error="Invalid refresh token"
            )
            raise AuthenticationError(
                message="Invalid or expired refresh token",
                error_code="INVALID_REFRESH_TOKEN"
            )
        
        user_id = payload.get("sub")
        
        # Create new access token
        access_token = create_access_token(data={"sub": user_id})
        
        auth_logger.log_token_operation(
            operation="refresh",
            user_id=user_id,
            success=True
        )
        
        return access_token
    
    def logout_user(
        self,
        user_id: str,
        refresh_token: Optional[str] = None,
        logout_all: bool = False
    ) -> bool:
        """
        Logout user by revoking refresh token(s).
        
        Args:
            user_id: User ID
            refresh_token: Specific refresh token to revoke
            logout_all: If True, revoke all refresh tokens
        
        Returns:
            True if successful
        """
        try:
            if logout_all:
                # Revoke all refresh tokens for user
                tokens = self.db.query(RefreshToken).filter(
                    RefreshToken.user_id == user_id,
                    RefreshToken.is_revoked == False
                ).all()
                
                for token in tokens:
                    token.is_revoked = True
                    token.revoked_at = datetime.now(timezone.utc)
                
                self.db.commit()
                
                auth_logger.log_logout(
                    user_id=user_id,
                    success=True
                )
                
                return True
            
            elif refresh_token:
                # Revoke specific refresh token
                token_hash = get_token_hash(refresh_token)
                db_token = self.db.query(RefreshToken).filter(
                    RefreshToken.user_id == user_id,
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.is_revoked == False
                ).first()
                
                if db_token:
                    db_token.is_revoked = True
                    db_token.revoked_at = datetime.now(timezone.utc)
                    self.db.commit()
                
                auth_logger.log_logout(
                    user_id=user_id,
                    success=True
                )
                
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            auth_logger.log_logout(
                user_id=user_id,
                success=False,
                error=str(e)
            )
            raise
    
    def change_password(
        self,
        user_id: str,
        password_data: ChangePassword
    ) -> bool:
        """
        Change user password and revoke all refresh tokens.
        
        Args:
            user_id: User ID
            password_data: Current and new password
        
        Returns:
            True if successful
        
        Raises:
            HTTPException: If current password is invalid
        """
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        # Verify current password
        if not user.verify_password(password_data.current_password):
            raise AuthenticationError(
                message="Current password is incorrect",
                error_code="INVALID_CURRENT_PASSWORD"
            )
        
        try:
            # Update password
            user.password_hash = get_password_hash(password_data.new_password)
            
            # Revoke all refresh tokens (force re-login on all devices)
            tokens = self.db.query(RefreshToken).filter(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            ).all()
            
            for token in tokens:
                token.is_revoked = True
                token.revoked_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise
    
    def update_profile(
        self,
        user_id: str,
        profile_data: UserUpdate
    ) -> User:
        """
        Update user profile.
        
        Args:
            user_id: User ID
            profile_data: Profile update data
        
        Returns:
            Updated user
        
        Raises:
            HTTPException: If user not found
        """
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        try:
            # Update fields
            update_data = profile_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            self.db.commit()
            self.db.refresh(user)
            
            return user
            
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
        
        Returns:
            User or None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
        
        Returns:
            User or None
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def _assign_freelancer_role(self, user_id: UUID) -> None:
        """
        Assign FREELANCER role to a new user.
        
        Creates org_member_roles record with organization_id=NULL and role_id=FREELANCER.
        
        Args:
            user_id: User ID
        
        Raises:
            Exception: If FREELANCER role not found
        """
        # Get FREELANCER role
        freelancer_role = self.db.query(Role).filter(Role.code == 'FREELANCER').first()
        if not freelancer_role:
            raise Exception("FREELANCER role not found in database")
        
        # Create org_member_roles record with organization_id=NULL
        member_role = OrgMemberRole(
            user_id=user_id,
            organization_id=None,  # NULL for freelancers
            role_id=freelancer_role.id,
            is_primary=True
        )
        
        self.db.add(member_role)
    
    def is_freelancer(self, user_id: UUID) -> bool:
        """
        Check if user is a freelancer (has FREELANCER role with organization_id=NULL).
        
        Args:
            user_id: User ID
        
        Returns:
            True if user is freelancer, False otherwise
        """
        freelancer_role = self.db.query(Role).filter(Role.code == 'FREELANCER').first()
        if not freelancer_role:
            return False
        
        member_role = self.db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == user_id,
            OrgMemberRole.organization_id == None,
            OrgMemberRole.role_id == freelancer_role.id
        ).first()
        
        return member_role is not None
    
    def get_user_roles(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all roles for a user across all organizations.
        
        Args:
            user_id: User ID
        
        Returns:
            List of role dictionaries with organization info
        """
        member_roles = self.db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == user_id
        ).all()
        
        roles = []
        for mr in member_roles:
            role_info = {
                "role_id": str(mr.role_id),
                "role_code": mr.role.code,
                "role_name": mr.role.name,
                "organization_id": str(mr.organization_id) if mr.organization_id else None,
                "is_primary": mr.is_primary,
                "is_freelancer": mr.organization_id is None
            }
            roles.append(role_info)
        
        return roles
    
    def remove_freelancer_role(self, user_id: UUID) -> None:
        """
        Remove FREELANCER role from user.
        
        Called when user creates an organization or accepts an invitation.
        
        Args:
            user_id: User ID
        """
        freelancer_role = self.db.query(Role).filter(Role.code == 'FREELANCER').first()
        if not freelancer_role:
            return
        
        # Delete org_member_roles record with organization_id=NULL
        self.db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == user_id,
            OrgMemberRole.organization_id == None,
            OrgMemberRole.role_id == freelancer_role.id
        ).delete()
        
        self.db.flush()
