import cv2
import concurrent.futures
import time

# Correct camera connection details
username = "admin"
password = "kohav3103"
ip_address = "149.106.255.141"
port = 57373  # RTSP typically uses port 554


# Define the function to test a single RTSP channel
def test_rtsp_channel(channel):
    rtsp_url = f"rtsp://{username}:{password}@{ip_address}:{port}/Streaming/Channels/{channel}01"
    print(f"Trying RTSP URL: {rtsp_url}")

    cap = cv2.VideoCapture(rtsp_url)

    start_time = time.time()

    # Timeout in seconds
    timeout = 10

    while True:
        # Check if the connection is opened
        if not cap.isOpened():
            print(f"Failed to open RTSP stream for channel {channel}")
            return False

        # Attempt to read the frame
        ret, frame = cap.read()

        # Break if we fail to grab a frame
        if not ret:
            print(f"Failed to grab frame for channel {channel}")
            break

        # Show the frame
        cv2.imshow(f'RTSP Stream Channel {channel}', frame)

        # Press 'q' to exit the stream display
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Check if the timeout has been reached
        if time.time() - start_time > timeout:
            print(f"Timeout reached for channel {channel}")
            break

    cap.release()
    cv2.destroyAllWindows()
    return True


# List of relevant channels (adjust according to your setup)
channels = list(range(1, 11))  # Testing channels 1 to 52

# Maximum number of threads to run in parallel
max_threads = 10  # Adjust this depending on your system's capability


def main():
    # Use ThreadPoolExecutor for concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Map each channel to the test function
        future_to_channel = {executor.submit(test_rtsp_channel, channel): channel for channel in channels}

        # Iterate through completed futures
        for future in concurrent.futures.as_completed(future_to_channel):
            channel = future_to_channel[future]
            try:
                # Adding a timeout of 20 seconds for each future to complete
                result = future.result(timeout=20)
                if result:
                    print(f"Successfully streamed channel {channel}")
                    break  # Stop once a valid channel is found
            except concurrent.futures.TimeoutError:
                print(f"Timeout error on channel {channel}")
            except Exception as e:
                print(f"Error occurred while streaming channel {channel}: {e}")


if __name__ == "__main__":
    main()
