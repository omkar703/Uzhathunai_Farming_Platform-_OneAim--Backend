-- Migration: Add specialization to users table
-- Description: Adds a specialization column to the users table to support freelancer search.

ALTER TABLE users ADD COLUMN IF NOT EXISTS specialization VARCHAR(200);
