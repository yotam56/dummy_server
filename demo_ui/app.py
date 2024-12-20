import streamlit as st
import time
from PIL import Image
import tempfile

from mock import mock_video_description
from gpt_connector import encode_image_to_base, analyze_image_with_chatgpt
from video_anlyzer import analyze_video

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

# Initialize session state
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

if "show_chat" not in st.session_state:
    st.session_state["show_chat"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi! How can I help you today?"}
    ]

# Typing animation function for line-by-line output
def typing_animation(full_text, chat_container, message_list, delay=1):
    """
    Prints the response line by line with a short delay.
    """
    lines = full_text.strip().split("\n")
    for line in lines:
        message_list.append({"role": "bot", "content": line})
        render_analysis_chat(chat_container, message_list)
        time.sleep(delay)

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
    def render_analysis_chat(container, messages):
        """Renders the video analysis chat messages."""
        chat_html = "<div class='chat-container'>"
        for message in messages:
            if message["role"] == "user":
                chat_html += f"<div class='user-message'><b>You:</b> {message['content']}</div>"
            else:
                chat_html += f"<div class='bot-message'>{message['content']}</div>"
        chat_html += "</div>"
        container.markdown(chat_html, unsafe_allow_html=True)

    video_chat_container = st.empty()
    render_analysis_chat(video_chat_container, st.session_state["video_messages"])

with col2:
    if st.session_state["uploaded_file"] and st.session_state["file_type"] == "image":
        # Display image
        image = Image.open(st.session_state["uploaded_file"])
        image = image.resize((300, 300))
        st.image(image, caption="Uploaded Image", use_container_width=True)
    elif st.session_state["uploaded_file"] and st.session_state["file_type"] == "video":
        st.video(st.session_state["uploaded_file"], format="video/mp4", start_time=0)
        if st.button("Play Video"):
            if not st.session_state["video_played"]:
                focus_prompt = ''  # The focus_prompt remains empty here as per previous logic

                # Save the uploaded video to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_extension) as temp:
                    temp.write(st.session_state["uploaded_file"].read())
                    temp_path = temp.name

                # Analyze video
                explanations_map, final_res, previous_explanations_string = analyze_video(
                    video_path=temp_path,
                    focus_prompt=focus_prompt
                )

                # Prepare response text for line-by-line animation
                response_text = ""
                for sec, explanation in explanations_map.items():
                    response_text += f"{sec} {explanation}\n"
                response_text += f"Final summary: {final_res}\n"

                st.session_state["video_played"] = True
                typing_animation(
                    response_text.strip(),
                    video_chat_container,
                    st.session_state["video_messages"],
                    delay=0.5
                )

# Place the Chat button at the bottom under all objects from the left
st.divider()
if st.button("Chat"):
    st.session_state["show_chat"] = not st.session_state["show_chat"]

# If the chat modal is open, display the provided chat interface
if st.session_state["show_chat"]:
    st.markdown("### Chat")
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Enter Your Prompt Here"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Handle image or video responses
        if st.session_state["uploaded_file"] and st.session_state["file_type"] == "image":
            image_base64 = encode_image_to_base(Image.open(st.session_state["uploaded_file"]))
            response = analyze_image_with_chatgpt(image_base64, prompt=prompt)
        else:
            response = "Video analysis for custom prompts after initial focus is not implemented."

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
