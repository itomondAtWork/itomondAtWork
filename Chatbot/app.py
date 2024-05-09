import os
import tempfile
import streamlit as st
from hdbcli import dbapi
from streamlit_chat import message
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.hanavector import HanaDB
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

def set_custom_styles():
    custom_css = """
    <style>
        .stButton>button {
            width: 100%;
            border-radius: 20px;
            font-size: 25px;
            padding: 10px 24px;
            background-color: #FF4B4B; /* ボタンの背景色 */
            color: white; /* ボタンの文字色 */
        }
        .stTextInput>div>div>input {
            font-size: 16px;
            padding: 10px;
            border-radius: 10px;
        }
        .css-1d391kg {
            padding: 10px 20px 20px;
        }
        /* チャットメッセージ用のカスタムスタイル */
        .message-user {
            background-color: #D0F0C0; /* ユーザーメッセージの背景色 */
            padding: 10px;
            border-radius: 15px;
            margin: 5px;
        }
        .message-bot {
            background-color: #F0D0FF; /* ボットメッセージの背景色 */
            padding: 10px;
            border-radius: 15px;
            margin: 5px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def main():
    set_custom_styles()
    load_dotenv()

    user_api_key = os.getenv('OPENAI_API_KEY')
    os.environ['OPENAI_API_KEY'] = user_api_key

    connection, db = initialize_database()

    uploaded_files = st.sidebar.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    webpage_urls = st.sidebar.text_area("Enter webpage URLs to load content", placeholder="https://example.com\nhttps://example2.com")
    url_list = st.session_state.get('url_list', [])

    if st.sidebar.button('Add URL'):
        if webpage_urls:
            url_list.extend(webpage_urls.split())
            st.session_state['url_list'] = url_list
            webpage_urls = ""  # Clear the text area

    url_container = st.sidebar.container()
    for i, url in enumerate(url_list):
        col1, col2 = url_container.columns([0.8, 0.2])
        col1.write(url)
        if col2.button("Remove", key=f'remove-{i}'):
            url_list.remove(url)
            st.session_state['url_list'] = url_list

    if uploaded_files:
        process_pdfs(uploaded_files, db)
    if url_list:
        for url in url_list:
            process_webpage(url, db)

    chain = setup_chain(db)
    initialize_session_state()
    display_interface(chain)

def process_webpage(url, db):
    loader = WebBaseLoader(url)
    loader.requests_kwargs = {'verify': False}
    text = loader.load()
    db.add_documents(text)

def initialize_database():
    connection = dbapi.connect(
        address=os.getenv("HANA_DB_ADDRESS"),
        port=os.getenv("HANA_DB_PORT"),
        user=os.getenv("HANA_DB_USER"),
        password=os.getenv("HANA_DB_PASSWORD"),
        autocommit=True,
        sslValidateCertificate=False,
    )
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    db = HanaDB(
        connection=connection,
        embedding=embeddings,
        table_name="ITO_DEMO_RETRIEVAL_CHAIN",
    )
    db.delete(filter={})
    return connection, db

def process_pdfs(uploaded_files, db):
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        loader = PyPDFLoader(file_path=tmp_file_path)
        documents = loader.load()
        db.add_documents(documents)

def setup_chain(db):
    llm = ChatOpenAI(
        model="gpt-4-turbo",
        temperature=0.2,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    prompt_template = """
    You are a helpful advisor. Context related to the prompt is provided.
    Please answer it by referring to the chat history, but also referring to the following context.
    ```
    {context}
    ```
    Chat History: {chat_history}
    Question: {question}
    """
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "chat_history", "question"]
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history", output_key="answer", return_messages=True
    )
    chain = ConversationalRetrievalChain.from_llm(
        llm,
        db.as_retriever(),
        return_source_documents=True,
        memory=memory,
        verbose=False,
        combine_docs_chain_kwargs={"prompt": PROMPT}
    )
    return chain

def initialize_session_state():
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["Hello! Feel free to ask about anything regarding the uploaded PDFs or webpage content."]
    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hi!"]

def display_interface(chain):
    response_container = st.container()
    container = st.container()
    set_custom_styles()
    with container:
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("Input:", placeholder="Please enter your message.", key='input')
            submit_button = st.form_submit_button(label='Send')
        if submit_button and user_input:
            output = run_conversational_chat(chain, user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
    if st.session_state['generated']:
        with response_container:
            for i in range(len(st.session_state['generated'])):
                st.markdown(f'<div class="message-user">😊 {st.session_state['past'][i]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="message-bot">🤖 {st.session_state['generated'][i]}</div>', unsafe_allow_html=True)

def run_conversational_chat(chain, query):
    result = chain({"question": query, "chat_history": st.session_state['history']})
    st.session_state['history'].append((query, result["answer"]))
    return result["answer"]

if __name__ == "__main__":
    main()