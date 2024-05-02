import os
import streamlit as st
from streamlit_chat import message
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter

def main():
    # Sidebar inputs
    user_api_key = st.sidebar.text_input(
        label="OpenAI API key",
        placeholder="Paste your OpenAI API key here",
        type="password"
    )
    
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type="pdf")
    
    # Set the OpenAI API key
    os.environ['OPENAI_API_KEY'] = user_api_key

    if uploaded_file:
        # Process the uploaded PDF
        data = process_pdf(uploaded_file)
        # Create a conversation chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo-16k'),
            retriever=data.as_retriever()
        )

        # Initialize session state
        initialize_session_state(uploaded_file.name)
        # Display conversation interface
        display_interface(chain)

def process_pdf(uploaded_file):
    # Save the uploaded file to a temporary path
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    # Load and split the PDF text
    loader = PyPDFLoader(file_path=tmp_file_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100, length_function=len)
    data = loader.load_and_split(text_splitter)

    # Create a vector store from the split text
    embeddings = OpenAIEmbeddings()
    vectors = FAISS.from_documents(data, embeddings)

    return vectors

def initialize_session_state(pdf_name):
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = [f"Hello! Feel free to ask about anything regarding {pdf_name}"]

    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hi!"]

def display_interface(chain):
    response_container = st.container()
    container = st.container()

    with container:
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("Input:", placeholder="Please enter your message regarding the PDF data.", key='input')
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            output = run_conversational_chat(chain, user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    # Display chat history
    if st.session_state['generated']:
        with response_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                message(st.session_state['generated'][i], key=str(i), avatar_style="thumbs")

def run_conversational_chat(chain, query):
    # Get the response from the chat model
    result = chain({"question": query, "chat_history": st.session_state['history']})
    # Update chat history
    st.session_state['history'].append((query, result["answer"]))
    return result["answer"]

if __name__ == "__main__":
    main()
