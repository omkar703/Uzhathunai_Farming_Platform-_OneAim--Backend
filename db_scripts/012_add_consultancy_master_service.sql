-- Add CONSULTANCY master service if it doesn't exist
-- Using validation logic to prevent duplicates

INSERT INTO master_services (code, name, description, status, sort_order)
SELECT 'CONSULTANCY', 'Consultancy', 'Agricultural consultancy and advisory services', 'ACTIVE', 1
WHERE NOT EXISTS (
    SELECT 1 FROM master_services WHERE code = 'CONSULTANCY'
);

-- Add translations
INSERT INTO master_service_translations (service_id, language_code, display_name, description)
SELECT id, 'en', 'Consultancy', 'Agricultural consultancy and advisory services'
FROM master_services WHERE code = 'CONSULTANCY'
AND NOT EXISTS (
    SELECT 1 FROM master_service_translations 
    WHERE service_id = (SELECT id FROM master_services WHERE code = 'CONSULTANCY') 
    AND language_code = 'en'
);

INSERT INTO master_service_translations (service_id, language_code, display_name, description)
SELECT id, 'ta', 'ஆலோசனை', 'Agricultural consultancy and advisory services'
FROM master_services WHERE code = 'CONSULTANCY'
AND NOT EXISTS (
    SELECT 1 FROM master_service_translations 
    WHERE service_id = (SELECT id FROM master_services WHERE code = 'CONSULTANCY') 
    AND language_code = 'ta'
);

INSERT INTO master_service_translations (service_id, language_code, display_name, description)
SELECT id, 'ml', 'കൺസൾട്ടൻസി', 'Agricultural consultancy and advisory services'
FROM master_services WHERE code = 'CONSULTANCY'
AND NOT EXISTS (
    SELECT 1 FROM master_service_translations 
    WHERE service_id = (SELECT id FROM master_services WHERE code = 'CONSULTANCY') 
    AND language_code = 'ml'
);
