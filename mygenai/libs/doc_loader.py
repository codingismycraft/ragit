"""Discovers and process all the available documents."""


def process_document(fullpath, chunk_size=500, chunk_overlap=40):
    """Saves the embeddings for the passed in document to the database.

    :param str fullpath: The fullpath to the document.
    :param int chunk_size: The chunk size to use.
    :param int chunk_overlap: The chunk overlap The overlap to use.
    """


def find_all_documents(directory):
    """Discovers all the documents under the given directory.

    :param str directory: The directory containing the documents.

    :return: A list of strings holding the full paths of the documents.
    :rtype: list[str]
    """


def find_unprocessed_documents(directory):
    """Discovers all the documents under the given directory to be processed.

    :param str directory: The directory containing the documents.

    :return: Only documents that are not already processed (meaning having
    their embeddings stored in the database) will be returned.
    :rtype: list[str]
    """
