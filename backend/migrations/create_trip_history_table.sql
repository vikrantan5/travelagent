-- Create trip_history table
CREATE TABLE IF NOT EXISTS trip_history (
    id VARCHAR(255) PRIMARY KEY,
    destination VARCHAR(500) NOT NULL,
    start_date VARCHAR(100),
    end_date VARCHAR(100),
    duration INTEGER NOT NULL,
    budget DECIMAL(10, 2),
    budget_currency VARCHAR(10) DEFAULT 'USD',
    travelers INTEGER DEFAULT 1,
    trip_plan_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Index for faster queries
    INDEX idx_created_at (created_at DESC),
    INDEX idx_trip_plan_id (trip_plan_id)
);

-- Add comment
COMMENT ON TABLE trip_history IS 'Stores user trip history for past trips';
