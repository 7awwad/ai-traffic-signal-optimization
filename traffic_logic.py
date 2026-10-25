# traffic_logic.py

import time
# We import everything from config.py to use the defined constants
from config import (
    LANE_PHASES, MIN_GREEN_TIME, MAX_GREEN_TIME, YELLOW_TIME, 
    MAX_DENSITY_THRESHOLD, EV_LANE_INDEX, EV_PRIORITY_TIME
)

# Global variables to track the state of the traffic controller
# main.py must access these by prefixing them with 'traffic_logic.'
current_phase_index = 0
phase_start_time = 0.0
is_yellow = False
is_ev_priority = False

# --- Core Logic Functions ---

def calculate_green_time(lane_index, density_list):
    """
    Adaptive Traffic Signal Optimization Algorithm.
    Calculates Green Time based on real-time vehicle density.
    """
    density = density_list[lane_index]
    
    clamped_density = min(density, MAX_DENSITY_THRESHOLD)
    scaling_factor = (MAX_GREEN_TIME - MIN_GREEN_TIME) / MAX_DENSITY_THRESHOLD
    adaptive_time = MIN_GREEN_TIME + (clamped_density * scaling_factor)
    
    return min(adaptive_time, MAX_GREEN_TIME)

def initialize_controller():
    """Initializes or resets the global controller state."""
    global current_phase_index, phase_start_time, is_yellow, is_ev_priority
    current_phase_index = 0
    phase_start_time = time.time()
    is_yellow = False
    is_ev_priority = False
    
    initial_lane = LANE_PHASES[current_phase_index]
    print(f"Controller Initialized. Starting phase: L{initial_lane}")

def determine_next_state(current_time, current_lane_density, ev_detection_count):
    """
    Main state machine logic for traffic signal transitions.
    """
    global current_phase_index, phase_start_time, is_yellow, is_ev_priority
    
    current_lane_idx = LANE_PHASES[current_phase_index]
    elapsed_time = current_time - phase_start_time
    
    # 1. Check for Emergency Vehicle (EV) Priority Override
    if ev_detection_count > 0 and not is_ev_priority:
         print("\n🚨 EMERGENCY VEHICLE DETECTED! Initiating Priority Override.")
         is_ev_priority = True
         is_yellow = True  # Quick yellow transition before EV green
         phase_start_time = current_time
         current_phase_index = LANE_PHASES.index(EV_LANE_INDEX) 
         return EV_LANE_INDEX, True, YELLOW_TIME

    if is_ev_priority:
        green_duration = EV_PRIORITY_TIME
        
        # A. EV Yellow Transition complete -> Switch to EV Green
        if is_yellow and elapsed_time >= YELLOW_TIME:
            is_yellow = False
            phase_start_time = current_time
            print(f"✅ Priority Green for Lane L{EV_LANE_INDEX} (EV).")
            return EV_LANE_INDEX, False, green_duration

        # B. EV Green running
        if not is_yellow:
            if current_lane_density[EV_LANE_INDEX] == 0 and elapsed_time > 5:
                print("✅ EV Passed. Resuming normal cycle.")
                is_ev_priority = False
                is_yellow = True 
                current_phase_index = (LANE_PHASES.index(EV_LANE_INDEX) + 1) % len(LANE_PHASES)
                phase_start_time = current_time
                return EV_LANE_INDEX, True, YELLOW_TIME

            if elapsed_time >= green_duration:
                print(f"⏱️ EV Priority time over. Transitioning to Yellow.")
                is_ev_priority = False
                is_yellow = True
                current_phase_index = (LANE_PHASES.index(EV_LANE_INDEX) + 1) % len(LANE_PHASES)
                phase_start_time = current_time
                return EV_LANE_INDEX, True, YELLOW_TIME
                
            return EV_LANE_INDEX, False, green_duration - elapsed_time
        
        # C. EV Yellow Transition running
        return EV_LANE_INDEX, True, YELLOW_TIME - elapsed_time

    # 2. Normal Adaptive Cycle Logic (Green Phase)
    if not is_yellow: 
        green_duration = calculate_green_time(current_lane_idx, current_lane_density)
        
        if elapsed_time >= green_duration:
            is_yellow = True
            phase_start_time = current_time
            print(f"🚥 Green time over for L{current_lane_idx}. Transitioning to Yellow.")
            return current_lane_idx, True, YELLOW_TIME
        else:
            return current_lane_idx, False, green_duration - elapsed_time

    # 3. Normal Adaptive Cycle Logic (Yellow Phase)
    else: # is_yellow is True
        if elapsed_time >= YELLOW_TIME:
            current_phase_index = (current_phase_index + 1) % len(LANE_PHASES)
            next_lane_idx = LANE_PHASES[current_phase_index]
            is_yellow = False
            phase_start_time = current_time
            
            # This is the line that had the SyntaxError: fixed now.
            new_green_duration = calculate_green_time(next_lane_idx, current_lane_density)
            print(f"🚦 Switched to Lane L{next_lane_idx}. New Green time: {new_green_duration:.1f}s (Density: {current_lane_density[next_lane_idx]})")
            
            return next_lane_idx, False, new_green_duration
        else:
            return current_lane_idx, True, YELLOW_TIME - elapsed_time

# Call initialize_controller when the script is imported/run
initialize_controller()