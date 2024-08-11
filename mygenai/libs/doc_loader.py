"""Discovers and process all the available documents."""

import os

import langchain.text_splitter as text_splitter_lib
import langchain_community.document_loaders as doc_loaders


def process_document(fullpath, chunk_size=500, chunk_overlap=40):
    """Saves the embeddings for the passed in document to the database.

    :param str fullpath: The fullpath to the document.
    :param int chunk_size: The chunk size to use.
    :param int chunk_overlap: The chunk overlap The overlap to use.
    """


def find_all_documents(directory):
    """Discovers all the documents under the given directory.

    :param str directory: The directory containing the documents.

    :return: A list of strings holding the full paths of the documents.
    :rtype: list[str]
    """


def find_unprocessed_documents(directory):
    """Discovers all the documents under the given directory to be processed.

    :param str directory: The directory containing the documents.

    :return: Only documents that are not already processed (meaning having
    their embeddings stored in the database) will be returned.
    :rtype: list[str]
    """


# Whatever follows this line is private to the module and should be
# used from the outside.

_SUPPORTED_DOCS = ["pdf", "docx", "md"]


def _split_to_chunks(fullpath, chunk_size=500, chunk_overlap=40):
    """Breaks down the passed in document to chunks.

    :param str fullpath: The fullpath to the document.
    :param int chunk_size: The chunk size to use.
    :param int chunk_overlap: The chunk overlap The overlap to use.

    :yields: A tuple of the text and the metadata for each chunk.
    """
    fullpath = fullpath.strip()
    if fullpath.endswith("pdf"):
        doc = _PdfDocument(fullpath, chunk_size, chunk_overlap)
    elif fullpath.endswith("docx"):
        doc = _DocxDocument(fullpath, chunk_size, chunk_overlap)
    elif fullpath.endswith("md"):
        doc = _MDDocument(fullpath, chunk_size, chunk_overlap)
    else:
        raise NotImplementedError

    return doc.get_chunks()


class _PdfDocument:
    """Holds the information of a PDF document.

    :ivar str _fullpath: The full path to the PDF file.
    :ivar _chunks: The text chunks from the document split.
    """

    _fullpath = None
    _chunks = None

    def __init__(self, fullpath, chunk_size, chunk_overlap):
        """Initializes a new instance.

        :param str fullpath: The full path to the PDF document
        """
        assert fullpath.endswith("pdf"), "not a pdf file"
        assert os.path.isfile(fullpath), f'{fullpath} does not exist'
        self._fullpath = fullpath

        text_splitter = text_splitter_lib.RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        loader = doc_loaders.PyPDFLoader(self._fullpath)
        self._chunks = loader.load_and_split(text_splitter=text_splitter)

    def get_chunks(self):
        """Iterates through the available chunks.

        :yields: The chunks as strings.
        """
        for chunk in self._chunks:
            yield chunk.page_content, chunk.metadata


class _DocxDocument:
    """Holds the information of a PDF document.

    :ivar str _fullpath: The full path to the PDF file.
    :ivar _chunks: The text chunks from the document split.
    """

    _fullpath = None
    _chunks = None

    def __init__(self, fullpath, chunk_size, chunk_overlap):
        """Initializes a new instance.

        :param str fullpath: The full path to the PDF document
        """
        assert fullpath.endswith("docx"), "not a docx file"
        assert os.path.isfile(fullpath), f'{fullpath} does not exist'
        self._fullpath = fullpath

        text_splitter = text_splitter_lib.RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        docx = doc_loaders.Docx2txtLoader(self._fullpath)
        pages = docx.load()
        self._chunks = text_splitter.split_documents(pages)

    def get_chunks(self):
        """Iterates through the available chunks.

        :yields: The chunks as strings.
        """
        for chunk in self._chunks:
            yield chunk.page_content, chunk.metadata


class _MDDocument:
    """Holds the information of a markdown document.

    :ivar str _fullpath: The full path to the PDF file.
    :ivar _chunks: The text chunks from the document split.
    """

    _fullpath = None
    _chunks = None

    def __init__(self, fullpath, chunk_size, chunk_overlap):
        """Initializes a new instance.

        :param str fullpath: The full path to the PDF document
        """
        assert fullpath.endswith("md"), "not a md file"
        assert os.path.isfile(fullpath), f'{fullpath} does not exist'
        self._fullpath = fullpath

        text_splitter = text_splitter_lib.RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        md = doc_loaders.TextLoader(
            self._fullpath
        )
        pages = md.load()
        self._chunks = text_splitter.split_documents(pages)

    def get_chunks(self):
        """Iterates through the available chunks.

        :yields: The chunks as strings.
        """
        for chunk in self._chunks:
            yield chunk.page_content, chunk.metadata
