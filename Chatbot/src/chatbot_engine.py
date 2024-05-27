import os
import requests
from hdbcli import dbapi
import streamlit as st
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores.hanavector import HanaDB
from langchain_core.prompts import PromptTemplate

def get_token():
    auth_url = os.getenv('AICORE_AUTH_URL')
    client_id = os.getenv('AICORE_CLIENT_ID')
    client_secret = os.getenv('AICORE_CLIENT_SECRET')

    token_url = f"{auth_url}/oauth/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()

    token = response.json().get('access_token')
    if not token:
        raise ValueError("トークンが取得できませんでした。")
    return token

def connect_database(proxy_client):
    connection = dbapi.connect(
        address=os.getenv("HANA_DB_ADDRESS"),
        port=os.getenv("HANA_DB_PORT"),
        user=os.getenv("HANA_DB_USER"),
        password=os.getenv("HANA_DB_PASSWORD"),
        autocommit=True,
        sslValidateCertificate=False,
    )
    embeddings = OpenAIEmbeddings(deployment_id=os.getenv('EMBEDDING_DEPLOYMENT_ID'), proxy_client=proxy_client)
    db = HanaDB(
        connection=connection,
        embedding=embeddings,
        table_name="FILE_EMBEDDINGS",
    )
    return db

def setup_chain(db, proxy_client):
    llm = ChatOpenAI(deployment_id=os.getenv('LLM_DEPLOYMENT_ID'), proxy_client=proxy_client)
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

    chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=db.as_retriever(),
        verbose=False,
        combine_docs_chain_kwargs={"prompt": PROMPT}
    )
    return chain

def initialize_session_state():
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []
    if 'past' not in st.session_state:
        st.session_state['past'] = []

def run_conversational_chat(chain, query, chat_history):
    # チェーンにクエリを投げて結果を取得
    result = chain({"question": query, "chat_history": chat_history})
    print("Chain Result:", result)

    # 新しいメッセージをチャット履歴に追加
    chat_history.append((query, result.get("answer", "No valid response found")))

    # 結果を返す
    return result.get("answer", "No valid response found")
