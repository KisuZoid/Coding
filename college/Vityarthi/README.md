# Motion Detection Security System 🎥

A real-time motion detection system built with Python and OpenCV. It monitors a webcam feed, detects movement using background subtraction, highlights moving objects with bounding boxes, and automatically saves snapshots when motion is detected.

---

## Problem Statement

Many households and small offices lack affordable security monitoring. Expensive systems require subscriptions or hardware. This project provides a lightweight, free, and fully local motion detection system that runs on any laptop with a webcam.

---

## Features

- Real-time motion detection via webcam
- Bounding boxes drawn around moving objects
- Automatic snapshot saving with timestamp when motion is detected
- Live HUD showing status, alert count, and runtime
- Red border alert when motion is active
- Noise filtering using morphological operations
- Shadow removal for cleaner detection

---

## How It Works

1. Each frame is passed through **MOG2 Background Subtractor** — it learns what the background looks like over time
2. Any pixel that differs significantly from the background is marked as **foreground (motion)**
3. Shadows (grey pixels) are removed via **thresholding**
4. **Morphological operations** (open + close) clean up noise
5. **Contours** are found on the cleaned mask — each contour is a moving object
6. If a contour exceeds the minimum area, it is flagged and boxed

---

## Setup

### Requirements

- Python 3.8+
- A working webcam

### Install dependencies

```bash
pip install opencv-python numpy
```

### Run

```bash
python main.py
```

Press **Q** to quit.

---

## Configuration

At the top of `main.py` you can adjust:

| Variable | Default | Description |
|---|---|---|
| `SENSITIVITY` | `500` | Minimum pixel area to count as motion |
| `ALERT_COOLDOWN` | `3` | Seconds between saved snapshots |
| `SAVE_SNAPSHOTS` | `True` | Enable/disable snapshot saving |
| `SNAPSHOT_DIR` | `"snapshots"` | Folder where snapshots are saved |

---

## Output

- **Security Monitor window** — live annotated feed
- **Motion Mask window** — binary mask showing detected motion
- **snapshots/** folder — timestamped images saved on each alert

---

## Project Structure

```
motion-detection/
│
├── main.py           # Core detection script
├── snapshots/        # Auto-created; stores alert images
└── README.md
```

---

## Dependencies

| Library | Purpose |
|---|---|
| `opencv-python` | Video capture, image processing, display |
| `numpy` | Array operations |

---

## Limitations

- Works best in stable lighting conditions
- Sudden lighting changes (turning a light on/off) may trigger false alerts — adjust `SENSITIVITY` if needed
- Designed for single-camera, local use

---

## Author
Name: Kislay Anand
Registration Number: 23BAI10359
Built as a BYOP capstone project for a Computer Vision course.