"""Tests the doc_loader module."""

import os
import unittest

import mygenai.libs.common as common
import mygenai.libs.doc_loader as doc_loader


class TestLoadingPdf(unittest.TestCase):
    """Tests loading a pdf file."""

    def test_get_metadata(self):
        """Tests the get_metadata method."""
        full_path = os.path.join(
            common.get_data_directory(),
            "patents.pdf"
        )
        doc = doc_loader.Document(full_path)
        retrieved = doc.get_metadata()
        self.assertIn("patents.pdf", retrieved["fullpath"])

    def test_get_chunks(self):
        """Tests the get_chunks method."""
        full_path = os.path.join(
            common.get_data_directory(),
            "patents.pdf"
        )
        doc = doc_loader.Document(full_path)
        for txt, meta in doc.get_chunks():
            self.assertIsInstance(txt, str)
            self.assertIsInstance(meta, dict)

