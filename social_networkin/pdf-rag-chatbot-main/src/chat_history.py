import streamlit as st


def initialize_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def add_message(role, content, sources=None, retrieved_chunks=None):
    st.session_state.chat_history.append(
        {
            "role": role,
            "content": content,
            "sources": sources or [],
            "retrieved_chunks": retrieved_chunks or [],
        }
    )


def render_chat_history():
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

            if message["sources"]:
                st.markdown("**Sources**")
                for source in message["sources"]:
                    st.caption(f"{source['source']} - page {source['page']}")
