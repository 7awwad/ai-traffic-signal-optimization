# AI-Powered Dynamic Traffic Signal Optimization

> **Real-Time Computer Vision & Adaptive Traffic Control Engine**  
> Powered by OpenCV (MOG2 Background Subtraction), Dynamic Queue Density Scaling, and Emergency Vehicle (EV) Preemption Override.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8.svg)](https://opencv.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243.svg)](https://numpy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Overview

Traditional static traffic signal controllers operate on rigid, pre-programmed timers that fail to account for fluctuating vehicular demand, leading to unnecessary delays, heightened fuel consumption, and bottlenecked intersections. Furthermore, conventional systems lack automated mechanisms to detect and grant immediate right-of-way to emergency response vehicles.

This project implements an **autonomous, vision-based dynamic traffic management system**. It monitors intersection approaches in real-time, estimates vehicular queue density through background subtraction and contour centroid analysis, dynamically computes optimal green-signal durations, and executes an instant **Emergency Vehicle (EV) Priority Preemption** sequence.

---

## ⚡ Key Capabilities

- **Real-Time Vehicle Density Estimation**: Utilizes Gaussian Mixture-based Background Subtraction (`cv2.createBackgroundSubtractorMOG2`) combined with morphological filtering (Opening and Closing) to isolate moving vehicles from static road infrastructure.
- **Centroid-Based Lane Assignment**: Computes spatial moments ($M_{10}/M_{00}$) to determine contour centroids and map detections accurately into calibrated Regions of Interest (ROIs).
- **Dynamic Green Phase Calculation**: Dynamically scales green light duration between a configurable minimum and maximum ($8\text{s} \le T_{\text{green}} \le 35\text{s}$) proportional to the real-time queue density.
- **Emergency Vehicle (EV) Preemption Override**: Detects oversized moving vehicle contours in designated priority lanes, immediately initiating a controlled yellow clearance followed by uninterrupted green signal privilege for first responders.
- **Decoupled Architecture**: Cleanly separated configuration (`config.py`), state-machine control logic (`traffic_logic.py`), and visualization/pipeline engine (`main.py`).

---

## 🏗️ System Architecture

```text
 ┌────────────────────────────────────────────────────────┐
 │            Video Surveillance Stream / Camera          │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │           Preprocessing & Frame Downscaling            │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │  MOG2 Background Subtraction + Morphological Denoising │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │        Contour Extraction & Spatial Moment Analysis     │
 └───────────────────────────┬────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
   [Per-Lane Density Count]       [EV Size Threshold Check]
              │                             │
              └──────────────┬──────────────┘
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │      Finite State Machine (FSM) Controller             │
 │  - Normal Phase: Linear Density-Based Green Allocation │
 │  - Yellow Clearance Transition                         │
 │  - Priority Preemption (Immediate EV Green)            │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │         HUD Visualization (ROIs, Counts, Timers)       │
 └────────────────────────────────────────────────────────┘
```

---

## 📐 Mathematical Model & Control Logic

### 1. Dynamic Green Time Scaling

Green signal duration for each approach is computed as a linear function of current vehicle density, clamped between configurable bounds:

$$T_{\text{green}} = \min\left(T_{\min} + \left(\min(D_i, D_{\max}) \times \frac{T_{\max} - T_{\min}}{D_{\max}}\right), T_{\max}\right)$$

Where:
- $D_i$: Current vehicular density for lane $i$
- $D_{\max}$: Saturation density threshold ($20\text{ vehicles}$)
- $T_{\min}$: Minimum green interval ($8\text{ seconds}$)
- $T_{\max}$: Maximum green interval ($35\text{ seconds}$)
- $T_{\text{yellow}}$: Clearance interval ($3\text{ seconds}$)

### 2. Emergency Preemption Sequence

When an emergency vehicle is detected ($A_{\text{contour}} > A_{\text{EV\_threshold}}$ in lane 1):
1. Normal phase immediately transitions to **Yellow Clearance** ($3\text{s}$).
2. Signal transitions to **Priority Green** for lane 1 ($20\text{s}$ ceiling).
3. **Early Return**: If the emergency vehicle clears the intersection before timeout, normal cycle resumes automatically.

---

## 📂 Project Structure

```text
ai-traffic-signal-optimization/
├── config.py                 # System parameters, timing limits, and ROI calibration
├── traffic_logic.py          # State-machine controller, scheduling algorithms, and EV logic
├── main.py                   # CV pipeline, video processing, and HUD rendering loop
├── requirements.txt          # Python runtime dependencies
├── .gitignore                # Git ignore configuration
├── mixkit-city-...mp4        # Test intersection surveillance footage
│
├── docs/
│   └── research/             # Academic literature, conference papers, and project decks
│       ├── Finalpaper_309.pdf
│       ├── shark tank.pdf
│       ├── shakti sip.pdf
│       └── ...
│
└── prototypes/               # Earlier iterative prototypes & single-file simulations
    ├── traffic_light_density.py
    └── traffic.mp4
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10, 3.11, or 3.12
- `pip` package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/7awwad/ai-traffic-signal-optimization.git
   cd ai-traffic-signal-optimization
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Simulation

Execute the main simulation:

```bash
python main.py
```

- Press **`q`** inside the display window to gracefully exit the simulation.

---

## 🛠️ Configuration & Calibration

You can customize camera calibration and timing thresholds directly in `config.py`:

```python
# Timing thresholds (in seconds)
MIN_GREEN_TIME = 8      
MAX_GREEN_TIME = 35     
YELLOW_TIME = 3         
MAX_DENSITY_THRESHOLD = 20 

# Computer vision contour bounds
AREA_MIN_THRESHOLD = 500  
AREA_MAX_THRESHOLD = 30000 

# Calibrated ROI boundaries: (x_start, y_start, x_end, y_end)
LANE_ROIS = [
    (380, 50, 620, 380),   # North Approach
    (600, 400, 950, 650),  # East Approach (EV Lane)
    (380, 680, 620, 980),  # South Approach
    (50, 400, 400, 650)    # West Approach
]
```

---

## 🗺️ Roadmap & Future Enhancements

- [ ] **YOLOv8 / YOLOv11 Vehicle Classification**: Transition from background subtraction to deep learning object detection for refined classification (cars, ambulances, buses, two-wheelers).
- [ ] **Reinforcement Learning Agent (DQN / PPO)**: Implement deep Q-learning to minimize multi-intersection wait time networks.
- [ ] **Connected Vehicle (V2X) Simulation**: Integrate SUMO (Simulation of Urban MObility) for large-scale urban grid validation.

---

## Project team

Developed together by **Mohammed Jawwad Nagarmat** and **Faris Ruknuddin**.

**Maintainer of this repository:** Mohammed Jawwad Nagarmat

[GitHub](https://github.com/7awwad) · [LinkedIn](https://linkedin.com/in/MohammedJawwadNagarmat) · [Email](mailto:mohammedjawwadnagarmat8@gmail.com)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
