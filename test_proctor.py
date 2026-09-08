import cv2

from proctoring.proctor import verify_candidate

camera = cv2.VideoCapture(0)

while True:

    success, frame = camera.read()

    if not success:
        break

    status = verify_candidate(frame)

    y = 40

    for key, value in status.items():

        color = (0,255,0) if value else (0,0,255)

        text = f"{key.upper()} : {'PASS' if value else 'FAIL'}"

        cv2.putText(
            frame,
            text,
            (20,y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

        y += 40

    cv2.imshow("AssessIQ AI - AI Verification", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()