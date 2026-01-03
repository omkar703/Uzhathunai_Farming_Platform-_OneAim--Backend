from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.work_order import WorkOrder
from app.models.video_session import VideoSession
# Add other models if needed for foreign keys, usually imports in the models/init help, 
# but I should import them explicitly if I want to be safe.
from app.models import organization, farm, crop, fsp_service

def init_db():
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    # Seed Initial Data
    db = SessionLocal()
    try:
        # Check/Create Master Service
        from app.models.fsp_service import MasterService
        import uuid
        
        # Use a fixed UUID so we can give it to the user in docs
        service_id = uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6") 
        
        ms = db.query(MasterService).filter(MasterService.id == service_id).first()
        if not ms:
            print("Seeding Master Service...")
            ms = MasterService(
                id=service_id,
                code="CONSULTATION",
                name="General Consultation",
                description="Expert advice on farming practices"
            )
            db.add(ms)
            db.commit()
            print(f"Seeded Master Service: {ms.name} (ID: {ms.id})")
        else:
            print(f"Master Service exists: {ms.id}")
            
        # Check/Create Roles
        from app.models.rbac import Role
        from app.models.enums import UserRoleScope
        
        roles_data = [
            {"code": "FREELANCER", "name": "Freelancer", "scope": UserRoleScope.SYSTEM, "description": "Independent user"},
            {"code": "OWNER", "name": "Owner", "scope": UserRoleScope.ORGANIZATION, "description": "Organization Owner"},
            {"code": "ADMIN", "name": "Admin", "scope": UserRoleScope.ORGANIZATION, "description": "Organization Admin"},
            {"code": "MEMBER", "name": "Member", "scope": UserRoleScope.ORGANIZATION, "description": "Organization Member"},
            {"code": "FSP_OWNER", "name": "FSP Owner", "scope": UserRoleScope.ORGANIZATION, "description": "FSP Organization Owner"},
            {"code": "FSP_ADMIN", "name": "FSP Admin", "scope": UserRoleScope.ORGANIZATION, "description": "FSP Organization Admin"},
            {"code": "FSP_AGENT", "name": "FSP Agent", "scope": UserRoleScope.ORGANIZATION, "description": "FSP Agent"},
            {"code": "SUPER_ADMIN", "name": "Super Admin", "scope": UserRoleScope.SYSTEM, "description": "System-wide Super Admin"}
        ]
        
        
        print(f"Roles data count: {len(roles_data)}")
        for r_data in roles_data:
            print(f"Checking role: {r_data['code']}")
            role = db.query(Role).filter(Role.code == r_data["code"]).first()
            if not role:
                print(f"Seeding Role: {r_data['name']}...")
                new_role = Role(
                    code=r_data["code"],
                    name=r_data["name"],
                    display_name=r_data["name"],
                    scope=r_data["scope"],
                    description=r_data["description"]
                )
                db.add(new_role)
            else:
                print(f"Role {r_data['code']} exists.")
        db.commit()
        print("Seeded Roles.")
            
    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
