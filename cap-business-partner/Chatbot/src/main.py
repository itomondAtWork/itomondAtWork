import streamlit as st
from dotenv import load_dotenv
from utils import set_custom_styles, display_interface
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from chatbot_engine import get_token, connect_database, setup_chain, initialize_session_state
from recommend_engine import run_similarity_search # type: ignore

def main():
    set_custom_styles()
    load_dotenv()
    token = get_token()
    proxy_client = get_proxy_client('gen-ai-hub', token=token)
    db = connect_database(proxy_client)
    chain = setup_chain(db, proxy_client)
    initialize_session_state()

    # タブの設定
    tab1, tab2 = st.tabs(["Chat", "Similarity Search"])

    with tab1:
        display_interface(chain)

    with tab2:
        st.header("Similarity Search")
        query = st.text_input("Enter search query:")
        if st.button("Search"):
            results = run_similarity_search(db, query)
            st.write("### Search Results")
            for result in results:
                st.write(f"**Rank**: {result['Rank']}")
                st.write(f"**Filename**: {result['Filename']}")
                st.write(f"**Similarity**: {result['Score']}")
                st.write("---")

if __name__ == "__main__":
    main()
