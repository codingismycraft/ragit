CREATE TABLE chunks
(
    scan_id       SERIAL PRIMARY KEY,
    fullpath      VARCHAR(255) NOT NULL,
    chunk_index   INTEGER NOT NULL,
    chunk         TEXT NOT NULL,
    embeddings    jsonb default NULL,
    metadata      jsonb default NULL,
    UNIQUE (fullpath, chunk_index)
);
