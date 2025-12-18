-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    owner_name VARCHAR(255) NOT NULL
);

-- Repository metrics - frequently changing data
CREATE TABLE IF NOT EXISTS repository_metrics (
    id SERIAL PRIMARY KEY,
    repository_id TEXT REFERENCES repositories(id) ON DELETE CASCADE,
    stars_count INTEGER NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
