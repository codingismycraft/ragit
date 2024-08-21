#!/usr/bin/env python3

"""Updates the chunks, embeddings and vector db for a RAG collection.


**Arguments:**

- `-n <collection-name>`: Name of the RAG collection to update. This identifies
  the directory containing documents and the database name.

**Assumptions:**

- Documents for the RAG collection are stored in the directory:
  `~/mygen-data/<collection-name>/documents`. Users need to create this
  directory beforehand and add the documents they want to use.

- Two directories will be created (if they do not exist already ):

- `~/mygen-data/<collection-name>/vectordb`: Stores the vector database files.

- `~/mygen-data/<collection-name>/backups`: Used for backups (implementation
  details not specified).

- A PostgreSQL database named `<collection-name>` is required. Use the script
  `mygenai/db/create-db.sh <collection-name>` to create it.

**Functionality:**

- Processes documents from the specified directory.

- Generates chunks, embeddings, and updates the vector database.

- Can be run repeatedly with the same collection name for updates if new
  documents are added.

**Notes:**

- This script assumes a specific directory structure (`~/mygen-data`) for
  storing data. Adjust the paths if needed.

- The script relies on an external script `mygenai/db/create-db.sh` for
  database creation (implementation not shown).

"""

import argparse

import mygenai.libs.common as common
import mygenai.libs.dbutil as dbutil
import mygenai.libs.rag_mgr as rag_mgr

_DESC ="Updates the chunks, embeddings, and vector" \
       " database for a RAG collection."


def parse_args():
    """Returns the command line arguments."""
    parser = argparse.ArgumentParser(description=_DESC)
    parser.add_argument(
        '-n',
        '--name',
        required=True,
        help='The name of the RAG collection.'
    )
    parser.add_argument(
        '-p',
        '--process_it',
        action='store_true',
        help='Insert missing embeddings and insert into vector db.'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_false',
        help='If true will print information about its progress.'
    )
    parsed_args = parser.parse_args()
    return parsed_args


def main():
    """Updates the vector db for any given directory."""
    args = parse_args()
    common.init_settings()
    conn_str = common.make_local_connection_string(args.name)
    dbutil.SimpleSQL.register_connection_string(conn_str)
    ragger = rag_mgr.RagManager(args.name)
    verbose = args.verbose

    with dbutil.SimpleSQL() as db:
        if args.process_it:
            count = ragger.insert_chunks_to_db(db, verbose=verbose)
            if verbose:
                print(f"Inserted {count} chunks.")

            count = ragger.insert_embeddings_to_db(db, verbose=verbose)
            if verbose:
                print(f"Inserted {count} embeddings.")

            count = ragger.update_vector_db(db, verbose=verbose)
            if verbose:
                print(f"Inserted {count} chunks to the vector db.")
        else:
            stats = ragger.get_metrics(db)
            print(stats)


if __name__ == '__main__':
    main()
