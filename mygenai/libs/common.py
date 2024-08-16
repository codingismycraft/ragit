"""Exposes commonly used functions."""

import json
import os
import pathlib
import shutil

_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
_TESTING_DATA_DIR = os.path.join(_CURRENT_DIR, "testing_data")
_CONN_STR = "postgres://myuser:password@localhost:5432/{db_name}"
_DEFAULT_DB_NAME = "dummy"


def make_local_connection_string(db_name=None):
    """Makes a connection string to use with the local postgres database.

    :return: The connection string for the postgresql.
    :rtype: str
    """
    db_name = db_name or _DEFAULT_DB_NAME
    return _CONN_STR.format(db_name=db_name)


def get_home_dir():
    """Returns the home directory for the current user.

    :return: The home directory for the current user.
    :rtype: str
    """
    return pathlib.Path.home()


def get_testing_output_dir(relative_path, wipe_out=False):
    """Returns a directory containing temporary output used for testing.

    As an example of what can go to this directory you can think of a
    vector database that is used for testing purposes or whatever else
    that might not be need to be stored.

    :param str relative_path: The path that is relative to the top level
    testing directory.

    :param bool wipe_out: If True, then whatever already exists under
    the relative path will be deleted and it will start with a clean state.

    :return: A string pointing to a directory containing testing output.
    :rtype: str

    :raises NotADirectoryError: the passed in relative_path is pointing
    to an exising file (not a directory).

    :raises: OSError: OS related error when creating or deleting the directory.
    """
    output_dir = os.path.join(get_home_dir(), "testing_output")

    # If pointing to a file raise an exception.
    if os.path.isfile(output_dir):
        raise NotADirectoryError

    # If the base output directory does not exist then create it.
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    fullpath = os.path.join(output_dir, relative_path)

    # If pointing to a file raise an exception.
    if os.path.isfile(fullpath):
        raise NotADirectoryError

    # If the directory already exists delete it if wipe_out is set.
    if os.path.isdir(fullpath) and wipe_out:
        shutil.rmtree(fullpath)
        os.makedirs(fullpath)

    # If the output directory does not exist then create it.
    if not os.path.isdir(fullpath):
        os.makedirs(fullpath)

    return fullpath


def init_settings():
    """Initializes the project's settings."""
    filepath = os.path.join(get_home_dir(), "settings.json")
    with open(filepath) as fin:
        settings = json.load(fin)
        for k, v in settings.items():
            os.environ[k] = v


def get_testing_data_directory():
    """Returns the directory holding the data files to use for samples.

    :return: The directory containing the data files for sample programs.
    :rtype: str
    """
    return _TESTING_DATA_DIR


def get_db_directory():
    """Returns the directory containing the database creation files.

    :return: The directory containing the database creation files.
    :rtype: str
    """
    path = os.path.join(_CURRENT_DIR, "..", "db")
    return path


class MyGenAIException(Exception):
    """Generic MyGenAI exception."""


def handle_exceptions(foo):
    """Decorator to handle exceptions and customize it."""

    def inner(*args, **kwargs):
        """The inner function of the decorator."""
        try:
            return foo(*args, **kwargs)
        except Exception as ex:
            raise MyGenAIException(str(ex)) from ex

    return inner
