-- PostgreSQL initialization script for PlaybookWiz
-- This script runs when the PostgreSQL container starts for the first time

-- Create additional databases if needed
-- CREATE DATABASE playbookwiz_test;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create indexes for better performance
-- These will be created by Alembic migrations, but we can prepare the database

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE playbookwiz TO playbookwiz;

-- Create a health check function
CREATE OR REPLACE FUNCTION health_check()
RETURNS TABLE(status text, timestamp timestamptz) AS $$
BEGIN
    RETURN QUERY SELECT 'healthy'::text, now();
END;
$$ LANGUAGE plpgsql;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'PlaybookWiz PostgreSQL database initialized successfully';
END $$;
