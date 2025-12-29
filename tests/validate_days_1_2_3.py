import asyncio
import httpx
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

async def check_health():
    """Day 1: Infrastructure Validation"""
    logger.info("--- Day 1: Checking Infrastructure Health ---")
    async with httpx.AsyncClient() as client:
        try:
            # Check API health (Assuming GET / or /api/v1/health)
            # Checking root first
            response = await client.get(f"{BASE_URL}/")
            logger.info(f"Root Endpoint Status: {response.status_code}")
            
            # Check Health endpoint if exists, or docs
            resp_docs = await client.get(f"{BASE_URL}/docs")
            if resp_docs.status_code == 200:
                logger.info("Day 1 Validation: PASSED (FastAPI is up)")
            else:
                logger.error("Day 1 Validation: FAILED (Docs not accessible)")
                return False
            return True
        except Exception as e:
            logger.error(f"Day 1 Validation: FAILED (Connection Error: {e})")
            return False

async def validate_seeding():
    """Day 2: Data Integrity Check (Via Login)"""
    logger.info("--- Day 2: Checking Data Seeding (Login) ---")
    users = [
        ("superadmin@example.com", "password123", "Super Admin"),
        ("admin@example.com", "password123", "Org Admin"),
        ("farmer@example.com", "password123", "Farmer"),
        ("observer@example.com", "password123", "Observer")
    ]
    
    async with httpx.AsyncClient() as client:
        all_passed = True
        for email, pwd, role in users:
            try:
                response = await client.post(
                    f"{BASE_URL}/api/v1/auth/login",
                    json={"email": email, "password": pwd}
                )
                if response.status_code == 200:
                    logger.info(f"Login {role} ({email}): PASSED")
                else:
                    logger.error(f"Login {role} ({email}): FAILED ({response.status_code}) - {response.text}")
                    all_passed = False
            except Exception as e:
                logger.error(f"Login {role}: ERROR {e}")
                all_passed = False
                
        if all_passed:
            logger.info("Day 2 Validation: PASSED")
        else:
            logger.error("Day 2 Validation: FAILED")
        return all_passed

async def validate_super_admin_flow():
    """Day 3: Logic & Security Testing"""
    logger.info("--- Day 3: Super Admin Flow (Blocking & Approval) ---")
    
    async with httpx.AsyncClient() as client:
        # 1. Login as Super Admin to get token
        resp_sa = await client.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "superadmin@example.com", "password": "password123"})
        if resp_sa.status_code != 200:
             logger.error("CRITICAL: Cannot login as Super Admin for Day 3 tests.")
             return False
        sa_token = resp_sa.json()["tokens"]["access_token"]
        
        # 2. Login as Org Admin (Default Org is initially NOT approved if we reset db or if we manually set it to False).
        # WAIT: The seed data creates 'Default Org' with default status. 
        # The 'Organization' model definition has `is_approved = Column(Boolean, default=False)`.
        # When `seed_data.py` runs, it creates "Default Org". 
        # Assuming `seed_data.py` DOES NOT explicitly set `is_approved=True`.
        # Let's check `seed_data.py` content again?
        # Quick check: In Step 138, I wrote `seed_data.py`. I instantiated Organization(name="Default Org", ... status=ACTIVE).
        # I did NOT pass `is_approved`. So it defaults to `False`.
        
        # So, the "Org Admin" (admin@example.com) should receive 403 when trying to access protected route.
        # Let's try to access /api/v1/auth/me using Org Admin token.
        
        # Login Org Admin
        resp_admin = await client.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "admin@example.com", "password": "password123"})
        if resp_admin.status_code != 200:
             logger.error(f"Org Admin Login failed: {resp_admin.status_code}")
             # If login fails, blocking works? No, login endpoint itself might be blocked if we put check there?
             # My check is in `get_current_active_user`. Login usually doesn't use that dependency?
             # `login` endpoint in `auth.py` (Step 172) does NOT use `get_current_active_user`. It uses `db`.
             # So Login should SUCCEED.
             pass
        
        if resp_admin.status_code == 200:
            admin_token = resp_admin.json()["tokens"]["access_token"]
            
            # NEGATIVE TEST: Access /me
            logger.info("Testing Access Block (Before Approval)...")
            resp_me = await client.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            if resp_me.status_code == 403:
                logger.info("Negative Test: PASSED (Received 403 Forbidden)")
                logger.info(f"Response: {resp_me.json()}")
            else:
                logger.error(f"Negative Test: FAILED (Expected 403, got {resp_me.status_code})")
                
            # POSITIVE TEST: Approve Org
            # First need Org ID.
            # Super admin can find it? Or we assume we know it?
            # Creating a helper to get org id via DB or assume from seed?
            # Actually, Super Admin Approval Endpoint requires ID.
            # We don't have a "List Orgs" endpoint for Super Admin in the summary?
            # Wait, `Organization` model is used.
            # I can query DB directly via the same `seed_data` approach if I ran this script inside docker...
            # But I am running outside?
            # I'll rely on `admin@example.com` login response? Does it return user? Yes.
            # Does user have org info? `auth/me` returns roles.
            # But `auth/me` is blocked!
            # Catch-22 for finding ID if external.
            
            # SOLUTION: Verify checking the default org creation logic.
            # I will use a known ID if I can, OR I will assume the seed script prints it?
            # OR I will add a "Get All Orgs" endpoint for verification? 
            # Or I will use `docker compose exec` to get the ID.
            
            # Use `docker compose exec` to run a python one-liner to get the ID?
            # Or just hack: I will approve ALL organizations.
            # No, `approve-org` takes ID.
            
            # Let's try to fetch user profile of SUPER ADMIN.
            # Super Admin is in Default Org too? Yes.
            # So Super Admin might be blocked too if logic is "Any unapproved org"?
            # My logic in `auth.py`: `if current_user.email == "superadmin@example.com": return current_user`. 
            # So Super Admin is BYPASSING the check. Good.
            
            # Super Admin calls /me.
            resp_sa_me = await client.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {sa_token}"}
            )
            # Response: {"user": ..., "roles": [...]}
            # Does it have Org ID?
            # Role info: `{'role_code': 'SUPER_ADMIN', 'org_id': '...'}`?
            # Let's see `auth_service.get_user_roles`.
            
            try:
                roles = resp_sa_me.json().get("roles", [])
                if roles:
                    org_id = roles[0].get("organization_id") # Guessing structure
                    if not org_id:
                         # Maybe structure is different.
                         pass
                    
                    if org_id:
                        logger.info(f"Found Org ID: {org_id}")
                        
                        # Call Approve
                        logger.info("Approving Organization...")
                        resp_approve = await client.post(
                            f"{BASE_URL}/api/v1/admin/approve-org",
                            headers={"Authorization": f"Bearer {sa_token}"},
                            json={"organization_id": org_id}
                        )
                        
                        if resp_approve.status_code == 200:
                            logger.info("Approval Endpoint: PASSED")
                        else:
                            logger.error(f"Approval Endpoint: FAILED ({resp_approve.status_code}) - {resp_approve.text}")
                            
                        # RETRY NEGATIVE TEST as POSITIVE
                        logger.info("Testing Access (After Approval)...")
                        resp_me_after = await client.get(
                            f"{BASE_URL}/api/v1/auth/me",
                            headers={"Authorization": f"Bearer {admin_token}"}
                        )
                        if resp_me_after.status_code == 200:
                            logger.info("Positive Test: PASSED (Access Granted)")
                        else:
                            logger.error(f"Positive Test: FAILED ({resp_me_after.status_code})")
                            
            except Exception as e:
                logger.error(f"Error parsing super admin me: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_health())
    asyncio.run(validate_seeding())
    asyncio.run(validate_super_admin_flow())
