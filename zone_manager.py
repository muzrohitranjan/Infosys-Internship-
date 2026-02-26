import cv2
import json
import numpy as np
from pathlib import Path

class ZoneManager:
    def __init__(self, zones_file='zones.json'):
        self.zones_file = zones_file
        self.zones = self.load_zones()
        self.drawing = False
        self.current_zone = []
        
    def load_zones(self):
        if Path(self.zones_file).exists():
            with open(self.zones_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_zones(self):
        with open(self.zones_file, 'w') as f:
            json.dump(self.zones, f)
    
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current_zone.append([x, y])
            self.drawing = True
        elif event == cv2.EVENT_RBUTTONDOWN and self.current_zone:
            self.zones.append({'points': self.current_zone, 'count': 0})
            self.save_zones()
            self.current_zone = []
            self.drawing = False
    
    def draw_zones(self, frame):
        for idx, zone in enumerate(self.zones):
            pts = np.array(zone['points'], np.int32)
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
            cv2.putText(frame, f"Zone {idx+1}: {zone['count']}", 
                       tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        if self.current_zone:
            for pt in self.current_zone:
                cv2.circle(frame, tuple(pt), 5, (0, 0, 255), -1)
        
        return frame
    
    def point_in_zone(self, point, zone_idx):
        pts = np.array(self.zones[zone_idx]['points'], np.int32)
        return cv2.pointPolygonTest(pts, point, False) >= 0
    
    def reset_counts(self):
        for zone in self.zones:
            zone['count'] = 0

class VideoFeed:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video source: {source}")
    
    def read(self):
        ret, frame = self.cap.read()
        return ret, frame
    
    def release(self):
        self.cap.release()
    
    def get_fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)

def setup_zones(source=0):
    video = VideoFeed(source)
    zone_mgr = ZoneManager()
    
    cv2.namedWindow('Zone Setup')
    cv2.setMouseCallback('Zone Setup', zone_mgr.mouse_callback)
    
    print("Left-click to add zone points, Right-click to complete zone, 'q' to quit, 'c' to clear zones")
    
    try:
        while True:
            ret, frame = video.read()
            if not ret:
                break
            
            frame = zone_mgr.draw_zones(frame)
            cv2.putText(frame, "Left-click: Add point | Right-click: Complete zone | C: Clear | Q: Quit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Zone Setup', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                zone_mgr.zones = []
                zone_mgr.save_zones()
    finally:
        video.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

if __name__ == '__main__':
    setup_zones()
