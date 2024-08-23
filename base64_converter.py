import base64

def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read()).decode('utf-8')
            return base64_string
    except FileNotFoundError:
        return "File not found. Please provide a valid image path."
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage:
image_path = "images/car stolen.png"
base64_string = image_to_base64(image_path)
print(base64_string)
