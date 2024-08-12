"""Sample application using the dementia related papers.

Assumes that we have a db named dementia available.
"""

import datetime

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.chunks_mgr as chunks_mgr
import mygenai.samples.dementia.settings as settings


def main():
    """Inserts the chunks to the database."""
    conn_str = common.make_local_connection_string(settings.DBNAME)
    dbutil.SimpleSQL.register_connection_string(conn_str)

    counter = 0
    with dbutil.SimpleSQL() as db:
        directory = settings.DIRECTORY
        for fullpath in chunks_mgr.find_documents_to_chunk(db, directory):
            counter += 1
            print(datetime.datetime.now(), counter, fullpath)
            chunks_mgr.save_chunks_to_db(db, fullpath)


if __name__ == '__main__':
    main()
