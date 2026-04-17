import cv2
import time
from zone_manager import VideoFeed, ZoneManager
from people_counter import PeopleCounter
from collections import defaultdict

class PeopleCountingSystem:
    def __init__(self, source=0):
        self.video = VideoFeed(source)
        self.zone_mgr = ZoneManager()
        self.counter = PeopleCounter()
        self.zone_people = defaultdict(set)
        self.stats = {'total': 0, 'zones': {}}
        
    def count_people_in_zones(self, detections):
        self.zone_mgr.reset_counts()
        current_zone_people = defaultdict(set)
        
        for det in detections:
            cx, cy = det['center']
            track_id = det['id']
            
            for idx in range(len(self.zone_mgr.zones)):
                if self.zone_mgr.point_in_zone((cx, cy), idx):
                    current_zone_people[idx].add(track_id)
        
        for idx, people_set in current_zone_people.items():
            self.zone_mgr.zones[idx]['count'] = len(people_set)
        
        self.zone_people = current_zone_people
        self.stats['total'] = len(detections)
        self.stats['zones'] = {f"Zone {i+1}": len(people_set) 
                               for i, people_set in current_zone_people.items()}
    
    def run(self):
        print("Starting People Counting System...")
        print("Press 'q' to quit, 's' to save snapshot")
        
        fps_time = time.time()
        fps = 0
        
        try:
            while True:
                ret, frame = self.video.read()
                if not ret:
                    break
                
                detections = self.counter.detect_and_track(frame)
                self.count_people_in_zones(detections)
                
                frame = self.counter.draw_detections(frame, detections)
                frame = self.zone_mgr.draw_zones(frame)
                
                fps = 1.0 / (time.time() - fps_time)
                fps_time = time.time()
                
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Total People: {self.stats['total']}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                y_offset = 90
                for zone_name, count in self.stats['zones'].items():
                    cv2.putText(frame, f"{zone_name}: {count}", (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    y_offset += 30
                
                cv2.imshow('People Counting System', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    cv2.imwrite(f'snapshot_{int(time.time())}.jpg', frame)
                    print("Snapshot saved")
        finally:
            self.cleanup()
    
    def cleanup(self):
        self.video.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        print("Camera released successfully")

if __name__ == '__main__':
    import sys
    
    source = sys.argv[1] if len(sys.argv) > 1 else 0
    
    system = PeopleCountingSystem(source)
    system.run()
