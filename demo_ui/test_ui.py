import streamlit as st
import time
from PIL import Image
import tempfile

from mock import mock_video_description
from gpt_connector import encode_image_to_base, analyze_image_with_chatgpt
from video_anlyzer import analyze_video, general_request

# Page Configuration
st.set_page_config(page_title="VisionAeye Demo", layout="wide")

# Define static sizes
chat_height = 400
new_width = 300
new_height = 300

# Custom CSS for ChatGPT-like UI and static height
st.markdown(
    f"""
    <style>
        .chat-container {{
            background-color: #333333;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.3);
            overflow-y: auto;
            height: {chat_height}px;
        }}
        .user-message {{
            background-color: #555555;
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            text-align: right;
        }}
        .bot-message {{
            background-color: #444444;
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            text-align: left;
        }}
        .image-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.title("VisionAeye Demo")

# Initialize session state for the analysis chat and uploads
if "video_messages" not in st.session_state:
    st.session_state["video_messages"] = []
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "file_type" not in st.session_state:
    st.session_state["file_type"] = None
if "video_played" not in st.session_state:
    st.session_state["video_played"] = False
if "waiting_for_response" not in st.session_state:
    st.session_state["waiting_for_response"] = False

# Initialize session state for modal chat visibility and messages
if "show_chat" not in st.session_state:
    st.session_state["show_chat"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi! How can I help you today?"}
    ]

# Button to toggle chat modal
if st.button("Chat"):
    st.session_state["show_chat"] = not st.session_state["show_chat"]

# File uploader (supports images and videos)
uploaded_file = st.file_uploader("Upload an Image or Video", type=["png", "jpg", "jpeg", "mp4", "mov"])
st.markdown("<h2 style='text-align: left;'>Video Analysis Chat</h2>", unsafe_allow_html=True)

if uploaded_file:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension in ["png", "jpg", "jpeg"]:
        st.session_state["file_type"] = "image"
        st.session_state["uploaded_file"] = uploaded_file
    elif file_extension in ["mp4", "mov"]:
        st.session_state["file_type"] = "video"
        st.session_state["uploaded_file"] = uploaded_file

col1, col2 = st.columns([2, 1])

# Left column: Video analysis chat display only
with col1:
    # Just display whatever is in video_messages
    def render_analysis_chat():
        chat_html = "<div class='chat-container'>"
        for message in st.session_state["video_messages"]:
            if message["role"] == "user":
                chat_html += f"<div class='user-message'><b>You:</b> {message['content']}</div>"
            else:
                chat_html += f"<div class='bot-message'>{message['content']}</div>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

    video_chat_container = st.empty()
    render_analysis_chat()

# Right column: Display uploaded media
with col2:
    if st.session_state["uploaded_file"] and st.session_state["file_type"] == "image":
        # Display image
        image = Image.open(st.session_state["uploaded_file"])
        image = image.resize((300, 300))
        st.image(image, caption="Uploaded Image", use_container_width=True)
    elif st.session_state["uploaded_file"] and st.session_state["file_type"] == "video":
        st.video(st.session_state["uploaded_file"], format="video/mp4", start_time=0)
        if st.button("Play Video"):
            # Once play is clicked, analyze video
            if not st.session_state["video_played"]:
                focus_prompt = ''
                # Since we removed GPT conversation logic, focus_prompt is empty here
                # In future, if you reintroduce logic to determine focus from user responses, you can do it here.

                # Save the uploaded video to a temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_extension) as temp:
                    temp.write(st.session_state["uploaded_file"].read())
                    temp_path = temp.name

                # Analyze video
                explanations_map, final_res, previous_explanations_string = analyze_video(
                    video_path=temp_path,
                    focus_prompt=focus_prompt
                )

                # Append results to video_messages
                response_text = ""
                for sec, explanation in explanations_map.items():
                    response_text += f"{sec} {explanation}\n"
                response_text += f"Final summary: {final_res}\n"

                st.session_state["video_played"] = True
                # Add to video_messages as bot role
                for line in response_text.strip().split("\n"):
                    st.session_state["video_messages"].append({"role": "bot", "content": line})
                render_analysis_chat()

# If the chat modal is open, display the provided chat interface
if st.session_state["show_chat"]:
    st.markdown("### Chat")
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Enter Your Prompt Here"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response using general_request
        reply = general_request(prompt=prompt)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": reply})
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(reply)
