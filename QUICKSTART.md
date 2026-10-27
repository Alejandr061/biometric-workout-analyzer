# 🚀 Quick Start Guide

Get up and running with the Biometric Workout Analyzer in 5 minutes!

## Step 1: Verify Setup

```bash
python verify_setup.py
```

This checks:
- ✅ All dependencies are installed
- ✅ Project structure is correct
- ✅ Modules can be imported
- ✅ Camera is available (optional)

## Step 2: Run Demo (No Camera Required)

Test the system without needing a camera or video:

```bash
python demo_no_camera.py
```

Expected output:
```
🎉 All tests passed! The system is ready to use.
```

## Step 3: Test with Webcam

```bash
python main.py --exercise curl --source 0
```

**Controls:**
- `q` or `ESC` - Quit
- `r` - Reset rep counter
- `s` - Toggle skeleton overlay

**Position yourself:**
- Stand 6-8 feet from camera
- Ensure full body or upper body is visible
- Good lighting is important
- Side profile works best for most exercises

## Step 4: Try Different Exercises

### Bicep Curl (Right Arm)
```bash
python main.py --exercise curl --side right --source 0
```

### Bicep Curl (Left Arm)
```bash
python main.py --exercise curl --side left --source 0
```

### Squat
```bash
python main.py --exercise squat --source 0
```

## Step 5: Test with Video File

1. Place a workout video in the `assets/` folder
2. Run:
```bash
python main.py --exercise squat --source assets/your_video.mp4
```

## Understanding the HUD

```
┌─────────────────────────┐
│ Bicep Curl (Right)      │ ← Exercise name
│ REPS: 5                 │ ← Rep counter (large)
│ State: CONCENTRIC       │ ← Current phase
│ Tempo: 3.2-0-2.1       │ ← Avg tempo (ecc-pause-con)
│ TUT: 26.5s             │ ← Total time under tension
└─────────────────────────┘

┌─────────────────────────┐
│ ▓▓▓▓▓▓▓░░░ 78.5°      │ ← Angle gauge with progress bar
└─────────────────────────┘

┌─────────────────────────────────────────┐
│ ⚠ Torso swinging (16.2°) - Keep stable! │ ← Form alerts (red banner)
└─────────────────────────────────────────┘
```

## Troubleshooting

### "No pose detected"
- **Solution**: Ensure full body is in frame with good lighting
- Move further from camera if too close
- Check camera permissions

### Low FPS (< 15 FPS)
- **Solution**: Use `--confidence 0.5` to reduce processing load
- Close other resource-intensive applications
- Consider using a lower resolution video

### "Module not found" errors
- **Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt
```

### Camera not working
- **Solution**: Check camera permissions in Windows settings
- Try a different camera index: `--source 1` or `--source 2`
- Test with a video file instead

## Tips for Best Results

### Camera Setup
- Use a tripod or stable surface
- Position camera at waist height for squats
- Position camera at chest height for upper body exercises
- Ensure side profile is visible

### Lighting
- Bright, even lighting works best
- Avoid backlighting (light source behind you)
- Natural daylight is ideal

### Clothing
- Wear fitted clothing for better landmark detection
- Contrasting colors from background help
- Avoid baggy or loose clothing

### Form
- Perform exercises with controlled tempo
- Full range of motion for accurate ROM tracking
- Avoid rapid, jerky movements

## Command Reference

### Basic Usage
```bash
python main.py --exercise {curl|squat} --source {0|video.mp4}
```

### All Options
```bash
python main.py \
  --exercise curl \           # Exercise type
  --source 0 \               # Video source (0=webcam, or path)
  --side right \             # Side to track (left/right)
  --confidence 0.6 \         # Landmark confidence (0.0-1.0)
  --no-skeleton              # Disable skeleton overlay
```

## Session Summary Example

After quitting (`q` key), you'll see:

```
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

## What's Next?

- **Phase 2 Features** (Coming Soon):
  - JSON/CSV export of session data
  - Symmetry analysis (left vs. right)
  - More exercises (shoulder press, deadlift, push-ups)
  - Web dashboard for progress tracking

- **Customize the System**:
  - Add new exercises in `src/exercises/`
  - Adjust form thresholds for your preferences
  - Modify HUD colors and layout
  - Export telemetry for external analysis

## Need Help?

- **Documentation**: See `README.md` for detailed info
- **Run Tests**: `python tests/test_geometry.py`
- **Check Setup**: `python verify_setup.py`
- **Demo Mode**: `python demo_no_camera.py`

---

**Ready to go? Start with:**
```bash
python main.py --exercise curl --source 0
```

Happy training! 🏋️💪
