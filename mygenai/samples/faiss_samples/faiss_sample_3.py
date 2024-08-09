from langchain.vectorstores import FAISS
import langchain.embeddings.openai as openai

import mygenai.libs.common as common


def make_embeddings(txt):
    embedding_maker = openai.OpenAIEmbeddings()
    e = embedding_maker.embed_query(txt)

    return e


def main():
    embedding_maker = openai.OpenAIEmbeddings()
    docs = [
        "this is a test"
    ]

    embedding_maker.embed_documents()

    # db = FAISS.from_texts(docs, embedding_maker)


if __name__ == '__main__':
    common.init_settings()
    main()
