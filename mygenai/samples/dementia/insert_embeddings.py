"""Inserts the embeddings to the database."""

import time

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.rag_mgr as rag_mgr
import mygenai.samples.dementia.settings as settings


def insert_embeddings(max_length=2000):
    """Inserts the chunks to the database.

    :param max_length: The number of chunks to calculate embeddings for.
    """
    common.init_settings()
    conn_str = common.make_local_connection_string(settings.DBNAME)
    dbutil.SimpleSQL.register_connection_string(conn_str)
    ragger = rag_mgr.RagManager(settings.RAG_COLLECTION_NAME)
    with dbutil.SimpleSQL() as db:
        inserted = ragger.insert_embeddings_to_db(
            db, max_count=max_length, verbose=True
        )
    return inserted


if __name__ == '__main__':
    total_counter = 0
    while True:
        insert_count = insert_embeddings()
        total_counter += insert_count
        if insert_count == 0:
            print(f"done inserting: {total_counter} embeddings.")
            break
        time.sleep(30)
