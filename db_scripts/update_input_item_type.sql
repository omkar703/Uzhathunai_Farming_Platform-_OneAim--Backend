-- Update input_item_type enum to include new values
ALTER TYPE input_item_type ADD VALUE IF NOT EXISTS 'MACHINERY';
ALTER TYPE input_item_type ADD VALUE IF NOT EXISTS 'LABOUR';
ALTER TYPE input_item_type ADD VALUE IF NOT EXISTS 'BIO_FERTILIZER';
ALTER TYPE input_item_type ADD VALUE IF NOT EXISTS 'ORGANIC_FERTILIZER';
