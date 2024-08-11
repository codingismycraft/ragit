"""Tests the doc_mgr module."""

import unittest

import mygenai.libs.common as common
import mygenai.libs.doc_mgr as doc_mgr


class TestModule(unittest.TestCase):
    """Tests."""

    def test_find_all_documents(self):
        """Tests the find_all_documents module."""
        directory = common.get_testing_data_directory()
        retrieved = doc_mgr.find_all_documents(directory)
        print(retrieved)
