-- Themis Database Initialization Script
-- PostgreSQL 16+

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create orchestrator state table
CREATE TABLE IF NOT EXISTS orchestrator_state (
    key TEXT PRIMARY KEY,
    memory JSONB NOT NULL DEFAULT '{}'::jsonb,
    plans JSONB NOT NULL DEFAULT '{}'::jsonb,
    executions JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_orchestrator_state_updated_at
    BEFORE UPDATE ON orchestrator_state
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_orchestrator_state_plans
    ON orchestrator_state USING GIN (plans);

CREATE INDEX IF NOT EXISTS idx_orchestrator_state_executions
    ON orchestrator_state USING GIN (executions);

-- Insert default singleton row
INSERT INTO orchestrator_state (key, memory, plans, executions)
VALUES ('singleton', '{}'::jsonb, '{}'::jsonb, '{}'::jsonb)
ON CONFLICT (key) DO NOTHING;

-- Grant permissions to themis user
GRANT ALL PRIVILEGES ON DATABASE themis TO themis;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO themis;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO themis;

-- Create audit log table (for future use)
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    user_id TEXT,
    ip_address INET,
    endpoint TEXT,
    method TEXT,
    status_code INTEGER,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp
    ON audit_log (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_event_type
    ON audit_log (event_type);

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Themis database initialized successfully!';
END $$;
