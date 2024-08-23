import cv2

def run_rtsp_stream():
    uri = "rtsp://admin:kohav3103@149.106.255.141:57373/Streaming/Channels/101"
    cap = cv2.VideoCapture(uri)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        cv2.imshow("RTSP Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_rtsp_stream()
