"""
Unit tests for smoothing filters.
Run with: python tests/test_smoothing.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.smoothing import EMAFilter


def test_ema_filter_initialization():
    """Test EMA filter initializes correctly."""
    filter = EMAFilter(alpha=0.5)
    assert filter.alpha == 0.5
    print("✅ EMA initialization test passed")


def test_ema_filter_first_frame():
    """Test that first frame returns raw value."""
    filter = EMAFilter(alpha=0.5)
    raw = (100, 200)
    smoothed = filter.smooth("test_landmark", raw)
    assert smoothed == raw, f"Expected {raw}, got {smoothed}"
    print("✅ EMA first frame test passed")


def test_ema_filter_smoothing():
    """Test that EMA actually smooths values."""
    filter = EMAFilter(alpha=0.3)
    
    # First frame
    filter.smooth("test", (100, 100))
    
    # Second frame with different value
    smoothed = filter.smooth("test", (200, 200))
    
    # With alpha=0.3, smoothed = 0.3*200 + 0.7*100 = 60 + 70 = 130
    expected_x = 0.3 * 200 + 0.7 * 100
    assert abs(smoothed[0] - expected_x) < 0.01, f"Expected {expected_x}, got {smoothed[0]}"
    print("✅ EMA smoothing test passed")


def test_ema_filter_reset():
    """Test filter reset clears state."""
    filter = EMAFilter(alpha=0.5)
    filter.smooth("test", (100, 100))
    filter.reset()
    
    # After reset, next frame should be treated as first frame
    raw = (200, 200)
    smoothed = filter.smooth("test", raw)
    assert smoothed == raw, "Reset should clear smoothing history"
    print("✅ EMA reset test passed")


if __name__ == "__main__":
    print("Running smoothing filter tests...")
    test_ema_filter_initialization()
    test_ema_filter_first_frame()
    test_ema_filter_smoothing()
    test_ema_filter_reset()
    print("\n✅ All smoothing tests passed!")
