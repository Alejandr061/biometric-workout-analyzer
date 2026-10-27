# Assets Folder

Place your workout videos here to test the analyzer.

## Recommended Video Format

- **Resolution**: 640x480 or 1280x720
- **Format**: MP4, AVI, MOV
- **Frame Rate**: 30 FPS
- **Duration**: 30 seconds to 5 minutes
- **Camera Angle**: Side profile showing full body

## Example Usage

```bash
# After placing video in this folder
python main.py --exercise squat --source assets/squat_workout.mp4
python main.py --exercise curl --source assets/bicep_curl.mp4
```

## Tips for Recording Good Videos

1. **Lighting**: Bright, even lighting (avoid backlighting)
2. **Position**: Side profile with full body visible
3. **Distance**: 6-8 feet from camera
4. **Clothing**: Fitted clothing for better pose detection
5. **Background**: Plain, contrasting background helps

## Getting Test Videos

You can:
- Record yourself performing exercises
- Use public domain workout videos
- Ask a friend to record you at the gym
- Use smartphone camera on a tripod

## Sample Videos (Not Included)

Due to licensing and size constraints, sample videos are not included.
You'll need to provide your own workout footage.

---

**Note**: Videos in this folder are ignored by git (see `.gitignore`).
Only `README.md` is tracked.
