import cv2
import mediapipe as mp

mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.6
)


def detect_face(frame):
    """
    Detects whether a face is present.
    Returns:
        True  -> Face detected
        False -> No face detected
    """

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_detector.process(rgb)

    if results.detections:
        return True

    return False