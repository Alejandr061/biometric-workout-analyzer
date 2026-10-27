"""
Squat biomechanical analysis.

Tracks:
- Knee angle (depth)
- Hip angle (depth)
- Torso inclination (form)
- Knee alignment (safety)
"""
from typing import Dict, List, Optional
from .base_exercise import BaseExercise, ExerciseState
from ..core.geometry import calculate_angle, calculate_vertical_inclination


class Squat(BaseExercise):
    """
    Biomechanical analyzer for squats.
    
    Key landmarks: hip, knee, ankle, shoulder
    Primary angle: Knee flexion angle
    
    Form checks:
    - Depth: Hip below parallel (knee angle < 90°)
    - Torso: Should not lean excessively forward
    - Knee tracking: Should track over toes
    """
    
    # Angle thresholds for state transitions
    STANDING_THRESHOLD = 160.0  # Degrees - starting position
    PARALLEL_THRESHOLD = 90.0   # Degrees - parallel depth
    DEEP_THRESHOLD = 70.0       # Degrees - deep squat
    
    # Form violation thresholds
    TORSO_LEAN_THRESHOLD = 45.0  # Degrees from vertical (relaxed for squat)
    MIN_DEPTH_ANGLE = 100.0      # Must go below this for valid rep
    
    def __init__(self, side: str = "right"):
        """
        Initialize squat analyzer.
        
        Args:
            side: Which leg to primarily track - "left" or "right"
        """
        super().__init__("Squat")
        
        if side not in ["left", "right"]:
            raise ValueError(f"Side must be 'left' or 'right', got '{side}'")
        
        self.side = side
        self._min_depth_achieved = False
        
    def get_target_landmarks(self) -> List[str]:
        """Return required landmarks for squat analysis."""
        return [
            f"{self.side}_hip",
            f"{self.side}_knee",
            f"{self.side}_ankle",
            f"{self.side}_shoulder",
        ]
    
    def analyze_frame(self, pose_detector) -> Dict[str, any]:
        """
        Analyze frame for squat biomechanics.
        
        Returns:
            Dictionary with:
            - state: Current exercise state
            - knee_angle: Knee flexion angle
            - hip_angle: Hip flexion angle
            - reps: Completed repetition count
            - alerts: List of form violation messages
            - depth: Depth category (partial/parallel/deep)
        """
        self._clear_alerts()
        
        # Get required landmarks
        hip, knee, ankle, shoulder = pose_detector.get_landmarks(
            f"{self.side}_hip",
            f"{self.side}_knee",
            f"{self.side}_ankle",
            f"{self.side}_shoulder"
        )
        
        # Check if all landmarks are visible
        if not all([hip, knee, ankle, shoulder]):
            return self._build_result(None, None)
        
        # Calculate angles
        frame_h, frame_w = 480, 640
        hip_px = hip.to_pixel_coords(frame_w, frame_h)
        knee_px = knee.to_pixel_coords(frame_w, frame_h)
        ankle_px = ankle.to_pixel_coords(frame_w, frame_h)
        shoulder_px = shoulder.to_pixel_coords(frame_w, frame_h)
        
        # Primary angle: knee flexion
        knee_angle = calculate_angle(hip_px, knee_px, ankle_px)
        self._track_angle(knee_angle)
        
        # Secondary angle: hip flexion (for depth confirmation)
        # Use shoulder-hip-knee angle as proxy
        hip_angle = calculate_angle(shoulder_px, hip_px, knee_px)
        
        # Check form violations
        self._check_depth(knee_angle)
        self._check_torso_lean(shoulder, hip)
        
        # Update FSM
        self._update_state_machine(knee_angle)
        
        return self._build_result(knee_angle, hip_angle)
    
    def _update_state_machine(self, knee_angle: float):
        """Update exercise state based on knee angle."""
        
        if self.state == ExerciseState.IDLE:
            # Start eccentric phase when knees begin to bend
            if knee_angle < self.STANDING_THRESHOLD - 10:
                self._transition_state(ExerciseState.ECCENTRIC)
                self._min_depth_achieved = False
        
        elif self.state == ExerciseState.ECCENTRIC:
            # Check if minimum depth achieved
            if knee_angle <= self.MIN_DEPTH_ANGLE:
                self._min_depth_achieved = True
            
            # Detect bottom when knee angle stops decreasing
            if knee_angle <= self.PARALLEL_THRESHOLD:
                self._transition_state(ExerciseState.BOTTOM)
        
        elif self.state == ExerciseState.BOTTOM:
            # Start concentric phase when angle begins to increase
            if knee_angle > self.PARALLEL_THRESHOLD + 5:
                self._transition_state(ExerciseState.CONCENTRIC)
        
        elif self.state == ExerciseState.CONCENTRIC:
            # Return to idle when standing upright
            if knee_angle >= self.STANDING_THRESHOLD:
                # Only count rep if minimum depth was achieved
                if not self._min_depth_achieved:
                    self._add_alert("⚠️ Rep not counted - Insufficient depth!")
                    # Reset without counting
                    self.state = ExerciseState.IDLE
                    self._eccentric_start = None
                    self._concentric_start = None
                else:
                    self._transition_state(ExerciseState.IDLE)
    
    def _check_depth(self, knee_angle: float):
        """Provide real-time depth feedback."""
        if self.state in [ExerciseState.ECCENTRIC, ExerciseState.BOTTOM]:
            if knee_angle > self.MIN_DEPTH_ANGLE:
                degrees_to_go = knee_angle - self.PARALLEL_THRESHOLD
                self._add_alert(f"⬇️ Go deeper ({degrees_to_go:.0f}° to parallel)")
    
    def _check_torso_lean(self, shoulder, hip):
        """Detect excessive forward lean (can strain lower back)."""
        shoulder_coords = (shoulder.x, shoulder.y)
        hip_coords = (hip.x, hip.y)
        
        inclination = calculate_vertical_inclination(shoulder_coords, hip_coords)
        
        if inclination > self.TORSO_LEAN_THRESHOLD:
            self._add_alert(f"⚠️ Excessive forward lean ({inclination:.1f}°) - Chest up!")
    
    def _get_depth_category(self, knee_angle: float) -> str:
        """Categorize squat depth."""
        if knee_angle >= self.MIN_DEPTH_ANGLE:
            return "PARTIAL"
        elif knee_angle >= self.PARALLEL_THRESHOLD:
            return "PARALLEL"
        elif knee_angle >= self.DEEP_THRESHOLD:
            return "DEEP"
        else:
            return "ATG"  # Ass to Grass
    
    def _build_result(
        self,
        knee_angle: Optional[float],
        hip_angle: Optional[float]
    ) -> Dict[str, any]:
        """Build analysis result dictionary."""
        depth = self._get_depth_category(knee_angle) if knee_angle else "N/A"
        
        return {
            'state': self.state.value,
            'knee_angle': knee_angle,
            'hip_angle': hip_angle,
            'reps': self.rep_count,
            'alerts': self.active_alerts.copy(),
            'depth': depth,
            'rom': self._max_angle_current_rep - self._min_angle_current_rep,
            'tempo': self.get_tempo(),
            'tut': self.get_total_tut()
        }
    
    def get_primary_angle(self) -> Optional[float]:
        """Return current knee angle."""
        if self._current_angles:
            return self._current_angles[-1]
        return None
