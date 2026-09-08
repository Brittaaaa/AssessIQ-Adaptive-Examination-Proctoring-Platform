import cv2

from proctoring.person_detection import detect_persons

camera = cv2.VideoCapture(0)

while True:

    success, frame = camera.read()

    if not success:
        break

    people = detect_persons(frame)

    color = (0,255,0)

    if people > 1:
        color = (0,0,255)

    cv2.putText(
        frame,
        f"People Detected : {people}",
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        2
    )

    cv2.imshow("AssessIQ AI - Person Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()