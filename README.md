# People Counting System

Real-time people counting system using computer vision and deep learning for public spaces.

## Features

- ✅ Real-time people detection and tracking using YOLOv8
- ✅ Multi-zone management (draw, save, edit zones)
- ✅ Live video feed from webcam/IP camera
- ✅ Interactive web dashboard with statistics
- ✅ Person tracking with unique IDs
- ✅ Zone-wise people counting

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The system will automatically download YOLOv8 model on first run.

## Usage

### Step 1: Setup Zones

Run the zone setup tool to define counting zones:

```bash
python zone_manager.py
```

**Controls:**
- Left-click: Add zone corner points
- Right-click: Complete current zone
- C: Clear all zones
- Q: Quit and save

### Step 2: Run Desktop Application

For standalone desktop application:

```bash
python main.py
```

**For IP camera:**
```bash
python main.py rtsp://username:password@ip:port/stream
```

**Controls:**
- Q: Quit
- S: Save snapshot

### Step 3: Run Web Dashboard

For web-based monitoring:

```bash
python dashboard.py
```

Open browser and navigate to: `http://localhost:5000`

## Project Structure

```
├── main.py              # Desktop application
├── dashboard.py         # Web dashboard
├── zone_manager.py      # Zone management & video feed
├── people_counter.py    # YOLOv8 detection & tracking
├── templates/
│   └── dashboard.html   # Web UI
├── requirements.txt     # Dependencies
└── zones.json          # Saved zones (auto-generated)
```

## How It Works

1. **Video Feed**: Captures frames from webcam/IP camera
2. **Detection**: YOLOv8 detects people in each frame
3. **Tracking**: Built-in tracker assigns unique IDs to each person
4. **Zone Counting**: Counts people whose center point falls within defined zones
5. **Display**: Shows live feed with bounding boxes, tracks, and statistics

## Configuration

- **Change camera source**: Pass camera index or RTSP URL as argument
- **Zones**: Stored in `zones.json`, can be edited manually
- **Model**: Uses YOLOv8n (nano) by default, can change in `people_counter.py`

## Requirements

- Python 3.8+
- Webcam or IP camera
- 4GB RAM minimum
- GPU recommended for better performance

## Milestones Completed

✅ **Weeks 1-2**: Video feed connection, zone drawing, zone management  
✅ **Weeks 3-4**: YOLOv8 integration, people detection & tracking, zone-based counting

## Next Steps

- Add density heatmaps
- Implement alert system for overcrowding
- Export reports with time-based trends
- Admin panel for camera management
- Database integration for historical data
