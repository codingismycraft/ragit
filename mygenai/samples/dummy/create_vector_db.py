import os

import mygenai.libs.common as common
import mygenai.libs.chunks_mgr as chunks_mgr
import mygenai.libs.dbutil as dbutil
import mygenai.libs.vector_db as vector_db

_DB_NAME = "dummy"
_SQL_CLEAR_CHUNKS = "DElETE FROM chunks"


def create_vector_db(fullpath_to_db, collection_name):
    """Creates the vector db using all the documents in the testing directory.

    Will discover all the docuement in the testing directory, create and
    save its chunks to the database and then insert all the related embeddings;
    after this it will build the vector database that will be used to
    query the vector db.

    :param str fullpath_to_db: The full path to the database file to create.
    :param str collection_name: The name of the collection to create.
    """
    with dbutil.SimpleSQL() as db:
        db.execute_non_query(_SQL_CLEAR_CHUNKS)
        directory = common.get_testing_data_directory()
        chunks_mgr.insert_chunks_to_db(db, directory, verbose=True)
        chunks_mgr.insert_embeddings_to_db(db, verbose=True)

        vdb = vector_db.VectorDb(fullpath_to_db, collection_name)

        chunks = []
        embeddings = []
        for chunk_id in chunks_mgr.find_chunks_with_embeddings(db):
            chunk, embedding = chunks_mgr.load_embeddings(db, chunk_id)
            chunks.append(chunk)
            embeddings.append(embedding)

        vdb.insert(chunks, embeddings)


def load_and_query_vector_db(fullpath_to_db, collection_name):
    """Loads and queries the dummy vector database.

    :param str fullpath_to_db: The full path to the database file to query.
    :param str collection_name: The name of the collection to query.
    """
    vdb = vector_db.VectorDb(fullpath_to_db, collection_name)
    result = vdb.query("Why sqlalchemy is bad?", k=2)
    for row in result:
        print(row)
        print("===================")

    result = vdb.query("Why patents are bad?", k=2)
    for row in result:
        print(row)
        print("===================")

    print("*********************************************")
    result = vdb.query("what is method chaining?", k=2)
    for row in result:
        print(row)
        print("===================")


if __name__ == '__main__':
    # Initialize the environment.
    common.init_settings()
    conn_str = common.make_local_connection_string(_DB_NAME)
    dbutil.SimpleSQL.register_connection_string(conn_str)

    # Create the filepath and the collection name for the vectordb.
    folder_path = common.get_testing_output_dir("dummy-app", wipe_out=True)
    fullpath_to_db = os.path.join(folder_path, "dummy.db")
    collection_name = "dummy"

    create_vector_db(fullpath_to_db, collection_name)
    load_and_query_vector_db(fullpath_to_db, collection_name)
