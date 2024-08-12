"""Tests the chunks_mgr module."""

import unittest

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.chunks_mgr as chunks_mgr


class TestModule(unittest.TestCase):
    """Tests the chunks_mgr module."""

    _DB_NAME = "dummy"
    _SQL_CLEAR_CHUNKS = "DElETE FROM chunks"

    def tearDown(self):
        """Cleans up the environment upon finishing a test."""
        dbutil.SimpleSQL.register_connection_string(None)

    def test_find_all_documents(self):
        """Tests the find_all_documents module."""
        directory = common.get_testing_data_directory()
        retrieved = chunks_mgr.find_all_documents(directory)
        self.assertTrue(len(retrieved))

    def test_invalid_find_documents_to_chunk(self):
        """Tests the find_documents_to_chunk raising expection."""
        with self.assertRaises(common.MyGenAIException):
            directory = common.get_testing_data_directory()
            chunks_mgr.find_documents_to_chunk(directory)

    def test_find_documents_to_chunk(self):
        """Tests the find_documents_to_chunk.

        To run this test the dummy database must be available.

        Clear all the records from the chunks' data table and discover all
        the documents under the testing_data_directory. After doing so,
        the find_documents_to_chunk should return the same list of
        documents (since none of them is already processed).
        """
        conn_str = common.make_local_connection_string(self._DB_NAME)
        dbutil.SimpleSQL.register_connection_string(conn_str)
        with dbutil.SimpleSQL() as db:
            db.execute_non_query(self._SQL_CLEAR_CHUNKS)
            directory = common.get_testing_data_directory()
            retrieved = chunks_mgr.find_documents_to_chunk(db, directory)
            expected = chunks_mgr.find_all_documents(
                common.get_testing_data_directory()
            )
            self.assertListEqual(sorted(expected), sorted(retrieved))

    def test_save_chunks_to_db(self):
        """Saves the chunks for a given file to the database."""
        conn_str = common.make_local_connection_string(self._DB_NAME)
        dbutil.SimpleSQL.register_connection_string(conn_str)

        # Verify that there are not chunks in the database.
        with dbutil.SimpleSQL() as db:
            db.execute_non_query(self._SQL_CLEAR_CHUNKS)

            directory = common.get_testing_data_directory()
            docs_to_chunk = chunks_mgr.find_documents_to_chunk(db, directory)

            # Only save the first two documents.
            for fullpath in docs_to_chunk[:2]:
                chunks_mgr.save_chunks_to_db(db, fullpath)

            # Verify that the first two documents are in the database.
            retrieved = chunks_mgr.find_documents_to_chunk(db, directory)
            expected = docs_to_chunk[2:]
            self.assertListEqual(sorted(expected), sorted(retrieved))

    def test_find_chunks_missing_embeddings(self):
        """Tests the find chunks with missing embeddings."""
        common.init_settings()
        conn_str = common.make_local_connection_string(self._DB_NAME)
        dbutil.SimpleSQL.register_connection_string(conn_str)

        # Verify that there are not chunks in the database.
        with dbutil.SimpleSQL() as db:
            db.execute_non_query(self._SQL_CLEAR_CHUNKS)

            directory = common.get_testing_data_directory()
            docs_to_chunk = chunks_mgr.find_documents_to_chunk(db, directory)
            docs_to_chunk = sorted(docs_to_chunk)

            # Only save the first two documents.
            for fullpath in docs_to_chunk[:2]:
                chunks_mgr.save_chunks_to_db(db, fullpath)

            # Only the above documents should be missing embeddings.
            chunk_ids_before = list(chunks_mgr.find_chunks_missing_embeddings(db))

            # Save the embeddings only for the first two chunk ids.
            saved = []
            for chunk_id in chunk_ids_before[:2]:
                saved.append(chunk_id)
                chunks_mgr.save_embeddings(db, chunk_id)

            # Compare before and after.
            chunk_ids_no_embeddings = list(
                chunks_mgr.find_chunks_missing_embeddings(db)
            )

            expected = sorted(chunk_ids_before)
            retrieved = sorted(chunk_ids_no_embeddings + saved)

            self.assertListEqual(expected, retrieved)

            chunk_id_with_embeddings = list(
                chunks_mgr.find_chunks_with_embeddings(db)
            )

            retrieved = sorted(
                chunk_ids_no_embeddings + chunk_id_with_embeddings
            )

            self.assertListEqual(expected, retrieved)

            chunk_id = chunk_id_with_embeddings[0]
            chunk, embeddings = chunks_mgr.load_embeddings(db, chunk_id)

            self.assertIsInstance(embeddings, list)
            self.assertEqual(len(embeddings), 1536)

            self.assertIsInstance(chunk, str)
            chunk_id = chunk_ids_no_embeddings[0]
            chunk, embeddings = chunks_mgr.load_embeddings(db, chunk_id)
            self.assertIsInstance(chunk, str)
            self.assertIsNone(embeddings)

