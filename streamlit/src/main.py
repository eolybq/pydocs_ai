import requests

import streamlit as st

from services.interface import render_chat_ui, get_docs, render_sidebar
from services.errors import render_db_error, render_error, render_http_error

st.set_page_config(
    page_title="PyDocs AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "https://github.com/eolybq/pydocs_ai"},
)


def main():
    try:
        get_docs()

        if st.session_state.docs == [] or st.session_state.docs is None:
            render_db_error()
            return

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the PyDocs AI API.")
        return
    except requests.exceptions.HTTPError as e:
        render_http_error(e)
        return
    except Exception:
        render_error()
        return

    option = render_sidebar()

    try:
        render_chat_ui(option)
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the PyDocs AI API.")
        return
    except requests.exceptions.HTTPError as e:
        render_http_error(e)
        return
    except Exception:
        render_error()
        return


if __name__ == "__main__":
    main()
