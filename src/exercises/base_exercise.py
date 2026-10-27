"""
Base abstract class for exercise analysis using Finite State Machines.
All exercise implementations inherit from this class.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import time


class ExerciseState(Enum):
    """Finite State Machine states for exercise repetitions."""
    IDLE = "idle"  # Starting position / between reps
    ECCENTRIC = "eccentric"  # Lowering phase (lengthening muscle)
    BOTTOM = "bottom"  # Bottom position / transition
    CONCENTRIC = "concentric"  # Lifting phase (shortening muscle)
    

@dataclass
class RepData:
    """Data collected for a single repetition."""
    rep_number: int
    rom_degrees: float  # Range of Motion in degrees
    eccentric_time: float  # Time for lowering phase (seconds)
    concentric_time: float  # Time for lifting phase (seconds)
    time_under_tension: float  # Total TUT for this rep (seconds)
    max_angle: float  # Maximum angle reached
    min_angle: float  # Minimum angle reached
    posture_alerts: List[str] = field(default_factory=list)  # Form violations
    timestamp: float = field(default_factory=time.time)
    

class BaseExercise(ABC):
    """
    Abstract base class for biomechanical exercise analysis.
    
    Each exercise must implement:
    - analyze_frame(): Process pose landmarks and update FSM
    - get_primary_angle(): Return the main angle being tracked
    - get_target_landmarks(): List required landmarks for this exercise
    """
    
    def __init__(self, name: str):
        """
        Initialize exercise analyzer.
        
        Args:
            name: Human-readable exercise name (e.g., "Bicep Curl")
        """
        self.name = name
        self.state = ExerciseState.IDLE
        
        # Rep counting
        self.rep_count = 0
        self.completed_reps: List[RepData] = []
        
        # Timing
        self._state_start_time = time.time()
        self._eccentric_start: Optional[float] = None
        self._concentric_start: Optional[float] = None
        
        # Angle tracking for current rep
        self._current_angles: List[float] = []
        self._min_angle_current_rep = float('inf')
        self._max_angle_current_rep = 0.0
        
        # Posture alerts
        self.active_alerts: List[str] = []
        self._rep_alerts: List[str] = []
        
        # Telemetry logger (optional, set externally)
        self.logger = None
    
    @abstractmethod
    def analyze_frame(self, pose_detector) -> Dict[str, any]:
        """
        Analyze current frame and update exercise state.
        
        Args:
            pose_detector: PoseDetector instance with processed frame
            
        Returns:
            Dictionary with analysis results:
            {
                'state': ExerciseState,
                'angle': float,
                'reps': int,
                'alerts': List[str],
                'rom': float,  # Current ROM
                ...
            }
        """
        pass
    
    @abstractmethod
    def get_primary_angle(self) -> Optional[float]:
        """Return the current primary angle being tracked (e.g., elbow, knee)."""
        pass
    
    @abstractmethod
    def get_target_landmarks(self) -> List[str]:
        """Return list of required landmark names for this exercise."""
        pass
    
    def _transition_state(self, new_state: ExerciseState):
        """
        Handle state transition with timing logic.
        
        Args:
            new_state: Target state to transition to
        """
        if new_state == self.state:
            return
        
        current_time = time.time()
        
        # Handle state exit
        if self.state == ExerciseState.IDLE and new_state == ExerciseState.ECCENTRIC:
            self._eccentric_start = current_time
            self._current_angles.clear()
            self._min_angle_current_rep = float('inf')
            self._max_angle_current_rep = 0.0
            self._rep_alerts.clear()
        
        elif self.state == ExerciseState.ECCENTRIC and new_state == ExerciseState.BOTTOM:
            pass  # Brief transition state
        
        elif self.state == ExerciseState.BOTTOM and new_state == ExerciseState.CONCENTRIC:
            self._concentric_start = current_time
        
        elif self.state == ExerciseState.CONCENTRIC and new_state == ExerciseState.IDLE:
            # Rep completed - record data
            self._complete_rep()
        
        # Update state
        self.state = new_state
        self._state_start_time = current_time
    
    def _complete_rep(self):
        """Record completed repetition with collected metrics."""
        if self._eccentric_start is None or self._concentric_start is None:
            return  # Incomplete rep data
        
        current_time = time.time()
        
        eccentric_time = self._concentric_start - self._eccentric_start
        concentric_time = current_time - self._concentric_start
        total_tut = eccentric_time + concentric_time
        
        rom = self._max_angle_current_rep - self._min_angle_current_rep
        
        rep_data = RepData(
            rep_number=self.rep_count + 1,
            rom_degrees=rom,
            eccentric_time=eccentric_time,
            concentric_time=concentric_time,
            time_under_tension=total_tut,
            max_angle=self._max_angle_current_rep,
            min_angle=self._min_angle_current_rep,
            posture_alerts=self._rep_alerts.copy()
        )
        
        self.completed_reps.append(rep_data)
        self.rep_count += 1
        
        # Log to telemetry if available
        if self.logger:
            self.logger.log_rep_completion(
                rep_number=rep_data.rep_number,
                rom_degrees=rep_data.rom_degrees,
                eccentric_time_s=rep_data.eccentric_time,
                concentric_time_s=rep_data.concentric_time,
                max_angle=rep_data.max_angle,
                min_angle=rep_data.min_angle,
                had_compensation=len(rep_data.posture_alerts) > 0
            )
        
        # Reset for next rep
        self._eccentric_start = None
        self._concentric_start = None
        self._rep_alerts.clear()
    
    def _track_angle(self, angle: float):
        """Track angle for ROM calculation."""
        if angle is None:
            return
        
        self._current_angles.append(angle)
        self._min_angle_current_rep = min(self._min_angle_current_rep, angle)
        self._max_angle_current_rep = max(self._max_angle_current_rep, angle)
    
    def _add_alert(self, alert_message: str):
        """
        Add a posture alert for current frame.
        
        Args:
            alert_message: Description of form violation
        """
        if alert_message not in self.active_alerts:
            self.active_alerts.append(alert_message)
        
        if alert_message not in self._rep_alerts:
            self._rep_alerts.append(alert_message)
    
    def _clear_alerts(self):
        """Clear active alerts (call at start of each frame analysis)."""
        self.active_alerts.clear()
    
    def get_state_duration(self) -> float:
        """Get time spent in current state (seconds)."""
        return time.time() - self._state_start_time
    
    def get_total_tut(self) -> float:
        """Get total Time Under Tension for all completed reps."""
        return sum(rep.time_under_tension for rep in self.completed_reps)
    
    def get_average_rom(self) -> float:
        """Get average Range of Motion across all reps."""
        if not self.completed_reps:
            return 0.0
        return sum(rep.rom_degrees for rep in self.completed_reps) / len(self.completed_reps)
    
    def get_tempo(self) -> str:
        """
        Get average tempo in standard notation: eccentric-bottom-concentric.
        Example: "3-0-2" = 3s down, 0s pause, 2s up
        """
        if not self.completed_reps:
            return "0-0-0"
        
        avg_ecc = sum(rep.eccentric_time for rep in self.completed_reps) / len(self.completed_reps)
        avg_con = sum(rep.concentric_time for rep in self.completed_reps) / len(self.completed_reps)
        
        return f"{avg_ecc:.1f}-0-{avg_con:.1f}"
    
    def set_logger(self, logger):
        """
        Attach telemetry logger to exercise.
        
        Args:
            logger: SessionLogger instance
        """
        self.logger = logger
    
    def reset(self):
        """Reset all exercise metrics (e.g., start new session)."""
        self.state = ExerciseState.IDLE
        self.rep_count = 0
        self.completed_reps.clear()
        self.active_alerts.clear()
        self._rep_alerts.clear()
        self._current_angles.clear()
        self._eccentric_start = None
        self._concentric_start = None
        self._state_start_time = time.time()
