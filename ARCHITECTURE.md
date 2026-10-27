# 🏗️ System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     VIDEO INPUT SOURCE                          │
│              (Webcam / Video File / Stream)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   POSE DETECTION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  MediaPipe Pose (33 Landmarks)                           │  │
│  │  • Confidence filtering (> 0.6)                          │  │
│  │  • Normalized coordinates                                 │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  EMA Smoothing Filter                                     │  │
│  │  • Reduces camera jitter                                  │  │
│  │  • Per-landmark state tracking                            │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GEOMETRY CALCULATION                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Vector Math (NumPy)                                      │  │
│  │  • Angle calculation (3 points)                          │  │
│  │  • Euclidean distance                                     │  │
│  │  • Vertical inclination (torso lean)                     │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              EXERCISE-SPECIFIC ANALYZER (FSM)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Finite State Machine                                     │  │
│  │  ┌────────┐  ┌──────────┐  ┌────────┐  ┌──────────────┐ │  │
│  │  │  IDLE  │→│ECCENTRIC │→│ BOTTOM │→│ CONCENTRIC   │ │  │
│  │  └───┬────┘  └──────────┘  └────────┘  └──────┬───────┘ │  │
│  │      │                                          │         │  │
│  │      └──────────────────────────────────────────┘         │  │
│  │                   (Rep Complete)                          │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  Form Validation                                          │  │
│  │  • Torso stability                                        │  │
│  │  • Joint alignment                                        │  │
│  │  • Range of motion                                        │  │
│  │  • Depth checking                                         │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  METRICS CALCULATION                            │
│  • Rep Count                                                    │
│  • Range of Motion (ROM)                                        │
│  • Time Under Tension (TUT)                                     │
│  • Tempo (Eccentric-Pause-Concentric)                          │
│  • Posture Alerts                                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HUD RENDERING                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Info Panel          Angle Gauge        Alert Banner    │  │
│  │  • Exercise name     • Progress bar     • Form warnings │  │
│  │  • Rep counter       • Current angle    • Red banner    │  │
│  │  • State             • Visual feedback  • Icon + text   │  │
│  │  • Tempo/TUT         •                  •               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT DISPLAY                               │
│              (OpenCV Window with Overlays)                      │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Frame → Pose Detector → Landmarks → Geometry → Exercise Analyzer → Metrics → HUD → Display
  ↓                        ↓           ↓             ↓              ↓        ↓
Video   Confidence    Smoothed     Angles      FSM State      Rep Data   Overlay
Input   Filtering     Coords       Distances   Transition     Collection Rendering
```

## Module Dependencies

```
main.py
  ├── src.core.pose_detector
  │   ├── mediapipe
  │   ├── opencv (cv2)
  │   └── src.core.smoothing
  │       └── numpy
  │
  ├── src.exercises.{bicep_curl | squat}
  │   ├── src.exercises.base_exercise
  │   │   └── (Enums, Dataclasses)
  │   └── src.core.geometry
  │       └── numpy
  │
  └── src.ui.hud
      ├── opencv (cv2)
      └── numpy
```

## State Machine (Exercise FSM)

```
                    Start
                      │
                      ▼
              ┌───────────────┐
              │     IDLE      │ ◄────────────┐
              │ (starting pos)│              │
              └───────┬───────┘              │
                      │                      │
          Joint starts│to flex               │
                      │                      │
                      ▼                      │
              ┌───────────────┐              │
              │  ECCENTRIC    │              │
              │ (lowering)    │              │
              └───────┬───────┘              │
                      │                      │
         Minimum angle│reached               │
                      │                      │
                      ▼                      │
              ┌───────────────┐              │
              │    BOTTOM     │              │
              │ (transition)  │              │
              └───────┬───────┘              │
                      │                      │
          Joint starts│to extend             │
                      │                      │
                      ▼                      │
              ┌───────────────┐              │
              │  CONCENTRIC   │              │
              │ (lifting)     │              │
              └───────┬───────┘              │
                      │                      │
         Return to    │starting              │
         position     │                      │
                      │                      │
                      └──────────────────────┘
                      (Rep Complete)
```

## Class Hierarchy

```
BaseExercise (ABC)
├── attributes
│   ├── state: ExerciseState
│   ├── rep_count: int
│   ├── completed_reps: List[RepData]
│   └── active_alerts: List[str]
│
├── abstract methods
│   ├── analyze_frame()
│   ├── get_primary_angle()
│   └── get_target_landmarks()
│
└── concrete methods
    ├── _transition_state()
    ├── _complete_rep()
    ├── _track_angle()
    ├── _add_alert()
    ├── get_total_tut()
    ├── get_average_rom()
    └── get_tempo()

BicepCurl(BaseExercise)
├── analyze_frame()
├── _check_torso_stability()
└── _check_elbow_drift()

Squat(BaseExercise)
├── analyze_frame()
├── _check_depth()
└── _check_torso_lean()
```

## Coordinate Systems

### MediaPipe Normalized Coordinates
```
(0,0) ────────────────► (1,0)
  │                        x
  │
  │   Normalized [0,1]
  │   • Independent of resolution
  │   • Origin at top-left
  │
  ▼
(0,1)                   (1,1)
  y
```

### Pixel Coordinates (OpenCV)
```
(0,0) ────────────────► (640,0)
  │                        x
  │
  │   Pixels
  │   • Resolution dependent
  │   • Used for rendering
  │
  ▼
(0,480)                 (640,480)
  y
```

## Signal Processing Pipeline

```
Raw Landmarks (jittery)
      │
      ▼
┌─────────────────┐
│  Confidence     │  Filter out landmarks
│  Filtering      │  with visibility < 0.6
│  (threshold)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  EMA Smoothing  │  Exponential Moving Average
│  (α = 0.5)      │  smoothed = α*raw + (1-α)*prev
└────────┬────────┘
         │
         ▼
Smoothed Landmarks (stable)
```

## Performance Characteristics

| Component         | Latency      | Bottleneck      |
|-------------------|--------------|-----------------|
| Video Capture     | ~33ms (30fps)| Camera/Video    |
| Pose Detection    | ~20-30ms     | MediaPipe       |
| Geometry Calc     | <1ms         | NumPy (fast)    |
| Exercise Analysis | <1ms         | FSM logic       |
| HUD Rendering     | ~5ms         | OpenCV drawing  |
| **Total**         | **~60ms**    | **~15-20 FPS**  |

*With optimization: 25-30 FPS achievable*

## Error Handling Strategy

```
┌─────────────────────────┐
│ Frame Capture           │
└───────┬─────────────────┘
        │ ✗ Failed to read
        ├──────────► Log + Exit
        │
        │ ✓ Success
        ▼
┌─────────────────────────┐
│ Pose Detection          │
└───────┬─────────────────┘
        │ ✗ No pose detected
        ├──────────► Display "No Pose" message
        │            Continue to next frame
        │
        │ ✓ Pose detected
        ▼
┌─────────────────────────┐
│ Landmark Retrieval      │
└───────┬─────────────────┘
        │ ✗ Required landmarks missing
        ├──────────► Skip analysis
        │            Continue to next frame
        │
        │ ✓ All required landmarks present
        ▼
┌─────────────────────────┐
│ Geometry Calculation    │
└───────┬─────────────────┘
        │ ✗ Degenerate vectors (division by zero)
        ├──────────► Return safe default (180°)
        │            Continue with default
        │
        │ ✓ Valid calculation
        ▼
┌─────────────────────────┐
│ Exercise Analysis       │
└───────┬─────────────────┘
        │ ✗ Invalid state
        ├──────────► Log warning
        │            Reset to IDLE
        │
        │ ✓ Valid state transition
        ▼
┌─────────────────────────┐
│ HUD Rendering          │
└─────────────────────────┘
```

## Extensibility Points

### Adding New Exercises

1. **Create new exercise class**:
```python
class PushUp(BaseExercise):
    def analyze_frame(self, pose_detector):
        # Custom analysis logic
        pass
    
    def get_primary_angle(self):
        return self._current_elbow_angle
    
    def get_target_landmarks(self):
        return ['left_shoulder', 'left_elbow', ...]
```

2. **Add to main.py**:
```python
parser.add_argument(
    '--exercise',
    choices=['curl', 'squat', 'pushup'],  # Add here
    ...
)
```

3. **Update factory function**:
```python
def create_exercise_analyzer(exercise_type: str, side: str):
    if exercise_type == 'pushup':
        return PushUp(side=side)
    ...
```

### Adding New Filters

Implement the filter interface in `src/core/smoothing.py`:
```python
class KalmanFilter:
    def smooth(self, landmark_name: str, raw_coords: Tuple) -> Tuple:
        # Implementation
        pass
    
    def reset(self):
        pass
```

### Adding Telemetry Export

```python
# src/telemetry/export.py
def export_session(exercise: BaseExercise, format: str = 'json'):
    data = {
        'exercise': exercise.name,
        'reps': [rep.__dict__ for rep in exercise.completed_reps],
        'summary': {
            'total_reps': exercise.rep_count,
            'total_tut': exercise.get_total_tut(),
            ...
        }
    }
    
    if format == 'json':
        save_json(data)
    elif format == 'csv':
        save_csv(data)
```

## Configuration Points

| Parameter              | Location                    | Default | Range      |
|------------------------|-----------------------------|---------|------------|
| Confidence threshold   | `main.py --confidence`      | 0.6     | 0.0 - 1.0  |
| EMA alpha             | `PoseDetector.__init__`     | 0.5     | 0.0 - 1.0  |
| Exercise thresholds   | Each exercise class         | Varies  | -          |
| HUD colors            | `src/ui/hud.py`             | BGR     | -          |
| State transition angles| Exercise class constants    | Varies  | Degrees    |

---

**This architecture enables:**
- ✅ Easy testing (mocked dependencies)
- ✅ Parallel development (independent modules)
- ✅ Simple debugging (clear data flow)
- ✅ Future expansion (plugin-style exercises)
- ✅ Maintenance (isolated concerns)
