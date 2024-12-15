
import cv2
import base64
import numpy as np
from PIL import Image
import openai

def encode_image_to_base(image) -> str:
    """
    Encodes a given image to a base64 string. The image can be a NumPy array,
    a PIL image, or other formats convertible to a NumPy array.

    Args:
        image: The input image, either as a NumPy array or a PIL Image.

    Returns:
        str: The base64 encoded string of the image in JPEG format.

    Raises:
        TypeError: If the input is not a NumPy array or PIL Image.
        ValueError: If the encoding fails.
    """
    try:
        # Check if the image is a PIL Image and convert to NumPy array
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Ensure the image is a NumPy array
        if not isinstance(image, np.ndarray):
            raise TypeError("Input must be a NumPy array or PIL image.")

        # Encode the image to JPEG format
        success, buffer = cv2.imencode(".jpg", image)
        if not success:
            raise ValueError("Image encoding to JPEG failed.")

        # Convert the encoded image to base64
        image_base64 = base64.b64encode(buffer).decode("utf-8")
        return image_base64

    except Exception as e:
        raise

default_prompt = f"Please provide a very detailed explanation of what is visible in this image, including objects, context, and any notable details."
def analyze_image_with_chatgpt(image_base64, prompt = default_prompt):
    response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt,
            },
            {
            "type": "image_url",
            "image_url": {
                "url":  f"data:image/jpeg;base64,{image_base64}"
            },
            },
        ],
        }
    ],
    )
    return response.choices[0].message.content.strip()