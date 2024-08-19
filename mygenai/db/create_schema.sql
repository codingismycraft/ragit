CREATE TABLE chunks
(
    chunk_id      SERIAL PRIMARY KEY,
    fullpath      VARCHAR(255) NOT NULL,
    chunk_index   INTEGER      NOT NULL,
    chunk         TEXT         NOT NULL,
    embeddings    jsonb                 default NULL,
    metadata      jsonb                 default NULL,
    stored_in_vdb INTEGER      NOT NULL default 0,
    UNIQUE (fullpath, chunk_index)
);

CREATE INDEX idx_stored_in_vdb ON chunks (stored_in_vdb);


CREATE TABLE question
{
    question_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    asked_time timestamp,
    answered_time timestamp,
    stars INTEGER DEFAULT NULL,
    stared_time timestamp
};