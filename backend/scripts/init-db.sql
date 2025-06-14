-- Initialize PostgreSQL database for Face Aesthetic AI (Development only)
-- Production uses Supabase

-- Create database if not exists
CREATE DATABASE face_aesthetic_dev;

-- Connect to the database
\c face_aesthetic_dev;

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    profile_image_url TEXT,
    preferences JSONB DEFAULT '{}',
    subscription_tier VARCHAR(50) DEFAULT 'free',
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Create analysis_results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    image_url TEXT NOT NULL,
    image_filename VARCHAR(255) NOT NULL,
    analysis_type VARCHAR(50) DEFAULT 'full',
    overall_score JSONB NOT NULL,
    face_angle JSONB NOT NULL,
    face_contour JSONB NOT NULL,
    eline_analysis JSONB NOT NULL,
    proportions_analysis JSONB NOT NULL,
    philtrum_chin_analysis JSONB NOT NULL,
    nasolabial_angle_analysis JSONB NOT NULL,
    vline_analysis JSONB NOT NULL,
    symmetry_analysis JSONB NOT NULL,
    dental_protrusion_analysis JSONB NOT NULL,
    facial_harmony JSONB NOT NULL,
    beauty_advice TEXT[] DEFAULT '{}',
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_public BOOLEAN DEFAULT FALSE,
    report_image_url TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    context_type VARCHAR(50) DEFAULT 'general',
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    message_count INTEGER DEFAULT 0,
    conversation_context JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    analysis_reference UUID REFERENCES analysis_results(id) ON DELETE SET NULL,
    model_used VARCHAR(100),
    tokens_used INTEGER,
    response_time_ms INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_usage table
CREATE TABLE IF NOT EXISTS user_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    analysis_count INTEGER DEFAULT 0,
    chat_message_count INTEGER DEFAULT 0,
    storage_used_mb DECIMAL(10,2) DEFAULT 0.0,
    last_analysis_at TIMESTAMP WITH TIME ZONE,
    subscription_start_date TIMESTAMP WITH TIME ZONE,
    subscription_end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create line_bot_users table
CREATE TABLE IF NOT EXISTS line_bot_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    line_user_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    display_name VARCHAR(255),
    picture_url TEXT,
    status_message TEXT,
    language VARCHAR(10) DEFAULT 'ja',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_interaction_at TIMESTAMP WITH TIME ZONE
);

-- Create analysis_feedback table
CREATE TABLE IF NOT EXISTS analysis_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    feedback_type VARCHAR(50) DEFAULT 'general',
    is_helpful BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

CREATE INDEX IF NOT EXISTS idx_analysis_results_user_id ON analysis_results(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_type ON analysis_results(analysis_type);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_analysis_id ON chat_sessions(analysis_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role);

CREATE INDEX IF NOT EXISTS idx_user_usage_user_id ON user_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_user_usage_last_analysis_at ON user_usage(last_analysis_at);

CREATE INDEX IF NOT EXISTS idx_line_bot_users_line_user_id ON line_bot_users(line_user_id);
CREATE INDEX IF NOT EXISTS idx_line_bot_users_user_id ON line_bot_users(user_id);
CREATE INDEX IF NOT EXISTS idx_line_bot_users_created_at ON line_bot_users(created_at);

CREATE INDEX IF NOT EXISTS idx_analysis_feedback_analysis_id ON analysis_feedback(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_feedback_user_id ON analysis_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_feedback_rating ON analysis_feedback(rating);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_results_updated_at BEFORE UPDATE ON analysis_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_usage_updated_at BEFORE UPDATE ON user_usage
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_line_bot_users_updated_at BEFORE UPDATE ON line_bot_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for development
INSERT INTO users (id, email, full_name, subscription_tier) VALUES
    (uuid_generate_v4(), 'demo@example.com', 'Demo User', 'premium'),
    (uuid_generate_v4(), 'test@example.com', 'Test User', 'free')
ON CONFLICT (email) DO NOTHING;

-- Create a function to clean up old data (for development)
CREATE OR REPLACE FUNCTION cleanup_old_data(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete old analysis results
    DELETE FROM analysis_results 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Delete old chat sessions
    DELETE FROM chat_sessions 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_old;
    
    -- Delete old chat messages (orphaned)
    DELETE FROM chat_messages 
    WHERE session_id NOT IN (SELECT id FROM chat_sessions);
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Create a read-only user for analytics (optional)
-- CREATE USER analytics_reader WITH PASSWORD 'analytics_password';
-- GRANT CONNECT ON DATABASE face_aesthetic_dev TO analytics_reader;
-- GRANT USAGE ON SCHEMA public TO analytics_reader;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_reader;

COMMIT;