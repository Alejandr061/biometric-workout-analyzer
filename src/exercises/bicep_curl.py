"""
Bicep Curl biomechanical analysis.

Tracks:
- Elbow angle (ROM)
- Torso stability (no swinging)
- Elbow position (should stay relatively fixed)
"""
from typing import Dict, List, Optional
from .base_exercise import BaseExercise, ExerciseState
from ..core.geometry import calculate_angle, calculate_vertical_inclination, euclidean_distance


class BicepCurl(BaseExercise):
    """
    Biomechanical analyzer for bicep curls.
    
    Key landmarks: shoulder, elbow, wrist, hip
    Primary angle: Elbow flexion angle
    
    Form checks:
    - Elbow should not drift forward significantly
    - Torso should remain upright (no swinging)
    - Full ROM: ~180° extended to ~30° flexed
    """
    
    # Angle thresholds for state transitions
    EXTENDED_THRESHOLD = 160.0  # Degrees - starting position
    FLEXED_THRESHOLD = 50.0     # Degrees - bottom position
    
    # Form violation thresholds
    TORSO_LEAN_THRESHOLD = 15.0  # Degrees from vertical
    ELBOW_DRIFT_THRESHOLD = 50.0  # Pixels forward from starting position
    
    def __init__(self, side: str = "right"):
        """
        Initialize bicep curl analyzer.
        
        Args:
            side: Which arm to track - "left" or "right"
        """
        super().__init__(f"Bicep Curl ({side.capitalize()})")
        
        if side not in ["left", "right"]:
            raise ValueError(f"Side must be 'left' or 'right', got '{side}'")
        
        self.side = side
        self._initial_elbow_x: Optional[float] = None
        
    def get_target_landmarks(self) -> List[str]:
        """Return required landmarks for bicep curl analysis."""
        return [
            f"{self.side}_shoulder",
            f"{self.side}_elbow",
            f"{self.side}_wrist",
            f"{self.side}_hip",
        ]
    
    def analyze_frame(self, pose_detector) -> Dict[str, any]:
        """
        Analyze frame for bicep curl biomechanics.
        
        Returns:
            Dictionary with:
            - state: Current exercise state
            - angle: Elbow angle in degrees
            - reps: Completed repetition count
            - alerts: List of form violation messages
            - rom: Range of motion so far
        """
        self._clear_alerts()
        
        # Get required landmarks
        shoulder, elbow, wrist, hip = pose_detector.get_landmarks(
            f"{self.side}_shoulder",
            f"{self.side}_elbow",
            f"{self.side}_wrist",
            f"{self.side}_hip"
        )
        
        # Check if all landmarks are visible
        if not all([shoulder, elbow, wrist, hip]):
            return self._build_result(None)
        
        # Calculate primary angle (elbow flexion)
        frame_h, frame_w = 480, 640  # Will be passed from actual frame
        shoulder_px = shoulder.to_pixel_coords(frame_w, frame_h)
        elbow_px = elbow.to_pixel_coords(frame_w, frame_h)
        wrist_px = wrist.to_pixel_coords(frame_w, frame_h)
        hip_px = hip.to_pixel_coords(frame_w, frame_h)
        
        elbow_angle = calculate_angle(shoulder_px, elbow_px, wrist_px)
        self._track_angle(elbow_angle)
        
        # Check form violations
        self._check_torso_stability(shoulder, hip)
        self._check_elbow_drift(elbow_px[0], frame_w)
        
        # Update FSM
        self._update_state_machine(elbow_angle)
        
        return self._build_result(elbow_angle)
    
    def _update_state_machine(self, elbow_angle: float):
        """Update exercise state based on elbow angle."""
        
        if self.state == ExerciseState.IDLE:
            # Start eccentric phase when elbow begins to flex
            if elbow_angle < self.EXTENDED_THRESHOLD - 10:
                self._transition_state(ExerciseState.ECCENTRIC)
        
        elif self.state == ExerciseState.ECCENTRIC:
            # Bottom reached when elbow is sufficiently flexed
            if elbow_angle <= self.FLEXED_THRESHOLD:
                self._transition_state(ExerciseState.BOTTOM)
        
        elif self.state == ExerciseState.BOTTOM:
            # Start concentric phase when angle begins to increase
            if elbow_angle > self.FLEXED_THRESHOLD + 5:
                self._transition_state(ExerciseState.CONCENTRIC)
        
        elif self.state == ExerciseState.CONCENTRIC:
            # Return to idle when arm is nearly extended
            if elbow_angle >= self.EXTENDED_THRESHOLD:
                self._transition_state(ExerciseState.IDLE)
    
    def _check_torso_stability(self, shoulder, hip):
        """Detect torso swinging (momentum assistance)."""
        # Calculate torso inclination from vertical
        shoulder_coords = (shoulder.x, shoulder.y)
        hip_coords = (hip.x, hip.y)
        
        inclination = calculate_vertical_inclination(shoulder_coords, hip_coords)
        
        if inclination > self.TORSO_LEAN_THRESHOLD:
            self._add_alert(f"⚠️ Torso swinging ({inclination:.1f}°) - Keep stable!")
    
    def _check_elbow_drift(self, current_elbow_x: float, frame_width: int):
        """Detect elbow drifting forward (reduces bicep isolation)."""
        # Track initial elbow position
        if self.state == ExerciseState.IDLE:
            self._initial_elbow_x = current_elbow_x
            return
        
        if self._initial_elbow_x is None:
            return
        
        # Check horizontal drift
        drift = abs(current_elbow_x - self._initial_elbow_x)
        
        if drift > self.ELBOW_DRIFT_THRESHOLD:
            drift_cm = drift * 100 / frame_width  # Rough conversion to cm
            self._add_alert(f"⚠️ Elbow drifting forward - Keep elbow fixed!")
    
    def _build_result(self, angle: Optional[float]) -> Dict[str, any]:
        """Build analysis result dictionary."""
        return {
            'state': self.state.value,
            'angle': angle,
            'reps': self.rep_count,
            'alerts': self.active_alerts.copy(),
            'rom': self._max_angle_current_rep - self._min_angle_current_rep,
            'tempo': self.get_tempo(),
            'tut': self.get_total_tut()
        }
    
    def get_primary_angle(self) -> Optional[float]:
        """Return current elbow angle."""
        if self._current_angles:
            return self._current_angles[-1]
        return None
