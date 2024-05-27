import streamlit as st
from dotenv import load_dotenv
from utils import set_custom_styles, display_interface
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from chatbot_engine import get_token, connect_database, setup_chain, initialize_session_state

def main():
    set_custom_styles()
    load_dotenv()
    token = get_token()
    proxy_client = get_proxy_client('gen-ai-hub', token=token)
    db = connect_database(proxy_client)
    chain = setup_chain(db, proxy_client)
    initialize_session_state()
    display_interface(chain)

if __name__ == "__main__":
    main()
