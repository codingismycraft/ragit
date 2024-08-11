"""Tests the chunks_mgr module."""

import unittest

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.chunks_mgr as chunks_mgr


class TestModule(unittest.TestCase):
    """Tests."""

    _DB_NAME = "dummy"

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
        conn_str = common.make_local_connection_string("dummy")
        dbutil.SimpleSQL.register_connection_string(conn_str)
        with dbutil.SimpleSQL() as db:
            db.execute_non_query("delete from chunks")
            directory = common.get_testing_data_directory()
            retrieved = chunks_mgr.find_documents_to_chunk(directory)
            expected = chunks_mgr.find_all_documents(
                common.get_testing_data_directory()
            )
            self.assertListEqual(sorted(expected), sorted(retrieved))
        dbutil.SimpleSQL.register_connection_string(None)
