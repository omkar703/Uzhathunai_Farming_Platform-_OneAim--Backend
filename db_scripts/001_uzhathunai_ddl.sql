-- Uzhathunai Database Schema for PostgreSQL with PostGIS
-- Version: 2.0
-- Description: Multi-tenant farming and FSP management system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For full-text search

-- Create custom types
CREATE TYPE organization_type AS ENUM ('FARMING', 'FSP');
CREATE TYPE organization_status AS ENUM ('NOT_STARTED', 'IN_PROGRESS', 'ACTIVE', 'INACTIVE', 'SUSPENDED');
CREATE TYPE user_role_scope AS ENUM ('SYSTEM', 'ORGANIZATION');
CREATE TYPE member_status AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED');
CREATE TYPE service_status AS ENUM ('ACTIVE', 'INACTIVE');
CREATE TYPE task_status AS ENUM ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'MISSED', 'CANCELLED', 'ON_HOLD');
CREATE TYPE crop_lifecycle AS ENUM ('PLANNED', 'PLANTED', 'TRANSPLANTED', 'PRODUCTION', 'COMPLETED', 'TERMINATED', 'CLOSED');
CREATE TYPE work_order_status AS ENUM ('PENDING', 'ACCEPTED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'REJECTED');
CREATE TYPE work_order_scope_type AS ENUM ('ORGANIZATION', 'FARM', 'PLOT', 'CROP');
CREATE TYPE query_status AS ENUM ('OPEN', 'IN_PROGRESS', 'PENDING_CLARIFICATION', 'RESOLVED', 'REOPEN', 'CLOSED');
CREATE TYPE invitation_status AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED', 'CANCELLED');
CREATE TYPE schedule_change_trigger AS ENUM ('MANUAL', 'QUERY', 'AUDIT');
CREATE TYPE transaction_type AS ENUM ('INCOME', 'EXPENSE');
CREATE TYPE permission_effect AS ENUM ('ALLOW', 'DENY');
CREATE TYPE subscription_plan AS ENUM ('FREE', 'BASIC', 'PREMIUM', 'ENTERPRISE');
CREATE TYPE parameter_type AS ENUM ('TEXT', 'NUMERIC', 'SINGLE_SELECT', 'MULTI_SELECT', 'DATE', 'BOOLEAN', 'PHOTO');
CREATE TYPE audit_status AS ENUM ('DRAFT', 'IN_PROGRESS', 'SUBMITTED', 'REVIEWED', 'FINALIZED', 'SHARED');
CREATE TYPE measurement_unit_category AS ENUM ('AREA', 'VOLUME', 'WEIGHT', 'LENGTH', 'COUNT');
CREATE TYPE task_category AS ENUM ('FARMING', 'FSP_CONSULTANCY');
CREATE TYPE payment_status AS ENUM ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED');
CREATE TYPE notification_type AS ENUM ('INFO', 'SUCCESS', 'WARNING', 'ALERT', 'REMINDER', 'ERROR');

-- ============================================
-- SYSTEM ADMINISTRATION TABLES
-- ============================================

-- Roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200) NOT NULL,
    scope user_role_scope NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Permissions table
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL UNIQUE,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Role permissions mapping
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    effect permission_effect DEFAULT 'ALLOW',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

-- Subscription plans
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name subscription_plan NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    category organization_type, -- FARMING, FSP, or NULL for universal plans
    resource_limits JSONB, -- {"crops": 50, "users": 10, "queries": 100}
    features JSONB, -- Feature flags
    pricing_details JSONB, -- {"currency": "INR", "billing_cycles": {"monthly": 1000, "quarterly": 2700, "yearly": 10000}}
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN subscription_plans.category IS 'Plan category: FARMING, FSP, or NULL for universal plans';
COMMENT ON COLUMN subscription_plans.resource_limits IS 'JSONB: {"crops": 50, "users": 10, "queries": 100, "audits": 20, "storage_gb": 5}';
COMMENT ON COLUMN subscription_plans.pricing_details IS 'JSONB: {"currency": "INR", "billing_cycles": {"monthly": 1000, "quarterly": 2700, "yearly": 10000}}';

-- AK: Moved subscription_plan_history table after creation of users table due to user_id reference in the table

-- ============================================
-- ORGANIZATION & USER MANAGEMENT
-- ============================================

-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    logo_url TEXT,
    organization_type organization_type NOT NULL,
    status organization_status DEFAULT 'NOT_STARTED',
    registration_number VARCHAR(100),
    address TEXT,
    district VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(20),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    subscription_plan_id UUID REFERENCES subscription_plans(id),
    subscription_start_date DATE,
    subscription_end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

CREATE INDEX idx_organizations_type ON organizations(organization_type);
CREATE INDEX idx_organizations_status ON organizations(status);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    preferred_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);

-- Organization member invitations
CREATE TABLE org_member_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    inviter_id UUID NOT NULL REFERENCES users(id),
    invitee_email VARCHAR(255) NOT NULL,
    invitee_user_id UUID REFERENCES users(id),
    role_id UUID NOT NULL REFERENCES roles(id),
    status invitation_status DEFAULT 'PENDING',
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_org_member_invitations_org ON org_member_invitations(organization_id);
CREATE INDEX idx_org_member_invitations_email ON org_member_invitations(invitee_email);
CREATE INDEX idx_org_member_invitations_status ON org_member_invitations(status);

-- Organization subscription history
CREATE TABLE org_subscription_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    subscription_plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    plan_version INTEGER, -- Links to subscription_plan_history.version
    change_type VARCHAR(50) NOT NULL, -- UPGRADE, DOWNGRADE, RENEWAL, CANCELLATION
    subscription_start_date DATE NOT NULL,
    subscription_end_date DATE,
    billing_cycle VARCHAR(20), -- MONTHLY, QUARTERLY, YEARLY
    amount DECIMAL(10, 2),
    payment_status payment_status DEFAULT 'PENDING',
    payment_date TIMESTAMP WITH TIME ZONE,
    payment_reference VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_org_sub_history_org ON org_subscription_history(organization_id);
CREATE INDEX idx_org_sub_history_plan ON org_subscription_history(subscription_plan_id);
CREATE INDEX idx_org_sub_history_dates ON org_subscription_history(subscription_start_date, subscription_end_date);

-- Organization members
CREATE TABLE org_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    status member_status DEFAULT 'ACTIVE',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP WITH TIME ZONE,
    invited_by UUID REFERENCES users(id),
    invitation_id UUID REFERENCES org_member_invitations(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, organization_id)
);

CREATE INDEX idx_org_members_user ON org_members(user_id);
CREATE INDEX idx_org_members_org ON org_members(organization_id);
CREATE INDEX idx_org_members_status ON org_members(status);

-- Organization member roles
CREATE TABLE org_member_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, organization_id, role_id)
);

CREATE INDEX idx_org_member_roles_user ON org_member_roles(user_id);
CREATE INDEX idx_org_member_roles_org ON org_member_roles(organization_id);

-- Organization role permission overrides
CREATE TABLE org_role_permission_overrides (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    effect permission_effect NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    UNIQUE(organization_id, role_id, permission_id)
);

-- Subscription plan history (tracks changes to plan definitions)
CREATE TABLE subscription_plan_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID NOT NULL REFERENCES subscription_plans(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    category organization_type,
    resource_limits JSONB,
    features JSONB,
    pricing_details JSONB,
    effective_from TIMESTAMP WITH TIME ZONE NOT NULL,
    effective_to TIMESTAMP WITH TIME ZONE,
    changed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plan_id, version)
);

CREATE INDEX idx_plan_history_plan ON subscription_plan_history(plan_id);
CREATE INDEX idx_plan_history_effective ON subscription_plan_history(effective_from, effective_to);

-- ============================================
-- REFERENCE DATA TABLES
-- ============================================

-- Common reference data with translations
CREATE TABLE reference_data_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reference_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_id UUID NOT NULL REFERENCES reference_data_types(id) ON DELETE CASCADE,
    code VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    reference_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(type_id, code)
);

CREATE INDEX idx_ref_data_type ON reference_data(type_id);

COMMENT ON COLUMN reference_data.reference_metadata IS 'JSONB: {"capacity_liters": 50000, "depth_meters": 15, "water_quality": "good", "seasonal_availability": ["summer", "winter"], "maintenance_required": true, "last_cleaned": "2024-01-15", "additional": {...}}';

-- Translations for reference data
CREATE TABLE reference_data_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_data_id UUID NOT NULL REFERENCES reference_data(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(reference_data_id, language_code)
);

CREATE INDEX idx_ref_translations_lang ON reference_data_translations(language_code);

-- Master services list
CREATE TABLE master_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status service_status DEFAULT 'ACTIVE',
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Service translations
CREATE TABLE master_service_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID NOT NULL REFERENCES master_services(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_id, language_code)
);

-- Measurement units with categories
CREATE TABLE measurement_units (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category measurement_unit_category NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    symbol VARCHAR(20),
    is_base_unit BOOLEAN DEFAULT false,
    conversion_factor DECIMAL(20, 10), -- Factor to convert to base unit
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_measurement_units_category ON measurement_units(category);

-- Measurement unit translations
CREATE TABLE measurement_unit_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    measurement_unit_id UUID NOT NULL REFERENCES measurement_units(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(measurement_unit_id, language_code)
);

CREATE INDEX idx_measurement_unit_translations_lang ON measurement_unit_translations(language_code);

-- Crop categories, types, varieties
CREATE TABLE crop_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crop_category_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_category_id UUID NOT NULL REFERENCES crop_categories(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    UNIQUE(crop_category_id, language_code)
);

CREATE TABLE crop_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES crop_categories(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL UNIQUE,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crop_type_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_type_id UUID NOT NULL REFERENCES crop_types(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    UNIQUE(crop_type_id, language_code)
);

CREATE TABLE crop_varieties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_type_id UUID NOT NULL REFERENCES crop_types(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL UNIQUE,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    variety_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN crop_varieties.variety_metadata IS 'JSONB: {"maturity_days": 90, "yield_potential_kg_per_acre": 15000, "plant_spacing_cm": 60, "row_spacing_cm": 90, "water_requirement": "high", "disease_resistance": ["early_blight", "late_blight"], "suitable_seasons": ["kharif", "rabi"], "additional": {...}}';

CREATE TABLE crop_variety_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_variety_id UUID NOT NULL REFERENCES crop_varieties(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    UNIQUE(crop_variety_id, language_code)
);

CREATE TYPE input_item_type AS ENUM ('FERTILIZER', 'PESTICIDE', 'OTHER');

-- Input item categories and items (system and organization-specific)
CREATE TABLE input_item_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL,
    is_system_defined BOOLEAN DEFAULT true,
    owner_org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    CONSTRAINT chk_input_category_ownership CHECK (
        (is_system_defined = true AND owner_org_id IS NULL) OR
        (is_system_defined = false AND owner_org_id IS NOT NULL)
    ),
    UNIQUE(code, is_system_defined, owner_org_id)
);

CREATE INDEX idx_input_item_categories_owner ON input_item_categories(owner_org_id);
CREATE INDEX idx_input_item_categories_system ON input_item_categories(is_system_defined);

COMMENT ON TABLE input_item_categories IS 'Input item categories (system-defined and organization-specific)';
COMMENT ON COLUMN input_item_categories.is_system_defined IS 'true for system-defined categories, false for organization-specific';
COMMENT ON COLUMN input_item_categories.owner_org_id IS 'NULL for system-defined, organization_id for org-specific categories';
COMMENT ON CONSTRAINT chk_input_category_ownership ON input_item_categories IS 'Ensures system categories have no owner, org categories have owner';

CREATE TABLE input_item_category_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES input_item_categories(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, language_code)
);

CREATE INDEX idx_input_item_category_translations_lang ON input_item_category_translations(language_code);

COMMENT ON TABLE input_item_category_translations IS 'Multilingual translations for input item categories (system and org-specific)';

CREATE TABLE input_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES input_item_categories(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,
    is_system_defined BOOLEAN DEFAULT true,
    owner_org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    type input_item_type,
    default_unit_id UUID REFERENCES measurement_units(id),
    item_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    CONSTRAINT chk_input_item_ownership CHECK (
        (is_system_defined = true AND owner_org_id IS NULL) OR
        (is_system_defined = false AND owner_org_id IS NOT NULL)
    ),
    UNIQUE(category_id, code, is_system_defined, owner_org_id)
);

CREATE INDEX idx_input_items_category ON input_items(category_id);
CREATE INDEX idx_input_items_owner ON input_items(owner_org_id);
CREATE INDEX idx_input_items_system ON input_items(is_system_defined);
CREATE UNIQUE INDEX idx_input_items_system_code ON input_items(code, is_system_defined) WHERE is_system_defined = TRUE;

-- Partial unique index for system-defined categories
CREATE UNIQUE INDEX idx_input_item_categories_system_code ON input_item_categories(code, is_system_defined) WHERE is_system_defined = TRUE;

COMMENT ON TABLE input_items IS 'Input items like fertilizers, pesticides (system-defined and organization-specific)';
COMMENT ON COLUMN input_items.is_system_defined IS 'true for system-defined items, false for organization-specific';
COMMENT ON COLUMN input_items.owner_org_id IS 'NULL for system-defined, organization_id for org-specific items';
--AK: Modified the JSONB structure
--COMMENT ON COLUMN input_items.item_metadata IS 'JSONB: {"brand": "Tata", "composition": "Urea 46% N", "npk_ratio": "46-0-0", "form": "granular", "solubility": "high", "manufacturer": "Tata Chemicals", "batch_number": "B12345", "expiry_date": "2025-12-31", "storage_instructions": "Keep in cool dry place", "application_method": ["soil", "fertigation"], "additional": {...}}';
COMMENT ON COLUMN input_items.item_metadata IS 'JSONB: {"nutrients": ["Nitrogen 46%", "Boron 0.1%"], "npk_ratio": "46-0-0", "active_ingredients": ["imidacloprid 35.8% w/w", "another chemical 1% w/v"], "mode_of_action": ["systemic", "contact", "systemic & contact"], "effective_against": ["thrips", "red mites", "leaf miner"], "application_method": ["soil", "fertigation"], "form": "granular", "solubility": "high", "brand": "Tata", "manufacturer": "Tata Chemicals","storage_instructions": "Keep in cool dry place", "additional": {...}}';
COMMENT ON CONSTRAINT chk_input_item_ownership ON input_items IS 'Ensures system items have no owner, org items have owner';

CREATE TABLE input_item_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    input_item_id UUID NOT NULL REFERENCES input_items(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(input_item_id, language_code)
);

CREATE INDEX idx_input_item_translations_lang ON input_item_translations(language_code);

COMMENT ON TABLE input_item_translations IS 'Multilingual translations for input items (system and org-specific)';

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    category task_category NOT NULL,
    requires_input_items BOOLEAN DEFAULT false,
    requires_concentration BOOLEAN DEFAULT false,
    requires_machinery BOOLEAN DEFAULT false,
    requires_labor BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    UNIQUE(task_id, language_code)
);

-- Finance transaction categories (system and organization-specific)
CREATE TABLE finance_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_type transaction_type NOT NULL,
    code VARCHAR(50) NOT NULL,
    is_system_defined BOOLEAN DEFAULT true,
    owner_org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    CONSTRAINT chk_finance_category_ownership CHECK (
        (is_system_defined = true AND owner_org_id IS NULL) OR
        (is_system_defined = false AND owner_org_id IS NOT NULL)
    ),
    UNIQUE(transaction_type, code, is_system_defined, owner_org_id)
);

CREATE INDEX idx_finance_categories_owner ON finance_categories(owner_org_id);
CREATE INDEX idx_finance_categories_system ON finance_categories(is_system_defined);
CREATE INDEX idx_finance_categories_type ON finance_categories(transaction_type);

COMMENT ON TABLE finance_categories IS 'Finance transaction categories (system-defined and organization-specific)';
COMMENT ON COLUMN finance_categories.is_system_defined IS 'true for system-defined categories, false for organization-specific';
COMMENT ON COLUMN finance_categories.owner_org_id IS 'NULL for system-defined, organization_id for org-specific categories';
COMMENT ON CONSTRAINT chk_finance_category_ownership ON finance_categories IS 'Ensures system categories have no owner, org categories have owner';

CREATE TABLE finance_category_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES finance_categories(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, language_code)
);

CREATE INDEX idx_finance_category_translations_lang ON finance_category_translations(language_code);

COMMENT ON TABLE finance_category_translations IS 'Multilingual translations for finance categories (system and org-specific)';

-- ============================================
-- FARMING ORGANIZATION TABLES
-- ============================================

-- Farms
CREATE TABLE farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    address TEXT,
    district VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(20),
    location GEOGRAPHY(POINT, 4326),
    boundary GEOGRAPHY(POLYGON, 4326),
    area DECIMAL(15, 4),
    area_unit_id UUID REFERENCES measurement_units(id),
    farm_attributes JSONB, -- {"soil_ec": 2.5, "soil_ph": 6.8, "water_ec": 1.2, "water_ph": 7.0}
    manager_id UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_farms_org ON farms(organization_id);
CREATE INDEX idx_farms_location ON farms USING GIST(location);
CREATE INDEX idx_farms_boundary ON farms USING GIST(boundary);
CREATE INDEX idx_farms_manager ON farms(manager_id);
CREATE INDEX idx_farms_attributes ON farms USING gin(farm_attributes);

COMMENT ON COLUMN farms.farm_attributes IS 'JSONB: {"soil_ec": 2.5, "soil_ph": 6.8, "water_ec": 1.2, "water_ph": 7.0, "additional": {...}}';

-- Farm supervisors (many-to-many relationship)
CREATE TABLE farm_supervisors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    supervisor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(farm_id, supervisor_id)
);

CREATE INDEX idx_farm_supervisors_farm ON farm_supervisors(farm_id);
CREATE INDEX idx_farm_supervisors_supervisor ON farm_supervisors(supervisor_id);

-- Farm water sources (many-to-many)
CREATE TABLE farm_water_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    water_source_id UUID NOT NULL REFERENCES reference_data(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(farm_id, water_source_id)
);

-- Farm soil types (many-to-many)
CREATE TABLE farm_soil_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    soil_type_id UUID NOT NULL REFERENCES reference_data(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(farm_id, soil_type_id)
);

-- Farm irrigation modes (many-to-many)
CREATE TABLE farm_irrigation_modes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    irrigation_mode_id UUID NOT NULL REFERENCES reference_data(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(farm_id, irrigation_mode_id)
);

-- Plots
CREATE TABLE plots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    boundary GEOGRAPHY(POLYGON, 4326),
    area DECIMAL(15, 4),
    area_unit_id UUID REFERENCES measurement_units(id),
    plot_attributes JSONB, -- {"soil_ec": 2.5, "soil_ph": 6.8, "water_ec": 1.2, "water_ph": 7.0}
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_plots_farm ON plots(farm_id);
CREATE INDEX idx_plots_boundary ON plots USING GIST(boundary);
CREATE INDEX idx_plots_attributes ON plots USING gin(plot_attributes);

COMMENT ON COLUMN plots.plot_attributes IS 'JSONB: {"soil_ec": 2.5, "soil_ph": 6.8, "water_ec": 1.2, "water_ph": 7.0, "additional": {...}}';

-- Plot water sources
CREATE TABLE plot_water_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_id UUID NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
    water_source_id UUID NOT NULL REFERENCES reference_data(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plot_id, water_source_id)
);

-- Plot soil types
CREATE TABLE plot_soil_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_id UUID NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
    soil_type_id UUID NOT NULL REFERENCES reference_data(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plot_id, soil_type_id)
);

-- Plot irrigation modes
CREATE TABLE plot_irrigation_modes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_id UUID NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
    irrigation_mode_id UUID NOT NULL REFERENCES reference_data(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plot_id, irrigation_mode_id)
);

-- Crops
CREATE TABLE crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_id UUID NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    crop_type_id UUID REFERENCES crop_types(id),
    crop_variety_id UUID REFERENCES crop_varieties(id),
    area DECIMAL(15, 4),
    area_unit_id UUID REFERENCES measurement_units(id),
    plant_count INTEGER,
    lifecycle crop_lifecycle DEFAULT 'PLANNED',
    planned_date DATE,
    planted_date DATE,
    transplanted_date DATE,
    production_start_date DATE,
    completed_date DATE,
    terminated_date DATE,
    closed_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_crops_plot ON crops(plot_id);
CREATE INDEX idx_crops_lifecycle ON crops(lifecycle);
CREATE INDEX idx_crops_type ON crops(crop_type_id);

-- Crop lifecycle photos (for yields and general crop documentation)
CREATE TABLE crop_lifecycle_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_id UUID NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    file_url VARCHAR(500) NOT NULL,
    file_key VARCHAR(500),
    caption TEXT,
    photo_date DATE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id)
);

CREATE INDEX idx_crop_lifecycle_photos_crop ON crop_lifecycle_photos(crop_id);
CREATE INDEX idx_crop_lifecycle_photos_date ON crop_lifecycle_photos(photo_date);

-- Crop yields
CREATE TABLE crop_yields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_id UUID NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    yield_type VARCHAR(20) NOT NULL, -- PLANNED, ACTUAL
    harvest_date DATE,
    quantity DECIMAL(15, 4) NOT NULL,
    quantity_unit_id UUID REFERENCES measurement_units(id),
    harvest_area DECIMAL(15, 4), -- Actual harvested area (optional, for area-based yields)
    harvest_area_unit_id UUID REFERENCES measurement_units(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    CONSTRAINT chk_harvest_area_unit CHECK (
        (harvest_area IS NULL AND harvest_area_unit_id IS NULL) OR
        (harvest_area IS NOT NULL AND harvest_area_unit_id IS NOT NULL)
    )
);

CREATE INDEX idx_crop_yields_crop ON crop_yields(crop_id);

COMMENT ON COLUMN crop_yields.harvest_area IS 'Actual harvested area (optional). Some harvests are area-based (e.g., vegetables), others are count-based (e.g., coconuts).';

-- Crop yield photos (many-to-many relationship)
CREATE TABLE crop_yield_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_yield_id UUID NOT NULL REFERENCES crop_yields(id) ON DELETE CASCADE,
    photo_id UUID NOT NULL REFERENCES crop_lifecycle_photos(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(crop_yield_id, photo_id)
);

CREATE INDEX idx_crop_yield_photos_yield ON crop_yield_photos(crop_yield_id);
CREATE INDEX idx_crop_yield_photos_photo ON crop_yield_photos(photo_id);

-- ============================================
-- SCHEDULE & TASK MANAGEMENT
-- ============================================

-- Schedule Templates
CREATE TABLE schedule_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL,
    crop_type_id UUID REFERENCES crop_types(id),
    crop_variety_id UUID REFERENCES crop_varieties(id),
    is_system_defined BOOLEAN DEFAULT true,
    owner_org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    CONSTRAINT chk_schedule_template_ownership CHECK (
        (is_system_defined = true AND owner_org_id IS NULL) OR
        (is_system_defined = false AND owner_org_id IS NOT NULL)
    ),
    UNIQUE(code, is_system_defined, owner_org_id)
);

CREATE INDEX idx_schedule_templates_crop_type ON schedule_templates(crop_type_id);
CREATE INDEX idx_schedule_templates_crop_variety ON schedule_templates(crop_variety_id);
CREATE INDEX idx_schedule_templates_owner ON schedule_templates(owner_org_id);
CREATE INDEX idx_schedule_templates_system ON schedule_templates(is_system_defined);

COMMENT ON TABLE schedule_templates IS 'Reusable schedule templates for crops (system-defined and organization-specific)';
COMMENT ON COLUMN schedule_templates.notes IS 'Internal notes for administrators (not translated)';

-- Schedule Template Translations
CREATE TABLE schedule_template_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_template_id UUID NOT NULL REFERENCES schedule_templates(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(schedule_template_id, language_code)
);

CREATE INDEX idx_schedule_template_translations_lang ON schedule_template_translations(language_code);

COMMENT ON TABLE schedule_template_translations IS 'Multilingual translations for schedule templates';
COMMENT ON COLUMN schedule_template_translations.description IS 'User-facing description (translated)';

-- Schedule Template Tasks
CREATE TABLE schedule_template_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_template_id UUID NOT NULL REFERENCES schedule_templates(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id),
    day_offset INTEGER NOT NULL,
    task_details_template JSONB NOT NULL,
    sort_order INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_schedule_template_tasks_template ON schedule_template_tasks(schedule_template_id);
CREATE INDEX idx_schedule_template_tasks_task ON schedule_template_tasks(task_id);
CREATE INDEX idx_schedule_template_tasks_offset ON schedule_template_tasks(day_offset);
CREATE INDEX idx_schedule_template_tasks_details ON schedule_template_tasks USING gin(task_details_template);

COMMENT ON TABLE schedule_template_tasks IS 'Tasks within schedule templates with calculation metadata';
COMMENT ON COLUMN schedule_template_tasks.day_offset IS 'Days offset from schedule start date (0 = start date)';
COMMENT ON COLUMN schedule_template_tasks.task_details_template IS 'JSONB with quantities and calculation_basis (per_acre, per_plant, fixed). Structure: {"input_items": [{"input_item_id": "uuid", "quantity": 100, "quantity_unit_id": "uuid", "calculation_basis": "per_acre"}], "labor": {"estimated_hours": 8, "calculation_basis": "per_acre"}, "machinery": {"equipment_type": "tractor", "estimated_hours": 3.5, "calculation_basis": "per_acre"}, "concentration": {"solution_volume": 80, "solution_volume_unit_id": "uuid", "calculation_basis": "per_plant", "ingredients": [{"input_item_id": "uuid", "concentration_per_liter": 3, "concentration_unit_id": "uuid"}]}}';

-- Schedules
CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_id UUID NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    template_id UUID REFERENCES schedule_templates(id),
    template_parameters JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_schedules_crop ON schedules(crop_id);
CREATE INDEX idx_schedules_template ON schedules(template_id);

COMMENT ON COLUMN schedules.template_id IS 'Reference to template if schedule was created from template';
COMMENT ON COLUMN schedules.template_parameters IS 'JSONB: {"area": 2.5, "area_unit_id": "uuid", "plant_count": 800, "start_date": "2024-09-25", "created_from_template_version": 1}';

-- Schedule tasks
CREATE TABLE schedule_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id UUID NOT NULL REFERENCES schedules(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id),
    due_date DATE NOT NULL,
    status task_status DEFAULT 'NOT_STARTED',
    completed_date DATE,
    task_details JSONB, -- Flexible storage for all task types (input items, labor, machinery, etc.)
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_schedule_tasks_schedule ON schedule_tasks(schedule_id);
CREATE INDEX idx_schedule_tasks_task ON schedule_tasks(task_id);
CREATE INDEX idx_schedule_tasks_status ON schedule_tasks(status);
CREATE INDEX idx_schedule_tasks_due_date ON schedule_tasks(due_date);
CREATE INDEX idx_schedule_tasks_details ON schedule_tasks USING gin(task_details);

COMMENT ON COLUMN schedule_tasks.task_details IS 'JSONB structure: {"input_items": [{"input_item_id": "uuid", "quantity": 10.5, "quantity_unit_id": "uuid"}], "labor": {"estimated_hours": 8, "worker_count": 3}, "machinery": {"equipment_type": "text", "estimated_hours": 2}, "concentration": {"total_solution_volume": 80000, "total_solution_volume_unit_id": "uuid", "ingredients": [{"input_item_id": "uuid", "total_quantity": 240, "quantity_unit_id": "uuid", "concentration_per_liter": 3}]}}';

-- Task actuals (consolidated table for both planned and adhoc tasks)
CREATE TABLE task_actuals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id UUID REFERENCES schedules(id), -- NULL for adhoc tasks
    schedule_task_id UUID REFERENCES schedule_tasks(id) ON DELETE CASCADE, -- NULL for adhoc tasks
    task_id UUID NOT NULL REFERENCES tasks(id),
    is_planned BOOLEAN NOT NULL, -- true = planned task, false = adhoc task
    crop_id UUID REFERENCES crops(id) ON DELETE CASCADE, -- Nullable to support plot-level tasks
    plot_id UUID REFERENCES plots(id), -- Optional plot-level task
    actual_date DATE NOT NULL,
    task_details JSONB, -- Same structure as schedule_tasks.task_details
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    CONSTRAINT chk_task_actuals_planned CHECK (
        (is_planned = true AND schedule_task_id IS NOT NULL) OR
        (is_planned = false AND schedule_task_id IS NULL)
    )
);

CREATE INDEX idx_task_actuals_schedule ON task_actuals(schedule_id);
CREATE INDEX idx_task_actuals_schedule_task ON task_actuals(schedule_task_id);
CREATE INDEX idx_task_actuals_task ON task_actuals(task_id);
CREATE INDEX idx_task_actuals_crop ON task_actuals(crop_id);
CREATE INDEX idx_task_actuals_plot ON task_actuals(plot_id);
CREATE INDEX idx_task_actuals_date ON task_actuals(actual_date);
CREATE INDEX idx_task_actuals_is_planned ON task_actuals(is_planned);
CREATE INDEX idx_task_actuals_details ON task_actuals USING gin(task_details);

COMMENT ON TABLE task_actuals IS 'Consolidated table for both planned and adhoc task actuals';
COMMENT ON COLUMN task_actuals.is_planned IS 'true = planned task from schedule, false = adhoc unplanned task';
COMMENT ON COLUMN task_actuals.crop_id IS 'Nullable to support plot-level tasks without specific crop';
COMMENT ON COLUMN task_actuals.task_details IS 'JSONB structure: Same as schedule_tasks.task_details - stores actual values for input items, labor, machinery, concentration used';

-- Task photos
CREATE TABLE task_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_actual_id UUID NOT NULL REFERENCES task_actuals(id) ON DELETE CASCADE,
    file_url VARCHAR(500) NOT NULL,
    file_key VARCHAR(500),
    caption TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id)
);

CREATE INDEX idx_task_photos_actual ON task_photos(task_actual_id);

COMMENT ON TABLE task_photos IS 'Photos for task actuals (both planned and adhoc)';

-- Schedule change log (for recommendations and manual changes)
CREATE TABLE schedule_change_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id UUID NOT NULL REFERENCES schedules(id) ON DELETE CASCADE,
    trigger_type schedule_change_trigger NOT NULL,
    trigger_reference_id UUID, -- Query ID or Audit ID or NULL for manual
    change_type VARCHAR(20) NOT NULL, -- ADD, MODIFY, DELETE
    task_id UUID REFERENCES schedule_tasks(id),
    task_details_before JSONB, -- Full task details before change (NULL for ADD)
    task_details_after JSONB, -- Full task details after change (NULL for DELETE)
    change_description TEXT,
    is_applied BOOLEAN DEFAULT false,
    applied_at TIMESTAMP WITH TIME ZONE,
    applied_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_schedule_change_log_schedule ON schedule_change_log(schedule_id);
CREATE INDEX idx_schedule_change_log_trigger ON schedule_change_log(trigger_type, trigger_reference_id);
CREATE INDEX idx_schedule_change_log_details_before ON schedule_change_log USING gin(task_details_before);
CREATE INDEX idx_schedule_change_log_details_after ON schedule_change_log USING gin(task_details_after);

COMMENT ON COLUMN schedule_change_log.task_details_before IS 'JSONB: Same structure as schedule_tasks.task_details. NULL for ADD operations';
COMMENT ON COLUMN schedule_change_log.task_details_after IS 'JSONB: Same structure as schedule_tasks.task_details. NULL for DELETE operations';

-- ============================================
-- FINANCE MANAGEMENT
-- ============================================

-- Finance transactions
CREATE TABLE finance_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    transaction_type transaction_type NOT NULL,
    category_id UUID NOT NULL REFERENCES finance_categories(id),
    transaction_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    description TEXT,
    reference_number VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_finance_trans_org ON finance_transactions(organization_id);
CREATE INDEX idx_finance_trans_category ON finance_transactions(category_id);
CREATE INDEX idx_finance_trans_date ON finance_transactions(transaction_date);
CREATE INDEX idx_finance_trans_type ON finance_transactions(transaction_type);

COMMENT ON TABLE finance_transactions IS 'Income and expense transactions with unified category reference';

-- Finance transaction attachments
CREATE TABLE finance_transaction_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES finance_transactions(id) ON DELETE CASCADE,
    file_url VARCHAR(500) NOT NULL,
    file_key VARCHAR(500),
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id)
);

CREATE INDEX idx_finance_attachments_trans ON finance_transaction_attachments(transaction_id);

-- Finance transaction splits (mapping to farm/plot/crop)
CREATE TABLE finance_transaction_splits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES finance_transactions(id) ON DELETE CASCADE,
    farm_id UUID REFERENCES farms(id),
    plot_id UUID REFERENCES plots(id),
    crop_id UUID REFERENCES crops(id),
    split_amount DECIMAL(15, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    CONSTRAINT chk_split_reference CHECK (
        (farm_id IS NOT NULL AND plot_id IS NULL AND crop_id IS NULL) OR
        (farm_id IS NULL AND plot_id IS NOT NULL AND crop_id IS NULL) OR
        (farm_id IS NULL AND plot_id IS NULL AND crop_id IS NOT NULL)
    )
);

CREATE INDEX idx_finance_splits_trans ON finance_transaction_splits(transaction_id);
CREATE INDEX idx_finance_splits_farm ON finance_transaction_splits(farm_id);
CREATE INDEX idx_finance_splits_plot ON finance_transaction_splits(plot_id);
CREATE INDEX idx_finance_splits_crop ON finance_transaction_splits(crop_id);

-- ============================================
-- FSP MARKETPLACE & WORK ORDERS
-- ============================================

-- FSP service listings
CREATE TABLE fsp_service_listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fsp_organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES master_services(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    service_area_districts TEXT[], -- Array of districts
    pricing_model VARCHAR(50), -- PER_HOUR, PER_DAY, PER_ACRE, FIXED, CUSTOM
    base_price DECIMAL(15, 2),
    currency VARCHAR(10) DEFAULT 'INR',
    status service_status DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_fsp_listings_org ON fsp_service_listings(fsp_organization_id);
CREATE INDEX idx_fsp_listings_service ON fsp_service_listings(service_id);
CREATE INDEX idx_fsp_listings_status ON fsp_service_listings(status);

-- FSP approval documents
CREATE TABLE fsp_approval_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fsp_organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_key VARCHAR(500),
    file_name VARCHAR(255),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id)
);

CREATE INDEX idx_fsp_docs_org ON fsp_approval_documents(fsp_organization_id);

-- Work orders
CREATE TABLE work_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farming_organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    fsp_organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    service_listing_id UUID REFERENCES fsp_service_listings(id),
    work_order_number VARCHAR(50) UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status work_order_status DEFAULT 'PENDING',
    terms_and_conditions TEXT,
    scope_metadata JSONB, -- Summary of scope items, e.g., {"farms": 2, "plots": 3, "crops": 1, "total_items": 6}
    start_date DATE,
    end_date DATE,
    total_amount DECIMAL(15, 2),
    currency VARCHAR(10) DEFAULT 'INR',
    service_snapshot JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    accepted_at TIMESTAMP WITH TIME ZONE,
    accepted_by UUID REFERENCES users(id),
    completed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_work_order_scope_metadata CHECK (
        scope_metadata IS NULL OR (
            jsonb_typeof(scope_metadata) = 'object' AND
            (scope_metadata ? 'total_items' OR scope_metadata ? 'farms' OR scope_metadata ? 'plots' OR scope_metadata ? 'crops' OR scope_metadata ? 'organizations')
        )
    )
);

COMMENT ON COLUMN work_orders.service_snapshot IS 'JSONB snapshot of service details at the time of creation: {"name": "...", "description": "..."}';

CREATE INDEX idx_work_orders_farming_org ON work_orders(farming_organization_id);
CREATE INDEX idx_work_orders_fsp_org ON work_orders(fsp_organization_id);
CREATE INDEX idx_work_orders_status ON work_orders(status);
CREATE INDEX idx_work_orders_scope_metadata ON work_orders USING gin(scope_metadata);

COMMENT ON COLUMN work_orders.scope_metadata IS 'JSONB summary of scope items: {"farms": 2, "plots": 3, "crops": 1, "total_items": 6}';

-- Work order scope (defines what resources are covered by the work order)
CREATE TABLE work_order_scope (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    scope work_order_scope_type NOT NULL,
    scope_id UUID NOT NULL, -- ID of organization, farm, plot, or crop
    access_permissions JSONB DEFAULT '{"read": true, "write": false, "track": false}'::jsonb,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    UNIQUE(work_order_id, scope, scope_id)
);

CREATE INDEX idx_work_order_scope_work_order ON work_order_scope(work_order_id);
CREATE INDEX idx_work_order_scope_scope_id ON work_order_scope(scope, scope_id);
CREATE INDEX idx_work_order_scope_permissions ON work_order_scope USING gin(access_permissions);

COMMENT ON TABLE work_order_scope IS 'Defines the scope of resources covered by a work order (can include multiple farms, plots, crops)';
COMMENT ON COLUMN work_order_scope.access_permissions IS 'JSONB permissions per scope item: {"read": true, "write": false, "track": false}. Default is read-only.';

-- ============================================
-- QUERY MANAGEMENT (CONSULTANCY)
-- ============================================

-- Queries
CREATE TABLE queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farming_organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    fsp_organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    query_number VARCHAR(50) UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    farm_id UUID REFERENCES farms(id),
    plot_id UUID REFERENCES plots(id),
    crop_id UUID REFERENCES crops(id),
    status query_status DEFAULT 'OPEN',
    priority VARCHAR(20) DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, URGENT
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    closed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_queries_farming_org ON queries(farming_organization_id);
CREATE INDEX idx_queries_fsp_org ON queries(fsp_organization_id);
CREATE INDEX idx_queries_work_order ON queries(work_order_id);
CREATE INDEX idx_queries_status ON queries(status);
CREATE INDEX idx_queries_crop ON queries(crop_id);

-- Query responses
CREATE TABLE query_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    response_text TEXT NOT NULL,
    has_recommendation BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_query_responses_query ON query_responses(query_id);

-- Query photos (can be attached to query or query response)
CREATE TABLE query_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID REFERENCES queries(id) ON DELETE CASCADE,
    query_response_id UUID REFERENCES query_responses(id) ON DELETE CASCADE,
    file_url VARCHAR(500) NOT NULL,
    file_key VARCHAR(500),
    caption TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id),
    CONSTRAINT chk_query_photos_reference CHECK (
        (query_id IS NOT NULL AND query_response_id IS NULL) OR
        (query_id IS NULL AND query_response_id IS NOT NULL)
    )
);

CREATE INDEX idx_query_photos_query ON query_photos(query_id);
CREATE INDEX idx_query_photos_response ON query_photos(query_response_id);

COMMENT ON TABLE query_photos IS 'Photos attached to queries (when submitted) or query responses (when FSP responds)';
COMMENT ON CONSTRAINT chk_query_photos_reference ON query_photos IS 'Photo must be linked to either query OR query_response, not both';

-- ============================================
-- AUDIT MANAGEMENT (CONSULTANCY)
-- ============================================

-- Option sets (reusable option lists for parameters)
CREATE TABLE option_sets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    is_system_defined BOOLEAN DEFAULT true,
    owner_org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_option_sets_owner ON option_sets(owner_org_id);
CREATE INDEX idx_option_sets_system ON option_sets(is_system_defined);

-- Options within option sets
CREATE TABLE options (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    option_set_id UUID NOT NULL REFERENCES option_sets(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(option_set_id, code)
);

CREATE INDEX idx_options_set ON options(option_set_id);

-- Option translations
CREATE TABLE option_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    option_id UUID NOT NULL REFERENCES options(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    display_text VARCHAR(200) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(option_id, language_code)
);

CREATE INDEX idx_option_translations_lang ON option_translations(language_code);

-- Parameters library (renamed from audit_parameters)
CREATE TABLE parameters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    parameter_type parameter_type NOT NULL,
    is_system_defined BOOLEAN DEFAULT true,
    owner_org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    parameter_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_parameters_type ON parameters(parameter_type);
CREATE INDEX idx_parameters_owner ON parameters(owner_org_id);
CREATE INDEX idx_parameters_system ON parameters(is_system_defined);

COMMENT ON COLUMN parameters.parameter_metadata IS 'JSONB: {"min_value": 0, "max_value": 100, "unit": "cm", "decimal_places": 2, "validation_rules": {"required": true, "range": [0, 100]}, "display_format": "0.00", "help_text": "Measure from soil level", "additional": {...}}';

-- Parameter translations (renamed from audit_parameter_translations)
CREATE TABLE parameter_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parameter_id UUID NOT NULL REFERENCES parameters(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    help_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parameter_id, language_code)
);

CREATE INDEX idx_parameter_translations_lang ON parameter_translations(language_code);

-- Parameter to option set mapping
CREATE TABLE parameter_option_set_map (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parameter_id UUID NOT NULL REFERENCES parameters(id) ON DELETE CASCADE,
    option_set_id UUID NOT NULL REFERENCES option_sets(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parameter_id, option_set_id)
);

CREATE INDEX idx_param_option_map_param ON parameter_option_set_map(parameter_id);
CREATE INDEX idx_param_option_map_optset ON parameter_option_set_map(option_set_id);

-- Sections library (renamed from audit_sections)
CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    is_system_defined BOOLEAN DEFAULT true,
    owner_org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_sections_owner ON sections(owner_org_id);
CREATE INDEX idx_sections_system ON sections(is_system_defined);

-- Section translations (renamed from audit_section_translations)
CREATE TABLE section_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id UUID NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(section_id, language_code)
);

CREATE INDEX idx_section_translations_lang ON section_translations(language_code);

-- Templates library (renamed from audit_templates)
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    is_system_defined BOOLEAN DEFAULT true,
    owner_org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    crop_type_id UUID REFERENCES crop_types(id),
    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_templates_owner ON templates(owner_org_id);
CREATE INDEX idx_templates_crop_type ON templates(crop_type_id);
CREATE INDEX idx_templates_system ON templates(is_system_defined);

-- Template translations
CREATE TABLE template_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(template_id, language_code)
);

CREATE INDEX idx_template_translations_lang ON template_translations(language_code);

-- Template sections (renamed from audit_template_sections)
CREATE TABLE template_sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    section_id UUID NOT NULL REFERENCES sections(id),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_template_sections_template ON template_sections(template_id);
CREATE INDEX idx_template_sections_section ON template_sections(section_id);

-- Template parameters (renamed from audit_template_parameters)
CREATE TABLE template_parameters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_section_id UUID NOT NULL REFERENCES template_sections(id) ON DELETE CASCADE,
    parameter_id UUID NOT NULL REFERENCES parameters(id),
    is_required BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    parameter_snapshot JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_template_params_section ON template_parameters(template_section_id);
CREATE INDEX idx_template_params_parameter ON template_parameters(parameter_id);

COMMENT ON COLUMN template_parameters.parameter_snapshot IS 'JSONB: {"parameter_id": "uuid", "code": "PLANT_HEIGHT", "parameter_type": "NUMERIC", "parameter_metadata": {"min_value": 0, "max_value": 500, "unit": "cm"}, "option_set_id": "uuid", "options": [{"option_id": "uuid", "code": "GREEN", "display_text": "Green"}], "translations": {"en": {"name": "Plant Height", "help_text": "Measure from soil"}}, "additional": {...}}';

-- Audits (instances of templates)
CREATE TABLE audits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fsp_organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    farming_organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    work_order_id UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
    crop_id UUID NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES templates(id),
    audit_number VARCHAR(50) UNIQUE,
    name VARCHAR(200) NOT NULL,
    status audit_status DEFAULT 'DRAFT',
    template_snapshot JSONB,
    audit_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    finalized_at TIMESTAMP WITH TIME ZONE,
    finalized_by UUID REFERENCES users(id),
    shared_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_audits_fsp_org ON audits(fsp_organization_id);
CREATE INDEX idx_audits_farming_org ON audits(farming_organization_id);
CREATE INDEX idx_audits_work_order ON audits(work_order_id);
CREATE INDEX idx_audits_crop ON audits(crop_id);
CREATE INDEX idx_audits_status ON audits(status);
CREATE INDEX idx_audits_template ON audits(template_id);

COMMENT ON COLUMN audits.template_snapshot IS 'JSONB: {"template_id": "uuid", "code": "TOMATO_AUDIT_V1", "version": 1, "sections": [{"section_id": "uuid", "code": "PLANT_HEALTH", "name": "Plant Health", "parameters": [{"parameter_id": "uuid", "code": "PLANT_HEIGHT", "parameter_type": "NUMERIC", "is_required": true, "parameter_snapshot": {...}}]}], "additional": {...}}';

-- Audit parameter instances (snapshot of parameters for each audit)
CREATE TABLE audit_parameter_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID NOT NULL REFERENCES audits(id) ON DELETE CASCADE,
    template_section_id UUID NOT NULL REFERENCES template_sections(id),
    parameter_id UUID NOT NULL REFERENCES parameters(id),
    sort_order INTEGER DEFAULT 0,
    is_required BOOLEAN DEFAULT false,
    parameter_snapshot JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_param_instances_audit ON audit_parameter_instances(audit_id);
CREATE INDEX idx_audit_param_instances_param ON audit_parameter_instances(parameter_id);
CREATE INDEX idx_audit_param_instances_section ON audit_parameter_instances(template_section_id);

COMMENT ON TABLE audit_parameter_instances IS 'Audit-specific parameter instances with full configuration snapshot';
COMMENT ON COLUMN audit_parameter_instances.parameter_snapshot IS 'JSONB: {"parameter_id": "uuid", "code": "PLANT_HEIGHT", "parameter_type": "NUMERIC", "parameter_metadata": {"min_value": 0, "max_value": 500, "unit": "cm"}, "option_set_id": "uuid", "options": [{"option_id": "uuid", "code": "GREEN", "display_text": "Green"}], "translations": {"en": {"name": "Plant Height", "help_text": "Measure from soil"}}, "additional": {...}}';

-- Audit responses (auditor responses)
CREATE TABLE audit_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID NOT NULL REFERENCES audits(id) ON DELETE CASCADE,
    audit_parameter_instance_id UUID NOT NULL REFERENCES audit_parameter_instances(id) ON DELETE CASCADE,
    response_text TEXT,
    response_numeric DECIMAL(15, 4),
    response_date DATE,
    response_options UUID[], -- Array of option IDs for single/multi select
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_audit_responses_audit ON audit_responses(audit_id);
CREATE INDEX idx_audit_responses_param_instance ON audit_responses(audit_parameter_instance_id);

COMMENT ON TABLE audit_responses IS 'Auditor responses to audit parameters';

-- Audit response photos
CREATE TABLE audit_response_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_response_id UUID NOT NULL REFERENCES audit_responses(id) ON DELETE CASCADE,
    file_url VARCHAR(500) NOT NULL,
    file_key VARCHAR(500),
    caption TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id)
);

CREATE INDEX idx_audit_response_photos_response ON audit_response_photos(audit_response_id);

COMMENT ON TABLE audit_response_photos IS 'Photos attached by auditor to audit responses';

-- Audit reviews (reviewer responses)
CREATE TABLE audit_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_response_id UUID NOT NULL REFERENCES audit_responses(id) ON DELETE CASCADE,
    response_text TEXT,
    response_numeric DECIMAL(15, 4),
    response_date DATE,
    response_option_ids UUID[], -- Array of option IDs chosen by reviewer
    is_flagged_for_report BOOLEAN DEFAULT false,
    reviewed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_by UUID REFERENCES users(id),
    UNIQUE(audit_response_id)
);

CREATE INDEX idx_audit_reviews_response ON audit_reviews(audit_response_id);
CREATE INDEX idx_audit_reviews_reviewer ON audit_reviews(reviewed_by);

COMMENT ON TABLE audit_reviews IS 'Reviewer responses that override or supplement auditor responses (one review per audit response)';
COMMENT ON COLUMN audit_reviews.response_option_ids IS 'Array of option IDs chosen by reviewer';

-- Audit review photos (reviewer photo annotations)
CREATE TABLE audit_review_photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_response_photo_id UUID NOT NULL REFERENCES audit_response_photos(id) ON DELETE CASCADE,
    is_flagged_for_report BOOLEAN DEFAULT false,
    caption TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_by UUID REFERENCES users(id)
);

CREATE INDEX idx_audit_review_photos_photo ON audit_review_photos(audit_response_photo_id);
CREATE INDEX idx_audit_review_photos_reviewer ON audit_review_photos(reviewed_by);

COMMENT ON TABLE audit_review_photos IS 'Reviewer annotations on auditor photos (marking for report, adding comments)';

-- Audit issues (identified during audit)
CREATE TABLE audit_issues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID NOT NULL REFERENCES audits(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity VARCHAR(20), -- LOW, MEDIUM, HIGH, CRITICAL
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_audit_issues_audit ON audit_issues(audit_id);

-- ============================================
-- NOTIFICATION SYSTEM
-- ============================================

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    notification_type notification_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    reference_type VARCHAR(50), -- QUERY, WORK_ORDER, AUDIT, TASK, INVITATION, etc.
    reference_id UUID,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,
    is_push_sent BOOLEAN DEFAULT false,
    push_sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_org ON notifications(organization_id);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at);

COMMENT ON COLUMN notifications.notification_type IS 'Notification category: INFO (general), SUCCESS (positive), WARNING (caution), ALERT (important), REMINDER (time-based), ERROR (failure)';
COMMENT ON COLUMN notifications.reference_type IS 'Entity type: QUERY, WORK_ORDER, AUDIT, TASK, INVITATION, MEMBER, PAYMENT, SUBSCRIPTION, etc.';

-- Push notification tokens
CREATE TABLE push_notification_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_token VARCHAR(500) NOT NULL,
    device_type VARCHAR(20), -- IOS, ANDROID
    device_id VARCHAR(200),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, device_token)
);

CREATE INDEX idx_push_tokens_user ON push_notification_tokens(user_id);

-- ============================================
-- AUDIT & TRACKING
-- ============================================

-- Audit log for tracking all changes
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_record ON audit_log(record_id);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Full-text search indexes
CREATE INDEX idx_farms_name_trgm ON farms USING gin(name gin_trgm_ops);
CREATE INDEX idx_plots_name_trgm ON plots USING gin(name gin_trgm_ops);
CREATE INDEX idx_crops_name_trgm ON crops USING gin(name gin_trgm_ops);
CREATE INDEX idx_queries_title_trgm ON queries USING gin(title gin_trgm_ops);

-- Composite indexes for common queries
CREATE INDEX idx_org_member_roles_composite ON org_member_roles(user_id, organization_id, role_id);
CREATE INDEX idx_schedule_tasks_composite ON schedule_tasks(schedule_id, status, due_date);
CREATE INDEX idx_work_orders_composite ON work_orders(farming_organization_id, fsp_organization_id, status);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_farms_updated_at BEFORE UPDATE ON farms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plots_updated_at BEFORE UPDATE ON plots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crops_updated_at BEFORE UPDATE ON crops
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_schedules_updated_at BEFORE UPDATE ON schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_schedule_tasks_updated_at BEFORE UPDATE ON schedule_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_input_item_categories_updated_at BEFORE UPDATE ON input_item_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_input_items_updated_at BEFORE UPDATE ON input_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_finance_categories_updated_at BEFORE UPDATE ON finance_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_finance_transactions_updated_at BEFORE UPDATE ON finance_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_orders_updated_at BEFORE UPDATE ON work_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_queries_updated_at BEFORE UPDATE ON queries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audits_updated_at BEFORE UPDATE ON audits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_option_sets_updated_at BEFORE UPDATE ON option_sets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parameters_updated_at BEFORE UPDATE ON parameters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sections_updated_at BEFORE UPDATE ON sections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audit_param_instances_updated_at BEFORE UPDATE ON audit_parameter_instances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audit_responses_updated_at BEFORE UPDATE ON audit_responses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_schedule_templates_updated_at BEFORE UPDATE ON schedule_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_schedule_template_tasks_updated_at BEFORE UPDATE ON schedule_template_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (RLS) SETUP
-- ============================================

-- Enable RLS on multi-tenant tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE farms ENABLE ROW LEVEL SECURITY;
ALTER TABLE plots ENABLE ROW LEVEL SECURITY;
ALTER TABLE crops ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedule_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE audits ENABLE ROW LEVEL SECURITY;

-- Comments for documentation
COMMENT ON TABLE organizations IS 'Stores farming and FSP organizations';
COMMENT ON TABLE users IS 'Application users with authentication details';
COMMENT ON TABLE org_members IS 'Organization membership with status tracking';
COMMENT ON TABLE org_member_roles IS 'User roles within organizations (supports multiple roles)';
COMMENT ON TABLE org_member_invitations IS 'Invitation workflow for adding members to organizations';
COMMENT ON TABLE farms IS 'Farms owned by farming organizations with GIS data';
COMMENT ON TABLE plots IS 'Subdivisions of farms with GIS boundaries';
COMMENT ON TABLE crops IS 'Crops grown in plots with lifecycle tracking';
COMMENT ON TABLE schedule_templates IS 'Reusable schedule templates for crops (system-defined and organization-specific)';
COMMENT ON TABLE schedule_template_translations IS 'Multilingual translations for schedule templates';
COMMENT ON TABLE schedule_template_tasks IS 'Tasks within schedule templates with calculation metadata';
COMMENT ON TABLE schedules IS 'Operation schedules for crops (can be created from templates)';
COMMENT ON TABLE schedule_tasks IS 'Individual tasks within schedules with flexible JSONB task_details';
COMMENT ON TABLE task_actuals IS 'Consolidated table for both planned and adhoc task actuals';
COMMENT ON TABLE task_photos IS 'Photos for task actuals (both planned and adhoc)';
COMMENT ON TABLE schedule_change_log IS 'Tracks all schedule changes from manual edits, queries, and audits with before/after task details';
COMMENT ON TABLE work_orders IS 'Contracts between farming orgs and FSPs';
COMMENT ON TABLE queries IS 'Consultation queries from farming orgs to FSPs';
COMMENT ON TABLE audits IS 'Crop audits conducted by FSPs';
COMMENT ON TABLE option_sets IS 'Reusable option lists for parameters (system or organization-specific)';
COMMENT ON TABLE options IS 'Individual options within option sets';
COMMENT ON TABLE parameters IS 'Parameter library for audits (system or organization-specific)';
COMMENT ON TABLE sections IS 'Section library for organizing audit parameters (system or organization-specific)';
COMMENT ON TABLE templates IS 'Template library for audit structures (system or organization-specific)';
COMMENT ON TABLE audit_parameter_instances IS 'Audit-specific parameter instances with configuration snapshots';
COMMENT ON TABLE audit_reviews IS 'Reviewer responses that override or supplement auditor responses';
COMMENT ON TABLE audit_review_photos IS 'Reviewer annotations on auditor photos';
