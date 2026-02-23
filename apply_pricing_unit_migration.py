import psycopg2

# Database connection parameters (targeting Docker mapped port 5433)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'farm_db',  # From docker-compose.yml: POSTGRES_DB: farm_db
    'user': 'postgres',     # From docker-compose.yml: POSTGRES_USER: postgres
    'password': 'postgres'  # From docker-compose.yml: POSTGRES_PASSWORD: postgres
}

def run_migration():
    try:
        print("Connecting to database on localhost:5433...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Executing: ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS pricing_unit VARCHAR(50);")
        cursor.execute("ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS pricing_unit VARCHAR(50);")
        
        conn.commit()
        print("✅ Migration applied successfully!")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    run_migration()
