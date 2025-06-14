"""Supabase database schema definitions and SQL migrations."""

# Supabase Database Schema for Face Aesthetic App
# Run these SQL commands in your Supabase SQL Editor

SUPABASE_SCHEMA_SQL = """
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ========================================
-- USERS TABLE (extends auth.users)
-- ========================================
-- Supabase Auth automatically provides auth.users table
-- We extend it with a profiles table for additional user data

CREATE TABLE public.user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    full_name TEXT NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    date_of_birth DATE,
    gender TEXT CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
    location TEXT,
    preferences JSONB DEFAULT '{}',
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium', 'pro')),
    analysis_count INTEGER DEFAULT 0,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- ANALYSIS RESULTS TABLE
-- ========================================
CREATE TABLE public.analysis_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    
    -- Image information
    original_image_url TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    image_size_bytes INTEGER NOT NULL,
    image_mime_type TEXT NOT NULL,
    image_dimensions TEXT, -- "WIDTHxHEIGHT"
    
    -- Analysis metadata
    analysis_type TEXT DEFAULT 'full',
    processing_time_seconds REAL,
    user_notes TEXT,
    
    -- Analysis results (JSON structure matching our Pydantic models)
    face_angle JSONB NOT NULL,
    face_contour JSONB NOT NULL,
    eline_analysis JSONB NOT NULL,
    face_proportions JSONB NOT NULL,
    philtrum_chin_ratio JSONB NOT NULL,
    nasolabial_angle JSONB NOT NULL,
    vline_analysis JSONB NOT NULL,
    symmetry_analysis JSONB NOT NULL,
    dental_protrusion JSONB NOT NULL,
    facial_harmony JSONB NOT NULL,
    overall_score JSONB NOT NULL,
    beauty_advice JSONB NOT NULL, -- Array of strings
    
    -- Generated content
    report_image_url TEXT, -- URL to generated visual report
    report_generated BOOLEAN DEFAULT false,
    
    -- Analysis quality indicators
    face_detection_confidence REAL,
    analysis_warnings JSONB DEFAULT '[]',
    angle_warning TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- CHAT SESSIONS TABLE
-- ========================================
CREATE TABLE public.chat_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    
    -- Session metadata
    title TEXT NOT NULL,
    context_type TEXT DEFAULT 'general' CHECK (context_type IN ('general', 'analysis_review', 'beauty_advice', 'improvement_plan')),
    analysis_id UUID REFERENCES public.analysis_results(id) ON DELETE SET NULL,
    
    -- Session state
    is_active BOOLEAN DEFAULT true,
    message_count INTEGER DEFAULT 0,
    
    -- Session data
    metadata JSONB DEFAULT '{}',
    conversation_context JSONB DEFAULT '{}', -- User preferences, goals, etc.
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- CHAT MESSAGES TABLE
-- ========================================
CREATE TABLE public.chat_messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.chat_sessions(id) ON DELETE CASCADE NOT NULL,
    
    -- Message content
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    
    -- Message metadata
    metadata JSONB DEFAULT '{}',
    analysis_reference UUID REFERENCES public.analysis_results(id) ON DELETE SET NULL,
    
    -- AI response data (for assistant messages)
    model_used TEXT, -- e.g., "gpt-4o-mini"
    tokens_used INTEGER,
    response_time_ms INTEGER,
    
    -- Message classification
    message_type TEXT DEFAULT 'text' CHECK (message_type IN ('text', 'analysis_summary', 'advice', 'suggestion')),
    sentiment_score REAL, -- Optional sentiment analysis
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- IMAGE STORAGE METADATA TABLE
-- ========================================
CREATE TABLE public.stored_images (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    
    -- File information
    original_filename TEXT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE, -- Path in Supabase Storage
    storage_bucket TEXT DEFAULT 'user-images',
    file_size_bytes INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    
    -- Image metadata
    width INTEGER,
    height INTEGER,
    image_hash TEXT, -- For duplicate detection
    
    -- Usage tracking
    image_type TEXT DEFAULT 'analysis' CHECK (image_type IN ('analysis', 'report', 'avatar')),
    used_in_analysis UUID REFERENCES public.analysis_results(id) ON DELETE SET NULL,
    
    -- Lifecycle management
    is_temporary BOOLEAN DEFAULT false,
    expires_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- USER ANALYTICS TABLE
-- ========================================
CREATE TABLE public.user_analytics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    
    -- Analytics data
    total_analyses INTEGER DEFAULT 0,
    total_chat_sessions INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    
    -- Score tracking
    average_beauty_score REAL,
    highest_beauty_score REAL,
    latest_beauty_score REAL,
    score_trend JSONB DEFAULT '[]', -- Array of {date, score} objects
    
    -- Feature usage
    most_analyzed_features JSONB DEFAULT '[]',
    improvement_areas JSONB DEFAULT '[]',
    
    -- Engagement metrics
    last_analysis_date TIMESTAMPTZ,
    last_chat_date TIMESTAMPTZ,
    days_active INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- LINE BOT USERS TABLE (for LINE Bot integration)
-- ========================================
CREATE TABLE public.line_bot_users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    line_user_id TEXT NOT NULL UNIQUE,
    
    -- Link to main user account (optional)
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    -- LINE profile data
    display_name TEXT,
    picture_url TEXT,
    status_message TEXT,
    
    -- Bot interaction data
    total_messages INTEGER DEFAULT 0,
    total_analyses INTEGER DEFAULT 0,
    preferred_language TEXT DEFAULT 'ja',
    
    -- State management
    current_state TEXT DEFAULT 'idle', -- For conversation flow
    state_data JSONB DEFAULT '{}',
    
    -- Timestamps
    first_interaction TIMESTAMPTZ DEFAULT NOW(),
    last_interaction TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- User profiles indexes
CREATE INDEX idx_user_profiles_subscription_tier ON public.user_profiles(subscription_tier);
CREATE INDEX idx_user_profiles_created_at ON public.user_profiles(created_at);

-- Analysis results indexes
CREATE INDEX idx_analysis_results_user_id ON public.analysis_results(user_id);
CREATE INDEX idx_analysis_results_created_at ON public.analysis_results(created_at);
CREATE INDEX idx_analysis_results_overall_score ON public.analysis_results USING GIN (overall_score);
CREATE INDEX idx_analysis_results_face_angle ON public.analysis_results USING GIN (face_angle);

-- Chat sessions indexes
CREATE INDEX idx_chat_sessions_user_id ON public.chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_analysis_id ON public.chat_sessions(analysis_id);
CREATE INDEX idx_chat_sessions_context_type ON public.chat_sessions(context_type);
CREATE INDEX idx_chat_sessions_created_at ON public.chat_sessions(created_at);

-- Chat messages indexes
CREATE INDEX idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX idx_chat_messages_role ON public.chat_messages(role);
CREATE INDEX idx_chat_messages_created_at ON public.chat_messages(created_at);

-- Stored images indexes
CREATE INDEX idx_stored_images_user_id ON public.stored_images(user_id);
CREATE INDEX idx_stored_images_storage_path ON public.stored_images(storage_path);
CREATE INDEX idx_stored_images_image_type ON public.stored_images(image_type);
CREATE INDEX idx_stored_images_expires_at ON public.stored_images(expires_at) WHERE expires_at IS NOT NULL;

-- Line bot users indexes
CREATE INDEX idx_line_bot_users_line_user_id ON public.line_bot_users(line_user_id);
CREATE INDEX idx_line_bot_users_user_id ON public.line_bot_users(user_id) WHERE user_id IS NOT NULL;

-- ========================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ========================================

-- Enable RLS on all tables
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.stored_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.line_bot_users ENABLE ROW LEVEL SECURITY;

-- User profiles policies
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Analysis results policies
CREATE POLICY "Users can view own analysis results" ON public.analysis_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analysis results" ON public.analysis_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analysis results" ON public.analysis_results
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own analysis results" ON public.analysis_results
    FOR DELETE USING (auth.uid() = user_id);

-- Chat sessions policies
CREATE POLICY "Users can view own chat sessions" ON public.chat_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat sessions" ON public.chat_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own chat sessions" ON public.chat_sessions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own chat sessions" ON public.chat_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- Chat messages policies (access through session ownership)
CREATE POLICY "Users can view messages in own sessions" ON public.chat_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.chat_sessions 
            WHERE chat_sessions.id = chat_messages.session_id 
            AND chat_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert messages in own sessions" ON public.chat_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.chat_sessions 
            WHERE chat_sessions.id = chat_messages.session_id 
            AND chat_sessions.user_id = auth.uid()
        )
    );

-- Stored images policies
CREATE POLICY "Users can view own images" ON public.stored_images
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own images" ON public.stored_images
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own images" ON public.stored_images
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own images" ON public.stored_images
    FOR DELETE USING (auth.uid() = user_id);

-- User analytics policies
CREATE POLICY "Users can view own analytics" ON public.user_analytics
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage user analytics" ON public.user_analytics
    FOR ALL USING (auth.role() = 'service_role');

-- ========================================
-- FUNCTIONS AND TRIGGERS
-- ========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_results_updated_at BEFORE UPDATE ON public.analysis_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON public.chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stored_images_updated_at BEFORE UPDATE ON public.stored_images
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update message count in chat sessions
CREATE OR REPLACE FUNCTION update_chat_session_message_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE public.chat_sessions 
        SET message_count = message_count + 1,
            updated_at = NOW()
        WHERE id = NEW.session_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE public.chat_sessions 
        SET message_count = message_count - 1,
            updated_at = NOW()
        WHERE id = OLD.session_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Add message count trigger
CREATE TRIGGER update_chat_session_message_count_trigger
    AFTER INSERT OR DELETE ON public.chat_messages
    FOR EACH ROW EXECUTE FUNCTION update_chat_session_message_count();

-- Function to update user analytics
CREATE OR REPLACE FUNCTION update_user_analytics()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Update or insert user analytics
        INSERT INTO public.user_analytics (user_id, total_analyses, last_analysis_date)
        VALUES (NEW.user_id, 1, NEW.created_at)
        ON CONFLICT (user_id) DO UPDATE SET
            total_analyses = user_analytics.total_analyses + 1,
            last_analysis_date = NEW.created_at,
            updated_at = NOW();
            
        -- Update user profile analysis count
        UPDATE public.user_profiles 
        SET analysis_count = analysis_count + 1
        WHERE id = NEW.user_id;
        
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Add analytics update trigger
CREATE TRIGGER update_user_analytics_trigger
    AFTER INSERT ON public.analysis_results
    FOR EACH ROW EXECUTE FUNCTION update_user_analytics();

-- ========================================
-- STORAGE BUCKETS SETUP
-- ========================================
-- Run these commands in Supabase Dashboard > Storage

/*
1. Create buckets:
   - user-images (for uploaded face images)
   - report-images (for generated diagnostic reports)
   - avatars (for user profile pictures)

2. Set bucket policies for user-images:
   - Allow authenticated users to upload images
   - Allow users to view their own images
   - Restrict file size to 10MB
   - Allow only image types (jpeg, png, webp)

3. Set bucket policies for report-images:
   - Allow service role to upload generated reports
   - Allow users to view reports for their analyses

4. Set bucket policies for avatars:
   - Allow users to upload their own avatar
   - Make avatars publicly readable
*/

-- ========================================
-- SAMPLE DATA FOR TESTING
-- ========================================
-- Uncomment to insert sample data for development

/*
-- Insert a test user profile (after creating user in Supabase Auth)
INSERT INTO public.user_profiles (id, full_name, bio) VALUES 
('your-test-user-uuid', 'Test User', 'テストユーザーです');

-- Insert sample analysis result
INSERT INTO public.analysis_results (
    user_id, 
    original_image_url, 
    original_filename,
    image_size_bytes,
    image_mime_type,
    face_angle,
    face_contour,
    eline_analysis,
    face_proportions,
    philtrum_chin_ratio,
    nasolabial_angle,
    vline_analysis,
    symmetry_analysis,
    dental_protrusion,
    facial_harmony,
    overall_score,
    beauty_advice
) VALUES (
    'your-test-user-uuid',
    'https://example.com/test-image.jpg',
    'test-image.jpg',
    1024000,
    'image/jpeg',
    '{"angle": "正面", "confidence": 0.95}',
    '{"face_area": 15000}',
    '{"status": "理想的"}',
    '{"aspect_ratio": 1.618}',
    '{"ratio": 2.0}',
    '{"angle": 105}',
    '{"jaw_angle": 110}',
    '{"symmetry_score": 85}',
    '{"max_upper_protrusion": 2.0}',
    '{"harmony_score": 78}',
    '{"score": 82.5, "level": "美人レベル"}',
    '["理想的なEライン", "良好な対称性"]'
);
*/
"""

# Storage bucket configurations
STORAGE_BUCKETS_CONFIG = [
    {
        "name": "user-images",
        "public": False,
        "file_size_limit": 10 * 1024 * 1024,  # 10MB
        "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"],
    },
    {
        "name": "report-images", 
        "public": False,
        "file_size_limit": 5 * 1024 * 1024,  # 5MB
        "allowed_mime_types": ["image/jpeg", "image/png"],
    },
    {
        "name": "avatars",
        "public": True,
        "file_size_limit": 2 * 1024 * 1024,  # 2MB  
        "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"],
    }
]