# Database Scripts

This folder contains all database DDL and DML scripts for Uzhathunai v2.0.

## Script Naming Convention

Scripts are numbered sequentially with a 3-digit prefix:

```
<nnn>_<descriptive_name>.sql
```

Where:
- `<nnn>` is a 3-digit sequence number (001, 002, 003, etc.)
- `<descriptive_name>` is a clear description of what the script does

## Execution Order

Scripts should be executed in numerical order:

1. `001_uzhathunai_ddl.sql` - Main database schema
2. `002_create_refresh_tokens_table.sql` - Refresh tokens for authentication
3. `a01_uzhathunai_dml.sql` - Sample data (optional)

## Script Types

### DDL Scripts (Data Definition Language)
- Create/modify tables, indexes, constraints
- Prefix: `<nnn>_`
- Examples: `001_uzhathunai_ddl.sql`, `002_create_refresh_tokens_table.sql`

### DML Scripts (Data Manipulation Language)
- Insert/update/delete data
- Prefix: `a<nn>_`
- Examples: `a01_uzhathunai_dml.sql`

## Current Scripts

### 001_uzhathunai_ddl.sql
**Purpose**: Main database schema for Uzhathunai v2.0  
**Created**: Initial version  
**Status**: ✅ Executed  
**Contains**:
- All custom types (ENUMs)
- System administration tables (roles, permissions, subscription_plans)
- Organization and user management tables
- Reference data tables
- Farm management tables
- Input items and finance tables
- Schedule management tables
- FSP and work order tables
- Query management tables
- Farm audit system tables
- Notification tables

### 002_create_refresh_tokens_table.sql
**Purpose**: Create refresh_tokens table for JWT authentication  
**Created**: 2025-11-19  
**Status**: ⏳ Pending execution  
**Contains**:
- refresh_tokens table
- Indexes for performance
- Comments for documentation

**To Execute**:
```bash
psql -U postgres -d uzhathunai_db_v2 -f backend/db_scripts/002_create_refresh_tokens_table.sql
```

### a01_uzhathunai_dml.sql
**Purpose**: Sample data for development and testing  
**Created**: Initial version  
**Status**: ⏳ Optional  
**Contains**:
- Sample reference data
- Sample organizations
- Sample users
- Sample roles and permissions

**To Execute** (optional):
```bash
psql -U postgres -d uzhathunai_db_v2 -f backend/db_scripts/a01_uzhathunai_dml.sql
```

## Adding New Scripts

When adding new database scripts:

1. **Determine the next sequence number**
   - Check existing scripts
   - Use next available number (e.g., 003, 004, etc.)

2. **Use proper naming**
   - DDL: `<nnn>_descriptive_name.sql`
   - DML: `a<nn>_descriptive_name.sql`

3. **Include header comment**
   ```sql
   -- <nnn>_script_name.sql
   -- Purpose: Brief description
   -- Author: Your name
   -- Date: YYYY-MM-DD
   -- Approved: Yes/No
   ```

4. **Add documentation**
   - Update this README.md
   - Document what the script does
   - Document execution status

5. **Get approval**
   - Database schema changes require approval
   - Exception: Observability/metrics tables

## Database Schema Rules

### ❌ DO NOT (Without Approval)
- Modify `001_uzhathunai_ddl.sql`
- Add/remove columns to existing tables
- Add/remove tables
- Change constraints
- Rename tables or columns

### ✅ CAN DO (With Proper Documentation)
- Create observability/metrics tables
- Create indexes for performance
- Add comments for documentation
- Create views for reporting

## Rollback Scripts

For each DDL script that modifies schema, consider creating a rollback script:

```
<nnn>_script_name.sql          # Forward migration
<nnn>_rollback_script_name.sql # Rollback migration
```

Example:
```
002_create_refresh_tokens_table.sql
002_rollback_refresh_tokens_table.sql
```

## Verification

After executing a script, verify:

1. **No errors in output**
   ```bash
   # Check for ERROR or FATAL in output
   ```

2. **Tables created**
   ```sql
   \dt  -- List all tables
   \d table_name  -- Describe specific table
   ```

3. **Indexes created**
   ```sql
   \di  -- List all indexes
   ```

4. **Constraints working**
   ```sql
   -- Try inserting invalid data to test constraints
   ```

## Troubleshooting

### Script fails with "relation already exists"
- Table already created
- Check if script was already executed
- Use `DROP TABLE IF EXISTS` in rollback script

### Script fails with "permission denied"
- Check database user permissions
- Ensure user has CREATE privileges

### Script fails with "syntax error"
- Check PostgreSQL version compatibility
- Verify SQL syntax
- Check for missing semicolons

## References

- Main DDL: `001_uzhathunai_ddl.sql`
- Database Design Docs: `db_design_evolution_reference/`
- Comprehensive Guide: `docs/uzhathunai_ver2.0.md`
