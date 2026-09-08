from proctoring.yolo_model import model


def detect_persons(frame):
    """
    Returns the number of people detected in the frame.
    """

    results = model(frame, verbose=False)

    person_count = 0

    for result in results:
        for box in result.boxes:

            class_id = int(box.cls[0])

            # COCO class 0 = Person
            if class_id == 0:
                person_count += 1

    return person_count