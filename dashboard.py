from flask import Flask, render_template, Response, jsonify
import cv2
import json
import os
import threading
import time
from zone_manager import VideoFeed, ZoneManager
from people_counter import PeopleCounter
from collections import defaultdict

app = Flask(__name__)

class DashboardSystem:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture('demo_video.mp4')
        self.zone_mgr = ZoneManager()
        self.counter = PeopleCounter()
        self.stats = {'total': 0, 'zones': {}, 'timestamp': time.time()}
        self.current_frame = None
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

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
                'zones': {f"Zone {i+1}": len(s) for i, s in zone_people.items()},
                'timestamp': time.time()
            }

            frame = self.counter.draw_detections(frame, detections)
            frame = self.zone_mgr.draw_zones(frame)
            cv2.putText(frame, f"Total: {self.stats['total']}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            ret2, buffer = cv2.imencode('.jpg', frame)
            if ret2:
                with self.lock:
                    self.current_frame = buffer.tobytes()

    def get_frame(self):
        with self.lock:
            return self.current_frame

    def stop(self):
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()


dashboard = DashboardSystem()


def generate_frames():
    while dashboard.running:
        frame = dashboard.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.03)


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stats')
def stats():
    return jsonify(dashboard.stats)


@app.route('/shutdown', methods=['POST'])
def shutdown():
    def stop():
        time.sleep(0.3)
        dashboard.stop()
        os._exit(0)
    threading.Thread(target=stop, daemon=True).start()
    return jsonify({'status': 'stopping'})


if __name__ == '__main__':
    import webbrowser
    chrome = webbrowser.get('C:/Program Files/Google/Chrome/Application/chrome.exe %s')
    threading.Timer(1.5, lambda: chrome.open('http://127.0.0.1:8080')).start()
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
