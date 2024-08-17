"""Inserts the chunks for new documents added to collection.

Assumes that we have a db named dementia available. If not you can
create one by running the mygenai/db/create_db.sh utility:

    cd mygenai/db
    ./create_db.sh dementia
"""

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.rag_mgr as rag_mgr
import mygenai.samples.dementia.settings as settings


def main():
    """Inserts the chunks to the database."""
    common.init_settings()
    conn_str = common.make_local_connection_string(settings.DBNAME)
    dbutil.SimpleSQL.register_connection_string(conn_str)

    ragger = rag_mgr.RagManager(settings.RAG_COLLECTION_NAME)

    with dbutil.SimpleSQL() as db:
        count = ragger.insert_chunks_to_db(db, verbose=True)
    print(f"Inserted {count} new chunks.")


if __name__ == '__main__':
    main()
