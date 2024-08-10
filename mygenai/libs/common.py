"""Exposes commonly used functions."""

import json
import os
import pathlib

_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
_TESTING_DATA_DIR = os.path.join(_CURRENT_DIR, "tests", "data")
_CONN_STR = "postgres://myuser:password@localhost:5432/{db_name}"
_DEFAULT_DB_NAME = "dummy"


def get_connection_string(db_name=None):
    """Returns the connection string for the postgresql.

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
