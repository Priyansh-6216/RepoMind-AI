-- IVFFlat index for fast similarity search using pgvector
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON code_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
