"""
Pose detection wrapper for MediaPipe Pose.
Provides clean interface with confidence filtering and coordinate smoothing.
Compatible with MediaPipe 0.10.30+ (tasks API).
"""
import cv2
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from .smoothing import EMAFilter


@dataclass
class Landmark:
    """Representation of a single pose landmark with confidence."""
    x: float  # Normalized x coordinate [0, 1]
    y: float  # Normalized y coordinate [0, 1]
    z: float  # Depth (relative to hips)
    visibility: float  # Confidence score [0, 1]
    
    def to_pixel_coords(self, frame_width: int, frame_height: int) -> Tuple[int, int]:
        """Convert normalized coordinates to pixel coordinates."""
        return (int(self.x * frame_width), int(self.y * frame_height))


class PoseDetector:
    """
    Wrapper for MediaPipe Pose estimation with built-in filtering.
    
    Features:
    - Automatic confidence thresholding
    - Optional EMA smoothing for jitter reduction
    - Easy landmark access by name
    """
    
    # MediaPipe landmark indices
    LANDMARKS = {
        'nose': 0,
        'left_eye_inner': 1,
        'left_eye': 2,
        'left_eye_outer': 3,
        'right_eye_inner': 4,
        'right_eye': 5,
        'right_eye_outer': 6,
        'left_ear': 7,
        'right_ear': 8,
        'mouth_left': 9,
        'mouth_right': 10,
        'left_shoulder': 11,
        'right_shoulder': 12,
        'left_elbow': 13,
        'right_elbow': 14,
        'left_wrist': 15,
        'right_wrist': 16,
        'left_pinky': 17,
        'right_pinky': 18,
        'left_index': 19,
        'right_index': 20,
        'left_thumb': 21,
        'right_thumb': 22,
        'left_hip': 23,
        'right_hip': 24,
        'left_knee': 25,
        'right_knee': 26,
        'left_ankle': 27,
        'right_ankle': 28,
        'left_heel': 29,
        'right_heel': 30,
        'left_foot_index': 31,
        'right_foot_index': 32,
    }
    
    def __init__(
        self,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.7,
        visibility_threshold: float = 0.6,
        enable_smoothing: bool = True,
        smoothing_alpha: float = 0.5
    ):
        """
        Initialize pose detector.
        
        Args:
            min_detection_confidence: Minimum confidence for initial detection
            min_tracking_confidence: Minimum confidence for tracking
            visibility_threshold: Minimum visibility to return landmark (0.6 recommended)
            enable_smoothing: Apply EMA filter to reduce jitter
            smoothing_alpha: EMA smoothing factor (0.3-0.7 recommended)
        """
        # Get model path
        import os
        from pathlib import Path
        
        # Try to find model in multiple locations
        script_dir = Path(__file__).parent.parent.parent  # Go up to project root
        model_paths = [
            script_dir / "models" / "pose_landmarker_lite.task",
            Path.cwd() / "models" / "pose_landmarker_lite.task",
        ]
        
        model_path = None
        for path in model_paths:
            if path.exists():
                model_path = str(path)
                break
        
        if model_path is None:
            raise FileNotFoundError(
                "MediaPipe pose model not found. Please download it:\n"
                "  mkdir models\n"
                "  # Download from: https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task\n"
                "  # Save to: models/pose_landmarker_lite.task"
            )
        
        # Create PoseLandmarker options
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            min_pose_detection_confidence=min_detection_confidence,
            min_pose_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_segmentation_masks=False
        )
        
        # Create detector
        self.detector = vision.PoseLandmarker.create_from_options(options)
        
        self.visibility_threshold = visibility_threshold
        self.enable_smoothing = enable_smoothing
        self.smoother = EMAFilter(alpha=smoothing_alpha) if enable_smoothing else None
        
        self._current_landmarks: Optional[Dict[str, Landmark]] = None
        self._frame_timestamp_ms = 0
    
    def process_frame(self, frame: np.ndarray) -> bool:
        """
        Process a video frame and extract pose landmarks.
        
        Args:
            frame: BGR image from OpenCV (numpy array)
            
        Returns:
            True if pose was detected, False otherwise
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect pose
        self._frame_timestamp_ms += 33  # Approximate 30 FPS
        detection_result = self.detector.detect_for_video(mp_image, self._frame_timestamp_ms)
        
        if not detection_result.pose_landmarks or len(detection_result.pose_landmarks) == 0:
            self._current_landmarks = None
            return False
        
        # Extract and filter landmarks (use first detected pose)
        pose_landmarks = detection_result.pose_landmarks[0]
        frame_height, frame_width = frame.shape[:2]
        landmarks = {}
        
        for name, idx in self.LANDMARKS.items():
            if idx >= len(pose_landmarks):
                continue
                
            lm = pose_landmarks[idx]
            
            # MediaPipe tasks API uses visibility field
            visibility = lm.visibility if hasattr(lm, 'visibility') else 1.0
            
            # Check visibility threshold
            if visibility < self.visibility_threshold:
                continue
            
            # Apply smoothing if enabled
            if self.enable_smoothing and self.smoother:
                smoothed_x, smoothed_y = self.smoother.smooth(name, (lm.x, lm.y))
            else:
                smoothed_x, smoothed_y = lm.x, lm.y
            
            landmarks[name] = Landmark(
                x=smoothed_x,
                y=smoothed_y,
                z=lm.z,
                visibility=visibility
            )
        
        self._current_landmarks = landmarks
        return True
    
    def get_landmark(self, name: str) -> Optional[Landmark]:
        """
        Get a specific landmark by name.
        
        Args:
            name: Landmark name (e.g., 'left_shoulder', 'right_knee')
            
        Returns:
            Landmark object or None if not visible/detected
        """
        if self._current_landmarks is None:
            return None
        return self._current_landmarks.get(name)
    
    def get_landmarks(self, *names: str) -> Tuple[Optional[Landmark], ...]:
        """
        Get multiple landmarks at once.
        
        Args:
            *names: Variable number of landmark names
            
        Returns:
            Tuple of Landmark objects (None for missing landmarks)
            
        Example:
            shoulder, elbow, wrist = detector.get_landmarks(
                'left_shoulder', 'left_elbow', 'left_wrist'
            )
        """
        return tuple(self.get_landmark(name) for name in names)
    
    def has_landmarks(self, *names: str) -> bool:
        """Check if all specified landmarks are currently visible."""
        return all(self.get_landmark(name) is not None for name in names)
    
    def draw_skeleton(
        self,
        frame: np.ndarray,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw pose skeleton overlay on frame.
        
        Args:
            frame: Input frame
            color: BGR color for skeleton lines
            thickness: Line thickness in pixels
            
        Returns:
            Frame with skeleton overlay
        """
        if self._current_landmarks is None:
            return frame
        
        frame_height, frame_width = frame.shape[:2]
        
        # Define skeleton connections
        connections = [
            # Torso
            ('left_shoulder', 'right_shoulder'),
            ('left_shoulder', 'left_hip'),
            ('right_shoulder', 'right_hip'),
            ('left_hip', 'right_hip'),
            # Left arm
            ('left_shoulder', 'left_elbow'),
            ('left_elbow', 'left_wrist'),
            # Right arm
            ('right_shoulder', 'right_elbow'),
            ('right_elbow', 'right_wrist'),
            # Left leg
            ('left_hip', 'left_knee'),
            ('left_knee', 'left_ankle'),
            # Right leg
            ('right_hip', 'right_knee'),
            ('right_knee', 'right_ankle'),
        ]
        
        # Draw connections
        for start_name, end_name in connections:
            start_lm = self.get_landmark(start_name)
            end_lm = self.get_landmark(end_name)
            
            if start_lm and end_lm:
                start_pt = start_lm.to_pixel_coords(frame_width, frame_height)
                end_pt = end_lm.to_pixel_coords(frame_width, frame_height)
                cv2.line(frame, start_pt, end_pt, color, thickness)
        
        # Draw landmarks as circles
        for landmark in self._current_landmarks.values():
            pt = landmark.to_pixel_coords(frame_width, frame_height)
            cv2.circle(frame, pt, 4, color, -1)
            cv2.circle(frame, pt, 5, (255, 255, 255), 1)
        
        return frame
    
    def reset(self):
        """Reset detector state (e.g., when switching video source)."""
        if self.smoother:
            self.smoother.reset()
        self._current_landmarks = None
        self._frame_timestamp_ms = 0
    
    def __del__(self):
        """Clean up MediaPipe resources."""
        if hasattr(self, 'detector'):
            self.detector.close()
