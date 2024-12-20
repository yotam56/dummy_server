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
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "file_type" not in st.session_state:
    st.session_state["file_type"] = None
if "video_played" not in st.session_state:
    st.session_state["video_played"] = False
if "waiting_for_response" not in st.session_state:
    st.session_state["waiting_for_response"] = False

def render_chat(container):
    """Renders the chat messages in a single container."""
    chat_html = "<div class='chat-container'>"
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            chat_html += f"<div class='user-message'><b>You:</b> {message['content']}</div>"
        else:
            chat_html += f"<div class='bot-message'>{message['content']}</div>"
    chat_html += "</div>"
    container.markdown(chat_html, unsafe_allow_html=True)

def typing_animation(full_text, chat_container, delay=1):
    """
    Prints the response line by line with a short delay.
    """
    lines = full_text.strip().split("\n")
    for line in lines:
        st.session_state["messages"].append({"role": "bot", "content": line})
        render_chat(chat_container)
        time.sleep(delay)

# File uploader at the top (now supports videos)
uploaded_file = st.file_uploader("Upload an Image or Video", type=["png", "jpg", "jpeg", "mp4", "mov"])
st.markdown("<h2 style='text-align: left;'>Chat</h2>", unsafe_allow_html=True)

if uploaded_file:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension in ["png", "jpg", "jpeg"]:
        st.session_state["file_type"] = "image"
        st.session_state["uploaded_file"] = uploaded_file
    elif file_extension in ["mp4", "mov"]:
        st.session_state["file_type"] = "video"
        st.session_state["uploaded_file"] = uploaded_file

    # Add a question in the chat box after uploading a file (only once)
    if not st.session_state["waiting_for_response"]:
        time.sleep(0.7)
        st.session_state["messages"].append({"role": "bot", "content": "“Is there anything specific you would like me to focus on? If so, could you please elaborate?”"})
        st.session_state["waiting_for_response"] = True

col1, col2 = st.columns([2, 1])

with col1:
    # Create the single chat container here, on the left side
    chat_container = st.empty()
    prompt_text = st.text_input("Enter your prompt here:", key="prompt_input")
    if st.button("Send"):
        # Your existing code for handling the "Send" button
        if st.session_state["uploaded_file"] and prompt_text:
            st.session_state["messages"].append({"role": "user", "content": prompt_text})
            render_chat(chat_container)

            if st.session_state["waiting_for_response"]:
                st.session_state["messages"].append({"role": "bot", "content": "Got it!"})
                st.session_state["waiting_for_response"] = False
                time.sleep(0.5)
                render_chat(chat_container)
            else:
                if st.session_state["file_type"] == "image":
                    image_base64 = encode_image_to_base(Image.open(st.session_state["uploaded_file"]))
                    response = analyze_image_with_chatgpt(image_base64, prompt=prompt_text)
                    typing_animation(response, chat_container)
                else:
                    response = "Video analysis for custom prompts after initial focus is not implemented."
                    typing_animation(response, chat_container)
        else:
            st.warning("Please upload a file and enter a prompt.")

    # Initial render
    render_chat(chat_container)

with col2:
    if st.session_state["uploaded_file"] and st.session_state["file_type"] == "image":
        # Display image
        image = Image.open(st.session_state["uploaded_file"])
        image = image.resize((300, 300))
        st.image(image, caption="Uploaded Image", use_container_width=True)
    elif st.session_state["uploaded_file"] and st.session_state["file_type"] == "video":
        st.video(st.session_state["uploaded_file"], format="video/mp4", start_time=0)
        if st.button("Play Video"):
            st.session_state["waiting_for_response"] = False
            if not st.session_state["video_played"]:
                # Determine focus_prompt
                focus_prompt = ''
                user_focus_response = ""
                for msg in reversed(st.session_state["messages"]):
                    if msg["role"] == "user":
                        user_focus_response = msg["content"].strip()
                        break

                if user_focus_response.lower().startswith("yes"):
                    focus_prompt = user_focus_response

                # Save the uploaded video to a temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_extension) as temp:
                    temp.write(st.session_state["uploaded_file"].read())
                    temp_path = temp.name

                # Analyze video
                explanations_map, final_res, previous_explanations_string = analyze_video(
                    video_path=temp_path,
                    focus_prompt=focus_prompt
                )

                # Append results to chat
                response_text = ""
                for sec, explanation in explanations_map.items():
                    response_text += f"{sec} {explanation}\n"
                response_text += f"Final summary: {final_res}\n"

                st.session_state["video_played"] = True
                # Use the existing chat_container in col1
                typing_animation(response_text, chat_container)

    render_chat(chat_container)
