import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/uzhathunai_db_v2")
engine = create_engine(DATABASE_URL)

def check_schema():
    with engine.connect() as conn:
        print("--- Table Definition: organizations ---")
        result = conn.execute(text("""
            SELECT column_name, data_type, udt_name, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'organizations';
        """))
        for row in result:
            print(f"Column: {row.column_name} | Type: {row.data_type} | UDT: {row.udt_name} | Default: {row.column_default}")

        print("\n--- Triggers on organizations ---")
        result = conn.execute(text("""
            SELECT trigger_name, event_manipulation, condition_timing, action_statement
            FROM information_schema.triggers
            WHERE event_object_table = 'organizations';
        """))
        triggers = result.all()
        if not triggers:
            print("No triggers found.")
        for row in triggers:
            print(f"Trigger: {row.trigger_name} | Event: {row.event_manipulation} | Timing: {row.condition_timing}")
            print(f"Action: {row.action_statement}\n")

        print("\n--- Constraint Definition: organizations ---")
        result = conn.execute(text("""
            SELECT conname, pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            WHERE t.relname = 'organizations';
        """))
        for row in result:
            print(f"Constraint: {row.conname} | Definition: {row.pg_get_constraintdef}")

if __name__ == "__main__":
    check_schema()
