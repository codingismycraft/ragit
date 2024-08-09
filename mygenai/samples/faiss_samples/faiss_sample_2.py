from uuid import uuid4

import langchain.embeddings.openai as openai
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
import mygenai.libs.common as common
from langchain_core.documents import Document


def create_indexes():
    embeddings = openai.OpenAIEmbeddings(model="text-embedding-3-large")
    txt = "hello world"
    a = embeddings.embed_query(txt)
    index = faiss.IndexFlatL2(len(a))

    vector_store1 = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    vector_store2 = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )

    document_1 = Document(
        page_content="I had chocalate chip pancakes and scrambled eggs for breakfast this morning.",
        metadata={"source": "tweet"},
    )

    document_2 = Document(
        page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",
        metadata={"source": "news"},
    )

    document_3 = Document(
        page_content="Building an exciting new project with LangChain - come check it out!",
        metadata={"source": "tweet"},
    )

    document_4 = Document(
        page_content="Robbers broke into the city bank and stole $1 million in cash.",
        metadata={"source": "news"},
    )

    document_5 = Document(
        page_content="Wow! That was an amazing movie. I can't wait to see it again.",
        metadata={"source": "tweet"},
    )

    document_6 = Document(
        page_content="Is the new iPhone worth the price? Read this review to find out.",
        metadata={"source": "website"},
    )

    document_7 = Document(
        page_content="The top 10 soccer players in the world right now.",
        metadata={"source": "website"},
    )

    document_8 = Document(
        page_content="LangGraph is the best framework for building stateful, agentic applications!",
        metadata={"source": "tweet"},
    )

    document_9 = Document(
        page_content="The stock market is down 500 points today due to fears of a recession.",
        metadata={"source": "news"},
    )

    document_10 = Document(
        page_content="I have a bad feeling I am going to get deleted :(",
        metadata={"source": "tweet"},
    )

    documents = [
        document_1,
        document_2,
        document_3,
        document_4,
        document_5,
        # document_6,
        # document_7,
        # document_8,
        # document_9,
        # document_10
    ]
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store1.add_documents(documents=documents, ids=uuids)
    vector_store1.save_local("faiss_index-1")


    documents = [
        document_6,
        document_7,
        document_8,
        document_9,
        document_10
    ]
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store2.add_documents(documents=documents, ids=uuids)
    vector_store2.save_local("faiss_index-2")

    # results = vector_store1.similarity_search(
    #     "what is the economy doing today?",
    #     k=2
    # )
    # for res in results:
    #     print(f"* {res.page_content} [{res.metadata}]")


def merge_indexes():
    embeddings = openai.OpenAIEmbeddings(model="text-embedding-3-large")
    # vector_store1 = FAISS.load_local(
    #     "faiss_index-1", embeddings, allow_dangerous_deserialization=True
    # )

    vector_store2 = FAISS.load_local(
        "faiss_index-2", embeddings, allow_dangerous_deserialization=True
    )

    # vector_store1.merge_from(vector_store2)


    results = vector_store2.similarity_search(
        "what is the economy doing today?",
        k=2
    )
    for res in results:
        print(f"* {res.page_content} [{res.metadata}]")


if __name__ == '__main__':
    common.init_settings()
    #create_indexes()
    merge_indexes()

