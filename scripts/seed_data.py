"""
Seed the database with initial data (Roles, Super Admin).
Usage: python -m scripts.seed_data
"""
import sys
import os
# import asyncio # No longer needed for sync

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import SessionLocal # Using sync session
from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.enums import OrganizationType, OrganizationStatus, UserRoleScope, MemberStatus
from app.core.security import get_password_hash

def seed_data():
    with SessionLocal() as session:
        print("Seeding data...")
        
        # 1. Create Default Organization
        result = session.execute(select(Organization).where(Organization.name == "Default Org"))
        default_org = result.scalars().first()
        if not default_org:
            default_org = Organization(
                name="Default Org", 
                # is_active=True, # Note: Check if is_active exists, model says 'status'
                status=OrganizationStatus.ACTIVE,
                organization_type=OrganizationType.FARMING
            )
            session.add(default_org)
            session.commit()
            session.refresh(default_org)
            print("Created Default Organization")
        
        # 2. Create Roles
        roles_data = [
            {"code": "SUPER_ADMIN", "name": "Super Administrator", "scope": UserRoleScope.SYSTEM},
            {"code": "ADMIN", "name": "Organization Admin", "scope": UserRoleScope.ORGANIZATION},
            {"code": "FARMER", "name": "Farmer", "scope": UserRoleScope.ORGANIZATION},
            {"code": "FIELD_OBSERVER", "name": "Field Observer", "scope": UserRoleScope.ORGANIZATION},
        ]
        
        db_roles = {}
        for r in roles_data:
            result = session.execute(select(Role).where(Role.code == r["code"]))
            role = result.scalars().first()
            if not role:
                role = Role(
                    code=r["code"],
                    name=r["name"],
                    display_name=r["name"],
                    scope=r["scope"],
                    description=f"{r['name']} Role"
                )
                session.add(role)
                session.flush() # Flush to get ID
                print(f"Created Role: {r['code']}")
            db_roles[r["code"]] = role
            
        session.commit()

        # 3. Create Users and Assign Roles
        users_data = [
            {"email": "superadmin@example.com", "name": "Super Admin", "role": "SUPER_ADMIN"},
            {"email": "admin@example.com", "name": "Org Admin", "role": "ADMIN"},
            {"email": "farmer@example.com", "name": "John Farmer", "role": "FARMER"},
            {"email": "observer@example.com", "name": "Field Observer", "role": "FIELD_OBSERVER"},
        ]

        for u in users_data:
            result = session.execute(select(User).where(User.email == u["email"]))
            user = result.scalars().first()
            if not user:
                # Create User
                user = User(
                    email=u["email"],
                    password_hash=get_password_hash("password123"),
                    first_name=u["name"].split()[0],
                    last_name=u["name"].split()[1] if len(u["name"].split()) > 1 else "",
                    is_active=True,
                    is_verified=True
                )
                session.add(user)
                session.flush()
                print(f"Created User: {u['email']}")

            # Create Org Member
            result = session.execute(select(OrgMember).where(
                OrgMember.user_id == user.id, 
                OrgMember.organization_id == default_org.id
            ))
            member = result.scalars().first() 
            if not member:
                member = OrgMember(
                    user_id=user.id,
                    organization_id=default_org.id,
                    status=MemberStatus.ACTIVE
                )
                session.add(member)
                session.flush()
            
            # Create Org Member Role
            role_obj = db_roles[u["role"]]
            result = session.execute(select(OrgMemberRole).where(
                OrgMemberRole.user_id == user.id,
                OrgMemberRole.organization_id == default_org.id,
                OrgMemberRole.role_id == role_obj.id
            ))
            member_role = result.scalars().first()
            if not member_role:
                member_role = OrgMemberRole(
                    user_id=user.id,
                    organization_id=default_org.id,
                    role_id=role_obj.id,
                    is_primary=True
                )
                session.add(member_role)
                print(f"Assigned {u['role']} to {u['email']}")

        session.commit()
        print("Seeding complete!")

if __name__ == "__main__":
    seed_data()
