import streamlit as st
from video_anlyzer import general_request

st.title("Chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! How can I help you today?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Enter Your Prompt Here"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response using general_request
    reply = general_request(prompt=prompt)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": reply})
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(reply)
