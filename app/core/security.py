"""
Security utilities for authentication and authorization.
"""
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def get_token_hash(token: str) -> str:
    """Generate token hash using SHA-256 (for long tokens like JWTs)."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, hashed_token: str) -> bool:
    """Verify token against its hash."""
    return get_token_hash(token) == hashed_token


def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None,
    organization_context: Optional[Dict[str, Any]] = None,
    user_roles: Optional[List[str]] = None,
    subscription_plan: Optional[str] = None
) -> str:
    """
    Create JWT access token with organization context and role information.
    
    Args:
        data: Base token data (must include 'sub' for user ID)
        expires_delta: Optional custom expiration time
        organization_context: Organization information for multi-tenant context
        user_roles: List of user roles in the organization
        subscription_plan: Organization's subscription plan for feature gating
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "jti": secrets.token_urlsafe(32)  # JWT ID for blacklisting
    })
    
    # Add organization context if provided
    if organization_context:
        to_encode["org"] = {
            "id": organization_context.get("id"),
            "name": organization_context.get("name"),
            "type": organization_context.get("type"),
            "status": organization_context.get("status")
        }
    
    # Add user roles if provided
    if user_roles:
        to_encode["roles"] = user_roles
    
    # Add subscription plan for feature gating
    if subscription_plan:
        to_encode["subscription"] = subscription_plan
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    user_id: str, 
    db: Session, 
    remember_me: bool = False,
    device_info: Optional[Dict[str, Any]] = None
) -> str:
    """Create JWT refresh token and store in database."""
    from app.models.user import RefreshToken
    
    if remember_me:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_REMEMBER_EXPIRE_DAYS)
    else:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    expire = datetime.now(timezone.utc) + expires_delta
    
    # Create token payload
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)
    }
    
    # Generate token
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Hash token for storage
    token_hash = get_token_hash(token)
    
    # Store in database
    db_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expire,
        device_info=device_info or {}
    )
    db.add(db_token)
    db.commit()
    
    return token


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            return None
            
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            return None
            
        return payload
        
    except JWTError:
        return None


# Blacklisting functions removed - not used in Phase 2
# Token revocation is handled via refresh_tokens.is_revoked flag


def revoke_refresh_token(token: str, db: Session) -> bool:
    """Revoke refresh token."""
    from app.models.user import RefreshToken
    
    try:
        # Verify token structure
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Calculate hash
        token_hash = get_token_hash(token)
        
        # Find and revoke token
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == payload.get("sub"),
            RefreshToken.is_revoked == False
        ).first()
        
        if db_token:
            db_token.is_revoked = True
            db_token.revoked_at = datetime.now(timezone.utc)
            db.commit()
            return True
            
    except JWTError:
        pass
        
    return False


def verify_refresh_token(token: str, db: Session) -> Optional[Dict[str, Any]]:
    """Verify refresh token against database."""
    from app.models.user import RefreshToken
    
    try:
        # Decode token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("type") != "refresh":
            return None
            
        # Calculate hash
        token_hash = get_token_hash(token)
            
        # Check database
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == payload.get("sub"),
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc)
        ).first()
        
        if db_token:
            return payload
            
    except JWTError:
        pass
        
    return None


def create_access_token_with_context(
    user_id: str,
    db: Session,
    organization_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create access token with full organization context and role information.
    
    Args:
        user_id: User ID for the token
        db: Database session for fetching organization context
        organization_id: Optional organization ID for context
        expires_delta: Optional custom expiration time
    
    Returns:
        JWT token with organization context and roles
    """
    from app.models.user import User
    from app.models.organization import Organization, OrgMember, MemberStatus
    from app.models.rbac import Role
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    
    # Base token data
    token_data = {"sub": user_id}
    organization_context = None
    user_roles = []
    subscription_plan = None
    
    # If organization_id is provided, get organization context
    if organization_id:
        # Get organization details
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        if organization:
            organization_context = {
                "id": str(organization.id),
                "name": organization.name,
                "type": organization.organization_type.value if organization.organization_type else None,
                "status": organization.status.value if organization.status else None
            }
            # subscription_plan is a relationship to SubscriptionPlan model, get its name
            subscription_plan = organization.subscription_plan.name if organization.subscription_plan else None
            
            # Get user's roles in this organization
            membership = db.query(OrgMember).filter(
                OrgMember.user_id == user_id,
                OrgMember.organization_id == organization_id,
                OrgMember.status == MemberStatus.ACTIVE
            ).first()
            
            if membership and membership.roles:
                 # Fetch primary role or all roles
                 # Logic in models/organization.py shows roles via OrgMemberRole
                 # We need to extract role codes.
                 # membership.roles is a list of OrgMemberRole.
                 # We want the Roles associated with them.
                 
                 # Optimized query might be better but let's stick to simple logic first
                 # given lazy loading.
                 # security.py imports models inside function to avoid circular deps.
                 
                for member_role in membership.roles:
                    if member_role.role:
                        user_roles.append(member_role.role.code)
    else:
        # If no organization specified, user is a freelancer
        user_roles = ["FREELANCER"]
    
    return create_access_token(
        data=token_data,
        expires_delta=expires_delta,
        organization_context=organization_context,
        user_roles=user_roles,
        subscription_plan=subscription_plan
    )


def extract_token_context(token_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract organization context and role information from JWT token payload.
    
    Args:
        token_payload: Decoded JWT token payload
    
    Returns:
        Dictionary with extracted context information
    """
    return {
        "user_id": token_payload.get("sub"),
        "organization": token_payload.get("org"),
        "roles": token_payload.get("roles", []),
        "subscription": token_payload.get("subscription"),
        "token_type": token_payload.get("type"),
        "jti": token_payload.get("jti"),
        "exp": token_payload.get("exp"),
        "iat": token_payload.get("iat")
    }


def cleanup_expired_tokens(db: Session):
    """Clean up expired tokens from database."""
    from app.models.user import RefreshToken
    
    # Remove expired refresh tokens
    db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.now(timezone.utc)
    ).delete()
    
    db.commit()