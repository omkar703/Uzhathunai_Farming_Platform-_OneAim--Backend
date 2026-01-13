-- 002_create_refresh_tokens_table.sql
-- Purpose: Create refresh_tokens table for JWT authentication
-- Author: Kiro AI Assistant
-- Date: 2025-11-19
-- Approved: Yes

-- Refresh tokens table for JWT token management
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT false,
    revoked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_revoked ON refresh_tokens(is_revoked);

-- Comments for documentation
COMMENT ON TABLE refresh_tokens IS 'Stores refresh tokens for JWT authentication';
COMMENT ON COLUMN refresh_tokens.token_hash IS 'SHA-256 hash of the refresh token for security';
COMMENT ON COLUMN refresh_tokens.device_info IS 'JSONB: {"device_type": "mobile", "device_name": "iPhone 12", "os": "iOS 15", "app_version": "2.0.0"}';
COMMENT ON COLUMN refresh_tokens.is_revoked IS 'True when user logs out or changes password';
