"""
RBAC service for Uzhathunai v2.0.
Handles permission checking with multiple roles support and caching.
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from uuid import UUID
import time

from app.models.organization import OrgMemberRole
from app.models.rbac import Role, Permission, RolePermission, OrgRolePermissionOverride
from app.models.enums import PermissionEffect
from app.core.logging import rbac_logger
from app.core.cache import cache_service

logger = rbac_logger


class RBACService:
    """Service for RBAC permission checking."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = rbac_logger
        self.cache = cache_service
    
    def check_permission(
        self,
        user_id: UUID,
        organization_id: UUID,
        resource: str,
        action: str
    ) -> bool:
        """
        Check if user has permission for resource.action in organization.
        Implements union of permissions from all roles with DENY precedence.
        
        Args:
            user_id: User ID
            organization_id: Organization ID
            resource: Resource name (e.g., "farms", "members")
            action: Action name (e.g., "create", "update", "delete")
        
        Returns:
            True if user has permission, False otherwise
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = f"permission:{user_id}:{organization_id}:{resource}:{action}"
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            self.logger.log_rbac_cache_operation(
                operation="check_permission",
                cache_key=cache_key,
                hit_miss="hit",
                user_id=str(user_id),
                organization_id=str(organization_id)
            )
            return cached_result == "ALLOW"
        
        # Get all user's roles in this organization
        user_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.user_id == user_id,
            OrgMemberRole.organization_id == organization_id
        ).all()
        
        if not user_roles:
            self.logger.log_permission_denial(
                user_id=str(user_id),
                organization_id=str(organization_id),
                resource=resource,
                action=action,
                denial_reason="No roles assigned",
                roles=[]
            )
            return False
        
        # Collect permissions from all roles
        all_permissions = []
        role_names = []
        base_permissions = {}
        org_overrides = {}
        
        for user_role in user_roles:
            role_names.append(user_role.role.code)
            
            # Check org-level overrides first
            override = self.db.query(OrgRolePermissionOverride).join(Permission).filter(
                OrgRolePermissionOverride.organization_id == organization_id,
                OrgRolePermissionOverride.role_id == user_role.role_id,
                Permission.resource == resource,
                Permission.action == action
            ).first()
            
            if override:
                all_permissions.append({
                    'role': user_role.role.code,
                    'effect': override.effect.value,
                    'source': 'override'
                })
                org_overrides[user_role.role.code] = override.effect.value
            else:
                # Check base role permissions
                role_perm = self.db.query(RolePermission).join(Permission).filter(
                    RolePermission.role_id == user_role.role_id,
                    Permission.resource == resource,
                    Permission.action == action
                ).first()
                
                if role_perm:
                    all_permissions.append({
                        'role': user_role.role.code,
                        'effect': role_perm.effect.value,
                        'source': 'base'
                    })
                    base_permissions[user_role.role.code] = role_perm.effect.value
        
        # Evaluate: DENY from any role takes precedence
        has_deny = any(p['effect'] == 'DENY' for p in all_permissions)
        has_allow = any(p['effect'] == 'ALLOW' for p in all_permissions)
        
        # Final decision
        if has_deny:
            final_effect = "DENY"
        elif has_allow:
            final_effect = "ALLOW"
        else:
            final_effect = "DENY"  # Default deny
        
        # Cache result (5 minutes TTL)
        self.cache.set(cache_key, final_effect, ttl=300)
        
        # Calculate evaluation duration
        evaluation_duration = time.time() - start_time
        
        # Log evaluation
        self.logger.log_permission_evaluation(
            user_id=str(user_id),
            organization_id=str(organization_id),
            resource=resource,
            action=action,
            effect=final_effect,
            source="multiple_roles" if len(user_roles) > 1 else "single_role",
            roles=role_names,
            evaluation_duration=evaluation_duration,
            base_permissions=base_permissions,
            org_overrides=org_overrides
        )
        
        return final_effect == "ALLOW"
    
    def invalidate_permission_cache(self, user_id: UUID, organization_id: UUID):
        """
        Invalidate permission cache when roles change.
        
        Args:
            user_id: User ID
            organization_id: Organization ID
        """
        pattern = f"permission:{user_id}:{organization_id}:*"
        deleted_count = self.cache.delete_pattern(pattern)
        
        self.logger.log_rbac_cache_operation(
            operation="invalidate",
            cache_key=pattern,
            hit_miss="invalidated",
            user_id=str(user_id),
            organization_id=str(organization_id)
        )
        
        return deleted_count
    
    def get_user_permissions(
        self,
        user_id: UUID,
        organization_id: UUID
    ) -> Dict[str, List[str]]:
        """
        Get all permissions for user in organization.
        Returns permissions grouped by resource.
        
        Args:
            user_id: User ID
            organization_id: Organization ID
        
        Returns:
            Dictionary mapping resource to list of allowed actions
        """
        # Get all user's roles in this organization
        user_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.user_id == user_id,
            OrgMemberRole.organization_id == organization_id
        ).all()
        
        if not user_roles:
            return {}
        
        # Collect all permissions
        permissions_map = {}
        
        for user_role in user_roles:
            # Get base role permissions
            role_perms = self.db.query(RolePermission).join(Permission).filter(
                RolePermission.role_id == user_role.role_id
            ).all()
            
            for rp in role_perms:
                resource = rp.permission.resource
                action = rp.permission.action
                
                # Check for org-level override
                override = self.db.query(OrgRolePermissionOverride).filter(
                    OrgRolePermissionOverride.organization_id == organization_id,
                    OrgRolePermissionOverride.role_id == user_role.role_id,
                    OrgRolePermissionOverride.permission_id == rp.permission_id
                ).first()
                
                effect = override.effect if override else rp.effect
                
                # Track permissions
                if resource not in permissions_map:
                    permissions_map[resource] = {}
                
                if action not in permissions_map[resource]:
                    permissions_map[resource][action] = []
                
                permissions_map[resource][action].append({
                    'role': user_role.role.code,
                    'effect': effect.value
                })
        
        # Apply DENY precedence and build final result
        result = {}
        for resource, actions in permissions_map.items():
            result[resource] = []
            for action, perms in actions.items():
                has_deny = any(p['effect'] == 'DENY' for p in perms)
                has_allow = any(p['effect'] == 'ALLOW' for p in perms)
                
                if not has_deny and has_allow:
                    result[resource].append(action)
        
        return result
    
    def create_permission_override(
        self,
        organization_id: UUID,
        role_id: UUID,
        permission_id: UUID,
        effect: PermissionEffect,
        created_by: UUID
    ) -> OrgRolePermissionOverride:
        """
        Create organization-level permission override.
        
        Args:
            organization_id: Organization ID
            role_id: Role ID
            permission_id: Permission ID
            effect: Permission effect (ALLOW/DENY)
            created_by: User ID creating the override
        
        Returns:
            Created override
        """
        # Check if override already exists
        existing = self.db.query(OrgRolePermissionOverride).filter(
            OrgRolePermissionOverride.organization_id == organization_id,
            OrgRolePermissionOverride.role_id == role_id,
            OrgRolePermissionOverride.permission_id == permission_id
        ).first()
        
        if existing:
            # Update existing override
            previous_effect = existing.effect.value
            existing.effect = effect
            self.db.commit()
            self.db.refresh(existing)
            
            # Get role and permission details for logging
            role = self.db.query(Role).filter(Role.id == role_id).first()
            permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
            
            self.logger.log_override_application(
                organization_id=str(organization_id),
                role_id=str(role_id),
                role_type=role.code if role else "unknown",
                permission_resource=permission.resource if permission else "unknown",
                permission_action=permission.action if permission else "unknown",
                effect=effect.value,
                operation="update",
                created_by=str(created_by),
                override_id=str(existing.id),
                previous_effect=previous_effect
            )
            
            # Invalidate cache for all users with this role
            self._invalidate_role_cache(organization_id, role_id)
            
            return existing
        else:
            # Create new override
            override = OrgRolePermissionOverride(
                organization_id=organization_id,
                role_id=role_id,
                permission_id=permission_id,
                effect=effect,
                created_by=created_by
            )
            self.db.add(override)
            self.db.commit()
            self.db.refresh(override)
            
            # Get role and permission details for logging
            role = self.db.query(Role).filter(Role.id == role_id).first()
            permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
            
            self.logger.log_override_application(
                organization_id=str(organization_id),
                role_id=str(role_id),
                role_type=role.code if role else "unknown",
                permission_resource=permission.resource if permission else "unknown",
                permission_action=permission.action if permission else "unknown",
                effect=effect.value,
                operation="create",
                created_by=str(created_by),
                override_id=str(override.id)
            )
            
            # Invalidate cache for all users with this role
            self._invalidate_role_cache(organization_id, role_id)
            
            return override
    
    def _invalidate_role_cache(self, organization_id: UUID, role_id: UUID):
        """
        Invalidate cache for all users with specific role in organization.
        
        Args:
            organization_id: Organization ID
            role_id: Role ID
        """
        # Get all users with this role
        user_roles = self.db.query(OrgMemberRole).filter(
            OrgMemberRole.organization_id == organization_id,
            OrgMemberRole.role_id == role_id
        ).all()
        
        # Invalidate cache for each user
        for user_role in user_roles:
            self.invalidate_permission_cache(user_role.user_id, organization_id)
