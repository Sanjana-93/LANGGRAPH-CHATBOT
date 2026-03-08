import streamlit as st
import time
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {"configurable": {"thread_id": "thread-1"}}

if "message_history" not in st.session_state:
    st.session_state.message_history = []

# display chat history
for message in st.session_state.message_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type here")

if user_input:

    # show user message
    st.session_state.message_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # assistant response streaming
    with st.chat_message("assistant"):

        message_placeholder = st.empty()
        full_response = ""

        for message_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages",
        ):
            if message_chunk.content:
        for char in message_chunk.content:
            full_response += char
            message_placeholder.markdown(full_response)
            time.sleep(0.01)
            
    st.session_state.message_history.append(
        {"role": "assistant", "content": full_response}
    )

