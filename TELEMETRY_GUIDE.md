# 📊 Telemetry & Dashboard System Guide

## Overview

The Biometric Workout Analyzer now includes a comprehensive telemetry system that automatically records, analyzes, and visualizes your workout biomechanics.

## Features

### 🎯 Real-Time Data Collection

**Frame-by-Frame Telemetry** (captured every frame):
- Timestamp (seconds since session start)
- Joint angle (smoothed)
- FSM state (IDLE, ECCENTRIC, BOTTOM, CONCENTRIC)
- Posture alerts (boolean + text)

**Rep-by-Rep Summary** (captured on rep completion):
- Rep number
- ROM (Range of Motion in degrees)
- Eccentric time (lowering phase duration)
- Concentric time (lifting phase duration)
- Concentric velocity (deg/s) - Key metric for VBT
- Compensation flag (form violations)
- Min/max angles reached

### 📁 Automatic Export

When you finish a session (press `q`), the system automatically exports:

1. **JSON File** - Complete session data
2. **CSV Files** - Rep summaries + frame data (sampled)
3. **Dashboard PNG** - High-res biomechanical visualization

All files are saved to `sessions/` directory with timestamp.

### 🎨 Post-Workout Dashboard

A beautiful, professional-grade dashboard is **automatically generated** and displayed when you quit the application (if you completed at least 1 rep).

#### Dashboard Panels:

**Panel 1: Joint Angle Curve & Posture Alerts** 📐
- Continuous angle tracking throughout entire session
- Red markers showing exactly when form broke down
- FSM state zones (color-coded background)
- Real biomechanical insight into your movement patterns

**Panel 2: Velocity-Based Training (VBT) Analysis** ⚡
- Bar chart showing concentric velocity for each rep
- Trend line revealing fatigue progression
- -20% velocity drop threshold (red line)
- Color-coded bars:
  - Blue/Cyan: Good velocity (>90% of max)
  - Yellow: Moderate drop (80-90%)
  - Red: Significant fatigue (<80%)

**Panel 3: Tempo & Time Under Tension** ⏱️
- Stacked bar chart: Eccentric (red) vs Concentric (cyan)
- Shows tempo consistency across reps
- Total TUT displayed on each bar
- Reveals if you're rushing or slowing down

#### KPI Summary (Top of Dashboard):
- Total Reps
- Total TUT (Time Under Tension)
- Average ROM
- Velocity Loss % (fatigue indicator)
- Clean Technique % (reps without compensation)

## Usage

### Automatic Operation

No extra steps required! The telemetry system works automatically:

```bash
# Just run the application as usual
python main.py --exercise curl --source 0

# Do your workout...

# Press 'q' when done
# → Dashboard opens automatically!
```

### Manual Data Analysis

Load session data programmatically:

```python
import json
import pandas as pd

# Load JSON
with open('sessions/session_Bicep_Curl_Right_20261027_201945.json') as f:
    data = json.load(f)

metadata = data['metadata']
frames = data['frame_data']
reps = data['rep_summaries']

# Load CSV
df = pd.read_csv('sessions/session_Bicep_Curl_Right_20261027_201945_reps.csv')

# Calculate custom metrics
print(f"Average velocity: {df['concentric_velocity_deg_s'].mean():.1f}°/s")
print(f"Consistency (ROM std): {df['rom_degrees'].std():.1f}°")
```

## Key Metrics Explained

### 📏 ROM (Range of Motion)
- **Formula**: |θ_max - θ_min|
- **Good target**: Exercise-specific (e.g., 140-170° for bicep curls)
- **Interpretation**: Measures movement completeness

### ⚡ Concentric Velocity
- **Formula**: Δθ / t_concentric
- **Units**: Degrees per second (°/s)
- **Interpretation**: Speed of lifting phase
- **VBT Application**: Drop >20% = approaching failure

### 🎯 Velocity Loss %
- **Formula**: ((V_max - V_last) / V_max) × 100
- **Thresholds**:
  - <10%: Low fatigue, can continue
  - 10-20%: Moderate fatigue, good training zone
  - >20%: High fatigue, consider stopping
- **Use**: Determine optimal training volume

### 🧘 Clean Technique %
- **Formula**: (Reps without alerts / Total reps) × 100
- **Good target**: >80%
- **Interpretation**: Form consistency throughout set

### ⏱️ Tempo (E-P-C)
- **Format**: Eccentric-Pause-Concentric (e.g., "3.0-0-2.1")
- **Units**: Seconds
- **Interpretation**: 
  - Eccentric: Controlled lowering (2-4s ideal)
  - Pause: Time at bottom (usually 0)
  - Concentric: Explosive lifting (1-2s ideal)

## Dashboard Aesthetics

The dashboard uses a modern dark theme optimized for:
- **Readability**: High contrast, large fonts
- **Professional Look**: Suitable for training logs
- **Print Quality**: 300 DPI, high resolution
- **Color Psychology**:
  - Neon Green (#00FFAA): Primary metric, positive
  - Neon Red (#FF3366): Alerts, fatigue, danger
  - Neon Blue (#00BFFF): Secondary metrics
  - Gold (#FFD700): Thresholds, warnings

## File Structure

```
sessions/
├── session_<exercise>_<timestamp>.json       # Complete data
├── session_<exercise>_<timestamp>_reps.csv   # Rep summaries
├── session_<exercise>_<timestamp>_frames.csv # Time-series (sampled)
└── report_<exercise>_<timestamp>.png         # Dashboard (300 DPI)
```

## Advanced Features

### Minimum Data Threshold

Dashboard generation requires:
- **At least 1 completed rep** OR
- **More than 3 seconds of recording**

For sessions with <3 reps, a simplified quick summary is shown instead.

### Data Sampling

Frame data is sampled (every 5th frame) in CSV export to keep file sizes manageable while retaining temporal detail.

### Error Handling

If dashboard generation fails, the session data is still saved. You can manually generate the dashboard later using the saved JSON file.

## Scientific Background

### Velocity-Based Training (VBT)

The velocity drop analysis is based on VBT research:
- Movement velocity decreases with muscular fatigue
- A 20% velocity drop typically indicates 3-5 RIR (reps in reserve)
- Useful for autoregulation (adjust volume based on fatigue)

**References**:
- Pareja-Blanco et al. (2017). *Velocity Loss as a Variable for Monitoring Resistance Exercise*
- González-Badillo & Sánchez-Medina (2010). *Movement Velocity as a Measure of Loading Intensity*

### Time Under Tension (TUT)

TUT is a key hypertrophy stimulus:
- Optimal range: 40-70s per set for muscle growth
- Balance between mechanical tension and metabolic stress
- Tracked automatically per rep and cumulative

### ROM & Biomechanics

Full ROM ensures:
- Complete muscle fiber recruitment
- Joint health and mobility
- Reduced injury risk
- Standardized rep counting

## Tips for Best Results

1. **Review Dashboard After Each Session**
   - Look for velocity drop patterns
   - Check form consistency (clean technique %)
   - Identify weak points in ROM

2. **Track Trends Over Time**
   - Compare velocity across sessions
   - Monitor ROM improvements
   - Watch for compensation patterns

3. **Adjust Training Volume**
   - Stop when velocity drops >20%
   - Aim for 80%+ clean technique
   - Use data to periodize training

4. **Export for External Analysis**
   - Import CSV into spreadsheets
   - Create custom visualizations
   - Track long-term progress

## Troubleshooting

### Dashboard doesn't appear
- Check console for errors
- Verify you completed at least 1 rep
- Ensure matplotlib is installed

### Missing data in CSV
- Some frames may be skipped if pose not detected
- Rep data only recorded when FSM completes full cycle

### Dashboard looks different
- Check matplotlib version
- Theme colors may vary by system
- Resolution depends on display

## Future Enhancements (Phase 3)

Potential additions:
- [ ] Asymmetry analysis (left vs right)
- [ ] Export to Google Sheets/Excel automatically
- [ ] Web dashboard for multi-session trends
- [ ] Mobile app version
- [ ] Social sharing features

---

**The telemetry system runs automatically - just train, press 'q', and enjoy your data! 🏋️📊**
