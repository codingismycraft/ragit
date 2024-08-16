"""Document Manager (Manages the document storage)."""

import datetime
import json
import os
import re

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.impl.embeddings_retriever as embeddings_retriever
import mygenai.libs.impl.splitter as splitter


@common.handle_exceptions
def insert_chunks_to_db(db, directory, max_count=None, verbose=False):
    """Inserts the chunks to the database.

    :param dbutil.SimpleSQL db: The database wrapper to use.
    :param directory: The directory where the files exist.
    :param int max_count: The maximum number of chunks to save; by
    default None will save all the available chunks.
    :param bool verbose: If true it will print out messages.

    :returns: The number of chunks saved to the database.
    """
    if verbose:
        if max_count is None:
            print("Will insert all available chunks to the database.")
        else:
            print(f"Insert at max {max_count} chunks to the database.")
    counter = 0
    for fullpath in find_documents_to_chunk(db, directory):
        counter += save_chunks_to_db(db, fullpath)
        if verbose:
            print(datetime.datetime.now(), counter, fullpath)
        if max_count and counter >= max_count:
            break
    return counter


@common.handle_exceptions
def insert_embeddings_to_db(db, max_count=None, verbose=False):
    """Insert embeddings to the database.

    :param dbutil.SimpleSQL db: The database wrapper to use.
    :param int max_count: The maximum number of embeddings to save; by
    default None will save all the available embeddings.
    :param bool verbose: If true it will print out messages.

    :return: The number of embeddings inserted.
    :rtype: int
    """
    if verbose:
        if max_count is None:
            print("Will insert all available embeddings to the database.")
        else:
            print(f"Insert at max {max_count} embeddings to the database.")
    counter = 0
    for chunk_id in find_chunks_missing_embeddings(db):
        counter += 1
        if max_count is not None and counter > max_count:
            break
        save_embeddings(db, chunk_id)
        if verbose:
            print(f"Embeddings count: {counter}")
    return counter


@common.handle_exceptions
def save_embeddings(db, chunk_id):
    """Retrieves and saves the embeddings for a given chunk.

    The chunk must already exist in the database with the given id.

    :param SimpleSQL db: The database wrapper to use.
    :param int chunk_id: The id of the chunk to save its embeddings.
    """
    # Get the chunk from the database.
    sql = _SQL_SELECT_CHUNK.format(chunk_id=chunk_id)
    chunk = None
    for row in db.execute_query(sql):
        chunk = row[0]
    assert chunk is not None
    # Retrieve the embeddings and store them in the database.
    embeddings = embeddings_retriever.get_embeddings(chunk)
    sql = _SQL_UPDATE_EMBEDDINGS.format(
        embeddings=json.dumps(embeddings),
        chunk_id=chunk_id
    )
    db.execute_non_query(sql)


@common.handle_exceptions
def find_chunks_missing_embeddings(db):
    """Finds the chunks that are missing embeddings.

    Since the embeddings can be calculated any time, it is quite possible
    that we will have chunks in the database that will have NULL as
    embeddings just because they were not calculated yet.

    This function is finding these chunks and yields their chunk_id(s).

    :param SimpleSQL db: The database wrapper to use.

    :yield: The chunk_id of the chunks that are missing embeddings.
    """
    for row in db.execute_query(_SQL_FIND_MISSING_EMBEDDINGS):
        yield row[0]


@common.handle_exceptions
def find_chunks_with_embeddings(db):
    """Finds the chunks with embeddings.

    :param SimpleSQL db: The database wrapper to use.

    :yield: The chunk_id of the chunks with embeddings.
    """
    for row in db.execute_query(_SQL_FIND_ASSIGNED_EMBEDDINGS):
        yield row[0]


@common.handle_exceptions
def load_embeddings(db, chunk_id):
    """Returns the embeddings for the passed in chunk_id.

    :param SimpleSQL db: The database wrapper to use.
    :param int chunk_id: The chunk id to fetch.

    :return: A tuple consisting with the chunk Text and the embeddings.
    :rtype: tuple
    """
    sql = _SQL_SELECT_EMBEDDINGS.format(chunk_id=chunk_id)
    for row in db.execute_query(sql):
        chunk = row[0]
        embeddings = row[1]
        return chunk, embeddings


@common.handle_exceptions
def save_chunks_to_db(db, fullpath, chunk_size=500, chunk_overlap=40):
    """Splits the passed in document and saves the chunks into the database.

    :param SimpleSQL db: The database wrapper to use.
    :param str fullpath: The fullpath to the document.
    :param int chunk_size: The chunk size to use.
    :param int chunk_overlap: The chunk overlap The overlap to use.

    :returns: The number of chunks saved.
    :rtype: int
    """
    assert os.path.isfile(fullpath)
    chunk_index = 0
    for chunk, metadata in splitter.split(fullpath, chunk_size, chunk_overlap):
        try:
            chunk = chunk.replace('"', "'")
            chunk = chunk.replace("'", "''")
            chunk = re.sub(r'[^\w\s]', '', chunk)
            chunk_index += 1
            meta = json.dumps(metadata)
            sql = _SQL_INSERT_CHUNK.format(
                filepath=fullpath,
                chunk_index=chunk_index,
                txt=chunk,
                meta=meta
            )
            db.execute_non_query(sql)
        except Exception as ex:
            print(ex)
    return chunk_index


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
def find_documents_to_chunk(db, directory):
    """Discovers all the documents under the given directory to be chunked.

    Discovers all the files that can be chunked and returns only those that
    are not already in the database.

    :param SimpleSQL db: The database wrapper to use.
    :param str directory: The directory containing the documents.

    :return: Only documents that are not already chunked will be returned.
    :rtype: list[str]
    """
    all_filepaths = set(find_all_documents(directory))
    already_chunked = set(_get_already_chunked_files(db))
    diff = all_filepaths - already_chunked
    return list(diff)


# Whatever follows this line is private to the module and should be
# used from the outside.

_SQL_SELECT_FULLPATHS = """
sELECT fullpath FROM chunks GROUP BY fullpath
"""

_SQL_INSERT_CHUNK = """
INSERT INTO chunks (fullpath, chunk_index, chunk, metadata) 
VALUES ('{filepath}', {chunk_index}, '{txt}', '{meta}')
"""

_SQL_SELECT_CHUNK = """
SELECT chunk FROM chunks WHERE chunk_id={chunk_id}
"""

_SQL_SELECT_EMBEDDINGS = """
SELECT chunk, embeddings FROM chunks WHERE chunk_id={chunk_id}
"""

_SQL_UPDATE_EMBEDDINGS = """
UPDATE chunks SET embeddings='{embeddings}' WHERE chunk_id={chunk_id}
"""

_SQL_FIND_MISSING_EMBEDDINGS = """
SELECT chunk_id FROM chunks WHERE embeddings IS NULL
"""

_SQL_FIND_ASSIGNED_EMBEDDINGS = """
SELECT chunk_id FROM chunks WHERE embeddings IS NOT NULL
"""


def _get_already_chunked_files(db):
    """Returns a list with the files that are already chunked and stored in db.

    :return: A list with the files that are already chunked.
    :rtype: list[str]
    """
    fullpaths = []
    for row in db.execute_query(_SQL_SELECT_FULLPATHS):
        fullpaths.append(row[0])
    return fullpaths
