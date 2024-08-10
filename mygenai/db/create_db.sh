##########################################################################
#
# Creates the database to hold the embeddings used form the RAG model.
#
# You can pass the database name to create in the command line as the
# first argument to the script.
# If you do not pass a database name then by default the name dummy will
# be used.
#
# If the database you are trying to create already exist then the script
# fail. If you are sure you want to recreate the database then you
# will have to delete it by running the dropdb command from the command line:
# dropdb -U myuser <dbname>
#
##########################################################################

if [ $# -gt 0 ]; then
  DB_NAME=$1
else
  DB_NAME=dummy
fi

echo "Creating database $DB_NAME"
createdb -U myuser $DB_NAME;

if [ $? -ne 0 ]; then
  echo "Failed to create database $DB_NAME"
  exit 1
fi

psql -U myuser -d $DB_NAME -f create_schema.sql

if [ $? -ne 0 ]; then
  echo "Failed to create database $DB_NAME"
  exit 1
fi
echo "$DB_NAME was created successfully."

