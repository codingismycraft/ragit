"""Discovers and process all the available documents."""

import os

import langchain.text_splitter as text_splitter_lib
import langchain_community.document_loaders as doc_loaders


class Document:
    """Holds the information about a document to use in RAG.

    :ivar _impl: Holds the instance that implements the lower level details.
    """

    _impl = None

    def __init__(self, location):
        """Loads and processes the document.

        :raises NotImplementedError
        """
        location = location.strip()
        if location.endswith("pdf"):
            self._impl = _PdfDocument(location)
        else:
            raise NotImplementedError

    def get_chunks(self):
        """Iterates through the available chunks.

        :yields: The chunks as strings.
        """
        return self._impl.get_chunks()

    def get_metadata(self):
        """Returns the metadata associated with the document.

        :returns: A dictionary holding the metadata for the document
        :rtype dict
        """
        return self._impl.get_metadata()


# Whatever follows this line is private to the module and should be
# used from the outside.

class _PdfDocument:
    """Holds the information of a PDF document.

    :ivar str _fullpath: The full path to the PDF file.
    """

    _fullpath = None

    def __init__(self, fullpath, chunk_size=500, chunk_overlap=40):
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

    def get_chunks(self, chunk_size=500, chunk_overlap=40):
        """Iterates through the available chunks.

        :yields: The chunks as strings.
        """
        for chunk in self._chunks:
            yield chunk.page_content, chunk.metadata

    def get_metadata(self):
        """Returns the metadata associated with the document.

        :returns: A dictionary holding the metadata for the document
        :rtype dict
        """
        return {
            "fullpath": self._fullpath
        }
