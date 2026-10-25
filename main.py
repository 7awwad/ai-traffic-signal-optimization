# main.py

import cv2
import numpy as np
import time

# --- CORRECTED IMPORT: Import the module to access its global state ---
import traffic_logic 
from config import * # Import all constants

# --- Initialization ---
VIDEO_SOURCE = 'mixkit-city-busy-traffic-intersection-time-lapse-1755-hd-ready.mp4'

# Load Background Subtractor MOG2 (AI/CV method)
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25, detectShadows=True)
kernel = np.ones(KERNEL, np.uint8)

# Initialize Video Capture (Already done by traffic_logic.initialize_controller() on import)

cap = cv2.VideoCapture(VIDEO_SOURCE)
if not cap.isOpened():
    print(f"Error: Could not open video source {VIDEO_SOURCE}. Check file path.")
    exit()
    
# Get original dimensions (for display only)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Define the scaling factor for display/processing efficiency
scale_percent = 50 
new_width = int(frame_width * scale_percent / 100)
new_height = int(frame_height * scale_percent / 100)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        # Loop video for continuous simulation
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # 1. Pre-Processing & Scaling
    frame = cv2.resize(frame, (new_width, new_height))
    frame_copy = frame.copy() 
    current_time = time.time()
    
    # Scale ROIs down to match the resized frame
    scaled_rois = []
    for x1, y1, x2, y2 in LANE_ROIS:
        scaled_x1 = int(x1 * scale_percent / 100)
        scaled_y1 = int(y1 * scale_percent / 100)
        scaled_x2 = int(x2 * scale_percent / 100)
        scaled_y2 = int(y2 * scale_percent / 100)
        scaled_rois.append((scaled_x1, scaled_y1, scaled_x2, scaled_y2))

    # --- 2. Computer Vision: Counting ---
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fgmask = fgbg.apply(gray) 
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel) 
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_lane_density = [0] * len(LANE_PHASES)
    ev_detection_count = 0

    for i, roi in enumerate(scaled_rois):
        x1, y1, x2, y2 = roi
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Find the center of the contour
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                continue

            # Check if contour center is within the ROI
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                if AREA_MIN_THRESHOLD < area < AREA_MAX_THRESHOLD:
                    current_lane_density[i] += 1
                
                # Check for Emergency Vehicle (abnormally large contour area)
                if i == EV_LANE_INDEX and area > EV_AREA_THRESHOLD:
                    ev_detection_count = 1 # Flag presence of EV-sized object

    # --- 3. AI/Control Logic ---
    # Call the logic function from the imported module
    current_lane_idx, is_yellow_status, time_left = traffic_logic.determine_next_state(
        current_time, 
        current_lane_density, 
        ev_detection_count
    )

    # --- 4. Visualization (Output Demonstration) ---
    
    # Draw ROIs and Status
    for i, roi in enumerate(scaled_rois):
        x1, y1, x2, y2 = roi
        
        color = (0, 0, 255) # Default Red
        # Check against the state variables in the traffic_logic module
        if i == current_lane_idx and not traffic_logic.is_yellow:
            color = (0, 255, 0) # Green
        elif i == current_lane_idx and traffic_logic.is_yellow:
            color = (0, 255, 255) # Yellow

        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 3)
        cv2.putText(frame_copy, f"L{i} D:{current_lane_density[i]}", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Display Global Status
    status_text = f"Phase: L{current_lane_idx} | Time: {time_left:.1f}s"
    
    # --- ERROR FIX APPLIED HERE: Accessing via module prefix ---
    if traffic_logic.is_ev_priority:
        status_text = "🚨 EV PRIORITY OVERRIDE 🚨"

    cv2.putText(frame_copy, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    # Show the results
    cv2.imshow('Dynamic Traffic Control Simulation', frame_copy)

    # Exit on 'q' press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()