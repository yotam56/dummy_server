import streamlit as st
import time
from PIL import Image

from mock import mock_video_description
from gpt_connector import encode_image_to_base, analyze_image_with_chatgpt

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
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "file_type" not in st.session_state:
    st.session_state["file_type"] = None
if "video_played" not in st.session_state:
    st.session_state["video_played"] = False

def render_chat(container):
    """Renders the chat messages in a single container."""
    chat_html = "<div class='chat-container'>"
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            chat_html += f"<div class='user-message'><b>You:</b> {message['content']}</div>"
        else:
            chat_html += f"<div class='bot-message'><b>Response:</b> {message['content']}</div>"
    chat_html += "</div>"
    container.markdown(chat_html, unsafe_allow_html=True)

def typing_animation(message_index, full_text, chat_container, delay=1):
    """
    Prints the mock description line by line with a short delay.
    Each line is separated by a blank line for spacing.
    """
    st.session_state["messages"][message_index]["content"] = ""
    lines = full_text.strip().split("\n")
    for line in lines:
        # Add the current line to the bot's message content
        st.session_state["messages"][message_index]["content"] += line + "\n\n"
        render_chat(chat_container)
        time.sleep(delay)

# File uploader at the top (now supports videos)
uploaded_file = st.file_uploader("Upload an Image or Video", type=["png", "jpg", "jpeg", "mp4", "mov"])

# Determine file type if uploaded
if uploaded_file:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension in ["png", "jpg", "jpeg"]:
        st.session_state["file_type"] = "image"
        st.session_state["uploaded_file"] = uploaded_file
    elif file_extension in ["mp4", "mov"]:
        st.session_state["file_type"] = "video"
        st.session_state["uploaded_file"] = uploaded_file

# Create the layout for chat and image/video side-by-side
col1, col2 = st.columns([2, 1])

with col2:
    # Display the uploaded file depending on its type
    if st.session_state["uploaded_file"] and st.session_state["file_type"] == "image":
        image = Image.open(st.session_state["uploaded_file"])
        image = image.resize((new_width, new_height))  # Resize image to fit predefined box
        st.image(image, caption="Uploaded Image", use_container_width=True)
    elif st.session_state["uploaded_file"] and st.session_state["file_type"] == "video":
        st.video(st.session_state["uploaded_file"], format="video/mp4", start_time=0)
        # Add a play button to simulate starting the video
        if st.button("Play Video"):
            # If not played before, trigger the mock description
            if not st.session_state["video_played"]:
                st.session_state["video_played"] = True
                # Add a bot message for the mock video description
                st.session_state["messages"].append({"role": "bot", "content": ""})

with col1:
    st.subheader("Chat")
    chat_container = st.empty()  # Single container for the chat display

    # If the video has been "played" and is a video, trigger the mock typing animation
    if st.session_state["video_played"] and st.session_state["file_type"] == "video":
        # Find the last bot message index (just appended)
        bot_message_index = len(st.session_state["messages"]) - 1
        typing_animation(bot_message_index, mock_video_description(), chat_container)

    # Input and Button
    prompt_text = st.text_input("Enter your prompt here:", key="prompt_input")
    if st.button("Send"):
        if st.session_state["uploaded_file"] and prompt_text:
            # Add user message
            st.session_state["messages"].append({"role": "user", "content": prompt_text})
            render_chat(chat_container)  # Update the chat to show user input

            if st.session_state["file_type"] == "image":
                # Process the image for GPT analysis
                image_base64 = encode_image_to_base(Image.open(st.session_state["uploaded_file"]))
                response = analyze_image_with_chatgpt(image_base64, prompt=prompt_text)
            else:
                # For video, currently no processing; just a placeholder
                response = "Video analysis is not yet implemented for custom prompts."

            # Add bot message and update with typing animation
            st.session_state["messages"].append({"role": "bot", "content": ""})
            typing_animation(len(st.session_state["messages"]) - 1, response, chat_container)
        else:
            st.warning("Please upload a file and enter a prompt.")

    # Initial render of chat history (if any)
    render_chat(chat_container)
