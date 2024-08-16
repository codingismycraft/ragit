"""Creates the vector db for the dummy database."""

import os

import mygenai.libs.common as common
import mygenai.libs.chunks_mgr as chunks_mgr
import mygenai.libs.dbutil as dbutil
import mygenai.libs.vector_db as vector_db
import mygenai.samples.dementia.settings as settings


def create_vector_db(fullpath_to_db, collection_name, max_count=10):
    """Creates the vector db using all the documents in the testing directory.

    * Will use the database that is already initialized from the caller.
    * Read the embeddings from the psql database and save then to the vector db.

    :param str fullpath_to_db: The full path to the database file to create.
    :param str collection_name: The name of the collection to create.
    :param int | None max_count: The maximum number of embeddings to save.
    """
    vdb = vector_db.VectorDb(fullpath_to_db, collection_name)
    with dbutil.SimpleSQL() as db:
        chunks = []
        embeddings = []

        for chunk_id in chunks_mgr.find_chunks_with_embeddings(db):
            print(chunk_id, len(embeddings))
            chunk, embedding = chunks_mgr.load_embeddings(db, chunk_id)
            chunks.append(chunk)
            embeddings.append(embedding)
            if max_count is not None and len(embeddings) >= max_count:
                break

            if len(embeddings) > 2000:
                vdb.insert(chunks, embeddings)
                chunks = []
                embeddings = []

        if len(embeddings):
            vdb.insert(chunks, embeddings)

if __name__ == '__main__':
    # Initialize the environment.
    common.init_settings()
    conn_str = common.make_local_connection_string(settings.DBNAME)
    dbutil.SimpleSQL.register_connection_string(conn_str)

    # Create the filepath and the collection name for the vectordb.
    folder_path = common.get_testing_output_dir("dementia", wipe_out=True)
    fullpath_to_db = os.path.join(folder_path, "dementia.db")
    collection_name = "chunks"

    create_vector_db(fullpath_to_db, collection_name, max_count=None)
