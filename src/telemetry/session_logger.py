"""
Session telemetry logger for real-time biomechanical data capture.
Records frame-by-frame time-series and rep-by-rep summaries.
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class FrameData:
    """Frame-level telemetry data point."""
    timestamp: float  # Seconds since session start
    angle: float  # Current joint angle in degrees
    fsm_state: str  # IDLE, ECCENTRIC, BOTTOM, CONCENTRIC
    has_posture_alert: bool  # True if any alert active
    alert_text: Optional[str] = None  # Alert message if any


@dataclass
class RepSummary:
    """Rep-level summary metrics."""
    rep_number: int
    rom_degrees: float  # |θ_max - θ_min|
    eccentric_time_s: float  # Time for lowering phase
    concentric_time_s: float  # Time for lifting phase
    concentric_velocity_deg_s: float  # Δθ / t_concentric
    had_compensation: bool  # True if posture alerts during rep
    max_angle: float
    min_angle: float
    

class SessionLogger:
    """
    Real-time telemetry logger for workout sessions.
    
    Captures:
    - Frame-by-frame time-series (angle, state, alerts)
    - Rep-by-rep biomechanical summaries
    
    Export formats: JSON, CSV
    """
    
    def __init__(self, exercise_name: str):
        """
        Initialize session logger.
        
        Args:
            exercise_name: Name of exercise being performed
        """
        self.exercise_name = exercise_name
        self.session_start_time = time.time()
        
        # Time-series data (frame-by-frame)
        self.frame_data: List[FrameData] = []
        
        # Rep summaries
        self.rep_summaries: List[RepSummary] = []
        
        # Session metadata
        self.metadata = {
            'exercise': exercise_name,
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_s': 0.0,
            'total_reps': 0
        }
    
    def log_frame(
        self,
        angle: Optional[float],
        fsm_state: str,
        alerts: List[str]
    ):
        """
        Log frame-level telemetry data.
        
        Args:
            angle: Current joint angle (None if not available)
            fsm_state: Current FSM state
            alerts: List of active posture alerts
        """
        if angle is None:
            return  # Skip frames without angle data
        
        timestamp = time.time() - self.session_start_time
        
        frame = FrameData(
            timestamp=timestamp,
            angle=angle,
            fsm_state=fsm_state,
            has_posture_alert=len(alerts) > 0,
            alert_text=alerts[0] if alerts else None
        )
        
        self.frame_data.append(frame)
    
    def log_rep_completion(
        self,
        rep_number: int,
        rom_degrees: float,
        eccentric_time_s: float,
        concentric_time_s: float,
        max_angle: float,
        min_angle: float,
        had_compensation: bool
    ):
        """
        Log completed repetition summary.
        
        Args:
            rep_number: Repetition number
            rom_degrees: Range of motion (max - min angle)
            eccentric_time_s: Eccentric phase duration
            concentric_time_s: Concentric phase duration
            max_angle: Maximum angle reached
            min_angle: Minimum angle reached
            had_compensation: True if posture alerts occurred
        """
        # Calculate concentric velocity
        if concentric_time_s > 0:
            concentric_velocity = rom_degrees / concentric_time_s
        else:
            concentric_velocity = 0.0
        
        rep_summary = RepSummary(
            rep_number=rep_number,
            rom_degrees=rom_degrees,
            eccentric_time_s=eccentric_time_s,
            concentric_time_s=concentric_time_s,
            concentric_velocity_deg_s=concentric_velocity,
            had_compensation=had_compensation,
            max_angle=max_angle,
            min_angle=min_angle
        )
        
        self.rep_summaries.append(rep_summary)
    
    def get_session_duration(self) -> float:
        """Get current session duration in seconds."""
        return time.time() - self.session_start_time
    
    def has_sufficient_data(self) -> bool:
        """Check if session has enough data for analysis."""
        return len(self.rep_summaries) >= 1 or self.get_session_duration() > 3.0
    
    def export_session(self, output_dir: str = "sessions") -> Dict[str, str]:
        """
        Export session data to JSON and CSV files.
        
        Args:
            output_dir: Directory to save files (created if doesn't exist)
            
        Returns:
            Dictionary with paths to created files
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate timestamp for filenames
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        base_filename = f"session_{self.exercise_name.replace(' ', '_')}_{timestamp}"
        
        # Update metadata
        self.metadata['duration_s'] = self.get_session_duration()
        self.metadata['total_reps'] = len(self.rep_summaries)
        self.metadata['total_frames'] = len(self.frame_data)
        
        # Export to JSON
        json_path = output_path / f"{base_filename}.json"
        session_data = {
            'metadata': self.metadata,
            'frame_data': [asdict(f) for f in self.frame_data],
            'rep_summaries': [asdict(r) for r in self.rep_summaries]
        }
        
        with open(json_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Export rep summaries to CSV
        csv_path = output_path / f"{base_filename}_reps.csv"
        if self.rep_summaries:
            df_reps = pd.DataFrame([asdict(r) for r in self.rep_summaries])
            df_reps.to_csv(csv_path, index=False)
        
        # Export frame data to CSV (sample every 5 frames to reduce size)
        csv_frames_path = output_path / f"{base_filename}_frames.csv"
        if self.frame_data:
            sampled_frames = self.frame_data[::5]  # Every 5th frame
            df_frames = pd.DataFrame([asdict(f) for f in sampled_frames])
            df_frames.to_csv(csv_frames_path, index=False)
        
        return {
            'json': str(json_path),
            'csv_reps': str(csv_path),
            'csv_frames': str(csv_frames_path),
            'session_data': session_data  # For dashboard generation
        }
    
    def get_session_summary(self) -> Dict:
        """
        Get comprehensive session summary statistics.
        
        Returns:
            Dictionary with summary metrics
        """
        if not self.rep_summaries:
            return {
                'total_reps': 0,
                'total_tut_s': 0.0,
                'avg_rom_deg': 0.0,
                'velocity_loss_pct': 0.0,
                'clean_technique_pct': 0.0
            }
        
        # Calculate metrics
        total_reps = len(self.rep_summaries)
        total_tut = sum(r.eccentric_time_s + r.concentric_time_s 
                       for r in self.rep_summaries)
        avg_rom = sum(r.rom_degrees for r in self.rep_summaries) / total_reps
        
        # Velocity loss (VBT analysis)
        velocities = [r.concentric_velocity_deg_s for r in self.rep_summaries]
        if velocities:
            max_velocity = max(velocities)
            last_velocity = velocities[-1]
            if max_velocity > 0:
                velocity_loss = ((max_velocity - last_velocity) / max_velocity) * 100
            else:
                velocity_loss = 0.0
        else:
            velocity_loss = 0.0
        
        # Clean technique percentage
        clean_reps = sum(1 for r in self.rep_summaries if not r.had_compensation)
        clean_pct = (clean_reps / total_reps) * 100 if total_reps > 0 else 0.0
        
        return {
            'total_reps': total_reps,
            'total_tut_s': total_tut,
            'avg_rom_deg': avg_rom,
            'velocity_loss_pct': velocity_loss,
            'clean_technique_pct': clean_pct,
            'avg_eccentric_time': sum(r.eccentric_time_s for r in self.rep_summaries) / total_reps,
            'avg_concentric_time': sum(r.concentric_time_s for r in self.rep_summaries) / total_reps
        }
