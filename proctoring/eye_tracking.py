import cv2
import mediapipe as mp
_mesh=mp.solutions.face_mesh.FaceMesh(static_image_mode=False,max_num_faces=1,refine_landmarks=True,min_detection_confidence=.55,min_tracking_confidence=.55)
def eye_state(frame):
    result=_mesh.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    if not result.multi_face_landmarks:return 'FACE_NOT_VISIBLE'
    # Iris position within each eye gives a stable, intentionally forgiving focus heuristic.
    points=result.multi_face_landmarks[0].landmark; left=(points[468].x-points[33].x)/(points[133].x-points[33].x); right=(points[473].x-points[362].x)/(points[263].x-points[362].x)
    average=(left+right)/2
    return 'LOOKING_AT_SCREEN' if .25 <= average <= .75 else ('LOOKING_LEFT' if average < .25 else 'LOOKING_RIGHT')
