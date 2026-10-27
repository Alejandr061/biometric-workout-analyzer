"""
Unit tests for geometry module.
Run with: python -m pytest tests/test_geometry.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.geometry import (
    calculate_angle,
    euclidean_distance,
    calculate_vertical_inclination
)


def test_calculate_angle_90_degrees():
    """Test 90-degree angle calculation."""
    # Right angle: shoulder at (1,1), elbow at (1,0), wrist at (0,0)
    angle = calculate_angle((1, 1), (1, 0), (0, 0))
    assert abs(angle - 90.0) < 1.0, f"Expected ~90°, got {angle}°"


def test_calculate_angle_180_degrees():
    """Test straight line (180 degrees)."""
    # Straight arm: shoulder at (2,0), elbow at (1,0), wrist at (0,0)
    angle = calculate_angle((2, 0), (1, 0), (0, 0))
    assert abs(angle - 180.0) < 1.0, f"Expected ~180°, got {angle}°"


def test_calculate_angle_45_degrees():
    """Test 45-degree angle."""
    angle = calculate_angle((0, 1), (0, 0), (1, 0))
    assert abs(angle - 90.0) < 1.0, f"Expected ~90°, got {angle}°"


def test_euclidean_distance():
    """Test distance calculation."""
    # Distance between (0,0) and (3,4) should be 5
    dist = euclidean_distance((0, 0), (3, 4))
    assert abs(dist - 5.0) < 0.01, f"Expected 5.0, got {dist}"


def test_vertical_inclination_perfect_vertical():
    """Test vertical line (0 degrees)."""
    inclination = calculate_vertical_inclination((0, 1), (0, 0))
    assert abs(inclination) < 1.0, f"Expected ~0°, got {inclination}°"


def test_vertical_inclination_45_degrees():
    """Test 45-degree inclination."""
    inclination = calculate_vertical_inclination((1, 1), (0, 0))
    assert abs(inclination - 45.0) < 1.0, f"Expected ~45°, got {inclination}°"


if __name__ == "__main__":
    print("Running geometry tests...")
    test_calculate_angle_90_degrees()
    test_calculate_angle_180_degrees()
    test_calculate_angle_45_degrees()
    test_euclidean_distance()
    test_vertical_inclination_perfect_vertical()
    test_vertical_inclination_45_degrees()
    print("✅ All geometry tests passed!")
