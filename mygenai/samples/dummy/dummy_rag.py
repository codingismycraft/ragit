import os
import shutil

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.rag_mgr as rag_mgr

_DB_NAME = "dummy"
_SQL_CLEAR_CHUNKS = "DElETE FROM chunks"

_QUESTIONS_TO_ASK = [
    "Why sqlalchemy is bad?",
    "what is method chaining?",
    "Why patents are bad?"
]


def make_queries():
    """Queries the RAG based LLM."""
    ragger = rag_mgr.RagManager(_DB_NAME)
    for question in _QUESTIONS_TO_ASK:
        answer = ragger.query(question)
        print(f"Question: {question}")
        print(f"Answer  : {answer}")


def remove_rag_dir():
    """Deletes the directory holding the data for the RAG collection."""
    base_dir = os.path.join(
        common.get_home_dir(), "mygen-data", _DB_NAME
    )

    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir)
    elif os.path.isfile(base_dir):
        os.remove(base_dir)


def create_rag():
    """Creates the RAG collection."""
    ragger = rag_mgr.RagManager(_DB_NAME)
    source_dir = common.get_testing_data_directory()
    destination_dir = ragger.get_documents_dir()
    shutil.rmtree(destination_dir)
    shutil.copytree(source_dir, destination_dir)

    with dbutil.SimpleSQL() as db:
        db.execute_non_query(_SQL_CLEAR_CHUNKS)
        ragger.insert_chunks_to_db(db, verbose=True)
        ragger.insert_embeddings_to_db(db, verbose=True)
        ragger.update_vector_db(db, verbose=True)


if __name__ == '__main__':
    common.init_settings()
    conn_str = common.make_local_connection_string(_DB_NAME)
    dbutil.SimpleSQL.register_connection_string(conn_str)

    remove_rag_dir()
    create_rag()
    make_queries()
