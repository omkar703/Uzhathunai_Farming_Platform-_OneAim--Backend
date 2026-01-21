import sys
import os
from datetime import date, timedelta
from uuid import UUID

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.models.organization import Organization
from app.services.farm_service import FarmService
from app.services.plot_service import PlotService
from app.services.crop_service import CropService
from app.services.schedule_service import ScheduleService
from app.schemas.farm import FarmCreate
from app.schemas.plot import PlotCreate
from app.schemas.crop import CropCreate
from app.models.enums import CropLifecycle

# IDs from prompt
USER_ID = "661068b0-348b-4ef9-974e-2fd5b237aab6"
ORG_ID = "79286b56-dea9-41dc-9ff2-46ca890fd67d"

def seed_data():
    db = SessionLocal()
    try:
        # 1. Get User
        user = db.query(User).filter(User.id == USER_ID).first()
        if not user:
            print(f"User {USER_ID} not found!")
            return
        
        # Set current organization context for the user (important for permission checks)
        user.current_organization_id = UUID(ORG_ID)
        print(f"Found User: {user.email}")

        # 2. Create/Get Farm
        farm_service = FarmService(db)
        # Check if farm exists
        from app.models.farm import Farm
        farm = db.query(Farm).filter(
            Farm.organization_id == ORG_ID,
            Farm.name == "Green Valley Farm"
        ).first()
        
        if not farm:
            print("Creating Green Valley Farm...")
            farm = farm_service.create_farm(
                data=FarmCreate(
                    name="Green Valley Farm",
                    organization_id=UUID(ORG_ID),
                    total_area=10.0,
                    latitude=11.0,
                    longitude=77.0,
                    location={"type": "Point", "coordinates": [77.0, 11.0]},
                    elevation=100,
                    address="123 Farm Road",
                    district="Coimbatore",
                    state="Tamil Nadu",
                    pincode="641001"
                ),
                org_id=user.current_organization_id,
                user_id=user.id
            )
        print(f"Farm: {farm.id}")

        # 3. Create/Get Plot
        plot_service = PlotService(db)
        from app.models.plot import Plot
        plot = db.query(Plot).filter(
            Plot.farm_id == farm.id,
            Plot.name == "North Field"
        ).first()
        
        if not plot:
            print("Creating North Field Plot...")
            plot = plot_service.create_plot(
                farm_id=farm.id,
                data=PlotCreate(
                    name="North Field",
                    farm_id=farm.id,
                    area=5.0,
                    soil_type="Red Soil",
                    description="Main plot"
                ),
                org_id=user.current_organization_id,
                user_id=user.id
            )
        print(f"Plot: {plot.id}")

        # 4. Create/Get Crop
        crop_service = CropService(db)
        from app.models.crop import Crop
        crop = db.query(Crop).filter(
            Crop.plot_id == plot.id,
            Crop.name == "Tomato"
        ).first()
        
        if not crop:
            print("Creating Tomato Crop...")
            # We need a valid crop type and variety. 
            from app.models.crop_data import CropType, CropVariety
            crop_type = db.query(CropType).first()
            variety = db.query(CropVariety).first()
            
            crop_type_id = crop_type.id if crop_type else UUID("00000000-0000-0000-0000-000000000001")
            variety_id = variety.id if variety else UUID("00000000-0000-0000-0000-000000000001")
            
            crop = crop_service.create_crop(
                plot_id=plot.id,
                org_id=user.current_organization_id,
                data=CropCreate(
                    name="Tomato",
                    plot_id=plot.id,
                    crop_type_id=crop_type_id,
                    variety_id=variety_id,
                    sowing_date=date.today(),
                    area=2.0
                ),
                user_id=user.id
            )
        print(f"Crop: {crop.id}")

        # 5. Create Schedules
        schedule_service = ScheduleService(db)
        
        schedules_data = [
            ("Tomato Sowing Plan", "Active schedule", date.today()),
            ("Fertilizer Schedule", "Pending schedule", date.today() + timedelta(days=5)),
            ("Harvest Plan", "Future schedule", date.today() + timedelta(days=60)),
        ]
        
        for name, desc, start in schedules_data:
            print(f"Creating schedule: {name}...")
            # Check if schedule already exists
            from app.models.schedule import Schedule
            existing = db.query(Schedule).filter(
                Schedule.crop_id == crop.id,
                Schedule.name == name
            ).first()
            
            if existing:
                print(f"Schedule '{name}' already exists: {existing.id}")
                continue

            schedule = schedule_service.create_schedule_from_scratch(
                crop_id=crop.id,
                name=name,
                description=desc,
                user=user
            )
            print(f"Schedule '{name}' created: {schedule.id}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
