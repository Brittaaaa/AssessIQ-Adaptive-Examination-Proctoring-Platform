import cv2

from proctoring.phone_detection import detect_phone

camera = cv2.VideoCapture(0)

while True:

    success, frame = camera.read()

    if not success:
        break

    phone_found = detect_phone(frame)

    if phone_found:

        text = "Phone Detected"
        color = (0, 0, 255)

    else:

        text = "No Phone"
        color = (0, 255, 0)

    cv2.putText(
        frame,
        text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        2
    )

    cv2.imshow("AssessIQ AI - Phone Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()