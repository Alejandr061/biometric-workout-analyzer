"""
Vector geometry utilities for biomechanical analysis.
All functions are vectorized with NumPy for real-time performance.
"""
import numpy as np
from typing import Tuple, Optional


def calculate_angle(
    point_a: Tuple[float, float],
    point_b: Tuple[float, float],
    point_c: Tuple[float, float]
) -> float:
    """
    Calculate the angle (in degrees) formed by three points: A-B-C.
    Point B is the vertex of the angle.
    
    Formula:
        angle = arccos((BA · BC) / (|BA| * |BC|))
    
    Args:
        point_a: First point (x, y) coordinates
        point_b: Vertex point (x, y) coordinates
        point_c: Third point (x, y) coordinates
        
    Returns:
        Angle in degrees [0, 180]
        
    Note:
        Returns 180.0 if vectors are degenerate (zero length) to avoid division by zero.
    """
    a = np.array(point_a)
    b = np.array(point_b)
    c = np.array(point_c)
    
    # Vectors from vertex B to points A and C
    ba = a - b
    bc = c - b
    
    # Calculate magnitudes with epsilon for numerical stability
    magnitude_ba = np.linalg.norm(ba)
    magnitude_bc = np.linalg.norm(bc)
    
    # Protect against division by zero
    if magnitude_ba < 1e-6 or magnitude_bc < 1e-6:
        return 180.0
    
    # Dot product and angle calculation
    cos_angle = np.dot(ba, bc) / (magnitude_ba * magnitude_bc)
    
    # Clamp to [-1, 1] to handle floating point errors
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    
    angle_rad = np.arccos(cos_angle)
    angle_deg = np.degrees(angle_rad)
    
    return float(angle_deg)


def euclidean_distance(
    point_a: Tuple[float, float],
    point_b: Tuple[float, float]
) -> float:
    """
    Calculate Euclidean distance between two 2D points.
    
    Formula:
        distance = sqrt((x2 - x1)² + (y2 - y1)²)
    
    Args:
        point_a: First point (x, y)
        point_b: Second point (x, y)
        
    Returns:
        Distance in pixels
    """
    a = np.array(point_a)
    b = np.array(point_b)
    return float(np.linalg.norm(b - a))


def calculate_vertical_inclination(
    point_top: Tuple[float, float],
    point_bottom: Tuple[float, float]
) -> float:
    """
    Calculate inclination angle (in degrees) of a segment relative to vertical axis.
    Used to detect torso lean, spine alignment, etc.
    
    Formula:
        inclination = arctan(|x2 - x1| / |y2 - y1|)
    
    Args:
        point_top: Upper point (x, y) - e.g., shoulder
        point_bottom: Lower point (x, y) - e.g., hip
        
    Returns:
        Inclination angle in degrees [0, 90]
        0° = perfectly vertical
        90° = perfectly horizontal
        
    Note:
        Returns 0.0 if segment is degenerate (points coincide).
    """
    delta_x = abs(point_top[0] - point_bottom[0])
    delta_y = abs(point_top[1] - point_bottom[1])
    
    # Protect against vertical segments
    if delta_y < 1e-6:
        return 90.0 if delta_x > 1e-6 else 0.0
    
    # Calculate angle from vertical
    angle_rad = np.arctan(delta_x / delta_y)
    angle_deg = np.degrees(angle_rad)
    
    return float(angle_deg)


def normalize_coordinates(
    point: Tuple[float, float],
    frame_width: int,
    frame_height: int
) -> Tuple[float, float]:
    """
    Normalize pixel coordinates to [0, 1] range.
    
    Args:
        point: Pixel coordinates (x, y)
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
        
    Returns:
        Normalized coordinates (x_norm, y_norm)
    """
    x_norm = point[0] / frame_width if frame_width > 0 else 0.0
    y_norm = point[1] / frame_height if frame_height > 0 else 0.0
    return (x_norm, y_norm)


def denormalize_coordinates(
    point: Tuple[float, float],
    frame_width: int,
    frame_height: int
) -> Tuple[int, int]:
    """
    Convert normalized coordinates [0, 1] to pixel coordinates.
    
    Args:
        point: Normalized coordinates (x_norm, y_norm)
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
        
    Returns:
        Pixel coordinates (x, y) as integers
    """
    x = int(point[0] * frame_width)
    y = int(point[1] * frame_height)
    return (x, y)
