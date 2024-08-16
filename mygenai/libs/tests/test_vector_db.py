"""Tests the vector_db module."""

import os
import unittest

import mygenai.libs.chunks_mgr as chunks_mgr
import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.vector_db as vector_db


class TestVectorDb(unittest.TestCase):
    """Tests the VectorDb class."""
    _SQL_CLEAR_CHUNKS = "DElETE FROM chunks"

    @classmethod
    def setUpClass(cls):
        """Class - level setup."""
        conn_str = common.make_local_connection_string("dummy")
        dbutil.SimpleSQL.register_connection_string(conn_str)
        common.init_settings()

    def _insert_chunks_to_db(self, db):
        """Inserts the chunks to the database."""
        db.execute_non_query(self._SQL_CLEAR_CHUNKS)
        directory = common.get_testing_data_directory()
        docs_to_chunk = chunks_mgr.find_documents_to_chunk(db, directory)
        for fullpath in docs_to_chunk:
            chunks_mgr.save_chunks_to_db(db, fullpath)

    def test_creation(self):
        """Tests creating a VectorDb."""
        parent_dir = common.get_testing_output_dir("creating-vector-db")
        collection = "dummy"
        fullpath = os.path.join(parent_dir, "test.db")
        vdb = vector_db.VectorDb(fullpath, collection)
        with dbutil.SimpleSQL() as db:
            self._insert_chunks_to_db(db)
            count = 0
            for chunk_id in chunks_mgr.find_chunks_missing_embeddings(db):
                count += 1
                chunks_mgr.save_embeddings(db, chunk_id)
                if count > 10:
                    break

            chunks = []
            embeddings = []
            for chunk_id in chunks_mgr.find_chunks_with_embeddings(db):
                chunk, embedding = chunks_mgr.load_embeddings(db, chunk_id)
                chunks.append(chunk)
                embeddings.append(embedding)

            count = len(vdb)
            self.assertEqual(count, 0)

            vdb.insert(chunks, embeddings[:4])

            count = len(vdb)
            self.assertEqual(count, 4)

            vdb.insert(chunks, embeddings[4:])

            count = len(vdb)
            self.assertEqual(count, len(embeddings))

            query = "Is SQL Alchemy good?"

            matches = vdb.query(query, 3)
            for match in matches:
                print(match)
