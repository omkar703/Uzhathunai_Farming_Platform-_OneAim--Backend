-- Chat Module Migration
-- Depends on: 007_audit_assignments.sql

-- Enums
CREATE TYPE chat_context_type AS ENUM ('WORK_ORDER', 'ORGANIZATION', 'SUPPORT');
CREATE TYPE message_type AS ENUM ('TEXT', 'IMAGE', 'FILE', 'SYSTEM');

-- Chat Channels
-- Represents a conversation thread
CREATE TABLE chat_channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_type chat_context_type NOT NULL,
    context_id UUID NOT NULL, -- Links to WorkOrder.id, Organization.id, etc.
    name VARCHAR(255), -- Optional custom name
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_chat_channels_context ON chat_channels(context_type, context_id);

-- Chat Channel Members
-- Links Organizations to Channels (Org-to-Org chat)
CREATE TABLE chat_channel_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel_id UUID REFERENCES chat_channels(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES users(id),
    
    UNIQUE(channel_id, organization_id)
);

CREATE INDEX idx_chat_members_channel ON chat_channel_members(channel_id);
CREATE INDEX idx_chat_members_org ON chat_channel_members(organization_id);

-- Chat Messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel_id UUID REFERENCES chat_channels(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id), -- User who sent the message
    sender_org_id UUID REFERENCES organizations(id), -- Organization the user was representing
    
    message_type message_type NOT NULL DEFAULT 'TEXT',
    content TEXT, -- Text content or file caption
    media_url TEXT, -- For images/files
    
    is_system_message BOOLEAN DEFAULT FALSE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_chat_messages_channel_dt ON chat_messages(channel_id, created_at DESC);

-- Add 'CHAT' permission to roles if needed in future, currently implicit for Org Members
