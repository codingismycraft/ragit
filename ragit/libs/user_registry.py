"""Exposes the UserRegistry static class."""

import datetime
import os
import re

import bcrypt
import sqlite3

import ragit.libs.common as common


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

    :cvar str _rag_collection_name: The name of the RAG Collection.
    """
    _DB_FILENAME = "{rag_collection}.user_registry.sqlite.db"
    _MAX_USER_NAME_LENGTH = 32
    _MAX_EMAIL_ADDRESS_LENGTH = 64
    _MAX_PASSWORD_LENGTH = 32

    _EMAIL_VALIDATOR = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    _NAME_VALIDATOR = r"^[a-zA-Z][a-zA-Z0-9_]*$"

    _SQL_CREATE_USER_TABLE = """
        CREATE TABLE users (
                    user_id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name        TEXT UNIQUE NOT NULL,
                    email            TEXT UNIQUE NOT NULL,
                    hashed_password  BLOB NOT NULL
                )
    """

    _SQL_CREATE_MSG_TABLE = """
        CREATE TABLE messages (
                    msg_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id       INTEGER,
                    received_at   TEXT, 
                    question      TEXT,
                    temperature   FLOAT DEFAULT NULL,
                    count_matches INTEGER DEFAULT NULL,
                    max_tokens    INTEGER DEFAULT NULL,
                    prompt        TEXT    DEFAULT NULL,
                    response      TEXT    DEFAULT NULL, 
                    responded_at  TEXT    DEFAULT NULL, 
                    thumps_up     INTEGER DEFAULT NULL, 
                    thumped_up_at TEXT    DEFAULT NULL 
        )
    """

    _SQL_CREATE_MATCHES_TABLE = """
        CREATE TABLE matches (
            match_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            msg_id          INTEGER,
            txt             TEXT DEFAULT NULL,
            distance        FLOAT DEFAULT NULL,
            source          TEXT DEFAULT NULL,
            page            INTEGER DEFAULT NULL
        )
        
    """

    _SQL_GET_LAST_ROW_ID = """SELECT last_insert_rowid()"""

    _SQL_GET_USER_ID = """SELECT user_id from users where user_name=? """

    _SQL_INSERT_MSG = """
    INSERT INTO messages 
        (
            user_id, received_at, question, temperature, count_matches, 
            max_tokens, prompt, response, responded_at
            ) 
    values 
        (?, ?, ?, ?, ?, ?, ?, ?, ? )
    """

    _SQL_INSERT_MATCH = """
        INSERT INTO 
            matches (msg_id, txt, distance, source, page) 
        VALUES (?, ?, ?, ?, ?)
    """

    _SQL_UPDATE_THUMPS_UP = """
        UPDATE messages SET thumps_up = ?, thumped_up_at = ? WHERE msg_id = ?
    """

    _SQL_SELECT_THUMPS_UP = """
        SELECT thumps_up, thumped_up_at FROM messages where msg_id = ? 
    """

    _SQL_INSERT_USER = """
    INSERT INTO users (user_name, email, hashed_password)
    VALUES (?, ?, ?);
    """

    _SQL_SELECT_EMAIL = """SELECT email from users where user_name=? """

    _SQL_SELECT_PASSWD = """
        SELECT hashed_password from users where user_name=?
    """

    _SQL_SELECT_QUERIES = """
        SELECT 
            msg_id, question, temperature, count_matches, 
            max_tokens, prompt, response, thumps_up, received_at 
        FROM 
            messages
        ORDER BY received_at DESC
    """
    _SQL_SELECT_MATCHES = """
        SELECT 
            txt, distance, source, page 
        FROM matches 
        WHERE msg_id=? 
        ORDER BY distance DESC
    """

    _SQL_DELETE_QUERY = """ DELETE FROM messages where msg_id=? """

    _THUMPS_UP_FLAG = 1
    _THUMPS_DOWN_FLAG = 0

    _base_dir = None  # By default, will be the shared directory.
    _rag_collection_name = None  # The name of the RAG collection.

    @classmethod
    def set_rag_collection_name(cls, name):
        """Sets the name of the RAG Collection.

        :param str name: The collection name to use. This name must match
        the subdirectory where the documents are stored.
        """
        cls._rag_collection_name = name

    @classmethod
    def get_rag_collection_name(cls):
        """Sets the name of the RAG Collection.

        :returns: The collection name that is assigned to the RagRegistry.
        :rtype: str
        """
        return cls._rag_collection_name

    @classmethod
    @common.handle_exceptions
    def set_thumps_up(cls, msg_id):
        """Sets the thumps up flag for the passed in message id.

        :param int msg_id: The message id to set thumps up for.
        """
        cls._update_thumps_up(msg_id, cls._THUMPS_UP_FLAG)

    @classmethod
    @common.handle_exceptions
    def delete_query(cls, msg_id):
        """Deletes the query with the passed in message id.

        :param int msg_id: The message id of the query to delete.
        """
        with sqlite3.connect(cls._get_full_path_to_db()) as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(cls._SQL_DELETE_QUERY, (msg_id,))
            finally:
                if cursor:
                    cursor.close()

    @classmethod
    @common.handle_exceptions
    def get_thumps_up(cls, msg_id):
        """Returns the thumps up flag for the passed in msg_id.

        :param int msg_id: The message id to return its flag.

        :returns: The email for the passed in user.
        :rtype: int | None

        :raises: MyGenAIException
        """
        with sqlite3.connect(cls._get_full_path_to_db()) as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                values = (msg_id,)
                for row in cursor.execute(cls._SQL_SELECT_THUMPS_UP, values):
                    return row[0], row[1]
            finally:
                if cursor:
                    cursor.close()
        raise ValueError(f"Message id {msg_id} not found.")

    @classmethod
    @common.handle_exceptions
    def set_thumps_down(cls, msg_id):
        """Sets the thumps down flag for the passed in message id.

        :param int msg_id: The message id to set thumps down for.
        """
        cls._update_thumps_up(msg_id, cls._THUMPS_DOWN_FLAG)

    @classmethod
    @common.handle_exceptions
    def insert_message(cls, user_name, received_at,
                       question, response, responded_at):
        """Inserts a new message in the message table.

        :param str user_name: The user name to insert the message for.
        :param datetime.datetime received_at: When send to LLM.
        :param str question: The message to process.
        :param QueryResponse response: The response we got back from the LLM.
        :param datetime.datetime responded_at: When LLM responded.

        :returns: The newly created message id.
        :rtype: int
        """
        with sqlite3.connect(cls._get_full_path_to_db()) as conn:
            cursor = None
            try:
                cursor = conn.cursor()

                # Get the user id from the user name.
                for row in cursor.execute(cls._SQL_GET_USER_ID, (user_name,)):
                    user_id = row[0]
                    break

                # Insert the message.
                data = (
                    user_id,
                    received_at.isoformat(),
                    question,
                    response.temperature,
                    response.matches_count,
                    response.max_tokens,
                    response.prompt,
                    response.response,
                    responded_at.isoformat()
                )
                cursor.execute(cls._SQL_INSERT_MSG, data)

                # Return the newly created message id:
                msg_id = None
                for row in cursor.execute(cls._SQL_GET_LAST_ROW_ID):
                    msg_id = row[0]

                assert msg_id is not None
                msg_id = int(msg_id)

                for match in response.matches:
                    try:
                        txt = match[0]
                        distance = float(match[1])
                        source = match[2]
                        page = match[3]
                        cursor.execute(
                            cls._SQL_INSERT_MATCH, (
                                msg_id, txt, distance, source, page
                            )
                        )
                    except Exception as ex:
                        print(ex)
                return msg_id
            finally:
                if cursor:
                    cursor.close()

    @classmethod
    @common.handle_exceptions
    def add_new_user(cls, user_name, email_address, password):
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

        cls._validate_name(user_name)

        if len(email_address) >= cls._MAX_EMAIL_ADDRESS_LENGTH:
            raise ValueError("Too long email address")

        cls._validate_email(email_address)

        if len(password) >= cls._MAX_PASSWORD_LENGTH:
            raise ValueError("Too long password")

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        with sqlite3.connect(cls._get_full_path_to_db()) as conn:
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
    def get_all_queries(cls):
        """Returns all the available queries.

        Meant to be used from the UI to populate a list with the available
        queries that will allow the user to view the details of them.

        :returns: A list containing the queries using dicts.
        :rtype: [dict]
        """
        queries = []
        with sqlite3.connect(cls._get_full_path_to_db()) as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                for row in cursor.execute(cls._SQL_SELECT_QUERIES):
                    query_info = {
                        "msg_id": row[0],
                        "question": row[1],
                        "temperature": row[2],
                        "count_matches": row[3],
                        "max_tokens": row[4],
                        "prompt": row[5],
                        "response": row[6],
                        "thumps_up": row[7],
                        "received_at": row[8]
                    }
                    queries.append(query_info)
                # Now that we have the queries let's get all the matches that
                # used for the RAG query when calling the vector database.
                for query_info in queries:
                    msg_id = (query_info["msg_id"],)
                    matches = []
                    for row in cursor.execute(cls._SQL_SELECT_MATCHES, msg_id):
                        try:
                            sorten_path = cls._shorten_file_path(row[2])
                        except common.MyGenAIException:
                            sorten_path = 'n/a'

                        matches.append({
                            "txt": row[0],
                            "distance": row[1],
                            "source": sorten_path,
                            "page": row[3] or None
                        })
                    query_info["matches"] = matches
                return queries
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
        with sqlite3.connect(cls._get_full_path_to_db()) as conn:
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
        with sqlite3.connect(cls._get_full_path_to_db()) as conn:
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
    def create_db_if_needed(cls):
        """Creates the database file if it does not exist.

        :raises: MyGenAIException
        """
        fullpath = cls._get_full_path_to_db()
        if os.path.exists(fullpath):
            return
        with sqlite3.connect(fullpath) as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(cls._SQL_CREATE_USER_TABLE)
                cursor.execute(cls._SQL_CREATE_MSG_TABLE)
                cursor.execute(cls._SQL_CREATE_MATCHES_TABLE)
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
    def _get_full_path_to_db(cls):
        """Returns the full path to the sqlite db file.

        :return: The full path to the sqlite db file.
        :rtype: str

        :raises: ValueError.
        """
        if not cls._rag_collection_name:
            raise ValueError("You must set the RAG Collection name.")
        base_dir = cls._base_dir or common.get_shared_directory()
        filename = cls._DB_FILENAME.format(
            rag_collection=cls._rag_collection_name
        )
        root = os.path.join(base_dir, cls._rag_collection_name, "registry")
        common.create_directory_if_not_exists(root)
        fullpath = os.path.join(root, filename)
        return fullpath

    @classmethod
    def _validate_email(cls, email_address):
        """Validates the passed in email address.

        :param str email_address: The email address to validate.

        :raises: ValueError if the passed in email address is invalid.
        """
        if not re.fullmatch(cls._EMAIL_VALIDATOR, email_address):
            raise ValueError("Invalid email.")

    @classmethod
    def _validate_name(cls, name):
        """Validates a user name.

        Ensure it contains only alphanumerics and underscores, and starts
        with a letter.

        :param str name: The name to validate.

        :raises: ValueError if the passed in name address is invalid.
        """
        if not re.match(cls._NAME_VALIDATOR, name):
            raise ValueError("Invalid Name.")

    @classmethod
    def _update_thumps_up(cls, msg_id, thump_up_or_down):
        """Updates the thumps up flag for the passed in msg_id.

        :param int msg_id: The message id to update.
        :param int thump_up_or_down: The value to set, must be 0 or 1.
        """
        with sqlite3.connect(cls._get_full_path_to_db()) as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                values = (
                    thump_up_or_down,
                    datetime.datetime.now().isoformat(),
                    msg_id
                )
                cursor.execute(cls._SQL_UPDATE_THUMPS_UP, values)
            finally:
                if cursor:
                    cursor.close()

    @classmethod
    @common.handle_exceptions
    def _shorten_file_path(cls, file_path):
        """Shortens the file path.

        Since all the documents will live under the <collection-name>/documents
        we are not removing the part of the path up to it and only return
        what follows the document.

        We consider valid the path that starts with:

        /home/<user>/ragit-data/<collection-name>/documents

        meaning that the five first subdirectories of the passed in filepath
        must match the above logic.

        :param file_path: The original file path to be shortened.

        :return: A shortened path to the file path.
        :rtype: str

        :raises MyGenAIException
        """
        if not file_path:
            raise ValueError("Invalid file path.")

        sub_dirs = file_path.split(os.sep)
        if len(sub_dirs) < 6:
            raise ValueError(f"Invalid file_path: {file_path}")

        if sub_dirs[5] != "documents":
            raise ValueError(f"Invalid file_path: {file_path}")

        if sub_dirs[4] != cls.get_rag_collection_name():
            raise ValueError(f"Invalid file_path: {file_path}")

        tokens = sub_dirs[6:]
        shortened_path = os.path.join(*tokens)

        return shortened_path
