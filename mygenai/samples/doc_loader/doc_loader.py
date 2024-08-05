"""Loads documents from the filesystem."""

import os

import langchain_community.document_loaders as loaders
import langchain_community.document_loaders.csv_loader as csv_loader
import langchain.text_splitter as txt_splitter

_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


# from langchain_community.document_loaders import Docx2txtLoader
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders.csv_loader import CSVLoader
# from langchain.text_splitter import CharacterTextSplitter


def main():
    all_documents = []
    full_path = os.path.join(
        _CURRENT_DIR,
        "data",
        "principles_of_marketing_book.pdf"
    )
    loader = loaders.PyPDFLoader(full_path)
    pages = loader.load_and_split()
    print(pages[7])


if __name__ == '__main__':
    main()
