# config.py

# --- Dynamic Traffic Logic Settings (KEPT THE SAME) ---
MIN_GREEN_TIME = 8      
MAX_GREEN_TIME = 35     
YELLOW_TIME = 3         
MAX_DENSITY_THRESHOLD = 20 

# --- OpenCV/Computer Vision Settings (KEPT THE SAME) ---
AREA_MIN_THRESHOLD = 500  
AREA_MAX_THRESHOLD = 30000 
KERNEL = (5, 5) 

# --- Intersection Setup (4-way intersection) ---
# Lane order for cycle: North (0) -> East (1) -> South (2) -> West (3)
LANE_PHASES = [0, 1, 2, 3]

# =========================================================================
# === FINAL CALIBRATED REGIONS OF INTEREST (ROIs) FOR THE PROVIDED VIDEO ===
# =========================================================================
# Format: (x_start, y_start, x_end, y_end) at ORIGINAL video resolution.
# Boundaries are expanded to cover all queuing lanes (including the wider EW road).

LANE_ROIS = [
    # Lane 0: North Approach (Covers both inbound lanes queuing)
    # Area: From the 'MAX 30' sign downwards, spanning the width of the road.
    (380, 50, 620, 380),  
    
    # Lane 1: East Approach (Covers all three queuing lanes before the crosswalk) - EV Lane
    # Area: Starts deep right (East) and spans the full vertical width of the Eastbound road.
    (600, 400, 950, 650), 
    
    # Lane 2: South Approach (Covers both inbound lanes queuing)
    # Area: From the bottom of the screen upwards, spanning the width of the road.
    (380, 680, 620, 980), 
    
    # Lane 3: West Approach (Covers all three queuing lanes before the crosswalk)
    # Area: Starts deep left (West) and spans the full vertical width of the Westbound road.
    (50, 400, 400, 650)   
]

# --- Emergency Vehicle (EV) Simulation ---
EV_LANE_INDEX = 1 # Lane 1 (East Approach)
EV_AREA_THRESHOLD = 18000 
EV_PRIORITY_TIME = 20