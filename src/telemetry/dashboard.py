"""
Post-workout biomechanical dashboard generator.
Creates comprehensive telemetry visualizations with modern dark aesthetics.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from typing import Dict, List
import time


# Modern dark theme colors
COLORS = {
    'bg': '#121212',
    'panel_bg': '#1E1E1E',
    'text': '#FFFFFF',
    'text_dim': '#AAAAAA',
    'primary': '#00FFAA',  # Neon green
    'danger': '#FF3366',   # Neon red
    'accent': '#00BFFF',   # Neon blue
    'warning': '#FFD700',  # Gold/yellow
    'eccentric': '#FF6B6B',
    'concentric': '#4ECDC4'
}


def generate_post_workout_dashboard(
    session_data: Dict,
    output_dir: str = "sessions",
    show: bool = True
) -> str:
    """
    Generate comprehensive post-workout biomechanical dashboard.
    
    Creates a 3-panel visualization:
    1. Joint angle curve with posture alerts
    2. Concentric velocity drop analysis (VBT)
    3. Tempo and TUT comparison (eccentric vs concentric)
    
    Args:
        session_data: Session data dictionary from SessionLogger
        output_dir: Directory to save dashboard image
        show: Whether to display dashboard window
        
    Returns:
        Path to saved dashboard image
    """
    # Extract data
    metadata = session_data['metadata']
    frame_data = session_data['frame_data']
    rep_summaries = session_data['rep_summaries']
    
    if not rep_summaries or not frame_data:
        print("⚠️  Insufficient data for dashboard generation")
        return None
    
    # Calculate summary stats
    total_reps = len(rep_summaries)
    total_tut = sum(r['eccentric_time_s'] + r['concentric_time_s'] 
                   for r in rep_summaries)
    avg_rom = sum(r['rom_degrees'] for r in rep_summaries) / total_reps
    
    # Velocity loss calculation
    velocities = [r['concentric_velocity_deg_s'] for r in rep_summaries]
    max_velocity = max(velocities) if velocities else 0
    last_velocity = velocities[-1] if velocities else 0
    velocity_loss = ((max_velocity - last_velocity) / max_velocity * 100) if max_velocity > 0 else 0
    
    # Clean technique percentage
    clean_reps = sum(1 for r in rep_summaries if not r['had_compensation'])
    clean_pct = (clean_reps / total_reps) * 100
    
    # Create figure with dark theme
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 10), facecolor=COLORS['bg'])
    
    # Main title with KPIs
    title_text = (
        f"🏋️ {metadata['exercise'].upper()} - POST-WORKOUT BIOMECHANICAL ANALYSIS\n"
        f"Reps: {total_reps} | TUT: {total_tut:.1f}s | "
        f"ROM: {avg_rom:.1f}° | Velocity Loss: {velocity_loss:.1f}% | "
        f"Clean Technique: {clean_pct:.0f}%"
    )
    fig.suptitle(
        title_text,
        fontsize=16,
        fontweight='bold',
        color=COLORS['text'],
        y=0.98
    )
    
    # Create 3 subplots
    gs = fig.add_gridspec(3, 1, hspace=0.35, top=0.92, bottom=0.08, left=0.08, right=0.95)
    
    # ============================================================
    # PANEL 1: Joint Angle Curve with Posture Alerts
    # ============================================================
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(COLORS['panel_bg'])
    
    # Extract time-series data
    timestamps = [f['timestamp'] for f in frame_data]
    angles = [f['angle'] for f in frame_data]
    alerts = [f['has_posture_alert'] for f in frame_data]
    
    # Plot angle curve
    ax1.plot(
        timestamps,
        angles,
        color=COLORS['primary'],
        linewidth=2,
        label='Joint Angle (θ)',
        alpha=0.9
    )
    
    # Mark posture alerts
    alert_times = [timestamps[i] for i, a in enumerate(alerts) if a]
    alert_angles = [angles[i] for i, a in enumerate(alerts) if a]
    
    if alert_times:
        ax1.scatter(
            alert_times,
            alert_angles,
            color=COLORS['danger'],
            s=50,
            marker='X',
            label='Posture Alert',
            zorder=5,
            edgecolors='white',
            linewidths=1
        )
    
    # Add FSM state zones (background shading)
    state_changes = []
    current_state = frame_data[0]['fsm_state']
    state_start = timestamps[0]
    
    for i, f in enumerate(frame_data):
        if f['fsm_state'] != current_state or i == len(frame_data) - 1:
            state_changes.append({
                'state': current_state,
                'start': state_start,
                'end': timestamps[i]
            })
            current_state = f['fsm_state']
            state_start = timestamps[i]
    
    # Shade FSM states
    state_colors = {
        'IDLE': COLORS['text_dim'],
        'ECCENTRIC': COLORS['eccentric'],
        'BOTTOM': COLORS['warning'],
        'CONCENTRIC': COLORS['concentric']
    }
    
    for sc in state_changes:
        ax1.axvspan(
            sc['start'],
            sc['end'],
            alpha=0.1,
            color=state_colors.get(sc['state'], COLORS['text_dim'])
        )
    
    ax1.set_xlabel('Time (seconds)', fontsize=12, color=COLORS['text'])
    ax1.set_ylabel('Angle (degrees)', fontsize=12, color=COLORS['text'])
    ax1.set_title(
        '📐 Joint Angle Curve & Posture Alerts',
        fontsize=14,
        fontweight='bold',
        color=COLORS['text'],
        pad=15
    )
    ax1.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax1.grid(True, alpha=0.2, linestyle='--')
    ax1.tick_params(colors=COLORS['text'])
    
    # ============================================================
    # PANEL 2: Concentric Velocity Drop (VBT Analysis)
    # ============================================================
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(COLORS['panel_bg'])
    
    rep_numbers = [r['rep_number'] for r in rep_summaries]
    velocities = [r['concentric_velocity_deg_s'] for r in rep_summaries]
    
    # Bar chart
    bars = ax2.bar(
        rep_numbers,
        velocities,
        color=COLORS['accent'],
        alpha=0.8,
        edgecolor='white',
        linewidth=1
    )
    
    # Color bars by velocity drop
    for i, bar in enumerate(bars):
        velocity_pct = (velocities[i] / max_velocity) * 100 if max_velocity > 0 else 100
        if velocity_pct < 80:  # Lost more than 20%
            bar.set_color(COLORS['danger'])
        elif velocity_pct < 90:
            bar.set_color(COLORS['warning'])
    
    # Trend line
    if len(rep_numbers) > 1:
        z = np.polyfit(rep_numbers, velocities, 1)
        p = np.poly1d(z)
        ax2.plot(
            rep_numbers,
            p(rep_numbers),
            color=COLORS['primary'],
            linestyle='--',
            linewidth=2,
            label='Trend',
            alpha=0.7
        )
    
    # 20% velocity drop threshold
    threshold_velocity = max_velocity * 0.8
    ax2.axhline(
        threshold_velocity,
        color=COLORS['danger'],
        linestyle='--',
        linewidth=2,
        label='-20% Fatigue Threshold',
        alpha=0.7
    )
    
    ax2.set_xlabel('Rep Number', fontsize=12, color=COLORS['text'])
    ax2.set_ylabel('Concentric Velocity (°/s)', fontsize=12, color=COLORS['text'])
    ax2.set_title(
        f'⚡ Velocity-Based Training (VBT) - Fatigue Analysis\n'
        f'Peak: {max_velocity:.1f}°/s | Final: {last_velocity:.1f}°/s | Loss: {velocity_loss:.1f}%',
        fontsize=14,
        fontweight='bold',
        color=COLORS['text'],
        pad=15
    )
    ax2.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax2.grid(True, alpha=0.2, linestyle='--')
    ax2.tick_params(colors=COLORS['text'])
    ax2.set_xticks(rep_numbers)
    
    # ============================================================
    # PANEL 3: Tempo & TUT (Eccentric vs Concentric)
    # ============================================================
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor(COLORS['panel_bg'])
    
    eccentric_times = [r['eccentric_time_s'] for r in rep_summaries]
    concentric_times = [r['concentric_time_s'] for r in rep_summaries]
    
    # Stacked bar chart
    x_pos = np.arange(len(rep_numbers))
    width = 0.6
    
    bars1 = ax3.bar(
        x_pos,
        eccentric_times,
        width,
        label='Eccentric (Lowering)',
        color=COLORS['eccentric'],
        alpha=0.9,
        edgecolor='white',
        linewidth=1
    )
    
    bars2 = ax3.bar(
        x_pos,
        concentric_times,
        width,
        bottom=eccentric_times,
        label='Concentric (Lifting)',
        color=COLORS['concentric'],
        alpha=0.9,
        edgecolor='white',
        linewidth=1
    )
    
    # Add total TUT labels on bars
    for i, (e, c) in enumerate(zip(eccentric_times, concentric_times)):
        total = e + c
        ax3.text(
            i,
            total + 0.1,
            f'{total:.1f}s',
            ha='center',
            va='bottom',
            fontsize=9,
            color=COLORS['text'],
            fontweight='bold'
        )
    
    # Average tempo line
    avg_ecc = sum(eccentric_times) / len(eccentric_times)
    avg_con = sum(concentric_times) / len(concentric_times)
    
    ax3.set_xlabel('Rep Number', fontsize=12, color=COLORS['text'])
    ax3.set_ylabel('Time Under Tension (seconds)', fontsize=12, color=COLORS['text'])
    ax3.set_title(
        f'⏱️ Tempo Analysis & Time Under Tension (TUT)\n'
        f'Avg Tempo: {avg_ecc:.1f}s-0-{avg_con:.1f}s | Total TUT: {total_tut:.1f}s',
        fontsize=14,
        fontweight='bold',
        color=COLORS['text'],
        pad=15
    )
    ax3.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax3.grid(True, alpha=0.2, linestyle='--', axis='y')
    ax3.tick_params(colors=COLORS['text'])
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(rep_numbers)
    
    # ============================================================
    # Save and display
    # ============================================================
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    exercise_name = metadata['exercise'].replace(' ', '_')
    dashboard_path = output_path / f"report_{exercise_name}_{timestamp}.png"
    
    plt.savefig(
        dashboard_path,
        dpi=300,
        facecolor=COLORS['bg'],
        edgecolor='none',
        bbox_inches='tight'
    )
    
    print(f"\n📊 Dashboard saved: {dashboard_path}")
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return str(dashboard_path)


def quick_summary_plot(session_data: Dict, show: bool = True):
    """
    Generate a quick summary plot for sessions with < 3 reps.
    
    Args:
        session_data: Session data dictionary
        show: Whether to display plot
    """
    rep_summaries = session_data['rep_summaries']
    
    if not rep_summaries:
        print("⚠️  No reps to display")
        return
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['panel_bg'])
    
    rep_numbers = [r['rep_number'] for r in rep_summaries]
    roms = [r['rom_degrees'] for r in rep_summaries]
    
    ax.bar(rep_numbers, roms, color=COLORS['primary'], alpha=0.8)
    ax.set_xlabel('Rep Number', fontsize=12)
    ax.set_ylabel('ROM (degrees)', fontsize=12)
    ax.set_title(
        f"Quick Session Summary - {session_data['metadata']['exercise']}",
        fontsize=14,
        fontweight='bold'
    )
    ax.grid(True, alpha=0.2)
    
    if show:
        plt.show()
    else:
        plt.close()
