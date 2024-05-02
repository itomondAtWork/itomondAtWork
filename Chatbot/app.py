import os
import streamlit as st
from streamlit_chat import message
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile

def initialize():
    # Initialize the Streamlit session state.
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["Hello! Feel free to ask about anything regarding this" + uploaded_file.name]

    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hi!"]

def setup_openai_key():
    # Set up OpenAI API key from the user's input.
    user_api_key = st.sidebar.text_input(
        label="OpenAI API key",
        placeholder="Paste your OpenAI API key here",
        type="password")
    os.environ['OPENAI_API_KEY'] = user_api_key

def load_pdf(uploaded_file):
    # Load and split the PDF file into chunks.
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100, length_function=len)
    loader = PyPDFLoader(file_path=tmp_file_path)
    data = loader.load_and_split(text_splitter)

    return data

def create_chain(data):
    # Create a ConversationalRetrievalChain for managing the conversation.
    embeddings = OpenAIEmbeddings()
    vectors = FAISS.from_documents(data, embeddings)

    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo-16k'),
        retriever=vectors.as_retriever()
    )

def conversational_chat(query, chain):
    # Manage conversation using ConversationalRetrievalChain.
    result = chain({"question": query, "chat_history": st.session_state['history']})
    st.session_state['history'].append((query, result["answer"]))
    return result["answer"]

def main():
    # Main function to manage the Streamlit app.
    setup_openai_key()

    uploaded_file = st.sidebar.file_uploader("upload", type="pdf")

    if uploaded_file:
        data = load_pdf(uploaded_file)
        chain = create_chain(data)

        initialize()

        response_container = st.container()
        container = st.container()

        with container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_input("Input:", placeholder="Please enter your message regarding the PDF data.", key='input')
                submit_button = st.form_submit_button(label='Send')

            if submit_button and user_input:
                output = conversational_chat(user_input, chain)
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                    message(st.session_state["generated"][i], key=str(i), avatar_style="thumbs")

if __name__ == '__main__':
    main()
