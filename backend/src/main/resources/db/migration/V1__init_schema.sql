-- ══════════════════════════════════════════════════════════════
--  RepoMind AI — Database Schema
--  PostgreSQL 16 + pgvector
-- ══════════════════════════════════════════════════════════════

-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ──────────────────────────────────────────────
-- Repositories
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS repositories (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url             TEXT NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    owner           VARCHAR(255) NOT NULL,
    default_branch  VARCHAR(100) DEFAULT 'main',
    description     TEXT,
    language        VARCHAR(50),
    status          VARCHAR(20) DEFAULT 'PENDING',
    file_count      INT DEFAULT 0,
    chunk_count     INT DEFAULT 0,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE repositories IS 'Tracked GitHub repositories';
COMMENT ON COLUMN repositories.status IS 'PENDING | INDEXING | READY | FAILED';

-- ──────────────────────────────────────────────
-- Index Jobs
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS index_jobs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    status          VARCHAR(20) DEFAULT 'QUEUED',
    progress        INT DEFAULT 0,
    total_files     INT DEFAULT 0,
    processed_files INT DEFAULT 0,
    error_message   TEXT,
    started_at      TIMESTAMP WITH TIME ZONE,
    completed_at    TIMESTAMP WITH TIME ZONE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE index_jobs IS 'Repository indexing pipeline jobs';
COMMENT ON COLUMN index_jobs.status IS 'QUEUED | CLONING | PARSING | EMBEDDING | COMPLETED | FAILED';

CREATE INDEX idx_jobs_repo ON index_jobs(repository_id);
CREATE INDEX idx_jobs_status ON index_jobs(status);

-- ──────────────────────────────────────────────
-- Code Files
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS code_files (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    file_path       TEXT NOT NULL,
    language        VARCHAR(50),
    size_bytes      INT,
    content         TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE code_files IS 'Individual source files from cloned repositories';

CREATE INDEX idx_files_repo ON code_files(repository_id);
CREATE INDEX idx_files_lang ON code_files(language);

-- ──────────────────────────────────────────────
-- Code Chunks (with vector embedding)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS code_chunks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id         UUID NOT NULL REFERENCES code_files(id) ON DELETE CASCADE,
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    chunk_type      VARCHAR(20) NOT NULL,
    name            VARCHAR(500),
    content         TEXT NOT NULL,
    start_line      INT,
    end_line         INT,
    embedding       vector(768),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE code_chunks IS 'Semantic code chunks with vector embeddings for RAG retrieval';
COMMENT ON COLUMN code_chunks.chunk_type IS 'FUNCTION | CLASS | METHOD | MODULE | BLOCK';
COMMENT ON COLUMN code_chunks.embedding IS '768-dim vector from nomic-embed-text via Ollama';

CREATE INDEX idx_chunks_repo ON code_chunks(repository_id);
CREATE INDEX idx_chunks_file ON code_chunks(file_id);
CREATE INDEX idx_chunks_type ON code_chunks(chunk_type);

-- IVFFlat index for fast similarity search
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ──────────────────────────────────────────────
-- Chat Sessions
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chat_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id   UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    title           VARCHAR(255),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE chat_sessions IS 'User conversation sessions scoped to a repository';

CREATE INDEX idx_sessions_repo ON chat_sessions(repository_id);

-- ──────────────────────────────────────────────
-- Chat Messages
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chat_messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id      UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role            VARCHAR(10) NOT NULL,
    content         TEXT NOT NULL,
    citations       JSONB DEFAULT '[]',
    token_count     INT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE chat_messages IS 'Individual messages within a chat session';
COMMENT ON COLUMN chat_messages.role IS 'USER | ASSISTANT';
COMMENT ON COLUMN chat_messages.citations IS 'Array of {file_path, chunk_id, start_line, end_line, relevance_score, snippet}';

CREATE INDEX idx_messages_session ON chat_messages(session_id);
CREATE INDEX idx_messages_role ON chat_messages(role);
