import os

import requests
from dotenv import load_dotenv

import streamlit as st

load_dotenv()
DEPLOY_URL = os.getenv("DEPLOY_API_URL")
LOCAL_URL = os.getenv("LOCAL_API_URL")
API_URL = DEPLOY_URL or LOCAL_URL


def get_docs():
    if "docs" not in st.session_state:
        with st.spinner("Fetching available docs..."):
            response = requests.get(f"{API_URL}/get_tables", timeout=10)
            response.raise_for_status()
            data = response.json()

        tables = data.get("tables")
        st.session_state.docs = tables


def render_header():
    if "docs" in st.session_state:
        with st.sidebar:
            st.markdown(
                """
                <style>
                .gradient-text {
                    font-weight: bold;
                    background: -webkit-linear-gradient(left, #ff4b1f, #1fddff);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    display: inline;
                    font-size: 3em;
                }
                </style>
                <div class="gradient-text">📚 PyDocs AI</div>
                """,
                unsafe_allow_html=True,
            )
            option = st.selectbox(
                label=" ",
                label_visibility="collapsed",
                placeholder="Documentation",
                index=None,
                options=st.session_state.get("docs", None),
            )

        return option


def fetch_response(prompt, option, context):
    with requests.post(
        f"{API_URL}/query",
        timeout=50,
        json={"prompt": prompt, "doc_name": option, "context": context},
        stream=True,
    ) as response:
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                text = chunk.decode("utf-8")
                yield text


def render_chat_ui(option):
    if "messages" not in st.session_state:
        with st.chat_message("assistant"):
            st.write(
                "Hello! I'am your python libraries AI assistant. Please first :blue[**select a documentation**] from the sidebar dropdown, and then ask me anything from :blue[**that documentation**]."
            )

        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message["content"])
            else:
                st.write(message["content"])

    if prompt := st.chat_input("Ask question:"):
        if not option:
            st.error("Please select documentation")
            return

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Generating response...", show_time=True):
                stream = fetch_response(prompt, option, st.session_state.messages)
                response_text = str(st.write_stream(stream, cursor="|"))

                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )
