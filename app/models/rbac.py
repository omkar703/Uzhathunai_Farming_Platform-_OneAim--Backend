"""
RBAC (Role-Based Access Control) models for Uzhathunai v2.0.

Models match database schema exactly from 001_uzhathunai_ddl.sql:
- Role (lines 40-50)
- Permission (lines 52-62)
- RolePermission (lines 64-75)
- OrgRolePermissionOverride (lines 225-235)
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import UserRoleScope, PermissionEffect


class Role(Base):
    """
    Role model - matches DDL lines 40-50 exactly.
    
    System-defined roles for RBAC. Read-only, populated via DML.
    """
    
    __tablename__ = "roles"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Role information
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    scope = Column(SQLEnum(UserRoleScope, name='user_role_scope'), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    member_roles = relationship("OrgMemberRole", back_populates="role")
    invitations = relationship("OrgMemberInvitation", back_populates="role")
    
    def __repr__(self):
        return f"<Role(id={self.id}, code={self.code}, name={self.name})>"


class Permission(Base):
    """
    Permission model - matches DDL lines 52-62 exactly.
    
    System-defined permissions for RBAC. Read-only, populated via DML.
    """
    
    __tablename__ = "permissions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Permission information
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission")
    org_overrides = relationship("OrgRolePermissionOverride", back_populates="permission")
    
    def __repr__(self):
        return f"<Permission(id={self.id}, code={self.code}, resource={self.resource}, action={self.action})>"


class RolePermission(Base):
    """
    Role-Permission mapping model - matches DDL lines 64-75 exactly.
    
    Maps permissions to roles with ALLOW/DENY effect.
    """
    
    __tablename__ = "role_permissions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)
    
    # Permission effect
    effect = Column(SQLEnum(PermissionEffect, name='permission_effect'), default=PermissionEffect.ALLOW)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    
    def __repr__(self):
        return f"<RolePermission(id={self.id}, role_id={self.role_id}, permission_id={self.permission_id}, effect={self.effect})>"


class OrgRolePermissionOverride(Base):
    """
    Organization role permission override model - matches DDL lines 225-235 exactly.
    
    Organization-specific permission overrides for roles.
    """
    
    __tablename__ = "org_role_permission_overrides"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)
    
    # Override effect
    effect = Column(SQLEnum(PermissionEffect, name='permission_effect'), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    organization = relationship("Organization")
    role = relationship("Role")
    permission = relationship("Permission", back_populates="org_overrides")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<OrgRolePermissionOverride(id={self.id}, org_id={self.organization_id}, role_id={self.role_id}, effect={self.effect})>"
