# app.py
import streamlit as st
from chat_page import render_chat_page
from financial_page import render_financial_page


def main():
    st.set_page_config(
        page_title="AI Dashboard",
        page_icon="🧠",
        layout="wide"
    )

    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Go to:",
        ["Chatbot", "Financial Extraction"]
    )

    if page == "Chatbot":
        render_chat_page()
    elif page == "Financial Extraction":
        render_financial_page()


if __name__ == "__main__":
    main()
