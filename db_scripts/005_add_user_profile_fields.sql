-- Migration: Add user profile fields
-- Version: 005
-- Description: Add bio, address, and profile_picture_url to users table for enhanced member details

-- Add new columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture_url VARCHAR(500);

-- Add comments for documentation
COMMENT ON COLUMN users.bio IS 'User biography/description for member profile';
COMMENT ON COLUMN users.address IS 'User physical address';
COMMENT ON COLUMN users.profile_picture_url IS 'URL to user profile picture/avatar';
