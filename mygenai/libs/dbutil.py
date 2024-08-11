"""Exposes the functionality to simplify the interaction with the database."""

import psycopg2


class SimpleSQL:
    """Provides a simplified interface for interacting with PostgreSQL."""

    _connection_string = None

    @classmethod
    def register_connection_string(cls, connection_string):
        """Registers the connection string for subsequent database interactions.

        :param connection_string: The connection string to the database.
        """
        cls._connection_string = connection_string

    def __enter__(self):
        """Establishes a database connection when entering a with block.

        : return: The SimpleSQL instance itself.

        :raises psycopg2.DatabaseError: If an error occurs during execution.
        """
        self._connection = psycopg2.connect(self._connection_string)
        return self

    def __exit__(self, exc_type, exc_value, trace):
        """Closes the database connection when exiting a with block.

        :param exc_type: The exception type.
        :param exc_value: The exception value.
        :param trace: The exception traceback.
        """
        assert self._connection
        self._connection.close()
        self._connection = None

    def execute_query(self, sql):
        """Executes a query and yields the results row by row.

        :param sql: The SQL SELECT statement to execute.

        :yield: A tuple representing each row of the query result.

        :raises psycopg2.DatabaseError: If an error occurs during execution.
        """
        assert self._connection
        with self._connection.cursor() as cursor:
            cursor.execute(sql)
            records = cursor.fetchall()
            for row in records:
                yield row

    def execute_non_query(self, sql):
        """Executes a non select statement.

        :param sql: the sql to execute

        :raise:psycopg2.DatabaseError
        """
        assert self._connection
        self._connection.autocommit = True
        with self._connection.cursor() as cursor:
            cursor.execute(sql)
