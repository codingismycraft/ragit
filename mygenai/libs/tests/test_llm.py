"""Tests the llm module."""

import unittest

import mygenai.libs.llm as llm
import mygenai.libs.common as common


class TestLLMWrapper(unittest.TestCase):
    """Tests the LLMWrapper class."""

    @classmethod
    def setUpClass(cls):
        """Initializes the environment."""
        common.init_settings()

    def test_get_embeddings(self):
        """Tests the get_embeddings function."""
        txt = "hello world."
        retrieved = llm.get_embeddings(txt)
        expected_len = 1536
        self.assertEqual(len(retrieved), expected_len)

