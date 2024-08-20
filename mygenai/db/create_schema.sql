-- The db schema to store embeddings and keep queries.


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


CREATE TABLE query
(
    query_id            uuid PRIMARY KEY DEFAULT get_random_uuid(),
    user_id             uuid,    -- The user who made the query.
    received_at         TIMESTAMP, -- When the query was received
    question            TEXT NOT NULL, -- The question / message of the query
    response            TEXT DEFAULT NULL, -- The reponse retrieved from the LLM
    responded_at        TIMESTAMP DEFAULT NULL, -- The time the response was received
    thumps_up           BOOL DEFAULT NULL, -- NULL no user action, True / False thumps up/down.
    thumped_up_at       TIMESTAMP DEFAULT NULL --When it was thumped up/down
);

CREATE INDEX idx_query_by_user ON query (user_id);
