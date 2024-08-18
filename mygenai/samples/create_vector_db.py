"""Builds a vector db for any given directory."""

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.rag_mgr as rag_mgr


def main(name):
    """Builds the vector db for any given directory.

    :param str name: the name of the database.
    """
    common.init_settings()
    conn_str = common.make_local_connection_string(name)
    dbutil.SimpleSQL.register_connection_string(conn_str)
    ragger = rag_mgr.RagManager(name)

    with dbutil.SimpleSQL() as db:
        count = ragger.insert_chunks_to_db(db, verbose=True)
        print(f"Inserted {count} chunks.")

        count = ragger.insert_embeddings_to_db(db, verbose=True)
        print(f"Inserted {count} embeddings.")

        count = ragger.update_vector_db(db, verbose=True)
        print(f"Inserted {count} chunks to the vector db.")


if __name__ == '__main__':
    main("<enter collection -name> ")
