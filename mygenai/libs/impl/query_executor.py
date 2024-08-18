"""Executes a query using the vector database."""

import openai

import mygenai.libs.common as common
import mygenai.libs.impl.vector_db as vector_db

DEFAULT_MODEL = "gpt-3.5-turbo"


@common.handle_exceptions
def initialize(fullpath_to_db, collection_name, model_name=DEFAULT_MODEL):
    """Initializes the executor.

    :param str fullpath_to_db: The full path to the database file to query.
    :param str collection_name: The name of the collection to query.
    :param str  model_name: The name of the model to use.
    """
    _QueryExecutor.initialize(fullpath_to_db, collection_name, model_name)


@common.handle_exceptions
def query(question, k=3):
    """Uses the RAG collection to enhance the LLM to answer the question.

    :param str question: The question to answer.
    :param int k: The number of vector matches to use.

    :return: The LLM generated answer using the vector db matches.
    :rtype: str
    """
    return _QueryExecutor.execute_query(question, k=k)


# Whatever follows this line is private to the module and should not be
# used from the outside.


class _QueryExecutor:
    """Manages the LLM session to get a RAG response.

    :cvar vector_db.VectorDb _vdb: The vector database.
    :cvar OpenAI _openai_client: The OpenAI client to use.
    :cvar str _model_name: The name of the model to use.
    """

    _vdb = None
    _openai_client = None
    _model_name = None

    _SYSTEM_PROMPT = """
    Human: You are an AI assistant. You are able to find answers to 
    the questions from the contextual passage snippets provided.
    """

    _USER_PROMPT = """
    Use the following pieces of information enclosed in 
    <context> tags to provide an answer to the question 
    enclosed in <question> tags.
    <context>
    {context}
    </context>
    <question>
    {question}
    </question>
    """

    @classmethod
    def execute_query(cls, question, k=3):
        """Executes a query getting a RAG response.

        :param str question: The question to ask.
        :param int k: The number of matches to return.

        :return: The response as a string.
        :rtype: str

        :raises ValueError
        """
        if not cls._vdb:
            raise ValueError("No vector database.")

        if not cls._openai_client:
            raise ValueError("No OpenAI client.")

        if not cls._model_name:
            raise ValueError("No Model name.")

        matches = cls._vdb.query(question, k)
        user_prompt = cls._USER_PROMPT.format(
            context=matches, question=question
        )

        response = cls._openai_client.chat.completions.create(
            model=cls._model_name,
            messages=[
                {"role": "system", "content": cls._SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        respose_content = response.choices[0].message.content

        return respose_content

    @classmethod
    def initialize(cls, fullpath_to_db, collection_name, model_name):
        """Initializes the executor.

        :param str fullpath_to_db: The full path to the database file to query.
        :param str collection_name: The name of the collection to query.
        :param str model_name: The name of the model to use.
        """
        try:
            cls._model_name = model_name
            cls._vdb = vector_db.VectorDb(fullpath_to_db, collection_name)
            cls._openai_client = openai.OpenAI()
        except Exception:
            cls._model_name = None
            cls._vdb = None
            cls._openai_client = None
            raise
