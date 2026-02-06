#!/usr/bin/env python3
"""
Quick script to test the schedule endpoint fix for schedule a2ea30cb-57cf-4b04-9ab1-75f5f909e700
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import UUID

# Import models and service
from app.models.user import User
from app.services.schedule_service import ScheduleService

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/farm_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_schedule():
    db = SessionLocal()
    try:
        # Get the FSP user (fsp1@gmail.com)
        user = db.query(User).filter(User.email == "fsp1@gmail.com").first()
        if not user:
            print("ERROR: User fsp1@gmail.com not found")
            return
        
        print(f"✓ Found user: {user.email}")
        
        # Get the schedule
        schedule_id = UUID("a2ea30cb-57cf-4b04-9ab1-75f5f909e700")
        service = ScheduleService(db)
        
        print(f"\n📋 Fetching schedule {schedule_id}...")
        response = service.get_schedule_with_details(user, schedule_id)
        
        print(f"\n✅ Schedule: {response.name}")
        print(f"   Area: {response.area}")
        print(f"   Area Unit: {response.area_unit}")
        print(f"   Total Tasks: {len(response.tasks)}")
        
        print(f"\n📝 Task Details:")
        for i, task in enumerate(response.tasks, 1):
            print(f"\n   Task {i}:")
            print(f"      Input Item: {task.input_item_name}")
            print(f"      Method: {task.application_method_name}")
            print(f"      Total Qty: {task.total_quantity_required}")
            print(f"      Dosage: {task.dosage}")
            print(f"      Task Details Empty: {not task.task_details or task.task_details == {}}")
            
            # Check for nulls
            if task.input_item_name is None:
                print(f"      ❌ ERROR: input_item_name is NULL")
            if task.application_method_name is None:
                print(f"      ❌ ERROR: application_method_name is NULL")
            if task.total_quantity_required is None:
                print(f"      ❌ ERROR: total_quantity_required is NULL")
            if task.dosage is None:
                print(f"      ⚠️  WARNING: dosage is NULL")
        
        print("\n✅ Fix verification complete!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_schedule()
