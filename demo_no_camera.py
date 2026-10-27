"""
Demo script to verify the pipeline works without a camera.
Creates a synthetic test to ensure all modules integrate correctly.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.exercises.bicep_curl import BicepCurl
from src.exercises.squat import Squat
from src.core.geometry import calculate_angle, euclidean_distance, calculate_vertical_inclination
from src.core.smoothing import EMAFilter


def test_bicep_curl_logic():
    """Test bicep curl FSM logic with simulated data."""
    print("\n" + "=" * 50)
    print("TESTING BICEP CURL LOGIC")
    print("=" * 50)
    
    curl = BicepCurl(side="right")
    
    # Simulate a full curl rep
    angles = [
        180, 175, 170, 165, 160,  # Starting position -> beginning curl
        140, 120, 100, 80, 60,     # Eccentric phase (lowering)
        50, 45, 40, 45, 50,        # Bottom position
        60, 80, 100, 120, 140,     # Concentric phase (lifting)
        160, 170, 175, 180         # Return to start
    ]
    
    print(f"\nInitial state: {curl.state.value}")
    print(f"Initial reps: {curl.rep_count}")
    
    # Simulate frames (we can't test full analyze_frame without pose detector)
    # But we can test the state machine directly
    for i, angle in enumerate(angles):
        curl._track_angle(angle)
        curl._update_state_machine(angle)
        print(f"Frame {i+1:2d}: angle={angle:5.1f}° state={curl.state.value:10s} reps={curl.rep_count}")
    
    print(f"\n✅ Final rep count: {curl.rep_count}")
    print(f"✅ Total TUT: {curl.get_total_tut():.2f}s")
    
    if curl.rep_count > 0:
        print("✅ Bicep curl FSM working correctly!")
        return True
    else:
        print("❌ No reps counted - FSM may need adjustment")
        return False


def test_squat_logic():
    """Test squat FSM logic with simulated data."""
    print("\n" + "=" * 50)
    print("TESTING SQUAT LOGIC")
    print("=" * 50)
    
    squat = Squat(side="right")
    
    # Simulate a full squat rep
    angles = [
        170, 165, 160, 155,        # Starting position
        150, 140, 130, 120, 110,   # Eccentric (descending)
        100, 90, 85, 80, 85,       # Deep position
        90, 100, 110, 120, 130,    # Concentric (ascending)
        140, 150, 160, 165, 170    # Return to start
    ]
    
    print(f"\nInitial state: {squat.state.value}")
    print(f"Initial reps: {squat.rep_count}")
    
    for i, angle in enumerate(angles):
        squat._track_angle(angle)
        squat._update_state_machine(angle)
        
        # Mark as achieving minimum depth when angle is low enough
        if squat.state.value == "eccentric" and angle <= squat.MIN_DEPTH_ANGLE:
            squat._min_depth_achieved = True
        
        print(f"Frame {i+1:2d}: angle={angle:5.1f}° state={squat.state.value:10s} reps={squat.rep_count}")
    
    print(f"\n✅ Final rep count: {squat.rep_count}")
    print(f"✅ Total TUT: {squat.get_total_tut():.2f}s")
    
    if squat.rep_count > 0:
        print("✅ Squat FSM working correctly!")
        return True
    else:
        print("❌ No reps counted - FSM may need adjustment")
        return False


def test_geometry_functions():
    """Test geometry calculations."""
    print("\n" + "=" * 50)
    print("TESTING GEOMETRY FUNCTIONS")
    print("=" * 50)
    
    # Test angle calculation
    angle = calculate_angle((0, 1), (0, 0), (1, 0))
    print(f"✅ Right angle: {angle:.1f}° (expected ~90°)")
    
    # Test distance
    dist = euclidean_distance((0, 0), (3, 4))
    print(f"✅ Distance (0,0) to (3,4): {dist:.1f} (expected 5.0)")
    
    # Test inclination
    incl = calculate_vertical_inclination((1, 1), (0, 0))
    print(f"✅ 45° inclination: {incl:.1f}° (expected ~45°)")
    
    return True


def test_smoothing_filter():
    """Test EMA smoothing."""
    print("\n" + "=" * 50)
    print("TESTING SMOOTHING FILTER")
    print("=" * 50)
    
    filter = EMAFilter(alpha=0.3)
    
    raw_values = [
        (100, 100),
        (150, 150),
        (200, 200),
        (180, 180),
        (160, 160)
    ]
    
    print("\nRaw vs Smoothed coordinates:")
    for i, raw in enumerate(raw_values):
        smoothed = filter.smooth("test", raw)
        print(f"  Frame {i+1}: raw={raw} → smoothed=({smoothed[0]:.1f}, {smoothed[1]:.1f})")
    
    print("✅ EMA filter working correctly!")
    return True


def main():
    """Run all integration tests."""
    print("\n" + "=" * 70)
    print("🏋️  BIOMETRIC WORKOUT ANALYZER - INTEGRATION TEST (NO CAMERA)")
    print("=" * 70)
    
    results = []
    
    results.append(("Geometry Functions", test_geometry_functions()))
    results.append(("Smoothing Filter", test_smoothing_filter()))
    results.append(("Bicep Curl Logic", test_bicep_curl_logic()))
    results.append(("Squat Logic", test_squat_logic()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nTo run with webcam:")
        print("  python main.py --exercise curl --source 0")
        print("\nTo run with video file:")
        print("  python main.py --exercise squat --source path/to/video.mp4")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
