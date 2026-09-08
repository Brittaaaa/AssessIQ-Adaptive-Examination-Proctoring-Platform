from proctoring.face_detection import detect_face
from proctoring.eye_tracking import eye_state
from proctoring.object_detection import detect_objects
def verify_candidate(frame):
    objects=detect_objects(frame); state=eye_state(frame)
    return {'camera':True,'face':detect_face(frame),'person':objects['person_count']==1,'person_count':objects['person_count'],'phone':objects['phone'],'book':objects['book'],'eye':state=='LOOKING_AT_SCREEN','eye_state':state,'detections':objects['detections']}
