"""
Setup verification script.
Checks that all modules are properly installed and accessible.
"""
import sys
from pathlib import Path

def check_imports():
    """Verify all required packages can be imported."""
    print("🔍 Checking package imports...")
    
    packages = {
        'opencv-python': 'cv2',
        'mediapipe': 'mediapipe',
        'numpy': 'numpy',
        'pydantic': 'pydantic'
    }
    
    all_ok = True
    
    for package_name, import_name in packages.items():
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✅ {package_name}: {version}")
        except ImportError as e:
            print(f"  ❌ {package_name}: NOT FOUND")
            all_ok = False
    
    return all_ok


def check_project_structure():
    """Verify project folder structure."""
    print("\n🔍 Checking project structure...")
    
    project_root = Path(__file__).parent
    
    required_paths = [
        'src',
        'src/core',
        'src/exercises',
        'src/ui',
        'src/telemetry',
        'tests',
        'assets',
        'src/core/geometry.py',
        'src/core/smoothing.py',
        'src/core/pose_detector.py',
        'src/exercises/base_exercise.py',
        'src/exercises/bicep_curl.py',
        'src/exercises/squat.py',
        'src/ui/hud.py',
        'main.py',
        'requirements.txt',
        'README.md',
        '.gitignore'
    ]
    
    all_ok = True
    
    for path_str in required_paths:
        path = project_root / path_str
        if path.exists():
            print(f"  ✅ {path_str}")
        else:
            print(f"  ❌ {path_str} - MISSING")
            all_ok = False
    
    return all_ok


def check_module_imports():
    """Verify custom modules can be imported."""
    print("\n🔍 Checking custom module imports...")
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    modules = [
        'src.core.geometry',
        'src.core.smoothing',
        'src.core.pose_detector',
        'src.exercises.base_exercise',
        'src.exercises.bicep_curl',
        'src.exercises.squat',
        'src.ui.hud'
    ]
    
    all_ok = True
    
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name}: {e}")
            all_ok = False
    
    return all_ok


def check_camera():
    """Check if camera is available (optional)."""
    print("\n🔍 Checking camera availability (optional)...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                print("  ✅ Camera detected and working")
                return True
            else:
                print("  ⚠️  Camera detected but cannot read frames")
                return False
        else:
            print("  ⚠️  No camera detected (you can still use video files)")
            return False
    except Exception as e:
        print(f"  ⚠️  Camera check failed: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS")
    print("=" * 70)
    print("""
1. Test with webcam (if available):
   python main.py --exercise curl --source 0

2. Test with video file:
   - Place a workout video in the assets/ folder
   - Run: python main.py --exercise squat --source assets/your_video.mp4

3. Run demo without camera:
   python demo_no_camera.py

4. Run unit tests:
   python tests/test_geometry.py
   python tests/test_smoothing.py

5. Read the full documentation:
   Open README.md for detailed usage instructions

6. Customize for your needs:
   - Add new exercises in src/exercises/
   - Adjust thresholds in exercise files
   - Modify HUD appearance in src/ui/hud.py
""")


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("🏋️  BIOMETRIC WORKOUT ANALYZER - SETUP VERIFICATION")
    print("=" * 70)
    
    results = []
    
    results.append(("Package Imports", check_imports()))
    results.append(("Project Structure", check_project_structure()))
    results.append(("Module Imports", check_module_imports()))
    
    # Camera check is optional
    camera_ok = check_camera()
    
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    camera_status = "✅ Available" if camera_ok else "⚠️  Not available (optional)"
    print(f"{camera_status} - Camera")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 Setup verification complete! Everything looks good.")
        print_next_steps()
        return 0
    else:
        print("\n❌ Setup verification failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("  - Ensure all dependencies are installed: pip install -r requirements.txt")
        print("  - Check that all files were created correctly")
        return 1


if __name__ == "__main__":
    sys.exit(main())
