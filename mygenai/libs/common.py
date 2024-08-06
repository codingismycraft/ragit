"""Exposes commonly used functions."""

import json
import os
import pathlib


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
