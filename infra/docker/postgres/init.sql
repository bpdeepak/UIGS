-- ============================================================================
-- UIGS PostgreSQL Initialization Script
-- Database: uigs_audit
-- Purpose: Immutable audit log for ingestion events
-- ============================================================================

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLES
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ingestion events table (append-only audit log)
CREATE TABLE IF NOT EXISTS ingestion_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('VC', 'OIDC', 'MANUAL')),
    raw_payload JSONB NOT NULL,
    checksum VARCHAR(64) NOT NULL,  -- SHA-256 hash for integrity
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexing for common queries
    CONSTRAINT valid_payload CHECK (raw_payload IS NOT NULL)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Index for querying events by user
CREATE INDEX IF NOT EXISTS idx_ingestion_events_user_id 
    ON ingestion_events(user_id);

-- Index for querying events by source type
CREATE INDEX IF NOT EXISTS idx_ingestion_events_source_type 
    ON ingestion_events(source_type);

-- Index for querying events by creation time
CREATE INDEX IF NOT EXISTS idx_ingestion_events_created_at 
    ON ingestion_events(created_at DESC);

-- Index for JSON path queries on raw_payload
CREATE INDEX IF NOT EXISTS idx_ingestion_events_payload 
    ON ingestion_events USING GIN (raw_payload);

-- ============================================================================
-- SAMPLE DATA (for development/testing)
-- ============================================================================

-- Insert a default test user
INSERT INTO users (user_id, username, password_hash, email)
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'testuser',
    -- bcrypt hash of 'password123'
    '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy',
    'testuser@example.com'
) ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- GRANTS (for application user)
-- ============================================================================

-- Note: In production, create a separate app user with limited permissions
-- GRANT SELECT, INSERT ON ingestion_events TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON users TO app_user;
