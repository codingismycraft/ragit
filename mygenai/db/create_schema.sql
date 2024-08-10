CREATE TABLE chunks
(
    scan_id       SERIAL PRIMARY KEY,
    location      VARCHAR(255),
    chunk         TEXT NOT NULL,
    embeddings    jsonb default NULL,
    metadata      jsonb default NULL
);
