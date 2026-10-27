"""
Biometric Workout Analyzer - Main Entry Point

Real-time biomechanical exercise analysis using computer vision.
Analyzes form, counts reps, and provides posture feedback.

Usage:
    python main.py --exercise curl --source 0
    python main.py --exercise squat --source path/to/video.mp4
"""
import cv2
import argparse
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.pose_detector import PoseDetector
from src.exercises.bicep_curl import BicepCurl
from src.exercises.squat import Squat
from src.ui.hud import HUD
from src.telemetry.session_logger import SessionLogger
from src.telemetry.dashboard import generate_post_workout_dashboard


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Biometric Workout Analyzer - Real-time exercise form analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --exercise curl --source 0
  %(prog)s --exercise squat --source workout.mp4
  %(prog)s --exercise curl --side left --source 0
        """
    )
    
    parser.add_argument(
        '--exercise',
        type=str,
        required=True,
        choices=['curl', 'squat'],
        help='Exercise to analyze (curl=bicep curl, squat=squat)'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        default='0',
        help='Video source: 0 for webcam, or path to video file'
    )
    
    parser.add_argument(
        '--side',
        type=str,
        default='right',
        choices=['left', 'right'],
        help='Side to analyze (for unilateral exercises)'
    )
    
    parser.add_argument(
        '--no-skeleton',
        action='store_true',
        help='Disable skeleton overlay'
    )
    
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.6,
        help='Minimum landmark visibility threshold (0.0-1.0)'
    )
    
    return parser.parse_args()


def initialize_video_source(source: str) -> cv2.VideoCapture:
    """
    Initialize video capture from webcam or file.
    
    Args:
        source: '0' for webcam or path to video file
        
    Returns:
        OpenCV VideoCapture object
    """
    # Try to parse as integer (webcam index)
    try:
        source_int = int(source)
        cap = cv2.VideoCapture(source_int)
    except ValueError:
        # Assume it's a file path
        if not Path(source).exists():
            print(f"❌ Error: Video file not found: {source}")
            sys.exit(1)
        cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"❌ Error: Could not open video source: {source}")
        sys.exit(1)
    
    # Set optimal resolution for webcam
    if isinstance(source_int, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    return cap


def create_exercise_analyzer(exercise_type: str, side: str):
    """
    Create appropriate exercise analyzer.
    
    Args:
        exercise_type: 'curl' or 'squat'
        side: 'left' or 'right'
        
    Returns:
        Exercise analyzer instance
    """
    if exercise_type == 'curl':
        return BicepCurl(side=side)
    elif exercise_type == 'squat':
        return Squat(side=side)
    else:
        raise ValueError(f"Unknown exercise type: {exercise_type}")


def main():
    """Main application loop."""
    # Parse arguments
    args = parse_arguments()
    
    print("🏋️  Biometric Workout Analyzer")
    print("=" * 50)
    print(f"Exercise: {args.exercise.upper()}")
    print(f"Side: {args.side.capitalize()}")
    print(f"Source: {args.source}")
    print(f"Confidence threshold: {args.confidence}")
    print("=" * 50)
    print("\nInitializing...")
    
    # Initialize components
    cap = initialize_video_source(args.source)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    pose_detector = PoseDetector(
        visibility_threshold=args.confidence,
        enable_smoothing=True,
        smoothing_alpha=0.5
    )
    
    exercise = create_exercise_analyzer(args.exercise, args.side)
    hud = HUD(width=frame_width, height=frame_height)
    
    # Initialize telemetry logger
    logger = SessionLogger(exercise_name=exercise.name)
    exercise.set_logger(logger)
    
    # FPS calculation
    fps = 0
    frame_count = 0
    fps_update_interval = 30
    fps_start_time = time.time()
    
    print("✅ Ready! Starting analysis...")
    print("\nControls:")
    print("  'q' or ESC - Quit")
    print("  'r' - Reset rep counter")
    print("  's' - Toggle skeleton overlay")
    print()
    
    show_skeleton = not args.no_skeleton
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("📹 End of video or camera disconnected")
                break
            
            # Process pose
            pose_detected = pose_detector.process_frame(frame)
            
            if pose_detected:
                # Analyze exercise
                result = exercise.analyze_frame(pose_detector)
                
                # Log telemetry data
                angle = result.get('angle') or result.get('knee_angle')
                logger.log_frame(
                    angle=angle,
                    fsm_state=result['state'],
                    alerts=result['alerts']
                )
                
                # Draw skeleton overlay
                if show_skeleton:
                    frame = pose_detector.draw_skeleton(
                        frame,
                        color=(0, 255, 0),
                        thickness=2
                    )
                
                # Render HUD
                angle = result.get('angle') or result.get('knee_angle')
                angle_range = (
                    exercise._min_angle_current_rep if exercise._min_angle_current_rep < float('inf') else 0,
                    exercise._max_angle_current_rep
                )
                
                frame = hud.render(
                    frame=frame,
                    fps=fps,
                    exercise_name=exercise.name,
                    state=result['state'],
                    reps=result['reps'],
                    angle=angle,
                    angle_range=angle_range,
                    alerts=result['alerts'],
                    tempo=result['tempo'],
                    tut=result['tut']
                )
            else:
                # No pose detected - show message
                cv2.putText(
                    frame,
                    "NO POSE DETECTED",
                    (frame_width // 2 - 150, frame_height // 2),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1.0,
                    (0, 0, 255),
                    2
                )
                cv2.putText(
                    frame,
                    "Position yourself in frame",
                    (frame_width // 2 - 180, frame_height // 2 + 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    1
                )
            
            # Calculate FPS
            frame_count += 1
            if frame_count % fps_update_interval == 0:
                elapsed = time.time() - fps_start_time
                fps = fps_update_interval / elapsed if elapsed > 0 else 0
                fps_start_time = time.time()
            
            # Display frame
            cv2.imshow('Biometric Workout Analyzer', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # 'q' or ESC
                print("\n👋 Quitting...")
                break
            elif key == ord('r'):
                print("\n🔄 Resetting rep counter...")
                exercise.reset()
            elif key == ord('s'):
                show_skeleton = not show_skeleton
                print(f"\n🦴 Skeleton overlay: {'ON' if show_skeleton else 'OFF'}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Print session summary
        print("\n" + "=" * 50)
        print("📊 SESSION SUMMARY")
        print("=" * 50)
        print(f"Exercise: {exercise.name}")
        print(f"Total reps: {exercise.rep_count}")
        print(f"Total TUT: {exercise.get_total_tut():.1f}s")
        print(f"Average tempo: {exercise.get_tempo()}")
        print(f"Average ROM: {exercise.get_average_rom():.1f}°")
        
        if exercise.completed_reps:
            print("\nRep breakdown:")
            for rep in exercise.completed_reps:
                print(f"  Rep {rep.rep_number}: "
                      f"ROM={rep.rom_degrees:.1f}° "
                      f"TUT={rep.time_under_tension:.1f}s "
                      f"Tempo={rep.eccentric_time:.1f}-0-{rep.concentric_time:.1f}")
                if rep.posture_alerts:
                    print(f"    Alerts: {', '.join(rep.posture_alerts)}")
        
        print("\n✅ Session complete!")
        
        # Export telemetry and generate dashboard
        if logger.has_sufficient_data():
            print("\n📁 Exporting session data...")
            try:
                export_result = logger.export_session()
                print(f"  ✅ JSON: {export_result['json']}")
                print(f"  ✅ CSV (Reps): {export_result['csv_reps']}")
                print(f"  ✅ CSV (Frames): {export_result['csv_frames']}")
                
                # Generate post-workout dashboard
                print("\n🎨 Generating biomechanical dashboard...")
                session_data = export_result['session_data']
                
                if len(exercise.completed_reps) >= 3:
                    # Full dashboard for >= 3 reps
                    dashboard_path = generate_post_workout_dashboard(
                        session_data=session_data,
                        show=True
                    )
                    if dashboard_path:
                        print(f"  ✅ Dashboard: {dashboard_path}")
                        print("\n📊 Opening dashboard...")
                else:
                    # Quick summary for < 3 reps
                    print("  ℹ️  Less than 3 reps - showing quick summary")
                    from src.telemetry.dashboard import quick_summary_plot
                    quick_summary_plot(session_data, show=True)
                
            except Exception as e:
                print(f"  ⚠️  Error generating dashboard: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("\n  ℹ️  Insufficient data for telemetry export (need >= 1 rep or > 3s)")
        
        print("\n🏋️  Thank you for training!")


if __name__ == "__main__":
    main()
