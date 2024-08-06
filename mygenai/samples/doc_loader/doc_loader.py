"""Loads documents from the filesystem."""

import os
import glob

import langchain_community.document_loaders as loaders
import langchain_community.document_loaders.csv_loader as csv_loader
import langchain.text_splitter as txt_splitter

_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
_DATA_DIR = os.path.join(_CURRENT_DIR, "data")


# from langchain_community.document_loaders import Docx2txtLoader
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders.csv_loader import CSVLoader
# from langchain.text_splitter import CharacterTextSplitter

def load_csv():
    """Returns all the csv files in the testing directory."""
    fullpaths = glob.glob(os.path.join(_DATA_DIR, "*.csv"))
    for fp in fullpaths:
        loader = csv_loader.CSVLoader(file_path=fp)
        data = loader.load()
        print(data)


def load_pdf():
    full_path = os.path.join(
        _CURRENT_DIR,
        "data",
        "principles_of_marketing_book.pdf"
    )
    loader = loaders.PyPDFLoader(full_path)
    pages = loader.load_and_split()
    print(pages[7])


def load_docx():
    """Splits a document using CharacterTextSplitter."""

    text_splitter = txt_splitter.CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=200, chunk_overlap=0
    )
    full_path = os.path.join(
        _CURRENT_DIR,
        "data",
        "hello-world.docx"
    )
    loader = loaders.Docx2txtLoader(full_path)
    pages = loader.load()
    chunks = text_splitter.split_documents(pages)
    print(chunks)


if __name__ == '__main__':
    # load_pdf()
    # load_csv()
    load_docx()
