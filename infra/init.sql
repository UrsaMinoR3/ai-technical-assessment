-- Database initialization script
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW()
);
