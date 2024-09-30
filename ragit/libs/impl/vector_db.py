"""Exposes a vector index db wrapper."""

import pymilvus

import ragit.libs.impl.embeddings_retriever as embeddings_retriever


class VectorDb:
    """Encapsulates a vector database.

    :ivar str _fullpath: The full path to the file holding the vector db.
    :ivar str _collection_name: The name of the collection.
    :ivar int _dimension: The dimensions of the embeddings array.
    """

    def __init__(self, fullpath, collection_name, dimension=1536):
        """Initializes the instance.

        :param str fullpath: The full path to the file holding the vector db.
        :param str collection_name: The name of the collection.
        :param int dimension: The length of the embeddings vector.
        """
        self._fullpath = f'file://{fullpath}'
        print(f"about to connect to {self._fullpath}")
        self._collection_name = collection_name
        self._milvus_client = pymilvus.MilvusClient(uri=fullpath)
        print("done with connnecting")
        self._dimension = dimension
        if not self._milvus_client.has_collection(collection_name):
            self._milvus_client.create_collection(
                collection_name=self._collection_name,
                dimension=self._dimension,
                metric_type="IP",  # Inner product distance
                consistency_level="Strong",  # Strong consistency level
            )

    def close(self):
        """Closes the milvus vector db."""
        if self._milvus_client:
            self._milvus_client.close()

    def __repr__(self):
        """Returns a string representation of this instance.

        :return: A string representation of this instance.
        :rtype: str
        """
        return f"{self._collection_name}, " \
               f"{self._collection_name}: " \
               f"{self._dimension}"

    def insert(self, chunks, embeddings):
        """Inserts a list of chunks and their embeddings into the db.

        Subsequent calls to this method append new chunks to and existing
        collection, effectively incrementally updating the database.

        :param list[str] chunks: The list of chunks to insert.
        :param list[ list[float]] embeddings: The list of the embeddings.
        """
        assert self._milvus_client, "Milvus Vector Collection is not open."
        data = []
        count = 0
        for chunk, embedding in zip(chunks, embeddings):
            data.append({"id": count, "vector": embedding, "text": chunk})
            count += 1
        self._milvus_client.insert(
            collection_name=self._collection_name,
            data=data
        )

    def __len__(self):
        """Returns the number of records in the collection.

        :return: The number of records in the collection.
        :rtype: int
        """
        assert self._milvus_client, "Milvus Vector Collection is not open."
        res = self._milvus_client.query(
            collection_name=self._collection_name,
            output_fields=["count(*)"]
        )
        counter = res[0]["count(*)"]
        return counter

    def query(self, query, k=3):
        """Queries the vector database for matching chunks.

        :param str query: The string to find matching chunks.
        :param int k: The number of matches to return.
        """
        assert self._milvus_client, "Milvus Vector Collection is not open."
        e = embeddings_retriever.get_embeddings(query)
        search_res = self._milvus_client.search(
            collection_name=self._collection_name,
            data=[e],
            limit=k,
            search_params={"metric_type": "IP", "params": {}},
            output_fields=["text"],  # Return the text field
        )

        matches = [
            (res["entity"]["text"], res["distance"]) for res in search_res[0]
        ]

        return matches
