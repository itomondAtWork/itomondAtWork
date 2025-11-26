import streamlit as st
from chatbot_engine import run_conversational_chat

def set_custom_styles():
    custom_css = """
    <style>
        .stButton>button {
            width: 100%;
            border-radius: 20px;
            font-size: 25px;
            padding: 10px 24px;
            background-color: #FF4B4B;
            color: white;
        }
        .stTextInput>div>div>input {
            font-size: 16px;
            padding: 10px;
            border-radius: 10px;
        }
        .css-1d391kg {
            padding: 10px 20px 20px;
        }
        .message-user {
            background-color: #D0F0C0;
            padding: 10px;
            border-radius: 15px;
            margin: 5px;
        }
        .message-bot {
            background-color: #F0D0FF;
            padding: 10px;
            border-radius: 15px;
            margin: 5px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def display_interface(chain):
    response_container = st.container()
    container = st.container()
    set_custom_styles()
    with container:
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("Input:", placeholder="Please enter your message.", key='input')
            submit_button = st.form_submit_button(label='Send')
        if submit_button and user_input:
            output = run_conversational_chat(chain, user_input, st.session_state['history'])
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
    if st.session_state['generated']:
        with response_container:
            for i in range(len(st.session_state['generated'])):
                st.markdown(f'<div class="message-user">😊 {st.session_state["past"][i]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="message-bot">🤖 {st.session_state["generated"][i]}</div>', unsafe_allow_html=True)
