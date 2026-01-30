-- Uzhathunai Database Initial Data (DML)
-- Version: 2.0
-- Description: Reference data and initial system configuration

-- ============================================
-- SUBSCRIPTION PLANS
-- ============================================

INSERT INTO subscription_plans (name, display_name, description, category, resource_limits, features, pricing_details, sort_order, is_active) VALUES
('FREE', 'Free Plan', 'Basic features for small farmers', 'FARMING', '{"crops": 10, "users": 2, "queries": 5}', '{"marketplace": false, "advanced_analytics": false, "api_access": false}', '{"currency": "INR", "billing_cycles": {"monthly": 0, "quarterly": 0, "yearly": 0}}', 1, true),
('BASIC', 'Basic Plan', 'Essential features for growing farms', 'FARMING', '{"crops": 50, "users": 5, "queries": 50}', '{"marketplace": true, "advanced_analytics": false, "api_access": false}', '{"currency": "INR", "billing_cycles": {"monthly": 499, "quarterly": 1397, "yearly": 4990}}', 2, true),
('PREMIUM', 'Premium Plan', 'Advanced features for professional farms', 'FARMING', '{"crops": 200, "users": 20, "queries": 200}', '{"marketplace": true, "advanced_analytics": true, "api_access": false}', '{"currency": "INR", "billing_cycles": {"monthly": 1999, "quarterly": 5597, "yearly": 19990}}', 3, true),
('ENTERPRISE', 'Enterprise Plan', 'Full features for large organizations', NULL, '{"crops": null, "users": null, "queries": null}', '{"marketplace": true, "advanced_analytics": true, "api_access": true, "custom_integrations": true}', '{"currency": "INR", "billing_cycles": {"monthly": null, "quarterly": null, "yearly": null}, "custom_pricing": true}', 4, true);

-- ============================================
-- ROLES
-- ============================================

-- System roles
INSERT INTO roles (code, name, display_name, scope, description) VALUES
('SUPER_ADMIN', 'SUPER_ADMIN', 'Super Admin', 'SYSTEM', 'System administrator with full access'),
('BILLING_ADMIN', 'BILLING_ADMIN', 'Billing Admin', 'SYSTEM', 'Manages billing and subscriptions'),
('SUPPORT_AGENT', 'SUPPORT_AGENT', 'Support Agent', 'SYSTEM', 'Customer support representative'),
('FREELANCER', 'FREELANCER', 'Freelancer', 'SYSTEM', 'Independent user without organization');

-- Farming organization roles
INSERT INTO roles (code, name, display_name, scope, description) VALUES
('OWNER', 'OWNER', 'Owner', 'ORGANIZATION', 'Farming organization owner'),
('ADMIN', 'ADMIN', 'Admin', 'ORGANIZATION', 'Farming organization administrator'),
('MANAGER', 'MANAGER', 'Manager', 'ORGANIZATION', 'Farming organization manager'),
('SUPERVISOR', 'SUPERVISOR', 'Supervisor', 'ORGANIZATION', 'Farming organization supervisor'),
('WORKER', 'WORKER', 'Worker', 'ORGANIZATION', 'Farming organization worker');

-- FSP organization roles
INSERT INTO roles (code, name, display_name, scope, description) VALUES
('FSP_OWNER', 'FSP_OWNER', 'FSP Owner', 'ORGANIZATION', 'FSP organization owner'),
('FSP_ADMIN', 'FSP_ADMIN', 'FSP Admin', 'ORGANIZATION', 'FSP organization administrator'),
('FSP_MANAGER', 'FSP_MANAGER', 'FSP Manager', 'ORGANIZATION', 'FSP organization manager'),
('FSP_SUPERVISOR', 'FSP_SUPERVISOR', 'FSP Supervisor', 'ORGANIZATION', 'FSP organization supervisor');

-- FSP consultancy service roles
INSERT INTO roles (code, name, display_name, scope, description) VALUES
('SENIOR_CONSULTANT', 'SENIOR_CONSULTANT', 'Senior Consultant', 'ORGANIZATION', 'Senior consultant for FSP'),
('CONSULTANT', 'CONSULTANT', 'Consultant', 'ORGANIZATION', 'Consultant for FSP'),
('TECHNICAL_ANALYST', 'TECHNICAL_ANALYST', 'Technical Analyst', 'ORGANIZATION', 'Technical analyst for FSP');

-- ============================================
-- PERMISSIONS (Sample - expand as needed)
-- ============================================

INSERT INTO permissions (code, name, resource, action, description) VALUES
-- Farm management
('FARM_CREATE', 'farm.create', 'farm', 'create', 'Create new farms'),
('FARM_READ', 'farm.read', 'farm', 'read', 'View farm details'),
('FARM_UPDATE', 'farm.update', 'farm', 'update', 'Update farm information'),
('FARM_DELETE', 'farm.delete', 'farm', 'delete', 'Delete farms'),

-- Plot management
('PLOT_CREATE', 'plot.create', 'plot', 'create', 'Create new plots'),
('PLOT_READ', 'plot.read', 'plot', 'read', 'View plot details'),
('PLOT_UPDATE', 'plot.update', 'plot', 'update', 'Update plot information'),
('PLOT_DELETE', 'plot.delete', 'plot', 'delete', 'Delete plots'),

-- Crop management
('CROP_CREATE', 'crop.create', 'crop', 'create', 'Create new crops'),
('CROP_READ', 'crop.read', 'crop', 'read', 'View crop details'),
('CROP_UPDATE', 'crop.update', 'crop', 'update', 'Update crop information'),
('CROP_DELETE', 'crop.delete', 'crop', 'delete', 'Delete crops'),

-- Schedule management
('SCHEDULE_CREATE', 'schedule.create', 'schedule', 'create', 'Create schedules'),
('SCHEDULE_READ', 'schedule.read', 'schedule', 'read', 'View schedules'),
('SCHEDULE_UPDATE', 'schedule.update', 'schedule', 'update', 'Update schedules'),
('SCHEDULE_DELETE', 'schedule.delete', 'schedule', 'delete', 'Delete schedules'),

-- Organization management
('ORGANIZATION_UPDATE', 'organization.update', 'organization', 'update', 'Update Organization'),
('ORGANIZATION_DELETE', 'organization.delete', 'organization', 'delete', 'Delete Organization'),
--AK: Below 3 permissions taken care by user & fsp_service(in a02) resource permissions
--('ORGANIZATION_INVITEMEMBERS', 'organization.invitemembers', 'organization', 'invitemembers', 'Invite Organization Members'),
--('ORGANIZATION_REMOVEMEMBERS', 'organization.removemembers', 'organization', 'removemembers', 'Remove Organization Members'),
--('ORGANIZATION_MANAGELISTINGS', 'organization.managelistings', 'organization', 'managelistings', 'Manage Organization Listings'),

-- Finance management
('FINANCE_CREATE', 'finance.create', 'finance', 'create', 'Create finance transactions'),
('FINANCE_READ', 'finance.read', 'finance', 'read', 'View finance transactions'),
('FINANCE_UPDATE', 'finance.update', 'finance', 'update', 'Update finance transactions'),
('FINANCE_DELETE', 'finance.delete', 'finance', 'delete', 'Delete finance transactions'),

-- User management
('USER_INVITE', 'user.invite', 'user', 'invite', 'Invite users to organization'),
('USER_MANAGE', 'user.manage', 'user', 'manage', 'Manage organization users'),

-- Query management
('QUERY_CREATE', 'query.create', 'query', 'create', 'Create queries'),
('QUERY_READ', 'query.read', 'query', 'read', 'View queries'),
('QUERY_RESPOND', 'query.respond', 'query', 'respond', 'Respond to queries'),

-- Audit management
('AUDIT_CREATE', 'audit.create', 'audit', 'create', 'Create audits'),
('AUDIT_READ', 'audit.read', 'audit', 'read', 'View audits'),
('AUDIT_UPDATE', 'audit.update', 'audit', 'update', 'Update audits'),
('AUDIT_REVIEW', 'audit.review', 'audit', 'review', 'Review and finalize audits'),
('AUDIT_SHARE', 'audit.share', 'audit', 'share', 'Share audit reports');

-- ============================================
-- MASTER SERVICES
-- ============================================

INSERT INTO master_services (code, name, description, status, sort_order) VALUES
('CONSULTANCY', 'Consultancy', 'Agricultural consultancy and advisory services', 'ACTIVE', 1),
('TRAINING', 'Training', 'Training and capacity building services', 'INACTIVE', 2),
('LABOR_SERVICE', 'Labor Service', 'Farm labor and workforce services', 'INACTIVE', 3),
('EQUIPMENT_RENTAL', 'Equipment Rental', 'Farm equipment and machinery rental', 'INACTIVE', 4),
('TRANSPORT', 'Transport', 'Agricultural produce transportation services', 'INACTIVE', 5);

-- Service translations
INSERT INTO master_service_translations (service_id, language_code, display_name, description)
SELECT id, 'en', name, description FROM master_services
UNION ALL
SELECT id, 'ta', 
    CASE code
        WHEN 'CONSULTANCY' THEN 'ஆலோசனை'
        WHEN 'TRAINING' THEN 'பயிற்சி'
        WHEN 'LABOR_SERVICE' THEN 'தொழிலாளர் சேவை'
        WHEN 'EQUIPMENT_RENTAL' THEN 'உபகரண வாடகை'
        WHEN 'TRANSPORT' THEN 'போக்குவரத்து'
    END,
    description
FROM master_services
UNION ALL
SELECT id, 'ml',
    CASE code
        WHEN 'CONSULTANCY' THEN 'കൺസൾട്ടൻസി'
        WHEN 'TRAINING' THEN 'പരിശീലനം'
        WHEN 'LABOR_SERVICE' THEN 'തൊഴിൽ സേവനം'
        WHEN 'EQUIPMENT_RENTAL' THEN 'ഉപകരണ വാടക'
        WHEN 'TRANSPORT' THEN 'ഗതാഗതം'
    END,
    description
FROM master_services;

-- ============================================
-- REFERENCE DATA TYPES
-- ============================================

INSERT INTO reference_data_types (code, name, description) VALUES
('WATER_SOURCE', 'Water Sources', 'Types of water sources for irrigation'),
('SOIL_TYPE', 'Soil Types', 'Types of soil'),
('IRRIGATION_MODE', 'Irrigation Modes', 'Methods of irrigation');

-- ============================================
-- REFERENCE DATA - WATER SOURCES
-- ============================================

INSERT INTO reference_data (type_id, code, sort_order, is_active)
SELECT id, 'WELL', 1, true FROM reference_data_types WHERE code = 'WATER_SOURCE'
UNION ALL
SELECT id, 'BOREWELL', 2, true FROM reference_data_types WHERE code = 'WATER_SOURCE'
UNION ALL
SELECT id, 'RIVER', 3, true FROM reference_data_types WHERE code = 'WATER_SOURCE'
UNION ALL
SELECT id, 'CANAL', 4, true FROM reference_data_types WHERE code = 'WATER_SOURCE'
UNION ALL
SELECT id, 'POND', 5, true FROM reference_data_types WHERE code = 'WATER_SOURCE'
UNION ALL
SELECT id, 'RAINWATER_ONLY', 6, true FROM reference_data_types WHERE code = 'WATER_SOURCE';

-- Water source translations
INSERT INTO reference_data_translations (reference_data_id, language_code, display_name)
SELECT rd.id, 'en',
    CASE rd.code
        WHEN 'WELL' THEN 'Well'
        WHEN 'BOREWELL' THEN 'Borewell'
        WHEN 'RIVER' THEN 'River'
        WHEN 'CANAL' THEN 'Canal'
        WHEN 'POND' THEN 'Pond'
        WHEN 'RAINWATER_ONLY' THEN 'Rainwater Only'
    END
FROM reference_data rd
JOIN reference_data_types rdt ON rd.type_id = rdt.id
WHERE rdt.code = 'WATER_SOURCE'
UNION ALL
SELECT rd.id, 'ta',
    CASE rd.code
        WHEN 'WELL' THEN 'கிணறு'
        WHEN 'BOREWELL' THEN 'ஆழ்துளை கிணறு'
        WHEN 'RIVER' THEN 'ஆறு'
        WHEN 'CANAL' THEN 'கால்வாய்'
        WHEN 'POND' THEN 'குளம்'
        WHEN 'RAINWATER_ONLY' THEN 'மழை நீர் மட்டும்'
    END
FROM reference_data rd
JOIN reference_data_types rdt ON rd.type_id = rdt.id
WHERE rdt.code = 'WATER_SOURCE'
UNION ALL
SELECT rd.id, 'ml',
    CASE rd.code
        WHEN 'WELL' THEN 'കിണർ'
        WHEN 'BOREWELL' THEN 'ബോർവെൽ'
        WHEN 'RIVER' THEN 'നദി'
        WHEN 'CANAL' THEN 'കനാൽ'
        WHEN 'POND' THEN 'കുളം'
        WHEN 'RAINWATER_ONLY' THEN 'മഴവെള്ളം മാത്രം'
    END
FROM reference_data rd
JOIN reference_data_types rdt ON rd.type_id = rdt.id
WHERE rdt.code = 'WATER_SOURCE';

-- ============================================
-- REFERENCE DATA - SOIL TYPES
-- ============================================

INSERT INTO reference_data (type_id, code, sort_order, is_active)
SELECT id, 'SAND', 1, true FROM reference_data_types WHERE code = 'SOIL_TYPE'
UNION ALL
SELECT id, 'CLAY', 2, true FROM reference_data_types WHERE code = 'SOIL_TYPE'
UNION ALL
SELECT id, 'LOAM', 3, true FROM reference_data_types WHERE code = 'SOIL_TYPE'
UNION ALL
SELECT id, 'CLAY_LOAM', 4, true FROM reference_data_types WHERE code = 'SOIL_TYPE'
UNION ALL
SELECT id, 'BLACK_COTTON', 5, true FROM reference_data_types WHERE code = 'SOIL_TYPE'
UNION ALL
SELECT id, 'RED_SOIL', 6, true FROM reference_data_types WHERE code = 'SOIL_TYPE';

-- Soil type translations
INSERT INTO reference_data_translations (reference_data_id, language_code, display_name)
SELECT rd.id, 'en',
    CASE rd.code
        WHEN 'SAND' THEN 'Sand'
        WHEN 'CLAY' THEN 'Clay'
        WHEN 'LOAM' THEN 'Loam'
        WHEN 'CLAY_LOAM' THEN 'Clay Loam'
        WHEN 'BLACK_COTTON' THEN 'Black Cotton'
        WHEN 'RED_SOIL' THEN 'Red Soil'
    END
FROM reference_data rd
JOIN reference_data_types rdt ON rd.type_id = rdt.id
WHERE rdt.code = 'SOIL_TYPE'
UNION ALL
SELECT rd.id, 'ta',
    CASE rd.code
        WHEN 'SAND' THEN 'மணல்'
        WHEN 'CLAY' THEN 'களிமண்'
        WHEN 'LOAM' THEN 'வண்டல்'
        WHEN 'CLAY_LOAM' THEN 'களிமண் வண்டல்'
        WHEN 'BLACK_COTTON' THEN 'கருப்பு பருத்தி மண்'
        WHEN 'RED_SOIL' THEN 'சிவப்பு மண்'
    END
FROM reference_data rd
JOIN reference_data_types rdt ON rd.type_id = rdt.id
WHERE rdt.code = 'SOIL_TYPE'
UNION ALL
SELECT rd.id, 'ml',
    CASE rd.code
        WHEN 'SAND' THEN 'മണൽ'
        WHEN 'CLAY' THEN 'കളിമണ്ണ്'
        WHEN 'LOAM' THEN 'ലോം'
        WHEN 'CLAY_LOAM' THEN 'കളിമണ്ണ് ലോം'
        WHEN 'BLACK_COTTON' THEN 'കറുത്ത പരുത്തി മണ്ണ്'
        WHEN 'RED_SOIL' THEN 'ചുവന്ന മണ്ണ്'
    END
FROM reference_data rd
JOIN reference_data_types rdt ON rd.type_id = rdt.id
WHERE rdt.code = 'SOIL_TYPE';

-- ============================================
-- REFERENCE DATA - IRRIGATION MODES
-- ============================================

INSERT INTO reference_data (type_id, code, sort_order, is_active)
SELECT id, 'DRIP', 1, true FROM reference_data_types WHERE code = 'IRRIGATION_MODE'
UNION ALL
SELECT id, 'SPRINKLER', 2, true FROM reference_data_types WHERE code = 'IRRIGATION_MODE'
UNION ALL
SELECT id, 'MICRO_SPRINKLER', 3, true FROM reference_data_types WHERE code = 'IRRIGATION_MODE'
UNION ALL
SELECT id, 'FLOOD', 4, true FROM reference_data_types WHERE code = 'IRRIGATION_MODE';

-- Irrigation mode translations
INSERT INTO reference_data_translations (reference_data_id, language_code, display_name)
SELECT rd.id, 'en',
    CASE rd.code
        WHEN 'DRIP' THEN 'Drip'
        WHEN 'SPRINKLER' THEN 'Sprinkler'
        WHEN 'MICRO_SPRINKLER' THEN 'Micro Sprinkler'
        WHEN 'FLOOD' THEN 'Flood'
    END
FROM reference_data rd
JOIN reference_data_types rdt ON rd.type_id = rdt.id
WHERE rdt.code = 'IRRIGATION_MODE'
UNION ALL
SELECT rd.id, 'ta',
    CASE rd.code
        WHEN 'DRIP' THEN 'சொட்டு நீர்'
        WHEN 'SPRINKLER' THEN 'தெளிப்பான்'
        WHEN 'MICRO_SPRINKLER' THEN 'நுண் தெளிப்பான்'
        WHEN 'FLOOD' THEN 'வெள்ள நீர்ப்பாசனம்'
    END
FROM reference_data rd
JOIN reference_data_types rdt ON rd.type_id = rdt.id
WHERE rdt.code = 'IRRIGATION_MODE'
UNION ALL
SELECT rd.id, 'ml',
    CASE rd.code
        WHEN 'DRIP' THEN 'ഡ്രിപ്പ്'
        WHEN 'SPRINKLER' THEN 'സ്പ്രിങ്ക്ലർ'
        WHEN 'MICRO_SPRINKLER' THEN 'മൈക്രോ സ്പ്രിങ്ക്ലർ'
        WHEN 'FLOOD' THEN 'വെള്ളപ്പൊക്ക ജലസേചനം'
    END
FROM reference_data rd
JOIN reference_data_types rdt ON rd.type_id = rdt.id
WHERE rdt.code = 'IRRIGATION_MODE';

-- ============================================
-- MEASUREMENT UNITS
-- ============================================

-- Area units
INSERT INTO measurement_units (category, code, symbol, is_base_unit, conversion_factor, sort_order) VALUES
('AREA', 'SQ_M', 'm²', true, 1.0, 1),
('AREA', 'SQ_FT', 'ft²', false, 0.092903, 2),
('AREA', 'CENT', 'cent', false, 40.4686, 3),
('AREA', 'ACRE', 'ac', false, 4046.86, 4),
('AREA', 'HECTARE', 'ha', false, 10000.0, 5);

-- Volume units
INSERT INTO measurement_units (category, code, symbol, is_base_unit, conversion_factor, sort_order) VALUES
('VOLUME', 'MILLILITER', 'mL', false, 0.001, 1),
('VOLUME', 'LITER', 'L', true, 1.0, 2),
('VOLUME', 'GALLON', 'gal', false, 3.78541, 3),
('VOLUME', 'CUBIC_M', 'm³', false, 1000.0, 4);

-- Weight units
INSERT INTO measurement_units (category, code, symbol, is_base_unit, conversion_factor, sort_order) VALUES
('WEIGHT', 'GRAM', 'g', false, 0.001, 1),
('WEIGHT', 'KG', 'kg', true, 1.0, 2),
('WEIGHT', 'QUINTAL', 'q', false, 100.0, 3),
('WEIGHT', 'TONNE', 't', false, 1000.0, 4),
('WEIGHT', 'POUND', 'lb', false, 0.453592, 5);

-- Length units
INSERT INTO measurement_units (category, code, symbol, is_base_unit, conversion_factor, sort_order) VALUES
('LENGTH', 'CENTIMETER', 'cm', false, 0.01, 1),
('LENGTH', 'INCH', 'in', false, 0.0254, 2),
('LENGTH', 'FEET', 'ft', false, 0.3048, 3),
('LENGTH', 'METER', 'm', true, 1.0, 4),
('LENGTH', 'KILOMETER', 'km', false, 1000.0, 5);

-- Count units
INSERT INTO measurement_units (category, code, symbol, is_base_unit, conversion_factor, sort_order) VALUES
('COUNT', 'UNIT', 'unit', true, 1.0, 1),
('COUNT', 'DOZEN', 'doz', false, 12.0, 2),
('COUNT', 'HUNDRED', '100', false, 100.0, 3);

-- Measurement unit translations
INSERT INTO measurement_unit_translations (measurement_unit_id, language_code, name)
SELECT id, 'en',
    CASE code
        WHEN 'SQ_M' THEN 'Square Meter'
        WHEN 'SQ_FT' THEN 'Square Feet'
        WHEN 'CENT' THEN 'Cent'
        WHEN 'ACRE' THEN 'Acre'
        WHEN 'HECTARE' THEN 'Hectare'
        WHEN 'MILLILITER' THEN 'Milliliter'
        WHEN 'LITER' THEN 'Liter'
        WHEN 'GALLON' THEN 'Gallon'
        WHEN 'CUBIC_M' THEN 'Cubic Meter'
        WHEN 'GRAM' THEN 'Gram'
        WHEN 'KG' THEN 'Kilogram'
        WHEN 'QUINTAL' THEN 'Quintal'
        WHEN 'TONNE' THEN 'Tonne'
        WHEN 'POUND' THEN 'Pound'
        WHEN 'CENTIMETER' THEN 'Centimeter'
        WHEN 'INCH' THEN 'Inch'
        WHEN 'FEET' THEN 'Feet'
        WHEN 'METER' THEN 'Meter'
        WHEN 'KILOMETER' THEN 'Kilometer'
        WHEN 'UNIT' THEN 'Unit'
        WHEN 'DOZEN' THEN 'Dozen'
        WHEN 'HUNDRED' THEN 'Hundred'
    END
FROM measurement_units
UNION ALL
SELECT id, 'ta',
    CASE code
        WHEN 'SQ_M' THEN 'சதுர மீட்டர்'
        WHEN 'SQ_FT' THEN 'சதுர அடி'
        WHEN 'CENT' THEN 'சென்ட்'
        WHEN 'ACRE' THEN 'ஏக்கர்'
        WHEN 'HECTARE' THEN 'ஹெக்டேர்'
        WHEN 'MILLILITER' THEN 'மில்லி லிட்டர்'
        WHEN 'LITER' THEN 'லிட்டர்'
        WHEN 'GALLON' THEN 'கேலன்'
        WHEN 'CUBIC_M' THEN 'கன மீட்டர்'
        WHEN 'GRAM' THEN 'கிராம்'
        WHEN 'KG' THEN 'கிலோகிராம்'
        WHEN 'QUINTAL' THEN 'குவிண்டால்'
        WHEN 'TONNE' THEN 'டன்'
        WHEN 'POUND' THEN 'பவுண்ட்'
        WHEN 'CENTIMETER' THEN 'சென்டிமீட்டர்'
        WHEN 'INCH' THEN 'அங்குலம்'
        WHEN 'FEET' THEN 'அடி'
        WHEN 'METER' THEN 'மீட்டர்'
        WHEN 'KILOMETER' THEN 'கிலோமீட்டர்'
        WHEN 'UNIT' THEN 'அலகு'
        WHEN 'DOZEN' THEN 'டஜன்'
        WHEN 'HUNDRED' THEN 'நூறு'
    END
FROM measurement_units
UNION ALL
SELECT id, 'ml',
    CASE code
        WHEN 'SQ_M' THEN 'ചതുരശ്ര മീറ്റർ'
        WHEN 'SQ_FT' THEN 'ചതുരശ്ര അടി'
        WHEN 'CENT' THEN 'സെന്റ്'
        WHEN 'ACRE' THEN 'ഏക്കർ'
        WHEN 'HECTARE' THEN 'ഹെക്ടർ'
        WHEN 'MILLILITER' THEN 'മില്ലി ലിറ്റർ'
        WHEN 'LITER' THEN 'ലിറ്റർ'
        WHEN 'GALLON' THEN 'ഗാലൻ'
        WHEN 'CUBIC_M' THEN 'ക്യൂബിക് മീറ്റർ'
        WHEN 'GRAM' THEN 'ഗ്രാം'
        WHEN 'KG' THEN 'കിലോഗ്രാം'
        WHEN 'QUINTAL' THEN 'ക്വിന്റൽ'
        WHEN 'TONNE' THEN 'ടൺ'
        WHEN 'POUND' THEN 'പൗണ്ട്'
        WHEN 'CENTIMETER' THEN 'സെന്റിമീറ്റർ'
        WHEN 'INCH' THEN 'ഇഞ്ച്'
        WHEN 'FEET' THEN 'അടി'
        WHEN 'METER' THEN 'മീറ്റർ'
        WHEN 'KILOMETER' THEN 'കിലോമീറ്റർ'
        WHEN 'UNIT' THEN 'യൂണിറ്റ്'
        WHEN 'DOZEN' THEN 'ഡസൻ'
        WHEN 'HUNDRED' THEN 'നൂറ്'
    END
FROM measurement_units;

-- ============================================
-- CROP CATEGORIES, TYPES, VARIETIES (Sample Data)
-- ============================================

-- Crop categories
INSERT INTO crop_categories (code, sort_order, is_active) VALUES
('VEGETABLES', 1, true),
('FRUITS', 2, true),
('CEREALS', 3, true),
('PULSES', 4, true),
('SPICES', 5, true);

-- Crop category translations
INSERT INTO crop_category_translations (crop_category_id, language_code, name, description)
SELECT id, 'en', 
    CASE code
        WHEN 'VEGETABLES' THEN 'Vegetables'
        WHEN 'FRUITS' THEN 'Fruits'
        WHEN 'CEREALS' THEN 'Cereals'
        WHEN 'PULSES' THEN 'Pulses'
        WHEN 'SPICES' THEN 'Spices'
    END,
    NULL
FROM crop_categories
UNION ALL
SELECT id, 'ta',
    CASE code
        WHEN 'VEGETABLES' THEN 'காய்கறிகள்'
        WHEN 'FRUITS' THEN 'பழங்கள்'
        WHEN 'CEREALS' THEN 'தானியங்கள்'
        WHEN 'PULSES' THEN 'பருப்பு வகைகள்'
        WHEN 'SPICES' THEN 'மசாலா பொருட்கள்'
    END,
    NULL
FROM crop_categories
UNION ALL
SELECT id, 'ml',
    CASE code
        WHEN 'VEGETABLES' THEN 'പച്ചക്കറികൾ'
        WHEN 'FRUITS' THEN 'പഴങ്ങൾ'
        WHEN 'CEREALS' THEN 'ധാന്യങ്ങൾ'
        WHEN 'PULSES' THEN 'പയർ വർഗ്ഗങ്ങൾ'
        WHEN 'SPICES' THEN 'സുഗന്ധവ്യഞ്ജനങ്ങൾ'
    END,
    NULL
FROM crop_categories;

-- Sample crop types
INSERT INTO crop_types (category_id, code, sort_order, is_active)
SELECT id, 'TOMATO', 1, true FROM crop_categories WHERE code = 'VEGETABLES'
UNION ALL
SELECT id, 'CHILI', 2, true FROM crop_categories WHERE code = 'VEGETABLES'
UNION ALL
SELECT id, 'BANANA', 1, true FROM crop_categories WHERE code = 'FRUITS'
UNION ALL
SELECT id, 'MANGO', 2, true FROM crop_categories WHERE code = 'FRUITS';

-- Crop type translations
INSERT INTO crop_type_translations (crop_type_id, language_code, name)
SELECT ct.id, 'en',
    CASE ct.code
        WHEN 'TOMATO' THEN 'Tomato'
        WHEN 'CHILI' THEN 'Chili'
        WHEN 'BANANA' THEN 'Banana'
        WHEN 'MANGO' THEN 'Mango'
    END
FROM crop_types ct
UNION ALL
SELECT ct.id, 'ta',
    CASE ct.code
        WHEN 'TOMATO' THEN 'தக்காளி'
        WHEN 'CHILI' THEN 'மிளகாய்'
        WHEN 'BANANA' THEN 'வாழை'
        WHEN 'MANGO' THEN 'மாம்பழம்'
    END
FROM crop_types ct
UNION ALL
SELECT ct.id, 'ml',
    CASE ct.code
        WHEN 'TOMATO' THEN 'തക്കാളി'
        WHEN 'CHILI' THEN 'മുളക്'
        WHEN 'BANANA' THEN 'വാഴപ്പഴം'
        WHEN 'MANGO' THEN 'മാങ്ങ'
    END
FROM crop_types ct;

-- ============================================
-- INPUT ITEM CATEGORIES & ITEMS (Sample Data)
-- ============================================

-- Input item categories (system-defined)
INSERT INTO input_item_categories (code, is_system_defined, owner_org_id, sort_order, is_active) VALUES
('FERTILIZER', true, NULL, 1, true),
('PESTICIDE', true, NULL, 2, true),
('HERBICIDE', true, NULL, 3, true),
('FYM', true, NULL, 4, true),
('GROWTH_REGULATOR', true, NULL, 5, true)
ON CONFLICT (code, is_system_defined) WHERE is_system_defined = TRUE DO NOTHING;

-- Input item category translations
INSERT INTO input_item_category_translations (category_id, language_code, name)
SELECT id, 'en',
    CASE code
        WHEN 'FERTILIZER' THEN 'Fertilizer'
        WHEN 'PESTICIDE' THEN 'Pesticide'
        WHEN 'HERBICIDE' THEN 'Herbicide'
        WHEN 'FYM' THEN 'Farm Yard Manure'
        WHEN 'GROWTH_REGULATOR' THEN 'Growth Regulator'
    END
FROM input_item_categories
UNION ALL
SELECT id, 'ta',
    CASE code
        WHEN 'FERTILIZER' THEN 'உரம்'
        WHEN 'PESTICIDE' THEN 'பூச்சிக்கொல்லி'
        WHEN 'HERBICIDE' THEN 'களைக்கொல்லி'
        WHEN 'FYM' THEN 'தொழு உரம்'
        WHEN 'GROWTH_REGULATOR' THEN 'வளர்ச்சி ஊக்கி'
    END
FROM input_item_categories
UNION ALL
SELECT id, 'ml',
    CASE code
        WHEN 'FERTILIZER' THEN 'വളം'
        WHEN 'PESTICIDE' THEN 'കീടനാശിനി'
        WHEN 'HERBICIDE' THEN 'കളനാശിനി'
        WHEN 'FYM' THEN 'ജൈവവളം'
        WHEN 'GROWTH_REGULATOR' THEN 'വളർച്ച നിയന്ത്രകം'
    END
FROM input_item_categories;

-- Sample input items (system-defined)
INSERT INTO input_items (category_id, code, is_system_defined, sort_order, is_active, item_metadata)
SELECT id, 'UREA', true, 1, true, '{"npk": "46-0-0"}'::jsonb FROM input_item_categories WHERE code = 'FERTILIZER'
UNION ALL
SELECT id, 'DAP', true, 2, true, '{"npk": "18-46-0"}'::jsonb FROM input_item_categories WHERE code = 'FERTILIZER'
UNION ALL
SELECT id, 'NPK_19_19_19', true, 3, true, '{"npk": "19-19-19"}'::jsonb FROM input_item_categories WHERE code = 'FERTILIZER'
ON CONFLICT (code, is_system_defined) WHERE is_system_defined = TRUE DO NOTHING;

-- Input item translations
INSERT INTO input_item_translations (input_item_id, language_code, name)
SELECT ii.id, 'en',
    CASE ii.code
        WHEN 'UREA' THEN 'Urea'
        WHEN 'DAP' THEN 'DAP (Di-Ammonium Phosphate)'
        WHEN 'NPK_19_19_19' THEN 'NPK 19:19:19'
    END
FROM input_items ii
UNION ALL
SELECT ii.id, 'ta',
    CASE ii.code
        WHEN 'UREA' THEN 'யூரியா'
        WHEN 'DAP' THEN 'டி.ஏ.பி'
        WHEN 'NPK_19_19_19' THEN 'என்.பி.கே 19:19:19'
    END
FROM input_items ii
UNION ALL
SELECT ii.id, 'ml',
    CASE ii.code
        WHEN 'UREA' THEN 'യൂറിയ'
        WHEN 'DAP' THEN 'ഡി.എ.പി'
        WHEN 'NPK_19_19_19' THEN 'എൻ.പി.കെ 19:19:19'
    END
FROM input_items ii;

-- ============================================
-- TASKS
-- ============================================

-- Farming tasks
INSERT INTO tasks (code, category, requires_input_items, requires_concentration, requires_machinery, requires_labor, sort_order, is_active) VALUES
('PLOUGHING', 'FARMING', false, false, true, true, 1, true),
('WEEDING', 'FARMING', false, false, false, true, 2, true),
('PRUNING', 'FARMING', false, false, false, true, 3, true),
('TRELLISING', 'FARMING', false, false, false, true, 4, true),
('HARVESTING', 'FARMING', false, false, false, true, 5, true),
('BASAL_DOSE', 'FARMING', true, false, false, true, 6, true),
('FERTIGATION', 'FARMING', true, true, false, true, 7, true),
('FOLIAR_SPRAY', 'FARMING', true, true, true, true, 8, true),
('DRENCHING', 'FARMING', true, true, false, true, 9, true),
('TOP_DRESSING', 'FARMING', true, false, false, true, 10, true),
('ROOT_FEEDING', 'FARMING', true, true, false, true, 11, true);

-- FSP consultancy tasks
INSERT INTO tasks (code, category, requires_input_items, requires_concentration, requires_machinery, requires_labor, sort_order, is_active) VALUES
('SOP_SCHEDULE_GENERATION', 'FSP_CONSULTANCY', false, false, false, false, 1, true),
('CROP_AUDIT', 'FSP_CONSULTANCY', false, false, false, false, 2, true),
('REMOTE_AUDIT', 'FSP_CONSULTANCY', false, false, false, false, 3, true),
('QUERY_RESOLUTION', 'FSP_CONSULTANCY', false, false, false, false, 4, true);

-- Task translations
INSERT INTO task_translations (task_id, language_code, name, description)
SELECT id, 'en',
    CASE code
        WHEN 'PLOUGHING' THEN 'Ploughing'
        WHEN 'WEEDING' THEN 'Weeding'
        WHEN 'PRUNING' THEN 'Pruning'
        WHEN 'TRELLISING' THEN 'Trellising'
        WHEN 'HARVESTING' THEN 'Harvesting'
        WHEN 'BASAL_DOSE' THEN 'Basal Dose'
        WHEN 'FERTIGATION' THEN 'Fertigation'
        WHEN 'FOLIAR_SPRAY' THEN 'Foliar Spray'
        WHEN 'DRENCHING' THEN 'Drenching'
        WHEN 'TOP_DRESSING' THEN 'Top Dressing'
        WHEN 'ROOT_FEEDING' THEN 'Root Feeding'
        WHEN 'SOP_SCHEDULE_GENERATION' THEN 'SOP Schedule Generation'
        WHEN 'CROP_AUDIT' THEN 'Crop Audit'
        WHEN 'REMOTE_AUDIT' THEN 'Remote Audit'
        WHEN 'QUERY_RESOLUTION' THEN 'Query Resolution'
    END,
    NULL
FROM tasks
UNION ALL
SELECT id, 'ta',
    CASE code
        WHEN 'PLOUGHING' THEN 'உழவு'
        WHEN 'WEEDING' THEN 'களை எடுத்தல்'
        WHEN 'PRUNING' THEN 'கிளை வெட்டுதல்'
        WHEN 'TRELLISING' THEN 'தாங்கு கட்டுதல்'
        WHEN 'HARVESTING' THEN 'அறுவடை'
        WHEN 'BASAL_DOSE' THEN 'அடி உரம்'
        WHEN 'FERTIGATION' THEN 'நீர் உரம்'
        WHEN 'FOLIAR_SPRAY' THEN 'இலை தெளிப்பு'
        WHEN 'DRENCHING' THEN 'வேர் ஊற்றுதல்'
        WHEN 'TOP_DRESSING' THEN 'மேல் உரம்'
        WHEN 'ROOT_FEEDING' THEN 'வேர் உணவு'
        WHEN 'SOP_SCHEDULE_GENERATION' THEN 'எஸ்.ஓ.பி அட்டவணை உருவாக்கம்'
        WHEN 'CROP_AUDIT' THEN 'பயிர் தணிக்கை'
        WHEN 'REMOTE_AUDIT' THEN 'தொலை தணிக்கை'
        WHEN 'QUERY_RESOLUTION' THEN 'வினா தீர்வு'
    END,
    NULL
FROM tasks;

-- ============================================
-- FINANCE CATEGORIES
-- ============================================

-- Income categories (system-defined)
INSERT INTO finance_categories (transaction_type, code, is_system_defined, owner_org_id, sort_order, is_active) VALUES
('INCOME', 'CROP_SALE', true, NULL, 1, true),
('INCOME', 'SUBSIDY', true, NULL, 2, true),
('INCOME', 'GRANT', true, NULL, 3, true),
('INCOME', 'OTHER_INCOME', true, NULL, 4, true);

-- Expense categories (system-defined)
INSERT INTO finance_categories (transaction_type, code, is_system_defined, owner_org_id, sort_order, is_active) VALUES
('EXPENSE', 'SEEDS', true, NULL, 1, true),
('EXPENSE', 'FERTILIZER', true, NULL, 2, true),
('EXPENSE', 'PESTICIDE', true, NULL, 3, true),
('EXPENSE', 'LABOR', true, NULL, 4, true),
('EXPENSE', 'EQUIPMENT', true, NULL, 5, true),
('EXPENSE', 'IRRIGATION', true, NULL, 6, true),
('EXPENSE', 'TRANSPORT', true, NULL, 7, true),
('EXPENSE', 'CONSULTANCY', true, NULL, 8, true),
('EXPENSE', 'OTHER_EXPENSE', true, NULL, 9, true);

-- Finance category translations
INSERT INTO finance_category_translations (category_id, language_code, name)
SELECT id, 'en',
    CASE code
        WHEN 'CROP_SALE' THEN 'Crop Sale'
        WHEN 'SUBSIDY' THEN 'Subsidy'
        WHEN 'GRANT' THEN 'Grant'
        WHEN 'OTHER_INCOME' THEN 'Other Income'
        WHEN 'SEEDS' THEN 'Seeds'
        WHEN 'FERTILIZER' THEN 'Fertilizer'
        WHEN 'PESTICIDE' THEN 'Pesticide'
        WHEN 'LABOR' THEN 'Labor'
        WHEN 'EQUIPMENT' THEN 'Equipment'
        WHEN 'IRRIGATION' THEN 'Irrigation'
        WHEN 'TRANSPORT' THEN 'Transport'
        WHEN 'CONSULTANCY' THEN 'Consultancy'
        WHEN 'OTHER_EXPENSE' THEN 'Other Expense'
    END
FROM finance_categories
UNION ALL
SELECT id, 'ta',
    CASE code
        WHEN 'CROP_SALE' THEN 'பயிர் விற்பனை'
        WHEN 'SUBSIDY' THEN 'மானியம்'
        WHEN 'GRANT' THEN 'நிதி உதவி'
        WHEN 'OTHER_INCOME' THEN 'மற்ற வருமானம்'
        WHEN 'SEEDS' THEN 'விதைகள்'
        WHEN 'FERTILIZER' THEN 'உரம்'
        WHEN 'PESTICIDE' THEN 'பூச்சிக்கொல்லி'
        WHEN 'LABOR' THEN 'தொழிலாளர்'
        WHEN 'EQUIPMENT' THEN 'உபகரணங்கள்'
        WHEN 'IRRIGATION' THEN 'நீர்ப்பாசனம்'
        WHEN 'TRANSPORT' THEN 'போக்குவரத்து'
        WHEN 'CONSULTANCY' THEN 'ஆலோசனை'
        WHEN 'OTHER_EXPENSE' THEN 'மற்ற செலவு'
    END
FROM finance_categories;

-- ============================================
-- SAMPLE AUDIT SECTIONS, PARAMETERS & OPTION SETS
-- ============================================

-- Option sets
INSERT INTO option_sets (code, is_system_defined, owner_org_id, is_active) VALUES
('LEAF_COLOR_OPTIONS', true, NULL, true),
('YES_NO_OPTIONS', true, NULL, true),
('SOIL_MOISTURE_OPTIONS', true, NULL, true);

-- Options for LEAF_COLOR_OPTIONS
INSERT INTO options (option_set_id, code, sort_order, is_active)
SELECT id, 'GREEN', 1, true FROM option_sets WHERE code = 'LEAF_COLOR_OPTIONS'
UNION ALL
SELECT id, 'YELLOW', 2, true FROM option_sets WHERE code = 'LEAF_COLOR_OPTIONS'
UNION ALL
SELECT id, 'BROWN', 3, true FROM option_sets WHERE code = 'LEAF_COLOR_OPTIONS';

-- Options for YES_NO_OPTIONS
INSERT INTO options (option_set_id, code, sort_order, is_active)
SELECT id, 'YES', 1, true FROM option_sets WHERE code = 'YES_NO_OPTIONS'
UNION ALL
SELECT id, 'NO', 2, true FROM option_sets WHERE code = 'YES_NO_OPTIONS';

-- Options for SOIL_MOISTURE_OPTIONS
INSERT INTO options (option_set_id, code, sort_order, is_active)
SELECT id, 'DRY', 1, true FROM option_sets WHERE code = 'SOIL_MOISTURE_OPTIONS'
UNION ALL
SELECT id, 'MOIST', 2, true FROM option_sets WHERE code = 'SOIL_MOISTURE_OPTIONS'
UNION ALL
SELECT id, 'WET', 3, true FROM option_sets WHERE code = 'SOIL_MOISTURE_OPTIONS';

-- Option translations
INSERT INTO option_translations (option_id, language_code, display_text)
SELECT o.id, 'en',
    CASE o.code
        WHEN 'GREEN' THEN 'Green'
        WHEN 'YELLOW' THEN 'Yellow'
        WHEN 'BROWN' THEN 'Brown'
        WHEN 'YES' THEN 'Yes'
        WHEN 'NO' THEN 'No'
        WHEN 'DRY' THEN 'Dry'
        WHEN 'MOIST' THEN 'Moist'
        WHEN 'WET' THEN 'Wet'
    END
FROM options o
UNION ALL
SELECT o.id, 'ta',
    CASE o.code
        WHEN 'GREEN' THEN 'பச்சை'
        WHEN 'YELLOW' THEN 'மஞ்சள்'
        WHEN 'BROWN' THEN 'பழுப்பு'
        WHEN 'YES' THEN 'ஆம்'
        WHEN 'NO' THEN 'இல்லை'
        WHEN 'DRY' THEN 'வறண்ட'
        WHEN 'MOIST' THEN 'ஈரமான'
        WHEN 'WET' THEN 'நனைந்த'
    END
FROM options o;

-- Sections
INSERT INTO sections (code, is_system_defined, owner_org_id, is_active) VALUES
('PLANT_HEALTH', true, NULL, true),
('SOIL_CONDITION', true, NULL, true),
('PEST_DISEASE', true, NULL, true),
('IRRIGATION', true, NULL, true);

-- Section translations
INSERT INTO section_translations (section_id, language_code, name)
SELECT id, 'en',
    CASE code
        WHEN 'PLANT_HEALTH' THEN 'Plant Health'
        WHEN 'SOIL_CONDITION' THEN 'Soil Condition'
        WHEN 'PEST_DISEASE' THEN 'Pest & Disease'
        WHEN 'IRRIGATION' THEN 'Irrigation'
    END
FROM sections
UNION ALL
SELECT id, 'ta',
    CASE code
        WHEN 'PLANT_HEALTH' THEN 'தாவர ஆரோக்கியம்'
        WHEN 'SOIL_CONDITION' THEN 'மண் நிலை'
        WHEN 'PEST_DISEASE' THEN 'பூச்சி & நோய்'
        WHEN 'IRRIGATION' THEN 'நீர்ப்பாசனம்'
    END
FROM sections;

-- Parameters
INSERT INTO parameters (code, parameter_type, is_system_defined, owner_org_id, is_active) VALUES
('PLANT_HEIGHT', 'NUMERIC', true, NULL, true),
('LEAF_COLOR', 'SINGLE_SELECT', true, NULL, true),
('PEST_PRESENCE', 'SINGLE_SELECT', true, NULL, true),
('SOIL_MOISTURE', 'SINGLE_SELECT', true, NULL, true);

-- Parameter translations
INSERT INTO parameter_translations (parameter_id, language_code, name, help_text)
SELECT id, 'en',
    CASE code
        WHEN 'PLANT_HEIGHT' THEN 'Plant Height (cm)'
        WHEN 'LEAF_COLOR' THEN 'Leaf Color'
        WHEN 'PEST_PRESENCE' THEN 'Pest Presence'
        WHEN 'SOIL_MOISTURE' THEN 'Soil Moisture Level'
    END,
    NULL
FROM parameters;

-- Parameter to option set mapping
INSERT INTO parameter_option_set_map (parameter_id, option_set_id)
SELECT p.id, os.id FROM parameters p, option_sets os 
WHERE p.code = 'LEAF_COLOR' AND os.code = 'LEAF_COLOR_OPTIONS'
UNION ALL
SELECT p.id, os.id FROM parameters p, option_sets os 
WHERE p.code = 'PEST_PRESENCE' AND os.code = 'YES_NO_OPTIONS'
UNION ALL
SELECT p.id, os.id FROM parameters p, option_sets os 
WHERE p.code = 'SOIL_MOISTURE' AND os.code = 'SOIL_MOISTURE_OPTIONS';

-- ============================================
-- SAMPLE SCHEDULE TEMPLATES
-- ============================================

-- Sample schedule template for Tomato
INSERT INTO schedule_templates (code, crop_type_id, crop_variety_id, is_system_defined, owner_org_id, version, is_active, notes)
SELECT 'TOMATO_STANDARD_PACKAGE', id, NULL, true, NULL, 1, true, 'Standard package of practice for tomato cultivation'
FROM crop_types WHERE code = 'TOMATO';

-- Schedule template translations
INSERT INTO schedule_template_translations (schedule_template_id, language_code, name, description)
SELECT id, 'en', 'Tomato Standard Package', 'Complete fertigation and pest management schedule for tomato cultivation (1 acre, 400 plants)'
FROM schedule_templates WHERE code = 'TOMATO_STANDARD_PACKAGE'
UNION ALL
SELECT id, 'ta', 'தக்காளி நிலையான தொகுப்பு', 'தக்காளி சாகுபடிக்கான முழுமையான நீர் உரம் மற்றும் பூச்சி மேலாண்மை அட்டவணை (1 ஏக்கர், 400 செடிகள்)'
FROM schedule_templates WHERE code = 'TOMATO_STANDARD_PACKAGE';

-- Sample schedule template tasks for Tomato
-- Task 1: Basal Dose (Day 0)
INSERT INTO schedule_template_tasks (schedule_template_id, task_id, day_offset, task_details_template, sort_order, notes)
SELECT 
    st.id,
    t.id,
    0,
    jsonb_build_object(
        'input_items', jsonb_build_array(
            jsonb_build_object(
                'input_item_id', (SELECT id FROM input_items WHERE code = 'UREA'),
                'quantity', 100,
                'quantity_unit_id', (SELECT id FROM measurement_units WHERE code = 'KG'),
                'calculation_basis', 'per_acre'
            ),
            jsonb_build_object(
                'input_item_id', (SELECT id FROM input_items WHERE code = 'DAP'),
                'quantity', 75,
                'quantity_unit_id', (SELECT id FROM measurement_units WHERE code = 'KG'),
                'calculation_basis', 'per_acre'
            )
        )
    ),
    1,
    'Apply before planting'
FROM schedule_templates st, tasks t
WHERE st.code = 'TOMATO_STANDARD_PACKAGE' AND t.code = 'BASAL_DOSE';

-- Task 2: Ploughing (Day 5)
INSERT INTO schedule_template_tasks (schedule_template_id, task_id, day_offset, task_details_template, sort_order, notes)
SELECT 
    st.id,
    t.id,
    5,
    jsonb_build_object(
        'machinery', jsonb_build_object(
            'equipment_type', 'tractor',
            'estimated_hours', 3.5,
            'calculation_basis', 'per_acre'
        )
    ),
    2,
    'Deep ploughing required'
FROM schedule_templates st, tasks t
WHERE st.code = 'TOMATO_STANDARD_PACKAGE' AND t.code = 'PLOUGHING';

-- Task 3: Drenching (Day 6)
INSERT INTO schedule_template_tasks (schedule_template_id, task_id, day_offset, task_details_template, sort_order, notes)
SELECT 
    st.id,
    t.id,
    6,
    jsonb_build_object(
        'concentration', jsonb_build_object(
            'solution_volume', 80,
            'solution_volume_unit_id', (SELECT id FROM measurement_units WHERE code = 'ML'),
            'calculation_basis', 'per_plant',
            'ingredients', jsonb_build_array(
                jsonb_build_object(
                    'input_item_id', (SELECT id FROM input_items WHERE code = 'NEEM_OIL'),
                    'concentration_per_liter', 3,
                    'concentration_unit_id', (SELECT id FROM measurement_units WHERE code = 'ML')
                )
            )
        )
    ),
    3,
    'Apply around root zone'
FROM schedule_templates st, tasks t
WHERE st.code = 'TOMATO_STANDARD_PACKAGE' AND t.code = 'DRENCHING';

-- Task 4: Fertigation (Day 15)
INSERT INTO schedule_template_tasks (schedule_template_id, task_id, day_offset, task_details_template, sort_order, notes)
SELECT 
    st.id,
    t.id,
    15,
    jsonb_build_object(
        'input_items', jsonb_build_array(
            jsonb_build_object(
                'input_item_id', (SELECT id FROM input_items WHERE code = 'NPK_19_19_19'),
                'quantity', 5,
                'quantity_unit_id', (SELECT id FROM measurement_units WHERE code = 'KG'),
                'calculation_basis', 'per_acre'
            )
        )
    ),
    4,
    'Apply through drip irrigation'
FROM schedule_templates st, tasks t
WHERE st.code = 'TOMATO_STANDARD_PACKAGE' AND t.code = 'FERTIGATION';

-- Task 5: Foliar Spray (Day 17)
INSERT INTO schedule_template_tasks (schedule_template_id, task_id, day_offset, task_details_template, sort_order, notes)
SELECT 
    st.id,
    t.id,
    17,
    jsonb_build_object(
        'concentration', jsonb_build_object(
            'solution_volume', 30,
            'solution_volume_unit_id', (SELECT id FROM measurement_units WHERE code = 'L'),
            'calculation_basis', 'per_acre',
            'ingredients', jsonb_build_array()
        )
    ),
    5,
    'Spray during early morning or evening'
FROM schedule_templates st, tasks t
WHERE st.code = 'TOMATO_STANDARD_PACKAGE' AND t.code = 'FOLIAR_SPRAY';

-- Task 6: Top Dressing (Day 30)
INSERT INTO schedule_template_tasks (schedule_template_id, task_id, day_offset, task_details_template, sort_order, notes)
SELECT 
    st.id,
    t.id,
    30,
    jsonb_build_object(
        'input_items', jsonb_build_array(
            jsonb_build_object(
                'input_item_id', (SELECT id FROM input_items WHERE code = 'UREA'),
                'quantity', 10,
                'quantity_unit_id', (SELECT id FROM measurement_units WHERE code = 'G'),
                'calculation_basis', 'per_plant'
            )
        )
    ),
    6,
    'Apply around plant base'
FROM schedule_templates st, tasks t
WHERE st.code = 'TOMATO_STANDARD_PACKAGE' AND t.code = 'TOP_DRESSING';

-- End of DML script
