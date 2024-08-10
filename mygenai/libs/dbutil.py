"""Exposes the functionality to simplify the interaction with the database."""

import psycopg2

import mygenai.libs.common as common

class SimpleSQL:

    def __init__(self, dbname=None):
        self._dbname = dbname

    def __enter__(self):
        conn_str = common.get_connection_string(self._dbname)
        self._connection = psycopg2.connect(conn_str)
        return self

    def __exit__(self, exc_type, exc_value, trace):
        assert self._connection
        self._connection.close()
        self._connection = None

    def execute_query(self, sql):
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
