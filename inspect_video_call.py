import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Try to find the DB URL from .env
db_url = "postgresql://postgres:postgres@localhost:5432/farm_db"
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if "DATABASE_URL" in line:
                db_url = line.split("=")[1].strip().strip('"')

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

print("--- RECENT NOTIFICATIONS ---")
result = session.execute(text("SELECT id, user_id, organization_id, notification_type, type, title, created_at FROM notifications ORDER BY created_at DESC LIMIT 10"))
for row in result:
    print(row)

print("\n--- RECENT VIDEO SESSIONS ---")
result = session.execute(text("SELECT id, work_order_id, status, created_at FROM video_sessions ORDER BY created_at DESC LIMIT 10"))
for row in result:
    print(row)

print("\n--- RECENT ORG MEMBERS ---")
result = session.execute(text("SELECT user_id, organization_id, status FROM org_members LIMIT 10"))
for row in result:
    print(row)

print("\n--- WORK ORDERS ---")
result = session.execute(text("SELECT id, farming_organization_id, fsp_organization_id, status FROM work_orders LIMIT 5"))
for row in result:
    print(row)

session.close()
