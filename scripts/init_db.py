from app.core.database import Base, engine
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

if __name__ == "__main__":
    init_db()
