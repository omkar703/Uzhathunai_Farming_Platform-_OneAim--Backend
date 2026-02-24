#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready..."

while ! pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done

echo "PostgreSQL is ready"

echo "Running database SQL scripts..."

psql "postgresql://postgres:postgres@db:5432/farm_db" <<'EOF'
\i db_scripts/001_uzhathunai_ddl.sql
\i db_scripts/002_create_refresh_tokens_table.sql
\i db_scripts/003_audit_module_changes.sql
\i db_scripts/fix_photos_schema.sql
\i db_scripts/create_audit_reports_table.sql
\i db_scripts/a01_uzhathunai_dml.sql
\i db_scripts/a02_uzhathunai_dml_RBAC.sql
\i db_scripts/a03_uzhathunai_dml_input_items.sql
EOF

echo "Database schema and seed data applied"

echo "Running migrations..."
python run_all_migrations.py

echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
