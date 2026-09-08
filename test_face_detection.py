import cv2

from proctoring.face_detection import detect_face

camera = cv2.VideoCapture(0)

while True:

    success, frame = camera.read()

    if not success:
        break

    face_found = detect_face(frame)

    if face_found:

        cv2.putText(
            frame,
            "Face Detected",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    else:

        cv2.putText(
            frame,
            "No Face",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,0,255),
            2
        )

    cv2.imshow("AssessIQ AI - Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()