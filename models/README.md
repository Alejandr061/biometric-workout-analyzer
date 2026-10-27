# MediaPipe Models Directory

This directory contains the MediaPipe Pose Landmarker model required for pose detection.

## Required Model

The application requires the **Pose Landmarker Lite** model:

- **File**: `pose_landmarker_lite.task`
- **Size**: ~10MB
- **Download URL**: https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task

## Installation

### Windows (PowerShell):
```powershell
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task" -OutFile "models/pose_landmarker_lite.task"
```

### macOS/Linux:
```bash
curl -L -o models/pose_landmarker_lite.task "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
```

## Verification

After downloading, verify the file exists:
```bash
# Should show the .task file
ls models/
```

The application will automatically detect and load the model from this directory.

## Model Information

- **Type**: Pose Landmarker (33 landmarks)
- **Precision**: Float16
- **Complexity**: Lite (balanced speed/accuracy)
- **License**: Apache 2.0 (MediaPipe)

## Troubleshooting

If you see a "model not found" error:
1. Ensure the file is named exactly `pose_landmarker_lite.task`
2. Verify it's in the `models/` directory at the project root
3. Check the file size is ~10MB (not a partial download)

---

**Note**: Model files are excluded from git by `.gitignore` due to their size.
