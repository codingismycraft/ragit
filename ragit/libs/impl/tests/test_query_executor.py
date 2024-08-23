"""Tests the query executor module."""

import os

import unittest

import ragit.libs.impl.chunks_mgr as chunks_mgr
import ragit.libs.common as common
import ragit.libs.dbutil as dbutil
import ragit.libs.impl.query_executor as query_executor
import ragit.libs.impl.vector_db as vector_db


class TestQueryExecutor(unittest.TestCase):
    """Tests the chunks_mgr module."""

    _DB_NAME = "dummy"
    _SQL_CLEAR_CHUNKS = "DElETE FROM chunks"

    @classmethod
    def _initialize_env(cls):
        """Initialize the environment.

        :returns: A tuple consisting from the full path to the vector db
        and the collection name to use.
        :rtype: tuple[str, str]
        """
        common.init_settings()
        conn_str = common.make_local_connection_string(cls._DB_NAME)
        dbutil.SimpleSQL.register_connection_string(conn_str)
        folder_path = common.get_testing_output_dir(
            "dummy-testing-query", wipe_out=True
        )

        fullpath_to_db = os.path.join(folder_path, "dummy-vector.db")
        collection_name = "dummy"

        return fullpath_to_db, collection_name

    @classmethod
    def _create_vector_db(cls, fullpath_to_db, collection_name):
        """Creates the vector db for the testing data.

        :param str fullpath_to_db: The full path to the database file to create.
        :param str collection_name: The name of the collection to create.
        """
        with dbutil.SimpleSQL() as db:
            db.execute_non_query(cls._SQL_CLEAR_CHUNKS)
            directory = common.get_testing_data_directory()
            chunks_mgr.insert_chunks_to_db(db, directory, verbose=False)
            chunks_mgr.insert_embeddings_to_db(db, verbose=False)

            vdb = vector_db.VectorDb(fullpath_to_db, collection_name)
            chunks = []
            embeddings = []
            for chunk_id in chunks_mgr.find_chunks_with_embeddings(db):
                chunk, embedding = chunks_mgr.load_embeddings(db, chunk_id)
                chunks.append(chunk)
                embeddings.append(embedding)
            vdb.insert(chunks, embeddings)

    def test_query(self):
        """Tests the query."""
        fullpath_to_db, collection_name = self._initialize_env()
        self._create_vector_db(fullpath_to_db, collection_name)
        query_executor.initialize(fullpath_to_db, collection_name)
        retrieved = query_executor.query("What is method chaining?")
        self.assertIn("method chaining", retrieved.lower())


