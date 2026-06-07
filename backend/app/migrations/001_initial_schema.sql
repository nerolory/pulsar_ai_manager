-- Initial schema migration
-- Version: 1
-- Description: Create initial database schema for chats, messages, model_cache, and model_groups

-- Create chats table
CREATE TABLE IF NOT EXISTS chats (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    sort_order INTEGER DEFAULT 0
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    chat_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    model TEXT,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_chat_created ON messages(chat_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chats_updated ON chats(updated_at DESC);

-- Create model_cache table for caching provider models
CREATE TABLE IF NOT EXISTS model_cache (
    provider TEXT NOT NULL,
    model_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    context_length INTEGER DEFAULT 4096,
    pricing TEXT,
    free_tier BOOLEAN DEFAULT 0,
    daily_limit INTEGER,
    limit_tokens INTEGER,
    balance REAL,
    is_free BOOLEAN DEFAULT 0,
    cached_at INTEGER NOT NULL,
    PRIMARY KEY (provider, model_id)
);

CREATE INDEX IF NOT EXISTS idx_model_cache_provider ON model_cache(provider, cached_at DESC);

-- Create model_groups table for grouping free/paid versions
CREATE TABLE IF NOT EXISTS model_groups (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);
