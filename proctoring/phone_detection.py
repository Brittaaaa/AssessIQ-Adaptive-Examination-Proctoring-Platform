from proctoring.yolo_model import model

def detect_phone(frame):

    results = model(frame, verbose=False)

    detected_phone = False

    for result in results:
        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            print(
                "Detected:",
                model.names[class_id],
                "| Confidence:",
                round(confidence, 2)
            )

            if model.names[class_id] == "cell phone" and confidence > 0.25:
                detected_phone = True

    return detected_phone