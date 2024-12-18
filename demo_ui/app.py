import streamlit as st
import time
from PIL import Image
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
if "uploaded_image" not in st.session_state:
    st.session_state["uploaded_image"] = None

# Typing Animation Function
def typing_animation(message_index, text, chat_container, delay=0.05):
    """Dynamically update the chat with a typing effect."""
    for char in text:
        st.session_state["messages"][message_index]["content"] += char
        render_chat(chat_container)
        time.sleep(delay)

# Function to render chat
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

# File uploader at the top
uploaded_image = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

# Create the layout for chat and image side-by-side
col1, col2 = st.columns([2, 1])

with col2:
    # Display the uploaded image if available, resized to fit the predefined box
    if uploaded_image:
        st.session_state["uploaded_image"] = uploaded_image
        image = Image.open(uploaded_image)
        image = image.resize((new_width, new_height))  # Resize image to fit predefined box
        st.image(image, caption="Uploaded Image", use_container_width=True)

with col1:
    st.subheader("Chat")
    chat_container = st.empty()  # Single container for the chat display

    # Input and Button
    prompt_text = st.text_input("Enter your prompt here:", key="prompt_input")
    if st.button("Send"):
        if uploaded_image and prompt_text:
            # Add user message
            st.session_state["messages"].append({"role": "user", "content": prompt_text})
            render_chat(chat_container)  # Update the chat to show user input

            # Convert image to base64 and analyze with GPT
            image_base64 = encode_image_to_base(Image.open(uploaded_image))
            response = analyze_image_with_chatgpt(image_base64, prompt=prompt_text)

            # Add bot message and update with typing animation
            st.session_state["messages"].append({"role": "bot", "content": ""})
            typing_animation(len(st.session_state["messages"]) - 1, response, chat_container)
        else:
            st.warning("Please upload an image and enter a prompt.")

    # Initial render of chat history
    render_chat(chat_container)
