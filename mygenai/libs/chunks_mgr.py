"""Document Manager (Manages the document storage)."""

import os

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.impl.doc_splitter_impl as doc_splitter_impl


def build_chunks(fullpath, chunk_size=500, chunk_overlap=40):
    """Splits the passed in document and saves the chunks into the database.

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
    extensions = doc_splitter_impl.get_supported_doc_extensions()
    matches = []
    for root, _, files in os.walk(directory):
        for file in files:
            for extension in extensions:
                if file.endswith(extension):
                    matches.append(os.path.join(root, file))
    return matches


@common.handle_exceptions
def find_documents_to_chunk(directory):
    """Discovers all the documents under the given directory to be chunked.

    Discovers all the files that can be chunked and returns only those that
    are not already in the database.

    :param str directory: The directory containing the documents.

    :return: Only documents that are not already chunked will be returned.
    :rtype: list[str]
    """
    all_filepaths = set(find_all_documents(directory))
    already_chunked = set(_get_already_chunked_files())
    diff = all_filepaths - already_chunked
    return list(diff)


# Whatever follows this line is private to the module and should be
# used from the outside.

_SQL_SELECT_FULLPATHS = """
Select fullpath from chunks group by fullpath
"""

def _get_already_chunked_files():
    """Returns a list with the files that are already chunked and stored in db.

    :return: A list with the files that are already chunked.
    :rtype: list[str]
    """
    fullpaths = []
    with dbutil.SimpleSQL() as db:
        for row in db.execute_query(_SQL_SELECT_FULLPATHS):
            fullpaths.append(row[0])
    return fullpaths



