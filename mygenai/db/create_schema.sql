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


CREATE TABLE user_msg
{
    user_msg_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4()
    user_id             INTEGER,
    received_at         TIMESTAMP,
    message             TEXT NOT NULL,
    response            TEXT DEFAULT NULL,
    responded_at        TIMESTAMP DEFAULT NULL,
    thumps_up           BOOL DEFAULT NULL,
    thumped_up_at       TIMESTAMP DEFAULT NULL
};

CREATE INDEX idx_user_msg_by_user ON user_msg (user_id);
