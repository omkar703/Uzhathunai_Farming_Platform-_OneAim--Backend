-- Add MACHINERY master service if it doesn't exist
-- Using validation logic to prevent duplicates

INSERT INTO master_services (code, name, description, status, sort_order)
SELECT 'MACHINERY', 'Farm Machinery', 'Farm equipment, tractors and machinery services', 'ACTIVE', 2
WHERE NOT EXISTS (
    SELECT 1 FROM master_services WHERE code = 'MACHINERY'
);

-- Add translations
INSERT INTO master_service_translations (service_id, language_code, display_name, description)
SELECT id, 'en', 'Farm Machinery', 'Farm equipment, tractors and machinery services'
FROM master_services WHERE code = 'MACHINERY'
AND NOT EXISTS (
    SELECT 1 FROM master_service_translations 
    WHERE service_id = (SELECT id FROM master_services WHERE code = 'MACHINERY') 
    AND language_code = 'en'
);

INSERT INTO master_service_translations (service_id, language_code, display_name, description)
SELECT id, 'ta', 'பண்ணை இயந்திரங்கள்', 'Farm equipment, tractors and machinery services'
FROM master_services WHERE code = 'MACHINERY'
AND NOT EXISTS (
    SELECT 1 FROM master_service_translations 
    WHERE service_id = (SELECT id FROM master_services WHERE code = 'MACHINERY') 
    AND language_code = 'ta'
);

INSERT INTO master_service_translations (service_id, language_code, display_name, description)
SELECT id, 'ml', 'ഫാം മെഷിനറി', 'Farm equipment, tractors and machinery services'
FROM master_services WHERE code = 'MACHINERY'
AND NOT EXISTS (
    SELECT 1 FROM master_service_translations 
    WHERE service_id = (SELECT id FROM master_services WHERE code = 'MACHINERY') 
    AND language_code = 'ml'
);
