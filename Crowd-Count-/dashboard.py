from flask import Flask, render_template, Response, jsonify
import cv2
import json
from zone_manager import VideoFeed, ZoneManager
from people_counter import PeopleCounter
from collections import defaultdict
import time

app = Flask(__name__)

class DashboardSystem:
    def __init__(self, source=0):
        self.video = VideoFeed(source)
        self.zone_mgr = ZoneManager()
        self.counter = PeopleCounter()
        self.stats = {'total': 0, 'zones': {}, 'timestamp': time.time()}
        
    def process_frame(self):
        ret, frame = self.video.read()
        if not ret:
            return None, None
        
        detections = self.counter.detect_and_track(frame)
        
        self.zone_mgr.reset_counts()
        zone_people = defaultdict(set)
        
        for det in detections:
            cx, cy = det['center']
            for idx in range(len(self.zone_mgr.zones)):
                if self.zone_mgr.point_in_zone((cx, cy), idx):
                    zone_people[idx].add(det['id'])
        
        for idx, people_set in zone_people.items():
            self.zone_mgr.zones[idx]['count'] = len(people_set)
        
        self.stats = {
            'total': len(detections),
            'zones': {f"Zone {i+1}": len(people_set) for i, people_set in zone_people.items()},
            'timestamp': time.time()
        }
        
        frame = self.counter.draw_detections(frame, detections)
        frame = self.zone_mgr.draw_zones(frame)
        
        cv2.putText(frame, f"Total: {self.stats['total']}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame, self.stats

dashboard = DashboardSystem()

def generate_frames():
    while True:
        frame, _ = dashboard.process_frame()
        if frame is None:
            break
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def stats():
    return jsonify(dashboard.stats)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
