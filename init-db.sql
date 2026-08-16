-- PostgreSQL initialization script for NaMo ACC Bot
-- Creates tables for session persistence

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Session table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    telegram_user_id BIGINT NOT NULL,
    relationship_stage INTEGER DEFAULT 1 CHECK (relationship_stage >= 1 AND relationship_stage <= 4),
    stage_progress VARCHAR(50) DEFAULT '0/25',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Emotion state table
CREATE TABLE IF NOT EXISTS emotion_states (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    arousal DECIMAL(3,2) DEFAULT 0.2 CHECK (arousal >= 0 AND arousal <= 1),
    trust DECIMAL(3,2) DEFAULT 0.4 CHECK (trust >= 0 AND trust <= 1),
    passion DECIMAL(3,2) DEFAULT 0.1 CHECK (passion >= 0 AND passion <= 1),
    temperament DECIMAL(3,2) DEFAULT 0.7 CHECK (temperament >= 0 AND temperament <= 1),
    resonance DECIMAL(3,2) DEFAULT 0.3 CHECK (resonance >= 0 AND resonance <= 1),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat history table
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    emotion_delta JSONB,
    relationship_stage INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Backup table for archival
CREATE TABLE IF NOT EXISTS session_backups (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    session_data JSONB NOT NULL,
    backup_reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_sessions_telegram_user_id ON sessions(telegram_user_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_updated_at ON sessions(updated_at);
CREATE INDEX idx_emotion_states_session_id ON emotion_states(session_id);
CREATE INDEX idx_emotion_states_recorded_at ON emotion_states(recorded_at);
CREATE INDEX idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);
CREATE INDEX idx_session_backups_session_id ON session_backups(session_id);
CREATE INDEX idx_session_backups_created_at ON session_backups(created_at);

-- Create update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for session summary
CREATE OR REPLACE VIEW session_summary AS
SELECT 
    s.session_id,
    s.telegram_user_id,
    s.relationship_stage,
    s.stage_progress,
    COUNT(ch.id) as total_messages,
    MAX(ch.created_at) as last_message,
    e.arousal,
    e.trust,
    e.passion,
    e.temperament,
    e.resonance
FROM sessions s
LEFT JOIN chat_history ch ON s.session_id = ch.session_id
LEFT JOIN emotion_states e ON s.session_id = e.session_id 
    AND e.recorded_at = (SELECT MAX(recorded_at) FROM emotion_states WHERE session_id = s.session_id)
GROUP BY s.id, s.session_id, s.telegram_user_id, s.relationship_stage, s.stage_progress,
         e.arousal, e.trust, e.passion, e.temperament, e.resonance;

-- Grant permissions
GRANT CONNECT ON DATABASE namo_sessions TO cognitive;
GRANT USAGE ON SCHEMA public TO cognitive;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cognitive;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cognitive;

-- Add comments
COMMENT ON TABLE sessions IS 'Stores user session information for ACC bot';
COMMENT ON TABLE emotion_states IS 'Tracks 5D emotion progression for each session';
COMMENT ON TABLE chat_history IS 'Stores conversation history between user and Vipha';
COMMENT ON TABLE session_backups IS 'Stores backups of session data for recovery';
