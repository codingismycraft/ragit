"""Tests the rag_manager module."""

import os
import shutil
import unittest

import ragit.libs.common as common
import ragit.libs.dbutil as dbutil
import ragit.libs.impl.metrics as metrics
import ragit.libs.rag_mgr as rag_mgr


class TestRagManager(unittest.TestCase):
    """Tests the RagManager class.

    Assumes that the dummy psql database exists.
    """

    _RAG_NAME = "dummy"
    _SQL_CLEAR_CHUNKS = "DElETE FROM chunks"

    @classmethod
    def setUpClass(cls):
        """Class - level setup.

        - Sets the connection string to point to the dummy db.
        - Initializes the openai key.
        """
        conn_str = common.make_local_connection_string("dummy")
        dbutil.SimpleSQL.register_connection_string(conn_str)
        common.init_settings()

    def _get_base_dir(self):
        """Returns the base directory for the collection used in the test.

        :return: The base directory for the collection used in the test.
        :rtype: str
        """
        fullpath = os.path.join(
            common.get_home_dir(), "mygen-data", self._RAG_NAME
        )
        return fullpath

    def setUp(self):
        """If the directory for the rag data exists then delete it."""
        fullpath = self._get_base_dir()

        if os.path.isdir(fullpath):
            shutil.rmtree(fullpath)
        elif os.path.isfile(fullpath):
            os.remove(fullpath)

    def test_creation(self):
        """Tests the creation of the Rag Collection.

        Staring with a "clean" shared directory (meaning that the corresponding
        directory for the collection used here does not exist) this test should
        validate that this directory is successfully created when an instance
        of the RagManager is created.
        """
        base_dir = self._get_base_dir()
        self.assertFalse(os.path.exists(base_dir))
        ragger = rag_mgr.RagManager(self._RAG_NAME)
        self.assertEqual(ragger.get_rag_collection_name(), self._RAG_NAME)
        self.assertTrue(os.path.exists(base_dir))
        self.assertTrue(os.path.exists(ragger.get_backups_dir()))
        self.assertTrue(os.path.exists(ragger.get_documents_dir()))

        # Copy the testing files to the RAG collection directory.

        source_dir = common.get_testing_data_directory()
        destination_dir = ragger.get_documents_dir()
        # To keep the copytree function happy delete the destination directory.
        shutil.rmtree(destination_dir)
        shutil.copytree(source_dir, destination_dir)
        # The destination directory is recreated and contains the copied files.
        self.assertTrue(os.path.exists(destination_dir))

        # Add the chunks for all the documents to the psql database.
        with dbutil.SimpleSQL() as db:
            db.execute_non_query(self._SQL_CLEAR_CHUNKS)

            # Insert the chunks.
            ragger.insert_chunks_to_db(db, verbose=True)

            counter = metrics.get_chunks_without_embeddings(db)
            assert counter > 10, "Too few documents, add some and try again"

            # Insert 5 of the missing embeddings.
            c1 = 5
            c2 = counter - c1

            assert c1 + c2 == counter
            ragger.insert_embeddings_to_db(db, max_count=c1)

            # Verify the counter.
            missing_count = metrics.get_chunks_without_embeddings(db)
            self.assertEqual(missing_count, c2)

            retrieved = ragger.update_vector_db(db)

            self.assertEqual(retrieved, c1)

            # Insert the missing embeddings,
            ragger.insert_embeddings_to_db(db)
            counter = metrics.get_chunks_without_embeddings(db)
            self.assertEqual(counter, 0)

            retrieved = ragger.update_vector_db(db)
            self.assertEqual(retrieved, c2)

            retrieved = ragger.query("What is method chaining?")
            self.assertIn("method chaining", retrieved.lower())

            coll_metrics = ragger.get_metrics(db)
            self.assertEqual(
                coll_metrics.total_chunks, coll_metrics.inserted_to_vectordb
            )
