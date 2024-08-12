"""Inserts the embeddings to the database."""

import time

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.chunks_mgr as chunks_mgr
import mygenai.samples.dementia.settings as settings


def main(max_length=1000):
    """Inserts the chunks to the database.

    :param max_length: The number of chunks to calculate embeddings for.
    """
    conn_str = common.make_local_connection_string(settings.DBNAME)
    dbutil.SimpleSQL.register_connection_string(conn_str)

    counter = 0
    with dbutil.SimpleSQL() as db:
        for chunk_id in chunks_mgr.find_chunks_missing_embeddings(db):
            counter += 1
            if counter > max_length:
                break
            chunks_mgr.save_embeddings(db, chunk_id)
            print(counter, chunk_id)


if __name__ == '__main__':
    common.init_settings()
    c = 0
    while c < 50:
        main()
        time.sleep(60)
        c += 1
