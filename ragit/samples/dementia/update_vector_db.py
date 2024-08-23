"""Creates the vector db for the dummy database."""

import ragit.libs.common as common
import ragit.libs.dbutil as dbutil
import ragit.libs.rag_mgr as rag_mgr
import ragit.samples.dementia.settings as settings


def update_vector_db():
    """Updates the vector db with pending chunks."""
    common.init_settings()
    conn_str = common.make_local_connection_string(settings.DBNAME)
    dbutil.SimpleSQL.register_connection_string(conn_str)

    ragger = rag_mgr.RagManager(settings.RAG_COLLECTION_NAME)
    with dbutil.SimpleSQL() as db:
        ragger.update_vector_db(db, verbose=True)


if __name__ == '__main__':
    update_vector_db()
