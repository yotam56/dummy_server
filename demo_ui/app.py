import streamlit as st
import time
from PIL import Image

from mock import mock_video_description, mock_chat_analyze
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
if "focus_prompt" not in st.session_state:
    st.session_state["focus_prompt"] = ""
if "mock_responses" not in st.session_state:
    st.session_state["mock_responses"] = mock_chat_analyze()  # Mock responses for chat
if "response_index" not in st.session_state:
    st.session_state["response_index"] = 0

if "show_chat" not in st.session_state:
    st.session_state["show_chat"] = False
if "messages" not in st.session_state:
    # On first load, we ask the user if there's a focus to set
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi! How can I help you?",
        }
    ]
    st.session_state["waiting_for_response"] = True

# Typing animation function for line-by-line output
def typing_animation_line(full_text, chat_container, message_list, delay=1.5):
    """
    Prints the response line by line with a short delay.
    """
    lines = full_text.strip().split("\n")
    for line in lines:
        message_list.append({"role": "bot", "content": line})
        render_analysis_chat(chat_container, message_list)
        time.sleep(delay)

def typing_animation_char(message_index, text, chat_container, delay=0.05):
    """Dynamically update the chat with a typing effect."""
    for char in text:
        st.session_state["messages"][message_index]["content"] += char
        render_analysis_chat(chat_container, text)
        time.sleep(delay)
# Add follow-up question in the chat
def add_follow_up_question():
    follow_up = "Is there anything else I can help you with?"
    st.session_state["messages"].append({"role": "assistant", "content": follow_up})
    with st.chat_message("assistant"):
        st.markdown(follow_up)

# File uploader (supports images and videos)
uploaded_file = st.file_uploader("Upload an Image or Video", type=["png", "jpg", "jpeg", "mp4", "mov"])

# Change the title from "Video Analysis Chat" to "Visual Analysis Chat"
st.markdown("<h2 style='text-align: left;'>Visual Analysis Chat</h2>", unsafe_allow_html=True)

if uploaded_file:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension in ["png", "jpg", "jpeg"]:
        st.session_state["file_type"] = "image"
        st.session_state["uploaded_file"] = uploaded_file
    elif file_extension in ["mp4", "mov"]:
        st.session_state["file_type"] = "video"
        st.session_state["uploaded_file"] = uploaded_file

# Layout
col1, col2 = st.columns([2, 1])

# Left column: Analysis chat display only
with col1:
    def render_analysis_chat(container, messages):
        """Renders the analysis chat messages."""
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

# Right column: Display uploaded image or video with an "Execute" button
with col2:
    if st.session_state["uploaded_file"] and st.session_state["file_type"] == "image":
        # Display image
        image = Image.open(st.session_state["uploaded_file"])
        image = image.resize((300, 300))
        st.image(image, caption="Uploaded Image", use_container_width=True)

    elif st.session_state["uploaded_file"] and st.session_state["file_type"] == "video":
        st.video(st.session_state["uploaded_file"], format="video/mp4", start_time=0)
        if st.button("Execute"):
            if not st.session_state["video_played"]:
                focus_prompt = st.session_state["focus_prompt"]  # Retrieve focus prompt (if any)

                # Simulate processing time
                time.sleep(2)

                # Use mock_video_description to generate a response
                mock_response = mock_video_description()
                time.sleep(1)

                # Display the mock response in the Visual Analysis Chat
                typing_animation_line(
                    mock_response.strip(),
                    video_chat_container,
                    st.session_state["video_messages"],
                    delay=0.5
                )
                st.session_state["video_played"] = True  # Set the video as "processed"

# Place the Chat button at the bottom
st.divider()
if st.button("Chat"):
    st.session_state["show_chat"] = not st.session_state["show_chat"]

# If the chat modal is open, display the provided chat interface
if st.session_state["show_chat"]:
    st.markdown("### Chat")
    # Display chat messages
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Enter Your Prompt Here"):
        # Add user message to chat history
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Respond with the next mock response
        if st.session_state["response_index"] < len(st.session_state["mock_responses"]):
            mock_response = st.session_state["mock_responses"][st.session_state["response_index"]]
            st.session_state["response_index"] += 1
        else:
            mock_response = "No further responses available."

        st.session_state["messages"].append({"role": "assistant", "content": mock_response})
        with st.chat_message("assistant"):
            formatted_response = mock_response.replace("\n", "<br>")  # Replace newlines with <br>
            response_container = st.empty()  # Create an empty container for the response
            current_text = ""  # Initialize the current text to display

            for char in formatted_response:
                current_text += char  # Add one character at a time
                response_container.markdown(current_text, unsafe_allow_html=True)  # Render the updated text
                time.sleep(0.02)  # Typing speed delay
