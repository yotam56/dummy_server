import streamlit as st
from PIL import Image
# Import from your gpt_connector file (adjust the import path as needed)
from gpt_connector import encode_image_to_base, analyze_image_with_chatgpt

# Page Configuration
st.set_page_config(page_title="VisionAeye Demo", layout="wide")

# Custom CSS for ChatGPT-like UI with Scroll and Height Limit
st.markdown(
    """
    <style>
        .chat-container {
            background-color: #333333;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.3);
            margin-bottom: 15px;
            height: 500px; /* Match image height */
            overflow-y: scroll;
        }
        .user-message {
            background-color: #555555;
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            text-align: right;
        }
        .bot-message {
            background-color: #444444;
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            text-align: left;
        }
        .input-box {
            margin-top: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.title("VisionAeye Demo")

# Upload Section
st.subheader("Upload your image and enter a prompt")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "uploaded_image" not in st.session_state:
    st.session_state["uploaded_image"] = None
if "initial_prompt_sent" not in st.session_state:
    st.session_state["initial_prompt_sent"] = False

# Image Upload and Prompt Input
uploaded_image = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"], key="image_upload")

# Disable the prompt input after first submission
if not st.session_state["initial_prompt_sent"]:
    prompt_text = st.text_input("Enter your prompt here:", key="prompt_input")
else:
    prompt_text = st.text_input("Enter your prompt here:", key="prompt_input", disabled=True)

# Submit Button for Initial Prompt
if st.button("Send"):
    if uploaded_image and prompt_text:
        # User message
        st.session_state["messages"].append({"role": "user", "content": prompt_text})
        
        # Convert uploaded image to PIL Image
        image = Image.open(uploaded_image)
        # Encode image to base64
        image_base64 = encode_image_to_base(image)
        
        # Call GPT function to analyze image and prompt
        response = analyze_image_with_chatgpt(image_base64, prompt=prompt_text)
        
        # Append bot response
        st.session_state["messages"].append({"role": "bot", "content": response})
        st.session_state["uploaded_image"] = uploaded_image
        st.session_state["initial_prompt_sent"] = True
    else:
        st.warning("Please upload an image and enter a prompt before submitting.")

# Split Layout Display
col1, col2 = st.columns(2)

# Right Column: Image Display
with col2:
    st.subheader("Uploaded Image")
    if st.session_state["uploaded_image"]:
        image = Image.open(st.session_state["uploaded_image"])
        st.image(image, caption="Uploaded Image", use_container_width=True)
    else:
        st.info("Uploaded image will appear here.")

# Left Column: Chat Display
with col1:
    st.subheader("Chat")
    chat_html = "<div class='chat-container'>"
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            chat_html += f"<div class='user-message'><b>You:</b> {message['content']}</div>"
        else:
            chat_html += f"<div class='bot-message'><b>Response:</b> {message['content']}</div>"
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)