"""Simple example of FISS use.

In this example we have a brutally simple solution of how to create
and save a FISS based vector db and also reload it and use it for
trivial similarity searches.

Obviously there are better ways to approach the problem and they will be
implemented in other programs in this repo but this program just explains
in very simple terms what is going on.
"""

import os
import json
import shutil

import faiss
import langchain.embeddings.openai as openai
import langchain.text_splitter as text_splitter_lib
import langchain_community.document_loaders as loaders
import numpy as np

import mygenai.libs.common as common

# Globals.
_PROGRAM_NAME = os.path.basename(__file__).replace('.py', '')
_OUTPUT_DIR = os.path.join(common.get_home_dir(), _PROGRAM_NAME)
_FAISS_INDEX_FILEPATH = os.path.join(_OUTPUT_DIR, "faiss.index")
_SPLIT_TEXT_FILEPATH = os.path.join(_OUTPUT_DIR, "split_text.json")


def load_pdf(filename):
    """Load a pdf file from the filesystem."""
    chunk_size = 500
    chunk_overlap = 40
    text_splitter = text_splitter_lib.RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    full_path = os.path.join(common.get_data_directory(), filename)
    loader = loaders.PyPDFLoader(full_path)
    pages = loader.load_and_split(text_splitter=text_splitter)
    return pages


def load_text(filename):
    """Loads a plain text file from the filesystem."""
    full_path = os.path.join(common.get_data_directory(), filename)
    with open(full_path) as fin:
        return fin.read()


def serialize_texts_with_index(filename, texts):
    """Serializes texts with indices to a JSON file.

    :param str filename: The filename to save the texts. (it will be
    created under the home directory).
    """
    indexed_texts = [{'index': i, 'text': text} for i, text in enumerate(texts)]
    with open(filename, 'w') as f:
        json.dump(indexed_texts, f, indent=4)


def deserialize_texts_with_index(filename):
    """Deserializes texts with indices from a JSON file."""
    with open(filename, 'r') as f:
        indexed_texts = json.load(f)
    return [item['text'] for item in indexed_texts]


def recreate_output_directory():
    """Recreates the output directory."""
    if os.path.exists(_OUTPUT_DIR):
        shutil.rmtree(_OUTPUT_DIR)
    os.makedirs(_OUTPUT_DIR)


def create_index(filename, chunk_size=200, chunk_overlap=50):
    recreate_output_directory()
    document = load_text(filename)
    text_splitter = text_splitter_lib.RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    texts = text_splitter.split_text(document)
    serialize_texts_with_index(_SPLIT_TEXT_FILEPATH, texts)

    embeddings = openai.OpenAIEmbeddings()
    text_embeddings = embeddings.embed_documents(texts)

    dimension = len(text_embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    embeddings_np = np.array(text_embeddings)

    index.add(embeddings_np)
    faiss.write_index(index, _FAISS_INDEX_FILEPATH)

    query_embedding = embeddings.embed_query(
        "why pattents are bad form the economy"
    )
    k = 5  # Number of nearest neighbors
    distances, indices = index.search(
        np.array([query_embedding], dtype=np.float32), k)

    results = [texts[i] for i in indices[0]]

    print(results)


def load_matching_vectors():
    """Loads the FISS index and the user can ask it questions."""
    index = faiss.read_index(_FAISS_INDEX_FILEPATH)
    embeddings = openai.OpenAIEmbeddings()

    while True:
        query_str = input("Enter the query string : => ")
        query_str = query_str.strip()
        if not query_str:
            break
        query_embedding = embeddings.embed_query(query_str)
        k = 3
        distances, indices = index.search(
            np.array([query_embedding], dtype=np.float32), k)
        texts = deserialize_texts_with_index(_SPLIT_TEXT_FILEPATH)
        results = [texts[i] for i in indices[0]]
        print(results)


def query_executor():
    pass


if __name__ == '__main__':
    common.init_settings()
    load_pdf("patents.pdf")

    # create_index("patents.txt")
    # load_matching_vectors()
