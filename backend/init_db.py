import asyncio
import asyncpg
import os
from loguru import logger


async def initialize_database():
    """Initialize database with required tables"""
    
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres.oktgigejkejrlvhdoaeq:vikrantan53168@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")
    
    # Remove postgresql+asyncpg:// if present
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        conn = await asyncpg.connect(database_url)
        logger.info("Connected to database")
        
        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)
        logger.info("✓ Users table created/verified")
        
        # Create user_planner_status table if not exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_planner_status (
                user_id VARCHAR(255) PRIMARY KEY,
                has_used_free_planner BOOLEAN DEFAULT FALSE,
                total_planners_created INT DEFAULT 0,
                is_premium BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        logger.info("✓ User planner status table created/verified")
        
        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_user_planner_status_user_id ON user_planner_status(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_planner_status_is_premium ON user_planner_status(is_premium);
        """)
        logger.info("✓ Indexes created/verified")
        
        # Create trip_plan table if not exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trip_plan (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                destination VARCHAR(255) NOT NULL,
                starting_location VARCHAR(255),
                travel_dates_start VARCHAR(100),
                travel_dates_end VARCHAR(100),
                date_input_type VARCHAR(50) DEFAULT 'picker',
                duration INT,
                traveling_with VARCHAR(100),
                adults INT DEFAULT 1,
                children INT DEFAULT 0,
                age_groups TEXT[],
                budget DECIMAL(10,2),
                budget_currency VARCHAR(10) DEFAULT 'USD',
                travel_style VARCHAR(100),
                budget_flexible BOOLEAN DEFAULT FALSE,
                vibes TEXT[],
                priorities TEXT[],
                interests TEXT,
                rooms INT DEFAULT 1,
                pace INT[],
                been_there_before TEXT,
                loved_places TEXT,
                additional_info TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                user_id VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        logger.info("✓ Trip plan table created/verified")
        
        # Create trip_plan_status table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trip_plan_status (
                id VARCHAR(255) PRIMARY KEY,
                trip_plan_id VARCHAR(255) UNIQUE NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                current_step VARCHAR(255),
                error TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (trip_plan_id) REFERENCES trip_plan(id) ON DELETE CASCADE
            )
        """)
        logger.info("✓ Trip plan status table created/verified")
        
        # Create trip_plan_output table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trip_plan_output (
                id VARCHAR(255) PRIMARY KEY,
                trip_plan_id VARCHAR(255) UNIQUE NOT NULL,
                itinerary TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (trip_plan_id) REFERENCES trip_plan(id) ON DELETE CASCADE
            )
        """)
        logger.info("✓ Trip plan output table created/verified")
        
        # Create payment_transactions table if not exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS payment_transactions (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                razorpay_order_id VARCHAR(255) UNIQUE NOT NULL,
                razorpay_payment_id VARCHAR(255),
                razorpay_signature VARCHAR(255),
                amount INT NOT NULL,
                currency VARCHAR(10) DEFAULT 'INR',
                plan_type VARCHAR(50),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES user_planner_status(user_id)
            )
        """)
        logger.info("✓ Payment transactions table created/verified")
        
        # Create plan_task_status enum if not exists
        await conn.execute("""
            DO $$ BEGIN
                CREATE TYPE plan_task_status AS ENUM ('queued', 'in_progress', 'success', 'error');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        # Create plan_tasks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS plan_tasks (
                id SERIAL PRIMARY KEY,
                trip_plan_id VARCHAR(255) NOT NULL,
                task_type VARCHAR(100) NOT NULL,
                status plan_task_status DEFAULT 'queued',
                input_data JSONB,
                output_data JSONB,
                error_message TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        logger.info("✓ Plan tasks table created/verified")
        
        # Create trip_history table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trip_history (
                id VARCHAR(255) PRIMARY KEY,
                destination VARCHAR(500) NOT NULL,
                start_date VARCHAR(100),
                end_date VARCHAR(100),
                duration INT NOT NULL,
                budget DECIMAL(10,2),
                budget_currency VARCHAR(10) DEFAULT 'USD',
                travelers INT DEFAULT 1,
                trip_plan_id VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        logger.info("✓ Trip history table created/verified")



        # Add user_id column to trip_plan if not exists (handle camelCase vs snake_case)
        await conn.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'trip_plan' AND column_name = 'user_id'
                ) THEN
                    ALTER TABLE trip_plan ADD COLUMN user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE;
                END IF;
            END $$;
        """)
        logger.info("✓ user_id column added to trip_plan")
        
        # Create additional indexes (use simple CREATE INDEX, ignore errors if exists)
        try:
            await conn.execute("CREATE INDEX idx_trip_plan_user_id ON trip_plan(user_id)")
        except:
            pass
        
        try:
            await conn.execute('CREATE INDEX idx_trip_plan_userid ON trip_plan("userId")')
        except:
            pass
            
        logger.info("✓ All indexes created/verified")
        
        await conn.close()
        logger.info("✅ Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(initialize_database())
