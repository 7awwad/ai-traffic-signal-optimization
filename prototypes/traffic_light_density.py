import cv2
import numpy as np
import time

def count_vehicles(frame, area_points, bg_subtractor):
    """
    Counts the number of objects (simulated vehicles) in a defined area.
    """
    # Create a mask to define the Region of Interest (ROI)
    roi_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(roi_mask, [np.array(area_points, dtype=np.int32)], 255)
    masked_frame = cv2.bitwise_and(frame, frame, mask=roi_mask)

    # Apply background subtraction to detect moving objects
    fg_mask = bg_subtractor.apply(masked_frame)
    
    # Use morphological operations to clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    
    # Find contours of the moving objects
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    vehicle_count = 0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 300:  # Filter out small detections
            vehicle_count += 1
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
    return vehicle_count

def main():
    # --- Video Source ---
    # Make sure this video file is in the same folder as the script
    cap = cv2.VideoCapture('traffic.mp4')
    if not cap.isOpened():
        print("Error: Could not open video source. Make sure the video file exists.")
        return

    # Initialize background subtractor for motion detection
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25, detectShadows=True)

    # --- Region of Interest (ROI) Calibration ---
    # These coordinates are calibrated for the provided simulation video.
    # [top-left, top-right, bottom-right, bottom-left]
    lane_1_roi = [(350, 0), (450, 0), (450, 250), (350, 250)]
    lane_2_roi = [(350, 350), (450, 350), (450, 600), (350, 600)]
    lane_3_roi = [(0, 350), (250, 350), (250, 450), (0, 450)]
    lane_4_roi = [(550, 350), (800, 350), (800, 450), (550, 450)]

    rois = {
        'Lane 1': {'points': lane_1_roi, 'vehicles': 0, 'color': (0, 255, 255), 'last_green_time': 0, 'history': []},
        'Lane 2': {'points': lane_2_roi, 'vehicles': 0, 'color': (0, 255, 255), 'last_green_time': 0, 'history': []},
        'Lane 3': {'points': lane_3_roi, 'vehicles': 0, 'color': (0, 255, 255), 'last_green_time': 0, 'history': []},
        'Lane 4': {'points': lane_4_roi, 'vehicles': 0, 'color': (0, 255, 255), 'last_green_time': 0, 'history': []}
    }
    
    rois['Lane 1']['last_green_time'] = time.time()
    current_green_lane = 'Lane 1'
    last_change_time = time.time()
    green_duration = 10 
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            # Loop the video if it ends
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (800, 600))
        display_frame = frame.copy()

        # Update vehicle count for each lane
        for lane_name, data in rois.items():
            vehicle_count = count_vehicles(frame, data['points'], bg_subtractor)
            data['history'].append(vehicle_count)
            # Keep a short history for a moving average
            if len(data['history']) > 5:
                data['history'].pop(0)
            
            smoothed_count = np.mean(data['history'])
            rois[lane_name]['vehicles'] = smoothed_count
            
            # Draw ROIs and display vehicle count
            cv2.polylines(display_frame, [np.array(data['points'], dtype=np.int32)], True, data['color'], 2)
            cv2.putText(display_frame, f'{lane_name}: {int(smoothed_count)}', (data['points'][0][0], data['points'][0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
        # --- Dynamic Traffic Light Logic ---
        # Check if it's time to change the green light
        if time.time() - last_change_time > green_duration:
            max_priority_score = -1
            next_green_lane = current_green_lane
            
            # Calculate a priority score for each lane
            for lane_name, data in rois.items():
                wait_time = time.time() - data['last_green_time']
                priority_score = data['vehicles'] + (wait_time * 0.5) # The "fairness" component
                
                if priority_score > max_priority_score:
                    max_priority_score = priority_score
                    next_green_lane = lane_name
            
            current_green_lane = next_green_lane
            last_change_time = time.time()
            rois[current_green_lane]['last_green_time'] = time.time()
            
            # Dynamically set the new green duration
            green_duration = min(5 + int(rois[current_green_lane]['vehicles'] / 2), 20)

        # Update traffic light colors and text
        for lane_name, data in rois.items():
            if lane_name == current_green_lane:
                rois[lane_name]['color'] = (0, 255, 0) # Green
                cv2.putText(display_frame, 'GO', (data['points'][0][0] + 50, data['points'][0][1] + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                rois[lane_name]['color'] = (0, 0, 255) # Red
                cv2.putText(display_frame, 'STOP', (data['points'][0][0] + 50, data['points'][0][1] + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the output frame in a window
        cv2.imshow('Dynamic Traffic Control Simulation', display_frame)
        
        # Exit when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
