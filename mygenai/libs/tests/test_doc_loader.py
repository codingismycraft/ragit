"""Tests the doc_loader module."""

import os
import unittest

import mygenai.libs.common as common
import mygenai.libs.doc_loader as doc_loader


class TestLoadingPdf(unittest.TestCase):
    """Tests loading a file."""

    def test_pdf(self):
        """Tests the get_chunks method for pdf."""
        full_path = os.path.join(
            common.get_data_directory(),
            "patents.pdf"
        )
        doc = doc_loader.Document(full_path)
        for txt, meta in doc.get_chunks():
            self.assertIsInstance(txt, str)
            self.assertIsInstance(meta, dict)

    def test_docx(self):
        """Tests the get_chunks method for docx."""
        full_path = os.path.join(
            common.get_data_directory(),
            "hello-world.docx"
        )
        doc = doc_loader.Document(full_path)
        for txt, meta in doc.get_chunks():
            self.assertIsInstance(txt, str)
            self.assertIsInstance(meta, dict)
            print(txt, meta)
