"""Queries the dementia vector database."""

import os

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.vector_db as vector_db
import mygenai.samples.dementia.settings as settings


def query_vector_db(fullpath_to_db, collection_name):
    """Loads and queries the vector database.

    :param str fullpath_to_db: The full path to the database file to query.
    :param str collection_name: The name of the collection to query.
    """
    vdb = vector_db.VectorDb(fullpath_to_db, collection_name)
    query = "can support vector machines be used to predict dementia?"
    result = vdb.query(query, k=20)
    result = list(result)[0]
    for row in result:
        print(row["entity"]["text"])
        print("===================")


if __name__ == '__main__':
    common.init_settings()
    conn_str = common.make_local_connection_string(settings.DBNAME)
    dbutil.SimpleSQL.register_connection_string(conn_str)

    # Create the filepath and the collection name for the vectordb.
    folder_path = common.get_testing_output_dir("dementia", wipe_out=False)
    fullpath_to_db = os.path.join(folder_path, "dementia.db")
    collection_name = "chunks"
    query_vector_db(fullpath_to_db, collection_name)
