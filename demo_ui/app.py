import streamlit as st
from PIL import Image

# Page Configuration
st.set_page_config(page_title="VisionAeye Demo", layout="wide")

# Header
st.title("VisionAeye Demo")

# Upload Section
st.subheader("Upload your image and enter a prompt")

# Initialize session state for storing responses and images
if "response" not in st.session_state:
    st.session_state["response"] = ""
if "uploaded_image" not in st.session_state:
    st.session_state["uploaded_image"] = None

# Image Upload and Prompt Input
uploaded_image = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"], key="image_upload")
prompt_text = st.text_input("Enter your prompt here:", key="prompt_input")

# Submit Button
if st.button("Send"):
    if uploaded_image and prompt_text:
        # Placeholder response logic
        response = "This is a simulated response for the provided input."
        st.session_state["response"] = response
        st.session_state["uploaded_image"] = uploaded_image
    else:
        st.warning("Please upload an image and enter a prompt before submitting.")

# Split Layout Display
col1, col2 = st.columns(2)

# Left Column: Response Display
with col1:
    st.subheader("Response")
    if st.session_state["response"]:
        st.markdown(
            f"""
            <div style='background-color: #f9f9f9; padding: 10px; border-radius: 5px; border: 1px solid #ddd;'>
                <p style='font-family: Arial; color: #333333;'><b>Response:</b> <span style='color: #555555;'>{st.session_state["response"]}</span></p>
                <textarea placeholder='Type your next question here...' style='width: 100%; height: 100px;'></textarea>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("Response will appear here after submission.")

# Right Column: Image Display
with col2:
    st.subheader("Uploaded Image")
    if st.session_state["uploaded_image"]:
        image = Image.open(st.session_state["uploaded_image"])
        st.image(image, caption="Uploaded Image", use_container_width=True)
    else:
        st.info("Uploaded image will appear here.")
