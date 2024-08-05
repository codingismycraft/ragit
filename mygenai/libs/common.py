"""Exposes commonly used functions."""

import pathlib


def get_home_dir():
    """Returns the home directory for the current user.

    :return: The home directory for the current user.
    :rtype: str
    """
    return pathlib.Path.home()
