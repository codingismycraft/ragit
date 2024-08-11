"""Document Manager (Manages the document storage)."""

import json
import os

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.impl.splitter as splitter


@common.handle_exceptions
def save_chunks_to_db(db, fullpath, chunk_size=500, chunk_overlap=40):
    """Splits the passed in document and saves the chunks into the database.

    :param SimpleSQL db: The database wrapper to use.
    :param str fullpath: The fullpath to the document.
    :param int chunk_size: The chunk size to use.
    :param int chunk_overlap: The chunk overlap The overlap to use.
    """
    assert os.path.isfile(fullpath)
    chunk_index = 0
    for chunk, metadata in splitter.split(fullpath, chunk_size, chunk_overlap):
        chunk = chunk.replace("'", "''")
        chunk_index += 1
        meta = json.dumps(metadata)
        sql = _SQL_INSERT_CHUNK.format(
            filepath=fullpath,
            chunk_index=chunk_index,
            txt=chunk,
            meta=meta
        )
        print(sql)
        db.execute_non_query(sql)


@common.handle_exceptions
def find_all_documents(directory):
    """Discovers all the documents under the given directory.

    :param str directory: The directory containing the documents.

    :return: A list of strings holding the full paths of the documents.
    :rtype: list[str]
    """
    extensions = splitter.get_supported_doc_extensions()
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

_SQL_INSERT_CHUNK = """
Insert into chunks (fullpath, chunk_index, chunk, metadata) 
values ('{filepath}', {chunk_index}, '{txt}', '{meta}')
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
