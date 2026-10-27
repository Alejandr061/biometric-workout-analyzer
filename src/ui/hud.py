"""
Modern HUD overlay for real-time exercise feedback.
Displays: FPS, reps, state, angle gauge, posture alerts.
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional


class HUD:
    """
    Head-Up Display renderer for exercise analysis.
    
    Features:
    - Semi-transparent panel overlay
    - Real-time angle gauge with progress bar
    - Rep counter and state indicator
    - Posture alert banner
    - FPS counter
    """
    
    # Color scheme (BGR format)
    COLOR_BG = (40, 40, 40)  # Dark gray background
    COLOR_PRIMARY = (0, 255, 0)  # Green
    COLOR_SECONDARY = (255, 165, 0)  # Orange
    COLOR_DANGER = (0, 0, 255)  # Red
    COLOR_TEXT = (255, 255, 255)  # White
    COLOR_ACCENT = (255, 255, 0)  # Cyan
    
    def __init__(self, width: int = 640, height: int = 480):
        """
        Initialize HUD renderer.
        
        Args:
            width: Frame width in pixels
            height: Frame height in pixels
        """
        self.width = width
        self.height = height
        
        # Panel dimensions
        self.panel_height = 180
        self.panel_margin = 20
        self.alert_banner_height = 60
    
    def render(
        self,
        frame: np.ndarray,
        fps: float,
        exercise_name: str,
        state: str,
        reps: int,
        angle: Optional[float],
        angle_range: Tuple[float, float],
        alerts: List[str],
        tempo: str = "0-0-0",
        tut: float = 0.0
    ) -> np.ndarray:
        """
        Render complete HUD overlay on frame.
        
        Args:
            frame: Input video frame
            fps: Current frames per second
            exercise_name: Name of exercise being performed
            state: Current FSM state (idle/eccentric/bottom/concentric)
            reps: Number of completed repetitions
            angle: Current primary angle (degrees)
            angle_range: (min_angle, max_angle) for progress bar
            alerts: List of active posture alert messages
            tempo: Tempo string (e.g., "3.0-0-2.5")
            tut: Total time under tension (seconds)
            
        Returns:
            Frame with HUD overlay
        """
        overlay = frame.copy()
        
        # Draw main info panel
        self._draw_info_panel(
            overlay, fps, exercise_name, state, reps, tempo, tut
        )
        
        # Draw angle gauge
        if angle is not None:
            self._draw_angle_gauge(overlay, angle, angle_range, state)
        
        # Draw alert banner
        if alerts:
            self._draw_alert_banner(overlay, alerts)
        
        # Blend overlay with original frame
        alpha = 0.85
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
    
    def _draw_info_panel(
        self,
        frame: np.ndarray,
        fps: float,
        exercise_name: str,
        state: str,
        reps: int,
        tempo: str,
        tut: float
    ):
        """Draw semi-transparent info panel at top-left."""
        x = self.panel_margin
        y = self.panel_margin
        panel_width = 300
        
        # Background rectangle with transparency
        cv2.rectangle(
            frame,
            (x, y),
            (x + panel_width, y + self.panel_height),
            self.COLOR_BG,
            -1
        )
        cv2.rectangle(
            frame,
            (x, y),
            (x + panel_width, y + self.panel_height),
            self.COLOR_PRIMARY,
            2
        )
        
        # Text rendering
        font = cv2.FONT_HERSHEY_DUPLEX
        text_x = x + 15
        line_height = 30
        current_y = y + 35
        
        # Exercise name
        cv2.putText(
            frame,
            exercise_name,
            (text_x, current_y),
            font,
            0.7,
            self.COLOR_ACCENT,
            2
        )
        current_y += line_height
        
        # Reps counter (large and prominent)
        cv2.putText(
            frame,
            f"REPS: {reps}",
            (text_x, current_y),
            font,
            0.8,
            self.COLOR_PRIMARY,
            2
        )
        current_y += line_height
        
        # State indicator with color coding
        state_color = self._get_state_color(state)
        cv2.putText(
            frame,
            f"State: {state.upper()}",
            (text_x, current_y),
            font,
            0.6,
            state_color,
            1
        )
        current_y += line_height
        
        # Tempo
        cv2.putText(
            frame,
            f"Tempo: {tempo}",
            (text_x, current_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.COLOR_TEXT,
            1
        )
        current_y += line_height
        
        # Total TUT
        cv2.putText(
            frame,
            f"TUT: {tut:.1f}s",
            (text_x, current_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.COLOR_TEXT,
            1
        )
        
        # FPS counter (top-right corner)
        fps_text = f"FPS: {fps:.1f}"
        fps_size = cv2.getTextSize(fps_text, font, 0.6, 1)[0]
        fps_x = self.width - fps_size[0] - 20
        cv2.putText(
            frame,
            fps_text,
            (fps_x, 40),
            font,
            0.6,
            self.COLOR_TEXT,
            1
        )
    
    def _draw_angle_gauge(
        self,
        frame: np.ndarray,
        angle: float,
        angle_range: Tuple[float, float],
        state: str
    ):
        """Draw angle progress bar with numeric display."""
        x = self.panel_margin
        y = self.panel_margin + self.panel_height + 20
        gauge_width = 300
        gauge_height = 40
        
        min_angle, max_angle = angle_range
        
        # Background
        cv2.rectangle(
            frame,
            (x, y),
            (x + gauge_width, y + gauge_height),
            self.COLOR_BG,
            -1
        )
        cv2.rectangle(
            frame,
            (x, y),
            (x + gauge_width, y + gauge_height),
            self.COLOR_TEXT,
            2
        )
        
        # Progress bar fill
        rom_range = max_angle - min_angle if max_angle > min_angle else 180
        if rom_range > 0:
            progress = (angle - min_angle) / rom_range
            progress = max(0, min(1, progress))
            
            fill_width = int(gauge_width * progress)
            bar_color = self._get_state_color(state)
            
            cv2.rectangle(
                frame,
                (x + 2, y + 2),
                (x + fill_width - 2, y + gauge_height - 2),
                bar_color,
                -1
            )
        
        # Angle text (centered)
        angle_text = f"{angle:.1f}°"
        text_size = cv2.getTextSize(
            angle_text, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2
        )[0]
        text_x = x + (gauge_width - text_size[0]) // 2
        text_y = y + (gauge_height + text_size[1]) // 2
        
        # Text with black outline for visibility
        cv2.putText(
            frame,
            angle_text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_DUPLEX,
            0.8,
            (0, 0, 0),
            4
        )
        cv2.putText(
            frame,
            angle_text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_DUPLEX,
            0.8,
            self.COLOR_TEXT,
            2
        )
    
    def _draw_alert_banner(self, frame: np.ndarray, alerts: List[str]):
        """Draw prominent alert banner for form violations."""
        banner_y = self.height - self.alert_banner_height - 20
        
        # Red background banner
        cv2.rectangle(
            frame,
            (0, banner_y),
            (self.width, banner_y + self.alert_banner_height),
            self.COLOR_DANGER,
            -1
        )
        
        # Alert icon (warning triangle)
        icon_x = 20
        icon_y = banner_y + self.alert_banner_height // 2
        triangle_points = np.array([
            [icon_x + 15, icon_y - 20],
            [icon_x, icon_y + 10],
            [icon_x + 30, icon_y + 10]
        ])
        cv2.fillPoly(frame, [triangle_points], (0, 255, 255))
        cv2.putText(
            frame,
            "!",
            (icon_x + 10, icon_y + 5),
            cv2.FONT_HERSHEY_DUPLEX,
            0.8,
            (0, 0, 0),
            2
        )
        
        # Alert text
        text_x = icon_x + 50
        text_y = banner_y + 25
        
        for i, alert in enumerate(alerts[:2]):  # Show max 2 alerts
            cv2.putText(
                frame,
                alert,
                (text_x, text_y + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                self.COLOR_TEXT,
                2
            )
    
    def _get_state_color(self, state: str) -> Tuple[int, int, int]:
        """Get color for exercise state."""
        state_colors = {
            'idle': self.COLOR_TEXT,
            'eccentric': self.COLOR_SECONDARY,  # Orange for lowering
            'bottom': self.COLOR_ACCENT,  # Cyan for transition
            'concentric': self.COLOR_PRIMARY,  # Green for lifting
        }
        return state_colors.get(state.lower(), self.COLOR_TEXT)
    
    def draw_skeleton_overlay(
        self,
        frame: np.ndarray,
        pose_detector,
        color: Tuple[int, int, int] = (0, 255, 0)
    ) -> np.ndarray:
        """
        Convenience method to draw skeleton on frame.
        
        Args:
            frame: Input frame
            pose_detector: PoseDetector instance
            color: Skeleton color (BGR)
            
        Returns:
            Frame with skeleton overlay
        """
        return pose_detector.draw_skeleton(frame, color, thickness=2)
