"""Loads documents from the filesystem."""

import os
import glob

import langchain_community.document_loaders as loaders
import langchain_community.document_loaders.csv_loader as csv_loader
import langchain.text_splitter as txt_splitter

import mygenai.libs.common as common


def load_csv():
    """Returns all the csv files in the testing directory."""
    fullpaths = glob.glob(os.path.join(common.get_data_directory(), "*.csv"))
    for fp in fullpaths:
        loader = csv_loader.CSVLoader(file_path=fp)
        data = loader.load()
        print(data)


def load_pdf():
    full_path = os.path.join(
        common.get_data_directory(),
        "patents.pdf"
    )
    loader = loaders.PyPDFLoader(full_path)
    pages = loader.load_and_split()
    p1 = pages[0]
    print(pages[7])


def load_docx():
    """Splits a document using CharacterTextSplitter."""
    text_splitter = txt_splitter.CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=200, chunk_overlap=0
    )
    full_path = os.path.join(
        common.get_data_directory(),
        "hello-world.docx"
    )
    loader = loaders.Docx2txtLoader(full_path)
    pages = loader.load()
    chunks = text_splitter.split_documents(pages)
    print(chunks)


if __name__ == '__main__':
    load_pdf()
    # load_csv()
    # load_docx()
