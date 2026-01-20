-- Migration: Add city column to farms table
-- Date: 2026-01-17
-- Description: Adds city VARCHAR(100) column to farms table for better address representation

ALTER TABLE farms ADD COLUMN IF NOT EXISTS city VARCHAR(100);

-- Verify the column was added
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'farms' AND column_name = 'city';
