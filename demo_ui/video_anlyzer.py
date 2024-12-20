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


def analyze_image_with_chatgpt(image_base64, second, previous_explanations="", focus_prompt=""):
    if focus_prompt != "":
        prompt = (
            f"Here is the narrative so far, up to second {second - 1}:\n"
            f"{previous_explanations}\n\n"
            f"Now at second {second}, analyze this new frame. Please provide a very detailed explanation "
            f"of what is visible in this image, building on the previous context and maintaining continuity.\n"
            f"Focus specifically on: {focus_prompt}.\n"
            f"Each response should be no more than 15 words."
        )
    else:
        prompt = (
            f"Here is the narrative so far, up to second {second - 1}:\n"
            f"{previous_explanations}\n\n"
            f"Now at second {second}, analyze this new frame. Please provide a very detailed explanation "
            f"of what is visible in this image, building on the previous context and maintaining continuity."
            f"each response should be no more than 15 words."
        )
        # print(f'Prompt for second {second}: \n {prompt}')

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
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content.strip()


def summarize_request(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": "Your task is to generate a summary of a video based on a prior second-by-second analysis."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content.strip()


def general_request(prompt, content=None):
    messages = []
    if content:
        messages.append({"role": "system", "content": content})
    messages.append({"role": "user", "content": prompt})

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content.strip()


def summarize_entire_video_prompt(previous_explanations):
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

    # Hard-coded path to your local MP4 file


def analyze_video(video_path="videos/pigua.mp4", focus_prompt=""):
    explanations_map = {}
    previous_explanations_string = ""  # Will hold a string of all previous explanations for context
    frame_count = 0

    # Extract frames per second and analyze
    for sec, frame in get_video_frames_per_second(video_path):
        # Format sec as MM:SS
        minutes, seconds = divmod(sec, 60)
        formatted_sec = f"{minutes:02}:{seconds:02}"

        image_b64 = frame_to_base64(frame)

        # Pass all previous explanations as context
        explanation = analyze_image_with_chatgpt(
            image_b64, sec,
            previous_explanations=previous_explanations_string,
            focus_prompt=focus_prompt
        )

        explanations_map[formatted_sec] = explanation
        previous_explanations_string += f"Second {formatted_sec}: {explanation}.\n\n"

        frame_count += 1

    final_res = summarize_request(prompt=summarize_entire_video_prompt(previous_explanations_string))

    return explanations_map, final_res, previous_explanations_string


if __name__ == "__main__":
    explanations, final_res, _ = analyze_video()
    for sec, explanation in explanations.items():
        print(f'Second {sec}: \n {explanation} \n')

    print(f'Summary: {final_res}')