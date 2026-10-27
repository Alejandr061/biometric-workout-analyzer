# 🏋️ Biometric Workout Analyzer

Real-time biomechanical exercise analysis using Computer Vision and MediaPipe. Tracks form, counts reps, and provides instant posture feedback.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Features

- **Real-time Pose Detection**: MediaPipe-powered landmark tracking with confidence filtering
- **Biomechanical Analysis**: Angle calculation, ROM tracking, and tempo measurement
- **Form Validation**: Detects common mistakes (torso swinging, elbow drift, insufficient depth)
- **Rep Counting**: Finite State Machine (FSM) for accurate repetition counting
- **Modern HUD**: Semi-transparent overlay with FPS, angle gauge, and posture alerts
- **Signal Smoothing**: EMA filtering to reduce camera jitter

## 🏗️ Architecture

Strictly modular and decoupled design:

```
src/
├── core/               # Pose detection and math utilities
│   ├── pose_detector.py   # MediaPipe wrapper
│   ├── geometry.py        # Vector math (angles, distances)
│   └── smoothing.py       # EMA and One Euro filters
├── exercises/          # Exercise-specific analyzers
│   ├── base_exercise.py   # Abstract FSM base class
│   ├── bicep_curl.py      # Bicep curl implementation
│   └── squat.py           # Squat implementation
├── ui/                 # HUD rendering
│   └── hud.py             # OpenCV overlay system
└── telemetry/          # Session logging (Phase 2)
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/biometric-workout-analyzer.git
cd biometric-workout-analyzer

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

**Webcam (Bicep Curl - Right Arm):**
```bash
python main.py --exercise curl --source 0
```

**Video File (Squat):**
```bash
python main.py --exercise squat --source assets/squat_demo.mp4
```

**Left Arm Analysis:**
```bash
python main.py --exercise curl --side left --source 0
```

### Controls

- `q` or `ESC` - Quit application
- `r` - Reset rep counter
- `s` - Toggle skeleton overlay

## 📊 Supported Exercises

### 1. Bicep Curl (`--exercise curl`)

**Tracks:**
- Elbow angle (ROM: 180° → 30°)
- Torso stability (detects swinging)
- Elbow position (should remain fixed)

**Form Alerts:**
- ⚠️ Torso swinging - Keep stable!
- ⚠️ Elbow drifting forward - Keep elbow fixed!

### 2. Squat (`--exercise squat`)

**Tracks:**
- Knee angle (depth indicator)
- Hip angle (secondary confirmation)
- Torso inclination

**Form Alerts:**
- ⬇️ Go deeper (X° to parallel)
- ⚠️ Excessive forward lean - Chest up!
- ⚠️ Rep not counted - Insufficient depth!

## 🧮 Metrics Collected

For each repetition:
- **Range of Motion (ROM)**: Maximum angle - Minimum angle
- **Eccentric Time**: Duration of lowering phase
- **Concentric Time**: Duration of lifting phase
- **Time Under Tension (TUT)**: Total rep duration
- **Tempo**: E.g., "3.0-0-2.5" (eccentric-pause-concentric)
- **Posture Alerts**: List of form violations

## 🔬 Technical Details

### Pose Detection
- **Model**: MediaPipe Pose (Complexity 1 - Full)
- **Confidence Threshold**: 0.6 (configurable via `--confidence`)
- **Smoothing**: EMA filter with α=0.5

### Geometry Calculations

**Angle Calculation (3 points):**
```python
angle = arccos((BA · BC) / (|BA| * |BC|))
```

**Vertical Inclination:**
```python
inclination = arctan(|Δx| / |Δy|)
```

### Finite State Machine

```
IDLE → ECCENTRIC → BOTTOM → CONCENTRIC → IDLE
  ↑                                        ↓
  └────────────── (rep complete) ──────────┘
```

## 🛠️ Requirements

- Python 3.11+
- OpenCV 4.10+
- MediaPipe 0.10+
- NumPy 1.26+
- Webcam or video file

## 📝 Example Output

```
🏋️  Biometric Workout Analyzer
==================================================
Exercise: CURL
Side: Right
Source: 0
Confidence threshold: 0.6
==================================================

✅ Ready! Starting analysis...

Controls:
  'q' or ESC - Quit
  'r' - Reset rep counter
  's' - Toggle skeleton overlay

==================================================
📊 SESSION SUMMARY
==================================================
Exercise: Bicep Curl (Right)
Total reps: 12
Total TUT: 48.3s
Average tempo: 3.2-0-2.1
Average ROM: 142.5°

Rep breakdown:
  Rep 1: ROM=145.2° TUT=5.1s Tempo=3.1-0-2.0
  Rep 2: ROM=148.7° TUT=4.9s Tempo=3.0-0-1.9
  ...
  Rep 12: ROM=138.4° TUT=5.3s Tempo=3.5-0-1.8
    Alerts: ⚠️ Torso swinging (16.2°) - Keep stable!

✅ Session complete!
```

## 🎓 Learning Points

This project demonstrates:
- **Clean Architecture**: Modular, decoupled, and testable
- **Real-time CV**: 30+ FPS pose estimation with filtering
- **FSM Design**: Robust state management for temporal logic
- **NumPy Vectorization**: Efficient geometry calculations
- **Type Safety**: Full type hints with Pydantic models
- **Professional Git**: Atomic commits with Conventional Commits

## 🚧 Roadmap (Phase 2)

- [ ] Telemetry export (JSON/CSV)
- [ ] Symmetry analysis (left vs. right side)
- [ ] More exercises (shoulder press, deadlift, push-up)
- [ ] One Euro Filter for adaptive smoothing
- [ ] Session replay and comparison
- [ ] Web dashboard for progress tracking

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feat/new-exercise`)
3. Commit using Conventional Commits (`feat:`, `fix:`, `docs:`)
4. Submit a Pull Request

## 👨‍💻 Author

**Alejandro Hidalgo**
- GitHub: [@yourusername](https://github.com/yourusername)
- Portfolio: [your-portfolio.com](https://your-portfolio.com)

---

⭐ If you find this project useful, please consider giving it a star!
