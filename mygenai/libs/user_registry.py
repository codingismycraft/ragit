"""Exposes the UserRegistry static class."""

import os
import re

import bcrypt
import sqlite3

import mygenai.libs.common as common


class UserRegistry:
    """Manages the user registry.

    The user registry is meant to be used from the RagIt front-end web
    application to hold the information for the users of the service.

    To keep things easier to manage the data are stored in sqlite instead of
    the postgres that is used for the heavy backend operations. Note that the
    postgres database is never deployed to the front-end servers both to keep
    the administrative tasks simpler but to also keep the required disk size
    small.

    The user registry is self-sufficient meaning that the database is created
    automatically by the code if needed under the well known shared directory.

    :cvar str _base_dir: The parent directory holding the sqlite db file. By
    default the shared directory will be used.
    """
    _DB_FILENAME = "user_registry.sqlite.db"
    _MAX_USER_NAME_LENGTH = 32
    _MAX_EMAIL_ADDRESS_LENGTH = 64
    _MAX_PASSWORD_LENGTH = 32

    _EMAIL_VALIDATOR = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    _SQL_CREATE_TABLE = """
        CREATE TABLE users (
                    user_name TEXT UNIQUE NOT NULL,
                    email     TEXT UNIQUE NOT NULL,
                    hashed_password  BLOB NOT NULL
                )
    """

    _SQL_INSERT_USER = """
    INSERT INTO users (user_name, email, hashed_password)
    VALUES (?, ?, ?);
    """

    _SQL_SELECT_EMAIL = """SELECT email from users where user_name=? """

    _SQL_SELECT_PASSWD = """
        SELECT hashed_password from users where user_name=?
    """

    _base_dir = None  # By default, will be the shared directory.

    @classmethod
    @common.handle_exceptions
    def save(cls, user_name, email_address, password):
        """Saves the info for the passed in user to the database.

        :param str user_name: The name of the user to save, it must be unique.

        :param str email_address: The email address of the user to save, it
        must be unique.

        :param str password: The password for the user to save.

        :raises: MyGenAIException
        """
        user_name = user_name.strip()
        email_address = email_address.strip()
        password = password.strip()

        if len(user_name) >= cls._MAX_USER_NAME_LENGTH:
            raise ValueError("Too long User name")

        if len(email_address) >= cls._MAX_EMAIL_ADDRESS_LENGTH:
            raise ValueError("Too long email address")

        cls._validate_email(email_address)

        if len(password) >= cls._MAX_PASSWORD_LENGTH:
            raise ValueError("Too long password")

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        with sqlite3.connect(cls._get_full_path()) as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(
                    cls._SQL_INSERT_USER,
                    (user_name, email_address, hashed_password)
                )
            finally:
                if cursor:
                    cursor.close()

    @classmethod
    @common.handle_exceptions
    def validate_password(cls, user_name, password):
        """Validates the passed in password.

        :param str user_name: The user to validate.
        :param str password: The password to validate.

        :raises: MyGenAIException
        """
        with sqlite3.connect(cls._get_full_path()) as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                for row in cursor.execute(cls._SQL_SELECT_PASSWD, (user_name,)):
                    hashed_passwd = row[0]
                    is_valid = bcrypt.checkpw(
                        password.encode('utf-8'), hashed_passwd
                    )
                    if not is_valid:
                        raise ConnectionRefusedError
                    else:
                        return
            finally:
                if cursor:
                    cursor.close()
        raise ValueError(f"User {user_name} not found.")

    @classmethod
    @common.handle_exceptions
    def get_email_address(cls, user_name):
        """Returns the email address for the passed in user.

        :param str user_name: The user to return the email for.

        :returns: The email for the passed in user.

        :raises: MyGenAIException
        """
        with sqlite3.connect(cls._get_full_path()) as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                for row in cursor.execute(cls._SQL_SELECT_EMAIL, (user_name,)):
                    return row[0]
            finally:
                if cursor:
                    cursor.close()
        raise ValueError(f"User {user_name} not found.")

    @classmethod
    @common.handle_exceptions
    def create_db(cls):
        """Creates the database file if it does not exist.

        :raises: MyGenAIException
        """
        fullpath = cls._get_full_path()
        if os.path.exists(fullpath):
            raise FileExistsError
        with sqlite3.connect(fullpath) as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(cls._SQL_CREATE_TABLE)
            finally:
                if cursor:
                    cursor.close()

    @classmethod
    @common.handle_exceptions
    def set_base_dir(cls, base_dir):
        """Allows to customize the directory where the sqlite db is held.

        :param str base_dir: The directory where the sqlite db is held; pass
        None to use the default location which points to the shared directory.

        :raises: MyGenAIException
        """
        if not os.path.isdir(base_dir):
            raise NotADirectoryError
        cls._base_dir = base_dir

    @classmethod
    def _get_full_path(cls):
        """Returns the full path to the sqlite db file.

        :return: The full path to the sqlite db file.
        :rtype: str
        """
        base_dir = cls._base_dir or common.get_shared_directory()
        fullpath = os.path.join(base_dir, cls._DB_FILENAME)
        return fullpath

    @classmethod
    def _validate_email(cls, email_address):
        """Validates the passed in email address.

        :param str email_address: The email address to validate.

        :raises: ValueError if the passed in email address is invalid.
        """
        if not re.fullmatch(cls._EMAIL_VALIDATOR, email_address):
            raise ValueError("Invalid email.")
