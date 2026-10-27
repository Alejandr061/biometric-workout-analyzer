"""
Signal smoothing filters for landmark coordinates.
Reduces camera jitter and pose estimation noise in real-time.
"""
from typing import Dict, Optional, Tuple
import numpy as np


class EMAFilter:
    """
    Exponential Moving Average (EMA) filter for 2D coordinate smoothing.
    
    Formula:
        smoothed[t] = alpha * raw[t] + (1 - alpha) * smoothed[t-1]
    
    Attributes:
        alpha: Smoothing factor [0, 1]
               - Higher values (e.g., 0.8): Less smoothing, faster response
               - Lower values (e.g., 0.2): More smoothing, slower response
    """
    
    def __init__(self, alpha: float = 0.5):
        """
        Initialize EMA filter.
        
        Args:
            alpha: Smoothing factor between 0 and 1
                   Recommended: 0.3-0.7 for real-time pose tracking
        """
        if not 0 <= alpha <= 1:
            raise ValueError(f"Alpha must be in [0, 1], got {alpha}")
        
        self.alpha = alpha
        self._smoothed_values: Dict[str, Tuple[float, float]] = {}
    
    def smooth(
        self,
        landmark_name: str,
        raw_coords: Tuple[float, float]
    ) -> Tuple[float, float]:
        """
        Apply EMA smoothing to a landmark coordinate.
        
        Args:
            landmark_name: Unique identifier for the landmark (e.g., "left_elbow")
            raw_coords: Raw (x, y) coordinates from pose estimator
            
        Returns:
            Smoothed (x, y) coordinates
        """
        if landmark_name not in self._smoothed_values:
            # First frame: initialize with raw value
            self._smoothed_values[landmark_name] = raw_coords
            return raw_coords
        
        prev_x, prev_y = self._smoothed_values[landmark_name]
        raw_x, raw_y = raw_coords
        
        # Apply EMA formula
        smoothed_x = self.alpha * raw_x + (1 - self.alpha) * prev_x
        smoothed_y = self.alpha * raw_y + (1 - self.alpha) * prev_y
        
        smoothed = (smoothed_x, smoothed_y)
        self._smoothed_values[landmark_name] = smoothed
        
        return smoothed
    
    def reset(self):
        """Clear all stored smoothed values (e.g., when video restarts)."""
        self._smoothed_values.clear()
    
    def reset_landmark(self, landmark_name: str):
        """Reset a specific landmark (e.g., when confidence drops)."""
        if landmark_name in self._smoothed_values:
            del self._smoothed_values[landmark_name]


class OneEuroFilter:
    """
    One Euro Filter: Adaptive smoothing that reduces lag during fast motion.
    
    Reference: Casiez et al., "1€ Filter: A Simple Speed-based Low-pass Filter"
    
    The filter adapts its smoothing based on movement speed:
    - Slow movements: Strong smoothing (reduces jitter)
    - Fast movements: Less smoothing (reduces lag)
    """
    
    def __init__(
        self,
        min_cutoff: float = 1.0,
        beta: float = 0.007,
        d_cutoff: float = 1.0
    ):
        """
        Initialize One Euro Filter.
        
        Args:
            min_cutoff: Minimum cutoff frequency (Hz) - controls minimum smoothing
            beta: Cutoff slope - controls adaptation to velocity
            d_cutoff: Cutoff frequency for derivative
        """
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        
        self._x_prev: Dict[str, float] = {}
        self._dx_prev: Dict[str, float] = {}
        self._y_prev: Dict[str, float] = {}
        self._dy_prev: Dict[str, float] = {}
        self._t_prev: Dict[str, float] = {}
    
    def _smooth_value(
        self,
        value: float,
        prev_value: float,
        prev_derivative: float,
        dt: float
    ) -> Tuple[float, float]:
        """Apply one-euro smoothing to a single scalar value."""
        # Estimate derivative
        derivative = (value - prev_value) / dt if dt > 0 else 0.0
        
        # Smooth derivative
        alpha_d = self._alpha(dt, self.d_cutoff)
        derivative_smooth = alpha_d * derivative + (1 - alpha_d) * prev_derivative
        
        # Adaptive cutoff frequency
        cutoff = self.min_cutoff + self.beta * abs(derivative_smooth)
        
        # Smooth value
        alpha = self._alpha(dt, cutoff)
        value_smooth = alpha * value + (1 - alpha) * prev_value
        
        return value_smooth, derivative_smooth
    
    @staticmethod
    def _alpha(dt: float, cutoff: float) -> float:
        """Calculate smoothing factor from cutoff frequency."""
        tau = 1.0 / (2 * np.pi * cutoff)
        return 1.0 / (1.0 + tau / dt) if dt > 0 else 1.0
    
    def smooth(
        self,
        landmark_name: str,
        raw_coords: Tuple[float, float],
        timestamp: float
    ) -> Tuple[float, float]:
        """
        Apply One Euro smoothing to landmark coordinates.
        
        Args:
            landmark_name: Unique identifier for the landmark
            raw_coords: Raw (x, y) coordinates
            timestamp: Current timestamp in seconds
            
        Returns:
            Smoothed (x, y) coordinates
        """
        if landmark_name not in self._x_prev:
            # Initialize
            self._x_prev[landmark_name] = raw_coords[0]
            self._y_prev[landmark_name] = raw_coords[1]
            self._dx_prev[landmark_name] = 0.0
            self._dy_prev[landmark_name] = 0.0
            self._t_prev[landmark_name] = timestamp
            return raw_coords
        
        # Calculate time delta
        dt = timestamp - self._t_prev[landmark_name]
        if dt <= 0:
            dt = 0.001  # Minimum 1ms to avoid division by zero
        
        # Smooth X coordinate
        x_smooth, dx_smooth = self._smooth_value(
            raw_coords[0],
            self._x_prev[landmark_name],
            self._dx_prev[landmark_name],
            dt
        )
        
        # Smooth Y coordinate
        y_smooth, dy_smooth = self._smooth_value(
            raw_coords[1],
            self._y_prev[landmark_name],
            self._dy_prev[landmark_name],
            dt
        )
        
        # Update state
        self._x_prev[landmark_name] = x_smooth
        self._y_prev[landmark_name] = y_smooth
        self._dx_prev[landmark_name] = dx_smooth
        self._dy_prev[landmark_name] = dy_smooth
        self._t_prev[landmark_name] = timestamp
        
        return (x_smooth, y_smooth)
    
    def reset(self):
        """Clear all stored filter state."""
        self._x_prev.clear()
        self._dx_prev.clear()
        self._y_prev.clear()
        self._dy_prev.clear()
        self._t_prev.clear()
