"""Queries the dementia vector database."""

import mygenai.libs.common as common
import mygenai.libs.rag_mgr as rag_mgr
import mygenai.samples.dementia.settings as settings


def query_vector_db():
    """Loads and queries the vector database.

    :param str fullpath_to_db: The full path to the database file to query.
    :param str collection_name: The name of the collection to query.
    """
    common.init_settings()

    ragger = rag_mgr.RagManager(settings.RAG_COLLECTION_NAME)
    query = "can support vector machines be used to predict dementia?"
    answer = ragger.query(query)
    print(query)
    print(answer)


if __name__ == '__main__':
    common.init_settings()
    query_vector_db()
