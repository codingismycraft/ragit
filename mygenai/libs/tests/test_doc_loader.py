"""Tests the doc_loader module."""

import os
import unittest

import mygenai.libs.common as common
import mygenai.libs.doc_loader as doc_loader


class TestSplittingToChunks(unittest.TestCase):
    """Tests the _split_to_chunks function."""

    def test_pdf(self):
        """Tests the get_chunks method for pdf."""
        full_path = os.path.join(
            common.get_testing_data_directory(),
            "patents.pdf"
        )
        for txt, meta in doc_loader._split_to_chunks(full_path):
            self.assertIsInstance(txt, str)
            self.assertIsInstance(meta, dict)

    def test_docx(self):
        """Tests the get_chunks method for docx."""
        full_path = os.path.join(
            common.get_testing_data_directory(),
            "hello-world.docx"
        )
        for txt, meta in doc_loader._split_to_chunks(full_path):
            self.assertIsInstance(txt, str)
            self.assertIsInstance(meta, dict)

    def test_markdown(self):
        """Tests the get_chunks method for markdown."""
        full_path = os.path.join(
            common.get_testing_data_directory(),
            "sql-alchemy-sucks.md"
        )
        for txt, meta in doc_loader._split_to_chunks(full_path):
            self.assertIsInstance(txt, str)
            self.assertIsInstance(meta, dict)
