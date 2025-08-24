-- Database initialization script for AI Mood Diary Bot
-- This script sets up the initial database structure and configuration

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create application user (if not exists)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'mood_app') THEN
      
      CREATE ROLE mood_app LOGIN PASSWORD 'app_password';
   END IF;
END
$do$;

-- Grant necessary permissions
GRANT CONNECT ON DATABASE mood_diary TO mood_app;
GRANT USAGE ON SCHEMA public TO mood_app;
GRANT CREATE ON SCHEMA public TO mood_app;

-- Create indexes for better performance (these will be created by SQLAlchemy migrations)
-- But we can prepare some basic settings

-- Set timezone
SET timezone = 'UTC';

-- Configure logging
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_duration = on;
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Performance settings for production
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();

-- Create a function for automatic updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a cleanup function for old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Example: Delete AI analyses older than 1 year
    -- DELETE FROM ai_analysis WHERE created_at < NOW() - INTERVAL '1 year';
    
    -- Example: Archive old mood entries (older than 2 years)
    -- This would move data to an archive table instead of deleting
    
    RAISE NOTICE 'Cleanup completed';
END;
$$ LANGUAGE plpgsql;

-- Create initial admin user function
CREATE OR REPLACE FUNCTION create_admin_user(
    p_telegram_id BIGINT,
    p_username TEXT,
    p_first_name TEXT DEFAULT NULL,
    p_last_name TEXT DEFAULT NULL
)
RETURNS void AS $$
BEGIN
    -- This function will be called by the application
    -- to create initial admin users
    RAISE NOTICE 'Admin user creation function ready';
END;
$$ LANGUAGE plpgsql;

-- Database health check function
CREATE OR REPLACE FUNCTION db_health_check()
RETURNS TABLE(
    metric TEXT,
    value TEXT,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'Database Size'::TEXT,
        pg_size_pretty(pg_database_size(current_database()))::TEXT,
        'OK'::TEXT
    UNION ALL
    SELECT 
        'Active Connections'::TEXT,
        (SELECT count(*)::TEXT FROM pg_stat_activity WHERE state = 'active'),
        CASE 
            WHEN (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') < 50 
            THEN 'OK'::TEXT 
            ELSE 'WARNING'::TEXT 
        END
    UNION ALL
    SELECT 
        'Last Backup'::TEXT,
        COALESCE(
            (SELECT created_at::TEXT FROM information_schema.tables WHERE table_name = 'backup_log' LIMIT 1),
            'No backup recorded'::TEXT
        ),
        'INFO'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Create backup log table
CREATE TABLE IF NOT EXISTS backup_log (
    id SERIAL PRIMARY KEY,
    backup_type VARCHAR(50) NOT NULL,
    backup_size BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'completed'
);

-- Insert initial backup log entry
INSERT INTO backup_log (backup_type, backup_size, status) 
VALUES ('initial', 0, 'completed');

COMMIT;