"""Abstracts the lower level details for a vector index."""

import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
import streamlit as st

import mygenai.libs.common as common



def document_data(query, chat_history):
    path = os.path.join(common.get_data_directory(), "patents.pdf")
    pdf_path = path
    loader = PyPDFLoader(file_path=pdf_path)
    doc = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                   chunk_overlap=100,
                                                   separators=["\n\n", "\n",
                                                               " ", ""])
    text = text_splitter.split_documents(documents=doc)

    # creating embeddings using OPENAI

    embeddings = OpenAIEmbeddings()

    vectorstore = FAISS.from_documents(text, embeddings)
    vectorstore.save_local("vectors")
    print("Embeddings successfully saved in vector Database and saved locally")

    # Loading the saved embeddings
    loaded_vectors = FAISS.load_local("vectors", embeddings)

    # ConversationalRetrievalChain
    qa = ConversationalRetrievalChain.from_llm(
        llm=OpenAI(),
        retriever=loaded_vectors.as_retriever()
    )

    return qa({"question": query, "chat_history": chat_history})


if __name__ == '__main__':
    common.init_settings()
    st.header("QA ChatBot")
    # ChatInput
    prompt = st.chat_input("Enter your questions here")

    if "user_prompt_history" not in st.session_state:
        st.session_state["user_prompt_history"] = []
    if "chat_answers_history" not in st.session_state:
        st.session_state["chat_answers_history"] = []
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if prompt:
        with st.spinner("Generating......"):
            output = document_data(query=prompt, chat_history=st.session_state[
                "chat_history"])

            # Storing the questions, answers and chat history

            st.session_state["chat_answers_history"].append(output['answer'])
            st.session_state["user_prompt_history"].append(prompt)
            st.session_state["chat_history"].append((prompt, output['answer']))

    # Displaying the chat history

    if st.session_state["chat_answers_history"]:
        for i, j in zip(st.session_state["chat_answers_history"],
                        st.session_state["user_prompt_history"]):
            message1 = st.chat_message("user")
            message1.write(j)
            message2 = st.chat_message("assistant")
            message2.write(i)