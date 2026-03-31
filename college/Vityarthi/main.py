import cv2
import numpy as np
import time
import os
from datetime import datetime

# ── CONFIG ─────────────────────────────────────────────────────────────────
SENSITIVITY      = 500     # minimum contour area to count as motion
ALERT_COOLDOWN   = 3       # seconds between saved snapshots
SAVE_SNAPSHOTS   = True    # save image when motion detected
SNAPSHOT_DIR     = "snapshots"
# ───────────────────────────────────────────────────────────────────────────

if SAVE_SNAPSHOTS and not os.path.exists(SNAPSHOT_DIR):
    os.makedirs(SNAPSHOT_DIR)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Background subtractor — learns what "still" looks like
bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=500, varThreshold=50, detectShadows=True
)

last_saved     = 0
motion_count   = 0
start_time     = time.time()

print("[SYSTEM] Motion Detection Active. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Cannot read from camera.")
        break

    frame = cv2.flip(frame, 1)
    display = frame.copy()

    # ── MOTION DETECTION PIPELINE ──────────────────────────────────────────

    # 1. Apply background subtraction
    fg_mask = bg_subtractor.apply(frame)

    # 2. Remove shadows (shadows are grey = 127, motion is white = 255)
    _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

    # 3. Reduce noise with morphological operations
    kernel  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN,  kernel, iterations=2)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 4. Find contours (moving objects)
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False
    motion_areas    = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < SENSITIVITY:
            continue  # ignore tiny noise

        motion_detected = True
        x, y, w, h = cv2.boundingRect(contour)
        motion_areas.append((x, y, w, h, area))

        # Draw bounding box around moving object
        cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(display, f"Motion ({int(area)}px)", (x, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

    # ── SAVE SNAPSHOT ──────────────────────────────────────────────────────
    now = time.time()
    if motion_detected and SAVE_SNAPSHOTS and (now - last_saved) > ALERT_COOLDOWN:
        timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
        path       = os.path.join(SNAPSHOT_DIR, f"motion_{timestamp}.jpg")
        cv2.imwrite(path, display)
        last_saved  = now
        motion_count += 1
        print(f"[ALERT] Motion detected! Snapshot saved → {path}")

    # ── HUD OVERLAY ────────────────────────────────────────────────────────
    elapsed = int(time.time() - start_time)

    # Status bar background
    overlay = display.copy()
    cv2.rectangle(overlay, (0, 0), (1280, 50), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, display, 0.4, 0, display)

    # Status text
    status_text  = "  MOTION DETECTED" if motion_detected else "  MONITORING"
    status_color = (0, 255, 0)         if motion_detected else (0, 200, 255)

    cv2.putText(display, f"[SECURITY CAM]", (10, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.putText(display, status_text, (220, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)

    cv2.putText(display, f"Alerts: {motion_count}  |  Runtime: {elapsed}s  |  Q to quit",
                (700, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)

    # Timestamp bottom right
    ts = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    cv2.putText(display, ts, (970, 710),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)

    # Red alert border when motion
    if motion_detected:
        cv2.rectangle(display, (0, 0), (1279, 719), (0, 0, 255), 4)

    # ── SHOW FRAMES ────────────────────────────────────────────────────────
    cv2.imshow("Security Monitor", display)
    cv2.imshow("Motion Mask",      fg_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print(f"\n[SYSTEM] Session ended. Total alerts: {motion_count}")
cap.release()
cv2.destroyAllWindows()