# Sessions Directory

This directory stores workout session data and post-workout dashboard reports.

## Automatically Generated Files

After each workout session (when you press `q` to quit), the following files are created:

### Session Data Files

1. **`session_<exercise>_<timestamp>.json`**
   - Complete session data in JSON format
   - Contains metadata, frame-by-frame data, and rep summaries
   - Useful for programmatic analysis

2. **`session_<exercise>_<timestamp>_reps.csv`**
   - Rep-by-rep summary in CSV format
   - Columns: rep_number, rom_degrees, eccentric_time_s, concentric_time_s, concentric_velocity_deg_s, had_compensation, max_angle, min_angle
   - Easy to import into Excel, Google Sheets, or data analysis tools

3. **`session_<exercise>_<timestamp>_frames.csv`**
   - Frame-level time-series data (sampled every 5 frames)
   - Columns: timestamp, angle, fsm_state, has_posture_alert, alert_text
   - Useful for detailed biomechanical analysis

### Dashboard Reports

4. **`report_<exercise>_<timestamp>.png`**
   - High-resolution (300 DPI) biomechanical dashboard
   - 3-panel visualization:
     - Joint angle curve with posture alerts
     - Velocity-based training (VBT) fatigue analysis
     - Tempo and time under tension comparison
   - Ready to share or include in training logs

## Example Files

```
sessions/
├── session_Bicep_Curl_Right_20261027_201945.json
├── session_Bicep_Curl_Right_20261027_201945_reps.csv
├── session_Bicep_Curl_Right_20261027_201945_frames.csv
├── report_Bicep_Curl_Right_20261027_201945.png
├── session_Squat_20261027_203012.json
└── ...
```

## Data Analysis Examples

### Load session in Python:
```python
import json
import pandas as pd

# Load complete session
with open('sessions/session_Bicep_Curl_Right_20261027_201945.json') as f:
    session = json.load(f)

# Load rep summaries
df_reps = pd.read_csv('sessions/session_Bicep_Curl_Right_20261027_201945_reps.csv')
print(df_reps.describe())
```

### Load in Excel/Google Sheets:
1. Open Excel/Sheets
2. Import CSV file
3. Analyze trends, create charts, calculate statistics

## Key Metrics Tracked

### Per Repetition:
- **ROM (Range of Motion)**: Total joint angle excursion
- **Eccentric Time**: Duration of lowering phase
- **Concentric Time**: Duration of lifting phase  
- **Concentric Velocity**: Speed of lifting (degrees/second)
- **Compensation**: Whether form violations occurred

### Session-wide:
- Total repetitions
- Total time under tension (TUT)
- Average ROM
- Velocity loss percentage (fatigue indicator)
- Clean technique percentage

## Dashboard Features

The auto-generated dashboard provides:

1. **📐 Angle Tracking**: See your joint angles throughout the entire workout
2. **⚡ Fatigue Analysis**: Track velocity drop to identify optimal training volume
3. **⏱️ Tempo Analysis**: Compare eccentric vs concentric phases
4. **🎯 Form Alerts**: Visual markers showing when technique broke down

## Privacy & Storage

- All session data is stored locally on your machine
- No data is sent to external servers
- You can delete old sessions at any time
- Consider backing up important sessions

---

**Tip**: Review your dashboard after each session to track progress and identify areas for improvement!
