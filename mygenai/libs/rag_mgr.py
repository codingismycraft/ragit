"""RagManager is a wrapper for the data handling for RAG creation and update."""

import os

import mygenai.libs.chunks_mgr as chunks_mgr
import mygenai.libs.common as common
import mygenai.libs.vector_db as vector_db
import mygenai.libs.query_executor as query_executor


class RagManager:
    """Provides the paths to the directories for data files for a specific RAG.

    Returns the shared directory used for RAG creation and management.

    Under a development/ local machine this directory is mapped from
    the host to the Vagrant guest while when running the service directly
    on the host machine the shared directory must be under the home directory
    and called mygen-data.

    The data for each RAG collection should be placed under a subdirectory
    inside the shared directory following the same structure outlined above.

    This RAG collection specific directory should have following structure:

    - **documents**: Source files (PDF, DOCX, MD, etc.) for RAG creation.

    - **vectordb: Stores the vector database.

    - **backups:** Contains backups of the PostgreSQL.
    """
    _SHARED_DIR = "mygen-data"
    _VECTOR_COLLECTION_NAME = "chunk_embeddings"

    def __init__(self, rag_name):
        """Initializer.

        :param str rag_name: The name of the RAG collection.
        """
        self._rag_name = rag_name
        self._base_dir = os.path.join(
            common.get_home_dir(),
            self._SHARED_DIR,
            self._rag_name
        )
        common.create_directory_if_not_exists(self._base_dir)

        homedir = common.get_home_dir()

        # Assign the documents directory.
        directory = os.path.join(homedir, self._base_dir, "documents")
        common.create_directory_if_not_exists(directory)
        self._documents_dir = directory

        # Assign the vectordb directory.
        directory = os.path.join(homedir, self._base_dir, "vectordb")
        common.create_directory_if_not_exists(directory)
        self._vectordb_fullpath = os.path.join(
            directory, f"{rag_name}-vector.db"
        )

        # Assign the backups directory.
        directory = os.path.join(homedir, self._base_dir, "backups")
        common.create_directory_if_not_exists(directory)
        self._backups_dir = directory

        query_executor.initialize(
            self._vectordb_fullpath,
            self._VECTOR_COLLECTION_NAME
        )

    def query(self, question, k=3):
        """Uses the RAG collection to enhance the LLM to answer the question.

        :param str question: The question to answer.
        :param int k: The number of vector matches to use.

        :return: The LLM generated answer using the vector db matches.
        :rtype: str

        :raises MyGenAIException
        """
        return query_executor.query(question, k)

    def get_base_dir(self):
        """Returns the base directory for the RAG collection.

        :return: The base directory for the RAG collection.
        :rtype: str
        """
        return self._base_dir

    def get_documents_dir(self):
        """Returns the directory containing the documents to use for RAG.

        :return: The directory containing the documents to use for RAG.
        :rtype: str
        """
        return self._documents_dir

    def get_vector_db_fullpath(self):
        """Returns the full path to the vector database for the given RAG.

        :return: The full path to the vector database for the given RAG.
        :rtype: str
        """
        return self._vectordb_fullpath

    def get_backups_dir(self):
        """Returns the full path to the backups directory for the given RAG.

        :return: The full path to the backups directory for the given RAG.
        :rtype: str
        """
        return self._backups_dir

    def insert_chunks_to_db(self, db, max_count=None, verbose=False):
        """Inserts the chunks to the database.

        :param dbutil.SimpleSQL db: The database wrapper to use.
        :param int max_count: The maximum number of chunks to save; by
        default None will save all the available chunks.
        :param bool verbose: If true it will print out messages.

        :returns: The number of chunks saved to the database.
        :rtype: int

        :raises MyGenAIException
        """
        return chunks_mgr.insert_chunks_to_db(
            db=db,
            directory=self.get_documents_dir(),
            max_count=max_count,
            verbose=verbose
        )

    def count_missing_embeddings(self, db):
        """Returns the number of chunks lacking embeddings.

        To optimize embedding generation, this function calculates the
        count of chunks without associated embeddings. As embedding
        creation can be computationally intensive, this is why we allow for
        incremental processing without requiring a full batch operation.

        :param SimpleSQL db: The database wrapper to use.

        :return: The number of embeddings that need to be evaluated and stored.
        :rtype: int

        :raises MyGenAIException
        """
        chunk_ids = list(chunks_mgr.find_chunks_missing_embeddings(db))
        return len(chunk_ids)

    def insert_embeddings_to_db(self, db, max_count=None, verbose=False):
        """Insert embeddings to the database.

        :param dbutil.SimpleSQL db: The database wrapper to use.
        :param int max_count: The maximum number of embeddings to save; by
        default None will save all the available embeddings.
        :param bool verbose: If true it will print out messages.

        :return: The number of embeddings inserted.
        :rtype: int

        :raises MyGenAIException
        """
        count = chunks_mgr.insert_embeddings_to_db(db, max_count, verbose)
        return count

    def update_vector_db(
            self, db, max_count=None,
            dimension=1536, batch_size=2000, verbose=False):
        """Updates the vector db.

        :param dbutil.SimpleSQL db: The database wrapper to use.

        :param int | None max_count: The maximum number of embeddings to
        save; if None then all the un-inserted chunks will be inserted.

        :param int dimension: The dimensions of the embeddings array.

        :param int batch_size: The size of the batch that is stored to
        the vector db each time (to avoid consuming the whole memory).

        :param bool verbose: If True then informative messages will be printed.

        :returns: The number of chunks that were inserted to the vector db.
        :rtype: int

        :raises MyGenAIException
        """
        if verbose:
            print("updating the vector db.")
        vdb = vector_db.VectorDb(
            fullpath=self.get_vector_db_fullpath(),
            collection_name=self._VECTOR_COLLECTION_NAME,
            dimension=dimension
        )

        total_inserted_counter = 0
        chunks = []
        embeddings = []
        vectorized_chunk_ids = []

        for chunk_id in chunks_mgr.get_chunk_ids_to_insert_to_vector_db(db):
            if verbose:
                print(chunk_id, len(embeddings))
            chunk, embedding = chunks_mgr.load_embeddings(db, chunk_id)
            chunks.append(chunk)
            embeddings.append(embedding)
            vectorized_chunk_ids.append(chunk_id)
            if max_count is not None and len(embeddings) >= max_count:
                break
            if len(embeddings) > batch_size:
                vdb.insert(chunks, embeddings)
                total_inserted_counter += len(embeddings)
                chunks_mgr.set_vectorized(db, vectorized_chunk_ids)
                chunks = []
                embeddings = []
                vectorized_chunk_ids = []

        # Insert leftovers if needed.
        if len(embeddings):
            vdb.insert(chunks, embeddings)
            total_inserted_counter += len(embeddings)
            chunks_mgr.set_vectorized(db, vectorized_chunk_ids)

        if verbose:
            print(f"Totally inserted records: {total_inserted_counter}")

        return total_inserted_counter
