from ultralytics import YOLO

# Load once when the application starts
model = YOLO("yolov8n.pt")