import cv2
from ultralytics import YOLO
from collections import defaultdict
import numpy as np

class PeopleCounter:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)
        self.track_history = defaultdict(lambda: [])
        
    def detect_and_track(self, frame):
        results = self.model.track(frame, persist=True, classes=[0], verbose=False)
        
        detections = []
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            confidences = results[0].boxes.conf.cpu().numpy()
            
            for box, track_id, conf in zip(boxes, track_ids, confidences):
                x1, y1, x2, y2 = box
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                
                detections.append({
                    'id': track_id,
                    'bbox': (int(x1), int(y1), int(x2), int(y2)),
                    'center': (cx, cy),
                    'confidence': conf
                })
                
                self.track_history[track_id].append((cx, cy))
                if len(self.track_history[track_id]) > 30:
                    self.track_history[track_id].pop(0)
        
        return detections
    
    def draw_detections(self, frame, detections):
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            cx, cy = det['center']
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 255, 255), -1)
            cv2.putText(frame, f"ID:{det['id']}", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            if det['id'] in self.track_history:
                points = np.array(self.track_history[det['id']], np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [points], False, (0, 255, 0), 2)
        
        return frame
