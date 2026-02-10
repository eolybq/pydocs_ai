import streamlit as st


def render_db_error():
    st.error("🔌 Database Connection Error")
    st.info("The database is currently unavailable. Please try again in a few minutes.")
    st.info(
        "**Error Context:** Could not fetch raw data from `PostreSQL` remote Database."
    )
    if st.button("Retry"):
        st.rerun()


def render_http_error(e):
    st.error("🛜 API HTTP error")
    st.info("System encountered an error while fetching available documentation.")
    st.info(f"**Error Context:** {e}")
    if st.button("Retry"):
        st.rerun()


def render_error():
    st.error("❌ Unexpected Error While Reporting Data")
    st.info("System encountered an unexpected error while fetching or processing data.")
