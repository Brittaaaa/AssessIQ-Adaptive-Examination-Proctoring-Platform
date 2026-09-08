import os
from proctoring.yolo_model import model
YOLO_CONFIDENCE=float(os.environ.get('YOLO_CONFIDENCE','0.40'))
TARGETS={0:'person',67:'cell phone',73:'book'}
def detect_objects(frame):
    found=[]
    for result in model(frame, verbose=False, conf=YOLO_CONFIDENCE, imgsz=640):
        for box in result.boxes:
            cls=int(box.cls[0]); conf=float(box.conf[0])
            if cls in TARGETS: found.append({'label':TARGETS[cls],'confidence':round(conf,3)})
    return {'person_count':sum(x['label']=='person' for x in found),'phone':any(x['label']=='cell phone' for x in found),'book':any(x['label']=='book' for x in found),'detections':found}
