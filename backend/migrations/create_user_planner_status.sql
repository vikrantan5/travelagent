-- Create user_planner_status table for payment tracking
CREATE TABLE IF NOT EXISTS user_planner_status (
    user_id VARCHAR(255) PRIMARY KEY,
    has_used_free_planner BOOLEAN DEFAULT FALSE,
    total_planners_created INTEGER DEFAULT 0,
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on is_premium for faster queries
CREATE INDEX IF NOT EXISTS idx_user_planner_status_premium ON user_planner_status(is_premium);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_planner_status_user_id ON user_planner_status(user_id);
