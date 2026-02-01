
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

# Connection parameters for the default postgres database
DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_PORT = "5432"
TARGET_DB = "farm_db"

def create_database():
    try:
        # Connect to default 'postgres' database
        con = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        
        # Check if database exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{TARGET_DB}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creating database {TARGET_DB}...")
            cur.execute(f"CREATE DATABASE {TARGET_DB}")
            print(f"Database {TARGET_DB} created successfully.")
        else:
            print(f"Database {TARGET_DB} already exists.")
            
        cur.close()
        con.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def create_tables():
    print("Creating tables...")
    try:
        # Set environment variable for SQLAlchemy to pick up
        os.environ["DATABASE_URL"] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{TARGET_DB}"
        
        # Import after setting env var
        from app.core.database import engine, Base
        import app.models # Import all models to register them
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if create_database():
        create_tables()
