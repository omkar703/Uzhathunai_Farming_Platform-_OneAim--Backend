import os
import sys
import time
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.organization import OrgMemberRole
from app.models.rbac import Role

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPER_ADMIN_EMAIL = "superadmin@uzhathunai.com"
SUPER_ADMIN_PASSWORD = "SuperSecure@Admin123"
SUPER_ADMIN_FIRST_NAME = "System"
SUPER_ADMIN_LAST_NAME = "Admin"
SUPER_ADMIN_PHONE = "+919000000001"

DB_SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db_scripts")

def wait_for_db():
    logger.info("Waiting for database connection...")
    retries = 30
    while retries > 0:
        try:
            # Try to create a session to check connection
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("Database connection established.")
            return
        except Exception as e:
            logger.warning(f"Database unavailable, retrying in 2 seconds... Error: {e}")
            time.sleep(2)
            retries -= 1
    
    logger.error("Could not connect to database after many retries.")
    sys.exit(1)

def run_sql_file(db: Session, filename: str):
    filepath = os.path.join(DB_SCRIPTS_DIR, filename)
    if not os.path.exists(filepath):
        logger.error(f"SQL file not found: {filepath}")
        return

    logger.info(f"Executing SQL script: {filename}")
    with open(filepath, "r") as f:
        sql_content = f.read()
        # Simple split by ';' might be fragile for complex PL/PGSQL or strings containing semicolons.
        # But for standard seed scripts it's usually okay if we execute as one block or split carefully.
        # SQLAlchemy execute(text()) can handle multiple statements if supported by driver, 
        # but often it's safer to read the whole file and let the DB execute it.
        # However, psycopg2 usually prefers one statement per execute unless configured otherwise.
        # Let's try executing the whole block first.
        try:
            db.execute(text(sql_content))
            db.commit()
            logger.info(f"Successfully executed {filename}")
        except Exception as e:
            logger.error(f"Failed to execute {filename}: {e}")
            db.rollback()
            # If it fails, we might want to exit or continue based on severity.
            # DDL failure is critical. DML failure might be due to duplicates.
            raise e

def initialize_db():
    wait_for_db()
    
    db = SessionLocal()
    try:
        # Check if users table exists to determine if we need to run DDL
        # Using a safer check than execute("SELECT 1 FROM users") which throws if table missing
        # We can check information_schema
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        ))
        users_table_exists = result.scalar()

        if not users_table_exists:
            logger.info("Database seems empty. Initializing schema...")
            run_sql_file(db, "001_uzhathunai_ddl.sql")
        else:
            logger.info("Schema (users) appears to exist.")

        # Check 002: Refresh Tokens
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'refresh_tokens')"
        ))
        if not result.scalar():
            logger.info("Missing refresh_tokens. Running 002_create_refresh_tokens_table.sql...")
            run_sql_file(db, "002_create_refresh_tokens_table.sql")
            
        # Check 003: Audit Changes (Check for sync_status column)
        # Note: We assume if sync_status is missing, the whole script needs to run. 
        # If partial application occurred, this might error on type creation, but manual intervention would be needed anyway.
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='audits' AND column_name='sync_status')"
        ))
        if not result.scalar():
            logger.info("Missing audit schema updates. Running 003_audit_module_changes.sql...")
            run_sql_file(db, "003_audit_module_changes.sql")

        # Check 004: Organization Approval (Check for is_approved column)
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='organizations' AND column_name='is_approved')"
        ))
        if not result.scalar():
            logger.info("Missing is_approved column. Running 004_add_is_approved_to_orgs.sql...")
            run_sql_file(db, "004_add_is_approved_to_orgs.sql")


        # Check if Roles exist (Seed Data)
        # Using count check
        role_count = db.execute(text("SELECT count(*) FROM roles")).scalar()
        if role_count == 0:
            logger.info("Seeding initial data (DML)...")
            run_sql_file(db, "a01_uzhathunai_dml.sql")
            run_sql_file(db, "a02_uzhathunai_dml_RBAC.sql")
            run_sql_file(db, "a03_uzhathunai_dml_input_items.sql")
        else:
            logger.info("Seed data appears to exist.")

        # Create Super Admin
        create_super_admin(db)
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)
    finally:
        db.close()

def create_super_admin(db: Session):
    user = db.query(User).filter(User.email == SUPER_ADMIN_EMAIL).first()
    if user:
        logger.info(f"Super Admin user ({SUPER_ADMIN_EMAIL}) already exists.")
        return

    logger.info(f"Creating Super Admin user: {SUPER_ADMIN_EMAIL}")
    
    try:
        new_user = User(
            email=SUPER_ADMIN_EMAIL,
            password_hash=get_password_hash(SUPER_ADMIN_PASSWORD),
            first_name=SUPER_ADMIN_FIRST_NAME,
            last_name=SUPER_ADMIN_LAST_NAME,
            phone=SUPER_ADMIN_PHONE,
            is_active=True,
            is_verified=True
        )
        db.add(new_user)
        db.flush() # Get ID
        
        # Assign SUPER_ADMIN role
        # Try to find the role ID from DB
        role = db.query(Role).filter(Role.code == 'SUPER_ADMIN').first()
        if not role:
            logger.error("SUPER_ADMIN role not found! Access control will fail.")
            # Depending on policy, we might create it here or fail. 
            # Ideally seeding scripts should have created it.
            return

        # Assign role in org_member_roles with organization_id = NULL (System Scope)
        member_role = OrgMemberRole(
            user_id=new_user.id,
            organization_id=None,
            role_id=role.id,
            is_primary=True
        )
        db.add(member_role)
        
        db.commit()
        logger.info("Super Admin created successfully via OrgMemberRole (System Scope).")
        
    except Exception as e:
        logger.error(f"Failed to create Super Admin: {e}")
        db.rollback()
        raise e

if __name__ == "__main__":
    initialize_db()
