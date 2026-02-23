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

    logger.info(f"Executing SQL script via psql: {filename}")
    
    # Use psql command line tool for better reliability with large scripts
    # We use the DATABASE_URL from environment which should be available
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL not found in environment")
        return

    import subprocess
    try:
        # Run psql command
        result = subprocess.run(
            ['psql', db_url, '-f', filepath],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Successfully executed {filename}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to execute {filename} via psql: {e.stderr}")
        # In case of DDL/DML errors, we might want to know if it's already applied
        if "already exists" in e.stderr.lower():
            logger.warning(f"Note: Some objects in {filename} may already exist.")
        else:
            raise e
    except Exception as e:
        logger.error(f"Unexpected error executing {filename}: {e}")
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

        # Check 005: User Profile Fields (bio, address, etc)
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='users' AND column_name='bio')"
        ))
        if not result.scalar():
            logger.info("Missing user profile fields. Running 005_add_user_profile_fields.sql...")
            run_sql_file(db, "005_add_user_profile_fields.sql")

        # Check 006: User Specialization
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='users' AND column_name='specialization')"
        ))
        if not result.scalar():
            logger.info("Missing user specialization column. Running 006_add_user_specialization.sql...")
            run_sql_file(db, "006_add_user_specialization.sql")

        # Check 007: Audit Assignments
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='audits' AND column_name='assigned_to_user_id')"
        ))
        if not result.scalar():
            logger.info("Missing audit assignment columns. Running 007_audit_assignments.sql...")
            run_sql_file(db, "007_audit_assignments.sql")

        # Check 008: Chat Module
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'chat_channels')"
        ))
        if not result.scalar():
            logger.info("Missing chat module tables. Running 008_chat_module.sql...")
            run_sql_file(db, "008_chat_module.sql")

        # Check 009: Work Order Assignment
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='work_orders' AND column_name='assigned_to_user_id')"
        ))
        if not result.scalar():
            logger.info("Missing work order assignment column. Running 009_work_order_assignment.sql...")
            run_sql_file(db, "009_work_order_assignment.sql")

        # Check: City in Farms
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='farms' AND column_name='city')"
        ))
        if not result.scalar():
            logger.info("Missing city column in farms. Running migration_add_city_to_farms.sql...")
            run_sql_file(db, "migration_add_city_to_farms.sql")

        # Check 010: Work Order Access Granted
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='work_orders' AND column_name='access_granted')"
        ))
        if not result.scalar():
            logger.info("Missing work order access_granted column. Running 010_add_work_order_access_granted.sql...")
            run_sql_file(db, "010_add_work_order_access_granted.sql")

        # Check 011: Audit Has Report
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='audits' AND column_name='has_report')"
        ))
        if not result.scalar():
            logger.info("Missing audit has_report column. Running 011_add_audit_has_report.sql...")
            run_sql_file(db, "011_add_audit_has_report.sql")

        # Check 012: Consultancy Master Service
        # We always run this as the SQL script handles idempotency (INSERT ... SELECT ... WHERE NOT EXISTS)
        logger.info("Ensuring CONSULTANCY master service exists. Running 012_add_consultancy_master_service.sql...")
        run_sql_file(db, "012_add_consultancy_master_service.sql")

        # Check 013: Video Sessions
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'video_sessions')"
        ))
        if not result.scalar():
            logger.info("Missing video_sessions table. Running 013_create_video_sessions.sql...")
            run_sql_file(db, "013_create_video_sessions.sql")

        # Check 014: Pricing Unit in Work Orders
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='work_orders' AND column_name='pricing_unit')"
        ))
        if not result.scalar():
            logger.info("Missing pricing_unit column. Running 014_add_pricing_unit_to_work_orders.sql...")
            run_sql_file(db, "014_add_pricing_unit_to_work_orders.sql")

        # Check 015: Machinery Master Service
        logger.info("Ensuring MACHINERY master service exists. Running 015_add_machinery_master_service.sql...")
        run_sql_file(db, "015_add_machinery_master_service.sql")

        # Fix Audit Photos Schema (v2)
        # Check for is_flagged_for_report column
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='audit_response_photos' AND column_name='is_flagged_for_report')"
        ))
        if not result.scalar():
            logger.info("Fixing audit photos schema. Running fix_audit_photos_schema_v2.sql...")
            run_sql_file(db, "fix_audit_photos_schema_v2.sql")

        # Fix Missing Audit Tables
        # Check for audit_report_templates table
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'audit_report_templates')"
        ))
        if not result.scalar():
            logger.info("Fixing missing audit tables. Running fix_missing_audit_tables.sql...")
            run_sql_file(db, "fix_missing_audit_tables.sql")

        # Update Input Item Type Enum
        logger.info("Updating input item type if needed. Running update_input_item_type.sql...")
        run_sql_file(db, "update_input_item_type.sql")


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
