import os
import cv2
import base64
import openai


def get_video_frames_per_second(video_path):
    """
    Generator that yields (second, frame) tuples from the video.
    For each second in the video, we extract one frame.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("Could not open video.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = int(total_frames / fps) if fps > 0 else 0

    # For each second in the duration, we seek to that frame and read it
    for sec in range(duration):
        frame_num = int(sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if not ret:
            break
        yield sec, frame

    cap.release()

def frame_to_base64(frame):
    """
    Convert a frame (numpy array) to a base64-encoded JPEG.
    """
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        raise RuntimeError("Failed to encode frame to JPEG.")
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text

def analyze_image_with_chatgpt(image_base64, second, previous_explanations = "", summarize_promt = ""):
    """
    Send the image to ChatGPT for a detailed explanation.
    Include the entire history of previous explanations in the prompt.
    """
    # Build a prompt that includes all previous context
    if summarize_promt != "":
        prompt = summarize_promt
        print(f'Summarize prompt: \n {prompt}')
    else:
        prompt = (
            f"Here is the narrative so far, up to second {second - 1}:\n"
            f"{previous_explanations}\n\n"
            f"Now at second {second}, analyze this new frame. Please provide a very detailed explanation "
            f"of what is visible in this image, building on the previous context and maintaining continuity."
        )
        print(f'Prompt for second {second}: \n {prompt}')

    # Use a ChatCompletion endpoint for GPT-4 (adjust model as needed)
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

def summarize_entire_video(previous_explanations):
    """
    Creates a prompt that includes all previous frame-by-frame explanations and
    asks the model to produce a unified, continuous narrative of the video as if
    a viewer is watching it unfold in real-time, integrating all the past details
    smoothly.
    """
    prompt = (
        "Below are detailed, second-by-second explanations of a video:\n\n"
        f"{previous_explanations}\n\n"
        "Please use this information to provide a continuous, straightforward explanation "
        "of what occurs in the video from start to finish. Do not list events by the second. "
        "Instead, combine all the details into one plain, coherent description that "
        "accurately reflects everything observed, maintaining an understanding of the sequence "
        "of events as they happen over time."
    )
    return prompt


def main():
    # Hard-coded path to your local MP4 file
    video_path = "/Users/nadavkurin/coding/VisionAEye/detector-server/WhatsApp Video 2024-12-15 at 19.06.52.mp4"

    explanations = {}
    previous_explanations = ""  # Will hold a string of all previous explanations for context
    frame_count = 0

    # Extract frames per second and analyze
    for sec, frame in get_video_frames_per_second(video_path):
        # if frame_count > 5:
        #     break
        image_b64 = frame_to_base64(frame)

        # Pass all previous explanations as context
        explanation = analyze_image_with_chatgpt(image_b64, sec, previous_explanations = previous_explanations)

        print(f"Explanation for second {sec}:\n{explanation}\n")

        # Store this explanation and append it to the running context
        explanations[sec] = explanation
        previous_explanations += f"Second {sec}: {explanation}\n\n"

        frame_count += 1
    
    final_res = analyze_image_with_chatgpt(image_b64, sec, previous_explanations = "", summarize_promt=summarize_entire_video(previous_explanations))
    print(f'Final result: \n {final_res}')
    # # Print the resulting dictionary
    # for second, expl in explanations.items():
    #     print(f"Second {second}:\n{expl}\n")

if __name__ == "__main__":
    main()