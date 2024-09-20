"""Executes a query using the vector database."""

import logging
import openai
import re

import ragit.libs.common as common
import ragit.libs.impl.vector_db as vector_db

DEFAULT_MODEL = "gpt-3.5-turbo"
# DEFAULT_MODEL = "gpt-4-turbo"
_DEFAULT_TEMPERATURE = 0.5
_DEFAULT_MAX_TOKENS = 800
_DEFAULT_CLOSES_MATCHES_COUNT = 6

# Aliases.
logger = logging.getLogger(__name__)


@common.handle_exceptions
def initialize(fullpath_to_db, collection_name, model_name=DEFAULT_MODEL):
    """Initializes the executor.

    :param str fullpath_to_db: The full path to the database file to query.
    :param str collection_name: The name of the collection to query.
    :param str  model_name: The name of the model to use.
    """
    _QueryExecutor.initialize(fullpath_to_db, collection_name, model_name)


@common.handle_exceptions
def close():
    """Closes query executor."""
    _QueryExecutor.close()


@common.handle_exceptions
def query(question, k=None, temperature=None, max_tokens=None):
    """Uses the RAG collection to enhance the LLM to answer the question.

    :param str question: The question to answer.
    :param int k: The number of vector matches to use.
    :param float temperature: The temperature to use for the query.
    :param float max_tokens: The max_tokens to use for the query.

    :return: The LLM generated answer using the vector db matches.
    :rtype: str
    """
    return _QueryExecutor.execute_query(
        question,
        k=k,
        temperature=temperature,
        max_tokens=max_tokens
    )


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

    _PYTHON_EXPERT = """You are an expert python programmer."""

    _FORMAT_PYTHON_PROMPT = """
    Reformat the passed in the <code> tags python code adding to it the 
    proper indentation and return to me the proper code in markdown format:
    <code>
    {python_code}
    </code>
    """

    @classmethod
    def _format_python_code(cls, python_code):
        """Formats the passed in python code.

        Used in the case what we have the LLM writing for us some code that
        can be wrongly formatted (mostly un-indented) to successfully
        reformat it.

        :param str python_code: The python code to format.

        :returns: The formatted python code.
        :rtype: str

        ------------ Example ----------------------
        An example of the input can be the following:

        def get_x(a):
        return a

        For the above input we should expect something like the following to
        be returned:

        ```python
        def get_x(a):
            return a
        ```
        """
        user_prompt = cls._FORMAT_PYTHON_PROMPT.format(
            python_code=python_code
        )

        if not cls._openai_client:
            cls._openai_client = openai.OpenAI()

        response = cls._openai_client.chat.completions.create(
            model=cls._model_name or DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": cls._PYTHON_EXPERT},
                {"role": "user", "content": user_prompt},
            ],
        )

        resp = response.choices[0].message.content
        match = re.search(r'```python(.*?)```', resp, re.DOTALL)
        if match:
            return match.group(0).strip()
        else:
            return ""

    @classmethod
    def _substitute_python_code(cls, content):
        """If the content contains python code reformat it.

        :param str content: The content to substitute python code if needed.

        :returns: The content with proper python code formatting if needed.
        :rtype: str
        """
        text = content
        code_blocks = [
            (match.start(), match.end())
            for match in re.finditer(r'```python.*?```', text, re.DOTALL)
        ]
        formatted_code = []
        pos = 0
        surrounding_code = []
        for (start, end) in code_blocks:
            surrounding_code.append(content[pos:start])
            pos = end
            txt = text[start: end]
            python_code = cls._get_internal_python_code(txt)
            python_code = cls._format_python_code(python_code)
            formatted_code.append(python_code)

        surrounding_code.append(content[pos:-1])

        final_txt = ''
        for index, c in enumerate(formatted_code):
            final_txt += surrounding_code[index]
            final_txt += c
        final_txt += surrounding_code[-1]

        return final_txt

    @classmethod
    def _get_internal_python_code(cls, txt):
        """Extracts the pure python code from markdown.

        :param str txt: The passed in text that contains the python code. Note
        that we expect only one chunk of code to exist in the txt and also
        this code must be enclosed in markdown tags.

        We expect the txt to be passed as follows:

        ```python
        def foo()...
            ....
        ```

        The objective of this function is to strip the markdown and return
        the clear python code.

        :returns: The "clear" python code without the tags.
        :rtype: str
        """
        txt = txt.strip()
        txt = txt.replace("```python", '').replace("```", "")
        return txt

    @classmethod
    def execute_query(cls, question, k=None, temperature=None, max_tokens=None):
        """Executes a query getting a RAG response.

        :param str question: The question to ask.
        :param int k: The number of matches to return.
        :param float temperature: The temperature to use for the query.
        :param float max_tokens: The max_tokens to use for the query.

        :return: The response as a string.
        :rtype: str

        :raises ValueError
        """
        if not cls._vdb:
            logger.error("The virtual db is not initialized.")
            raise ValueError("No vector database.")

        if not cls._openai_client:
            logger.error("The OpenAI client is not initialized.")
            raise ValueError("No OpenAI client.")

        if not cls._model_name:
            logger.error("No model name was assigned for the query.")
            raise ValueError("No Model name.")

        if not k:
            k = _DEFAULT_CLOSES_MATCHES_COUNT

        matches = cls._vdb.query(question, k)
        user_prompt = cls._USER_PROMPT.format(
            context=matches, question=question
        )

        if not temperature:
            temperature = _DEFAULT_TEMPERATURE

        if not max_tokens:
            max_tokens = _DEFAULT_MAX_TOKENS

        response = cls._openai_client.chat.completions.create(
            model=cls._model_name,
            messages=[
                {"role": "system", "content": cls._SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        response_content = response.choices[0].message.content

        # Make content substitutions (if needed).
        response_content = cls._substitute_python_code(response_content)

        return response_content

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
        except Exception as ex:
            logger.exception(ex)
            logger.error(
                "Failed to init vectordb: %s %s %s",
                fullpath_to_db, collection_name, model_name
            )
            cls._model_name = None
            cls._openai_client = None
            if cls._vdb:
                cls._vdb.close()
                cls._vdb = None
            raise
        else:
            logger.info(
                "Successfully initialized vector db: %s %s %s",
                fullpath_to_db, collection_name, model_name
            )

    @classmethod
    def close(cls):
        """Closes the vector db and clears the openai client."""
        if cls._vdb:
            cls._vdb.close()
            cls._vdb = None
        cls._model_name = None
        cls._openai_client = None


