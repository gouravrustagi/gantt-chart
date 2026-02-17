from flask import Flask, render_template, request, jsonify, send_file, session, send_from_directory
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io
import base64
import re
from functools import wraps
import google.generativeai as genai
import os

app = Flask(__name__)
app.secret_key = 'gantt-chart-secret-key-2026-secure'  # Change this to a random secret key

# Create downloads directory
DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

# Gemini API Key verification
def verify_gemini_key(api_key):
    """Verify Gemini API key by attempting to configure and list models"""
    try:
        genai.configure(api_key=api_key)
        # Try to list models as a verification step
        list(genai.list_models())
        return True
    except Exception as e:
        print(f"Gemini API verification failed: {e}")
        return False

# API Key validation decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session first
        if session.get('authenticated'):
            return f(*args, **kwargs)
        
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    return decorated_function

class GanttChartGenerator:
    def __init__(self):
        self.tasks = []
        self.progressive_mode = True  # Progressive mode enabled by default
        
        # Define color palettes
        self.color_palettes = {
            'corporate': {
                'primary': ['#2E5266', '#6E8898', '#9FB1BC', '#4A90A4', '#5A7A8A', 
                           '#3E6080', '#7E98A8', '#4E7088', '#8EA8B8', '#2A4E62'],
                'accent': '#1A3A4A',
                'timeline': '#1F4788',
                'milestone': ['#5B4B8A', '#7B6BA8', '#6B5B9A', '#8B7BB8', '#9C8EC0'],
                'completed': '#43A047',
                'remaining': '#FB8C00',
                'critical': '#E53935',
                'normal': '#757575'
            },
            'vibrant': {
                'primary': ['#E53935', '#1E88E5', '#43A047', '#FB8C00', '#8E24AA',
                           '#D81B60', '#3949AB', '#00897B', '#FDD835', '#C0CA33'],
                'accent': '#212121',
                'timeline': '#1565C0',
                'milestone': ['#C62828', '#1565C0', '#2E7D32', '#EF6C00', '#6A1B9A'],
                'completed': '#2E7D32',
                'remaining': '#EF6C00',
                'critical': '#D32F2F',
                'normal': '#616161'
            },
            'pastel': {
                'primary': ['#F48FB1', '#81D4FA', '#A5D6A7', '#FFE082', '#CE93D8',
                           '#FFAB91', '#80CBC4', '#FFD54F', '#90CAF9', '#BCAAA4'],
                'accent': '#5D4037',
                'timeline': '#4FC3F7',
                'milestone': ['#F06292', '#4FC3F7', '#81C784', '#FFD54F', '#BA68C8'],
                'completed': '#66BB6A',
                'remaining': '#FFA726',
                'critical': '#EF5350',
                'normal': '#9E9E9E'
            },
            'ocean': {
                'primary': ['#006064', '#00838F', '#0097A7', '#00ACC1', '#00BCD4',
                           '#26C6DA', '#4DD0E1', '#00838F', '#006064', '#01579B'],
                'accent': '#004D40',
                'timeline': '#006064',
                'milestone': ['#004D40', '#00695C', '#00796B', '#00897B', '#009688'],
                'completed': '#00897B',
                'remaining': '#FB8C00',
                'critical': '#D84315',
                'normal': '#607D8B'
            },
            'sunset': {
                'primary': ['#BF360C', '#E64A19', '#FF6F00', '#FF8F00', '#F57C00',
                           '#E65100', '#FF6F00', '#F57F17', '#FF8A65', '#FF5722'],
                'accent': '#3E2723',
                'timeline': '#D84315',
                'milestone': ['#BF360C', '#D84315', '#E64A19', '#F4511E', '#FF5722'],
                'completed': '#66BB6A',
                'remaining': '#FF6F00',
                'critical': '#B71C1C',
                'normal': '#795548'
            },
            'forest': {
                'primary': ['#1B5E20', '#2E7D32', '#388E3C', '#43A047', '#4CAF50',
                           '#66BB6A', '#81C784', '#2E7D32', '#1B5E20', '#33691E'],
                'accent': '#1B5E20',
                'timeline': '#2E7D32',
                'milestone': ['#1B5E20', '#2E7D32', '#388E3C', '#43A047', '#558B2F'],
                'completed': '#388E3C',
                'remaining': '#F57C00',
                'critical': '#C62828',
                'normal': '#616161'
            },
            'monochrome': {
                'primary': ['#212121', '#424242', '#616161', '#757575', '#9E9E9E',
                           '#BDBDBD', '#E0E0E0', '#616161', '#424242', '#757575'],
                'accent': '#000000',
                'timeline': '#424242',
                'milestone': ['#212121', '#424242', '#616161', '#757575', '#9E9E9E'],
                'completed': '#666666',
                'remaining': '#AAAAAA',
                'critical': '#212121',
                'normal': '#888888'
            },
            'neon': {
                'primary': ['#FF006E', '#00F5FF', '#39FF14', '#FFFF00', '#FF3131',
                           '#BC13FE', '#FF10F0', '#00FF41', '#FE4164', '#08F7FE'],
                'accent': '#1A1A2E',
                'timeline': '#0F4C75',
                'milestone': ['#FF006E', '#00F5FF', '#39FF14', '#FFFF00', '#BC13FE'],
                'completed': '#39FF14',
                'remaining': '#FFFF00',
                'critical': '#FF3131',
                'normal': '#A0A0A0'
            },
            'autumn': {
                'primary': ['#8B4513', '#D2691E', '#CD853F', '#DEB887', '#F4A460',
                           '#B8860B', '#DAA520', '#CD853F', '#8B4513', '#A0522D'],
                'accent': '#2F1B0C',
                'timeline': '#8B4513',
                'milestone': ['#8B4513', '#D2691E', '#CD853F', '#B8860B', '#A0522D'],
                'completed': '#6B8E23',
                'remaining': '#FF8C00',
                'critical': '#8B0000',
                'normal': '#8B7355'
            },
            'spring': {
                'primary': ['#98D8C8', '#F7DC6F', '#F8B4D9', '#B4E7CE', '#FFD3B6',
                           '#AAFFAA', '#FFAADD', '#AAE3FF', '#FFDDAA', '#DDAAFF'],
                'accent': '#2E5339',
                'timeline': '#52B788',
                'milestone': ['#98D8C8', '#F7DC6F', '#F8B4D9', '#B4E7CE', '#AAFFAA'],
                'completed': '#52B788',
                'remaining': '#FFA600',
                'critical': '#D62828',
                'normal': '#718096'
            },
            'midnight': {
                'primary': ['#120136', '#1C0A4F', '#2E1A47', '#4A2C5E', '#6A4C93',
                           '#8B6BBD', '#A68BCC', '#4A2C5E', '#2E1A47', '#1C0A4F'],
                'accent': '#000000',
                'timeline': '#2E1A47',
                'milestone': ['#120136', '#1C0A4F', '#2E1A47', '#4A2C5E', '#6A4C93'],
                'completed': '#4A9D71',
                'remaining': '#F39C12',
                'critical': '#C0392B',
                'normal': '#566573'
            },
            'candy': {
                'primary': ['#FF69B4', '#FF1493', '#FF69CC', '#FF85D3', '#FF99DD',
                           '#FFB3E6', '#FFC8EC', '#FF85D3', '#FF69CC', '#FF1493'],
                'accent': '#8B008B',
                'timeline': '#FF1493',
                'milestone': ['#FF69B4', '#FF1493', '#FF69CC', '#FF85D3', '#FFB3E6'],
                'completed': '#98D8C8',
                'remaining': '#FFD700',
                'critical': '#DC143C',
                'normal': '#9370DB'
            },
            'earth': {
                'primary': ['#6B4423', '#8B5A3C', '#A0826D', '#B8956A', '#C9A88A',
                           '#8B7355', '#9F8170', '#A68A64', '#8B7355', '#6B4423'],
                'accent': '#3E2723',
                'timeline': '#6B4423',
                'milestone': ['#6B4423', '#8B5A3C', '#A0826D', '#B8956A', '#8B7355'],
                'completed': '#7CB342',
                'remaining': '#F57F17',
                'critical': '#BF360C',
                'normal': '#795548'
            },
            'tropical': {
                'primary': ['#00CED1', '#FF6B6B', '#FFD93D', '#6BCB77', '#4D96FF',
                           '#FF6FB5', '#95E1D3', '#FFA07A', '#20B2AA', '#FF7F50'],
                'accent': '#004D4D',
                'timeline': '#00CED1',
                'milestone': ['#00CED1', '#FF6B6B', '#FFD93D', '#6BCB77', '#4D96FF'],
                'completed': '#6BCB77',
                'remaining': '#FFD93D',
                'critical': '#FF6B6B',
                'normal': '#48929B'
            }
        }
    
    def parse_duration(self, duration_str):
        """Parse duration string and return total hours and formatted string"""
        duration_str = duration_str.lower().strip()
        total_hours = 0
        
        # Parse days
        days_match = re.search(r'(\d+)\s*d', duration_str)
        if days_match:
            total_hours += int(days_match.group(1)) * 24
        
        # Parse hours
        hours_match = re.search(r'(\d+)\s*h', duration_str)
        if hours_match:
            total_hours += int(hours_match.group(1))
        
        # Parse minutes
        minutes_match = re.search(r'(\d+)\s*m', duration_str)
        if minutes_match:
            total_hours += int(minutes_match.group(1)) / 60
        
        if total_hours <= 0:
            raise ValueError("Invalid duration format")
        
        # Create formatted string
        days = int(total_hours // 24)
        hours = int(total_hours % 24)
        minutes = int((total_hours * 60) % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        
        formatted = " ".join(parts) if parts else "0h"
        
        return total_hours, formatted
    
    def recalculate_sequence(self, start_index=0):
        """Recalculate task sequence from start_index onwards"""
        if not self.progressive_mode or start_index >= len(self.tasks):
            return 0
        
        count = 0
        for i in range(start_index, len(self.tasks)):
            if i == 0:
                # First task keeps its original start date
                continue
            
            prev_task = self.tasks[i - 1]
            current_task = self.tasks[i]
            
            # Start this task after the previous one ends
            new_start = prev_task['end']
            new_end = new_start + timedelta(hours=current_task['duration_hours'])
            
            # Only update if different
            if current_task['start'] != new_start:
                self.tasks[i]['start'] = new_start
                self.tasks[i]['end'] = new_end
                count += 1
        
        return count
    
    def add_task(self, name, start_date_str, duration_str, start_time_str='00:00'):
        """Add a task"""
        # Parse date and time
        datetime_str = f"{start_date_str} {start_time_str}"
        start_date = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        
        # If progressive mode is on and there are existing tasks, start after the last task
        if self.progressive_mode and self.tasks:
            last_task = self.tasks[-1]
            start_date = last_task['end']
        
        total_hours, formatted_duration = self.parse_duration(duration_str)
        end_date = start_date + timedelta(hours=total_hours)
        
        task = {
            'name': name,
            'start': start_date,
            'duration_hours': total_hours,
            'duration_str': formatted_duration,
            'end': end_date
        }
        self.tasks.append(task)
        return task
    
    def generate_chart(self, chart_type='standard', color_scheme='corporate'):
        """Generate chart and return as base64 image"""
        if not self.tasks:
            return None
        
        # Set the color palette
        self.current_palette = self.color_palettes.get(color_scheme, self.color_palettes['corporate'])
        
        if chart_type == 'standard':
            return self._generate_standard_chart()
        elif chart_type == 'timeline':
            return self._generate_timeline_chart()
        elif chart_type == 'milestone':
            return self._generate_milestone_chart()
        elif chart_type == 'compact':
            return self._generate_compact_chart()
        elif chart_type == 'waterfall':
            return self._generate_waterfall_chart()
        elif chart_type == 'critical-path':
            return self._generate_critical_path_chart()
        elif chart_type == 'resource':
            return self._generate_resource_chart()
        elif chart_type == 'progress':
            return self._generate_progress_chart()
        elif chart_type == 'dependencies':
            return self._generate_dependencies_chart()
        elif chart_type == 'baseline':
            return self._generate_baseline_chart()
        elif chart_type == 'swimlane':
            return self._generate_swimlane_chart()
        elif chart_type == 'calendar':
            return self._generate_calendar_chart()
        elif chart_type == 'gantt-bars':
            return self._generate_gantt_bars_chart()
        elif chart_type == 'comparison':
            return self._generate_comparison_chart()
    
    def _generate_standard_chart(self):
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = self.current_palette['primary']
        
        for idx, task in enumerate(self.tasks):
            color = colors[idx % len(colors)]
            duration_days = task['duration_hours'] / 24
            
            # Main task bar
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.6, color=color, edgecolor=self.current_palette['accent'], 
                   linewidth=2, alpha=0.85, zorder=2)
            
            # Duration label in center
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, task['duration_str'], 
                   ha='center', va='center', fontweight='bold', fontsize=10, 
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                            edgecolor=self.current_palette['accent'], linewidth=1.5, alpha=0.9),
                   zorder=3)
            
            # Start and End dates on sides
            ax.text(task['start'], idx, task['start'].strftime('%b %d'), 
                   ha='right', va='center', fontsize=7, color=self.current_palette['accent'],
                   fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', 
                   facecolor='lightyellow', alpha=0.8), zorder=3)
            ax.text(task['end'], idx, task['end'].strftime('%b %d'), 
                   ha='left', va='center', fontsize=7, color=self.current_palette['accent'],
                   fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', 
                   facecolor='lightgreen', alpha=0.8), zorder=3)
        
        ax.invert_yaxis()
        return self._format_and_encode(ax, fig, 'Standard Gantt Chart')
    
    def _generate_timeline_chart(self):
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = self.current_palette['primary']
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            color = colors[idx % len(colors)]
            
            # Timeline bar with gradient effect
            ax.barh(idx, duration_days, left=task['start'], 
                   height=0.4, color=color, 
                   edgecolor=self.current_palette['accent'], linewidth=2.5, alpha=0.85, zorder=2)
            
            # Task name in center
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, f"{task['name']}\n({task['duration_str']})", 
                   ha='center', va='center', fontweight='bold', fontsize=9, 
                   color='white', zorder=3)
            
            # Start marker (circle)
            ax.plot(task['start'], idx, 'o', markersize=10, color='white', 
                   markeredgecolor=self.current_palette['accent'], markeredgewidth=2, zorder=4)
            ax.text(task['start'], idx - 0.3, task['start'].strftime('%b %d\n%H:%M'), 
                   ha='center', va='top', fontsize=7, color=self.current_palette['accent'],
                   fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', 
                   facecolor='lightyellow', alpha=0.9), zorder=4)
            
            # End marker (square)
            ax.plot(task['end'], idx, 's', markersize=10, color='white', 
                   markeredgecolor=self.current_palette['completed'], markeredgewidth=2, zorder=4)
            ax.text(task['end'], idx - 0.3, task['end'].strftime('%b %d\n%H:%M'), 
                   ha='center', va='top', fontsize=7, color=self.current_palette['completed'],
                   fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', 
                   facecolor='lightgreen', alpha=0.9), zorder=4)
        
        ax.set_yticks([])
        ax.set_ylim(-0.8, len(self.tasks) - 0.2)
        return self._format_and_encode(ax, fig, 'Enhanced Timeline View')
    
    def _generate_milestone_chart(self):
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = self.current_palette['milestone']
        
        for idx, task in enumerate(self.tasks):
            color = colors[idx % len(colors)]
            
            # Connection line
            ax.plot([task['start'], task['end']], [idx, idx], 
                   color=color, linewidth=4, alpha=0.7, zorder=1)
            
            # Start milestone (circle)
            ax.plot(task['start'], idx, marker='o', markersize=16, 
                   color=color, markeredgecolor=self.current_palette['accent'], 
                   markeredgewidth=3, zorder=3, label='Start' if idx == 0 else '')
            ax.text(task['start'], idx, 'S', ha='center', va='center', 
                   fontsize=8, fontweight='bold', color='white', zorder=4)
            
            # End milestone (diamond)
            ax.plot(task['end'], idx, marker='D', markersize=16, 
                   color=color, markeredgecolor=self.current_palette['accent'], 
                   markeredgewidth=3, zorder=3, label='End' if idx == 0 else '')
            ax.text(task['end'], idx, 'E', ha='center', va='center', 
                   fontsize=8, fontweight='bold', color='white', zorder=4)
            
            # Task information
            mid_point = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(mid_point, idx - 0.25, task['name'], 
                   ha='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                            edgecolor=color, linewidth=2, alpha=0.9), zorder=2)
            ax.text(mid_point, idx + 0.25, f"{task['duration_str']} | {task['start'].strftime('%b %d')} → {task['end'].strftime('%b %d')}", 
                   ha='center', fontsize=8, style='italic', 
                   color=self.current_palette['accent'], fontweight='bold', zorder=2)
        
        ax.set_yticks([])
        return self._format_and_encode(ax, fig, 'Milestone Chart')
    
    def _generate_compact_chart(self):
        fig, ax = plt.subplots(figsize=(14, max(6, len(self.tasks) * 0.8)))
        colors = self.current_palette['primary']
        
        # Calculate total duration
        total_duration = sum(t['duration_hours'] for t in self.tasks)
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            color = colors[idx % len(colors)]
            percentage = (task['duration_hours'] / total_duration) * 100
            
            # Compact bar
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.75, color=color, 
                   edgecolor=self.current_palette['accent'], linewidth=2.5, alpha=0.85, zorder=2)
            
            # Duration and percentage label
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, f"{task['duration_str']}\n{percentage:.1f}%", 
                   ha='center', va='center', fontweight='bold', fontsize=9, 
                   color='white', zorder=3,
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.3))
            
            # Task index
            ax.text(task['start'], idx, f" #{idx+1}", 
                   ha='right', va='center', fontsize=8, 
                   fontweight='bold', color=color,
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9), zorder=3)
        
        # Add statistics
        avg_duration = total_duration / len(self.tasks)
        stats_text = f"Total: {int(total_duration)}h | Avg: {int(avg_duration)}h | Tasks: {len(self.tasks)}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               fontsize=10, fontweight='bold', va='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                        edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.95))
        
        ax.invert_yaxis()
        return self._format_and_encode(ax, fig, 'Compact View')
    
    def _generate_waterfall_chart(self):
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = self.current_palette['primary']
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            color = colors[idx % len(colors)]
            
            # Simulated progress (based on current date)
            today = datetime.now()
            if today > task['end']:
                progress_pct = 100
            elif today < task['start']:
                progress_pct = 0
            else:
                elapsed = (today - task['start']).total_seconds() / 3600
                progress_pct = min(100, (elapsed / task['duration_hours']) * 100)
            
            progress_duration = duration_days * (progress_pct / 100)
            remaining_duration = duration_days - progress_duration
            
            # Completed portion (filled)
            if progress_duration > 0:
                ax.barh(task['name'], progress_duration, left=task['start'], 
                       height=0.65, color=self.current_palette['completed'], 
                       edgecolor=self.current_palette['accent'], 
                       linewidth=2, alpha=0.85, label='Completed' if idx == 0 else '', zorder=2)
            
            # Remaining portion (lighter)
            if remaining_duration > 0:
                ax.barh(task['name'], remaining_duration, 
                       left=task['start'] + timedelta(days=progress_duration), 
                       height=0.65, color=color, edgecolor=self.current_palette['accent'], 
                       linewidth=2, alpha=0.5, label='Remaining' if idx == 0 else '', zorder=2)
            
            # Progress label
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            status = '✓ Done' if progress_pct >= 100 else f'{progress_pct:.0f}%'
            ax.text(label_position, idx, f"{task['duration_str']}\n{status}", 
                   ha='center', va='center', fontweight='bold', fontsize=9, 
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                            edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.95), zorder=3)
        
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
        ax.invert_yaxis()
        return self._format_and_encode(ax, fig, 'Waterfall Progress View')
    
    def _generate_critical_path_chart(self):
        """Generate critical path chart highlighting longest tasks"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Calculate critical path (tasks with longest duration)
        avg_duration = sum(t['duration_hours'] for t in self.tasks) / len(self.tasks)
        max_duration = max(t['duration_hours'] for t in self.tasks)
        critical_tasks = [t for t in self.tasks if t['duration_hours'] >= avg_duration]
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            is_critical = task in critical_tasks
            color = self.current_palette['critical'] if is_critical else self.current_palette['normal']
            linewidth = 4 if is_critical else 2
            alpha = 0.9 if is_critical else 0.6
            height = 0.7 if is_critical else 0.5
            
            # Task bar
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=height, color=color, edgecolor=self.current_palette['accent'], 
                   linewidth=linewidth, alpha=alpha, zorder=2 if is_critical else 1)
            
            # Priority indicator
            priority_text = "CRITICAL" if is_critical else "Normal"
            priority_icon = "⚠" if is_critical else "✓"
            text_color = 'white' if is_critical else self.current_palette['accent']
            
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, f"{priority_icon} {task['duration_str']}\n{priority_text}", 
                   ha='center', va='center', fontweight='bold', fontsize=10 if is_critical else 8,
                   color=text_color if not is_critical else text_color,
                   bbox=dict(boxstyle='round,pad=0.4', 
                            facecolor=color if is_critical else 'white',
                            edgecolor=self.current_palette['critical'] if is_critical else self.current_palette['normal'], 
                            linewidth=3 if is_critical else 1.5, alpha=0.95), zorder=3)
            
            # Duration percentage of max
            pct_of_max = (task['duration_hours'] / max_duration) * 100
            ax.text(task['end'], idx, f" {pct_of_max:.0f}%", 
                   ha='left', va='center', fontsize=8, 
                   fontweight='bold', color=color,
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9), zorder=3)
        
        # Add statistics
        critical_count = len(critical_tasks)
        stats_text = f"Critical Tasks: {critical_count}/{len(self.tasks)} | Threshold: {int(avg_duration)}h"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               fontsize=10, fontweight='bold', va='top', color=self.current_palette['critical'],
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                        edgecolor=self.current_palette['critical'], linewidth=2.5, alpha=0.95))
        
        ax.invert_yaxis()
        return self._format_and_encode(ax, fig, 'Critical Path Analysis')
    
    def _generate_resource_chart(self):
        """Generate resource allocation chart with color-coded teams"""
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = self.current_palette['primary']
        team_colors = {f'Team {chr(65+i)}': colors[i % len(colors)] for i in range(5)}
        teams = list(team_colors.keys())
        
        # Track team workload
        team_hours = {team: 0 for team in teams}
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            team = teams[idx % len(teams)]
            color = team_colors[team]
            team_hours[team] += task['duration_hours']
            
            # Resource bar
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.7, color=color, edgecolor=self.current_palette['accent'], 
                   linewidth=2.5, alpha=0.8, label=team if idx < len(teams) else '', zorder=2)
            
            # Team and duration label
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, f"{task['duration_str']}\n{team}", 
                   ha='center', va='center', fontweight='bold', fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                            edgecolor=color, linewidth=2.5, alpha=0.95), zorder=3)
            
            # Resource utilization indicator
            utilization = min(100, (team_hours[team] / sum(team_hours.values())) * 100 * len(teams))
            util_color = self.current_palette['critical'] if utilization > 80 else \
                        self.current_palette['remaining'] if utilization > 50 else \
                        self.current_palette['completed']
            ax.text(task['start'], idx, f" {utilization:.0f}%", 
                   ha='right', va='center', fontsize=7, 
                   fontweight='bold', color='white',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor=util_color, 
                            edgecolor=self.current_palette['accent'], linewidth=1.5, alpha=0.9), zorder=3)
        
        # Add workload distribution
        workload_text = " | ".join([f"{team.split()[1]}: {int(hrs)}h" for team, hrs in team_hours.items()])
        ax.text(0.02, 0.98, f"Workload Distribution: {workload_text}", transform=ax.transAxes, 
               fontsize=9, fontweight='bold', va='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                        edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.95))
        
        ax.invert_yaxis()
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=10, framealpha=0.9)
        return self._format_and_encode(ax, fig, 'Resource Allocation View')
    
    def _generate_progress_chart(self):
        """Generate progress tracking chart with completion percentages"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            # Simulate progress based on task index (30-90%)
            progress_pct = min(30 + (idx * 15), 90)
            completed_duration = duration_days * (progress_pct / 100)
            remaining_duration = duration_days - completed_duration
            
            # Completed portion with pattern
            completed_bar = ax.barh(task['name'], completed_duration, left=task['start'], 
                   height=0.7, color=self.current_palette['completed'], 
                   edgecolor=self.current_palette['accent'], 
                   linewidth=2, alpha=0.85, label='Completed' if idx == 0 else '', zorder=2)
            
            # Remaining portion
            remaining_bar = ax.barh(task['name'], remaining_duration, 
                   left=task['start'] + timedelta(days=completed_duration), 
                   height=0.7, color=self.current_palette['remaining'], 
                   edgecolor=self.current_palette['accent'], 
                   linewidth=2, alpha=0.7, label='Remaining' if idx == 0 else '', zorder=2)
            
            # Progress percentage label
            label_position = task['start'] + timedelta(days=duration_days/2)
            status_icon = '✓' if progress_pct >= 90 else '⚡' if progress_pct >= 50 else '○'
            ax.text(label_position, idx, f"{status_icon} {progress_pct}%\n{task['duration_str']}", 
                   ha='center', va='center', fontweight='bold', fontsize=10,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                            edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.95), zorder=3)
            
            # Completion date estimate
            days_remaining = task['duration_hours'] * (100 - progress_pct) / 100 / 24
            est_completion = datetime.now() + timedelta(days=days_remaining)
            ax.text(task['end'], idx, f"Est: {est_completion.strftime('%b %d')}", 
                   ha='left', va='center', fontsize=7, color=self.current_palette['remaining'],
                   fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', 
                   facecolor='white', alpha=0.9), zorder=3)
        
        # Overall progress statistics
        total_progress = sum([min(30 + (i * 15), 90) for i in range(len(self.tasks))]) / len(self.tasks)
        completed_tasks = sum(1 for i in range(len(self.tasks)) if min(30 + (i * 15), 90) >= 90)
        stats_text = f"Overall Progress: {total_progress:.1f}% | Completed: {completed_tasks}/{len(self.tasks)}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               fontsize=10, fontweight='bold', va='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                        edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.95))
        
        ax.invert_yaxis()
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
        return self._format_and_encode(ax, fig, 'Progress Tracking')
    
    def _generate_dependencies_chart(self):
        """Generate chart showing task dependencies with arrows"""
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = self.current_palette['primary']
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            color = colors[idx % len(colors)]
            
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.6, color=color, edgecolor=self.current_palette['accent'], 
                   linewidth=2.5, alpha=0.85, zorder=2)
            
            # Draw dependency arrows to next task
            if idx < len(self.tasks) - 1:
                next_task = self.tasks[idx + 1]
                # Calculate gap time
                gap = (next_task['start'] - task['end']).total_seconds() / 3600
                arrow_color = self.current_palette['completed'] if gap >= 0 else self.current_palette['critical']
                
                ax.annotate('', xy=(next_task['start'], idx + 1), 
                           xytext=(task['end'], idx),
                           arrowprops=dict(arrowstyle='->', lw=3, color=arrow_color, 
                                         alpha=0.8, linestyle='--'), zorder=1)
                
                # Gap duration label
                mid_x = task['end'] + (next_task['start'] - task['end']) / 2
                mid_y = idx + 0.5
                if abs(gap) >= 1:
                    gap_text = f"{abs(int(gap))}h gap" if gap >= 0 else f"{abs(int(gap))}h overlap"
                    ax.text(mid_x, mid_y, gap_text, 
                           ha='center', va='center', fontsize=7, 
                           color=arrow_color, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                    edgecolor=arrow_color, alpha=0.8), zorder=2)
            
            # Task label
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, f"{task['duration_str']}", 
                   ha='center', va='center', fontweight='bold', fontsize=10,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                            edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.95), zorder=3)
            
            # Task number badge
            ax.text(task['start'], idx, f" #{idx+1}", 
                   ha='right', va='center', fontsize=8, 
                   fontweight='bold', color='white',
                   bbox=dict(boxstyle='circle,pad=0.3', facecolor=color, 
                            edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.9), zorder=3)
        
        # Dependency statistics
        total_gaps = sum(1 for i in range(len(self.tasks)-1) 
                        if (self.tasks[i+1]['start'] - self.tasks[i]['end']).total_seconds() / 3600 > 0)
        overlaps = (len(self.tasks) - 1) - total_gaps
        stats_text = f"Dependencies: {len(self.tasks)-1} | Gaps: {total_gaps} | Overlaps: {overlaps}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               fontsize=10, fontweight='bold', va='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                        edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.95))
        
        ax.invert_yaxis()
        return self._format_and_encode(ax, fig, 'Task Dependencies')
    
    def _generate_baseline_chart(self):
        """Generate baseline comparison chart (planned vs actual)"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            
            # Simulate actual duration (±15% variation)
            actual_duration = duration_days * (0.85 + (idx % 3) * 0.1)
            variance = ((actual_duration - duration_days) / duration_days * 100)
            is_ahead = variance < 0
            
            # Baseline (planned) - top bar
            ax.barh(idx - 0.25, duration_days, left=task['start'], 
                   height=0.4, color=self.current_palette['normal'], 
                   edgecolor=self.current_palette['accent'], 
                   linewidth=2, alpha=0.7, label='Baseline (Planned)' if idx == 0 else '', zorder=2)
            
            # Actual - bottom bar
            actual_color = self.current_palette['completed'] if is_ahead else self.current_palette['critical']
            ax.barh(idx + 0.25, actual_duration, left=task['start'], 
                   height=0.4, color=actual_color, 
                   edgecolor=self.current_palette['accent'], 
                   linewidth=2, alpha=0.85, label='Actual' if idx == 0 else '', zorder=2)
            
            # Task name on left
            ax.text(task['start'] - timedelta(days=0.5), idx, task['name'], 
                   ha='right', va='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                            edgecolor=self.current_palette['accent'], linewidth=1.5, alpha=0.95))
            
            # Variance indicator
            variance_icon = "↑" if is_ahead else "↓"
            variance_text = f"{variance_icon} {abs(variance):.1f}%"
            variance_color = self.current_palette['completed'] if is_ahead else self.current_palette['critical']
            ax.text(max(task['end'], task['start'] + timedelta(days=actual_duration)) + timedelta(days=0.5), 
                   idx, variance_text, 
                   ha='left', va='center', fontsize=9, color='white', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=variance_color, 
                            edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.95), zorder=3)
            
            # Duration labels
            mid_baseline = task['start'] + timedelta(days=duration_days/2)
            ax.text(mid_baseline, idx - 0.25, task['duration_str'], 
                   ha='center', va='center', fontsize=7, fontweight='bold',
                   color=self.current_palette['accent'])
            
            mid_actual = task['start'] + timedelta(days=actual_duration/2)
            actual_hours = int(task['duration_hours'] * (actual_duration / duration_days))
            actual_duration_str = f"{actual_hours}h"
            ax.text(mid_actual, idx + 0.25, actual_duration_str, 
                   ha='center', va='center', fontsize=7, fontweight='bold', color='white')
        
        # Summary statistics
        on_track = sum(1 for idx in range(len(self.tasks)) 
                      if (0.85 + (idx % 3) * 0.1) <= 1.0)
        delayed = len(self.tasks) - on_track
        ax.text(0.02, 0.98, f"Status: {on_track} On Track | {delayed} Delayed", 
               transform=ax.transAxes, fontsize=11, fontweight='bold', va='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                        edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.95))
        
        ax.set_yticks([])
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
        return self._format_and_encode(ax, fig, 'Baseline Comparison')
    
    def _generate_swimlane_chart(self):
        """Generate swimlane-style Gantt chart with phases"""
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = self.current_palette['primary']
        
        # Group tasks into phases (every 2-3 tasks per phase)
        phase_size = max(2, len(self.tasks) // 4)
        
        y_pos = 0
        for phase_idx in range((len(self.tasks) + phase_size - 1) // phase_size):
            start_idx = phase_idx * phase_size
            end_idx = min(start_idx + phase_size, len(self.tasks))
            phase_tasks = self.tasks[start_idx:end_idx]
            
            # Phase background
            ax.axhspan(y_pos - 0.5, y_pos + len(phase_tasks) + 0.5, 
                      facecolor=colors[phase_idx % len(colors)], alpha=0.1)
            
            # Phase label
            ax.text(-0.02, y_pos + len(phase_tasks) / 2, f'Phase {phase_idx + 1}', 
                   transform=ax.get_yaxis_transform(), ha='right', va='center',
                   fontsize=11, fontweight='bold', rotation=90,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor=colors[phase_idx % len(colors)], 
                            edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.8))
            
            for task_idx, task in enumerate(phase_tasks):
                duration_days = task['duration_hours'] / 24
                color = colors[(start_idx + task_idx) % len(colors)]
                
                # Task bar
                ax.barh(y_pos + task_idx, duration_days, left=task['start'], 
                       height=0.7, color=color, edgecolor=self.current_palette['accent'], 
                       linewidth=2, alpha=0.85, zorder=2)
                
                # Task label
                ax.text(task['start'], y_pos + task_idx, f" {task['name']}", 
                       ha='left', va='center', fontsize=9, fontweight='bold',
                       color='white', zorder=3)
            
            y_pos += len(phase_tasks) + 1
        
        ax.set_yticks([])
        ax.set_ylim(-0.5, y_pos - 0.5)
        ax.invert_yaxis()
        return self._format_and_encode(ax, fig, 'Swimlane Gantt Chart')
    
    def _generate_calendar_chart(self):
        """Generate calendar-style view"""
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = self.current_palette['primary']
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            color = colors[idx % len(colors)]
            
            # Calendar block with border
            ax.barh(idx, duration_days, left=task['start'], 
                   height=0.8, color=color, edgecolor='white', 
                   linewidth=3, alpha=0.85, zorder=2)
            
            # Inner detail box
            ax.barh(idx, duration_days * 0.95, left=task['start'] + timedelta(hours=task['duration_hours'] * 0.025), 
                   height=0.6, color='white', alpha=0.3, zorder=3)
            
            # Task name (large)
            mid_point = task['start'] + timedelta(hours=task['duration_hours'] / 2)
            ax.text(mid_point, idx + 0.15, task['name'], 
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   color=self.current_palette['accent'], zorder=4)
            
            # Duration (small)
            ax.text(mid_point, idx - 0.15, f"⏱ {task['duration_str']}", 
                   ha='center', va='center', fontsize=8,
                   color=self.current_palette['accent'], style='italic', zorder=4)
            
            # Date markers
            ax.text(task['start'], idx - 0.45, task['start'].strftime('%b %d'), 
                   ha='center', va='top', fontsize=7, color=color,
                   fontweight='bold', zorder=4)
            ax.text(task['end'], idx - 0.45, task['end'].strftime('%b %d'), 
                   ha='center', va='top', fontsize=7, color=color,
                   fontweight='bold', zorder=4)
        
        ax.set_yticks([])
        ax.invert_yaxis()
        return self._format_and_encode(ax, fig, 'Calendar View')
    
    def _generate_gantt_bars_chart(self):
        """Generate traditional Gantt bars with solid styling"""
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = self.current_palette['primary']
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            color = colors[idx % len(colors)]
            
            # Solid bar with shadow effect
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.8, color=color, edgecolor=self.current_palette['accent'], 
                   linewidth=3, alpha=0.9, zorder=2)
            
            # Shadow
            ax.barh(task['name'], duration_days, left=task['start'] + timedelta(hours=6), 
                   height=0.8, color='black', alpha=0.15, zorder=1)
            
            # Timeline marker
            for day_offset in range(0, int(duration_days) + 1, max(1, int(duration_days) // 5)):
                marker_date = task['start'] + timedelta(days=day_offset)
                if marker_date <= task['end']:
                    ax.plot(marker_date, idx, 'o', markersize=6, color='white', 
                           markeredgecolor=self.current_palette['accent'], markeredgewidth=2, zorder=3)
            
            # Duration at center
            mid_point = task['start'] + timedelta(hours=task['duration_hours'] / 2)
            ax.text(mid_point, idx, task['duration_str'], 
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   color='white', zorder=4)
        
        ax.invert_yaxis()
        return self._format_and_encode(ax, fig, 'Traditional Gantt Bars')
    
    def _generate_comparison_chart(self):
        """Generate comparison view with metrics"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={'width_ratios': [3, 1]})
        colors = self.current_palette['primary']
        
        # Left: Gantt chart
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            color = colors[idx % len(colors)]
            
            ax1.barh(task['name'], duration_days, left=task['start'], 
                    height=0.7, color=color, edgecolor=self.current_palette['accent'], 
                    linewidth=2, alpha=0.85)
            
            mid_point = task['start'] + timedelta(hours=task['duration_hours'] / 2)
            ax1.text(mid_point, idx, task['duration_str'], 
                    ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        
        ax1.invert_yaxis()
        ax1.set_title('Task Timeline', fontsize=12, fontweight='bold', pad=15)
        
        # Right: Duration comparison bar chart
        task_names = [t['name'][:15] + '...' if len(t['name']) > 15 else t['name'] for t in self.tasks]
        durations = [t['duration_hours'] for t in self.tasks]
        
        bars = ax2.barh(task_names, durations, color=colors[:len(self.tasks)], 
                       edgecolor=self.current_palette['accent'], linewidth=2, alpha=0.85)
        
        for idx, (bar, duration) in enumerate(zip(bars, durations)):
            ax2.text(duration, idx, f' {int(duration)}h', 
                    va='center', fontsize=9, fontweight='bold')
        
        ax2.invert_yaxis()
        ax2.set_xlabel('Duration (hours)', fontsize=10, fontweight='bold')
        ax2.set_title('Duration Comparison', fontsize=12, fontweight='bold', pad=15)
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Style both axes
        for ax in [ax1, ax2]:
            ax.set_facecolor('#F5F5F5')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_base64
    
    def _format_and_encode(self, ax, fig, title):
        """Format chart and return as base64"""
        max_duration_hours = max(task['duration_hours'] for task in self.tasks)
        
        # Professional styling
        ax.set_facecolor('#F5F5F5')
        fig.patch.set_facecolor('white')
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, color='#BDBDBD')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#757575')
        ax.spines['bottom'].set_color('#757575')
        
        if max_duration_hours <= 48:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, int(max_duration_hours // 10))))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(self.tasks) // 2)))
        
        plt.xticks(rotation=45, ha='right', fontsize=9, color='#424242')
        ax.set_xlabel('Date', fontsize=11, fontweight='bold', color='#212121')
        if 'Timeline' not in title and 'Milestone' not in title:
            ax.set_ylabel('Tasks', fontsize=11, fontweight='bold', color='#212121')
            ax.tick_params(axis='y', labelsize=9, colors='#424242')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20, color='#1A237E')
        ax.set_axisbelow(True)
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64

# User-specific generator storage
user_generators = {}

def get_user_generator():
    """Get or create a generator for the current user based on session ID"""
    # Use session ID or create a unique user identifier
    if 'user_id' not in session:
        import uuid
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    
    # Create generator if it doesn't exist for this user
    if user_id not in user_generators:
        generator = GanttChartGenerator()
        # Don't add sample tasks - let users start fresh
        user_generators[user_id] = generator
    
    return user_generators[user_id]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/verify_api_key', methods=['POST'])
def verify_api_key():
    try:
        data = request.json
        api_key = data.get('api_key', '')
        
        if not api_key:
            return jsonify({'success': False, 'error': 'API key is required'}), 400
        
        # Verify the Gemini API key
        if verify_gemini_key(api_key):
            session['authenticated'] = True
            session['api_key'] = api_key
            return jsonify({'success': True, 'message': 'Gemini API key verified successfully'})
        else:
            return jsonify({'success': False, 'error': 'Invalid Gemini API key. Please verify your key at https://aistudio.google.com/app/apikey'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/logout', methods=['POST'])
def logout():
    # Remove user's data when logging out
    if 'user_id' in session:
        user_id = session['user_id']
        if user_id in user_generators:
            del user_generators[user_id]
    session.clear()
    return jsonify({'success': True})

@app.route('/add_task', methods=['POST'])
@require_api_key
def add_task():
    try:
        generator = get_user_generator()
        data = request.json
        start_time = data.get('start_time', '00:00')
        task = generator.add_task(data['name'], data['start_date'], data['duration'], start_time)
        return jsonify({
            'success': True,
            'task': {
                'name': task['name'],
                'start': task['start'].strftime('%Y-%m-%d'),
                'time': task['start'].strftime('%H:%M'),
                'duration': task['duration_str']
            },
            'task_count': len(generator.tasks)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/generate_chart', methods=['POST'])
@require_api_key
def generate_chart():
    try:
        generator = get_user_generator()
        data = request.json
        chart_type = data.get('chart_type', 'standard')
        color_scheme = data.get('color_scheme', 'corporate')
        img_base64 = generator.generate_chart(chart_type, color_scheme)
        
        if img_base64:
            return jsonify({'success': True, 'image': img_base64})
        else:
            return jsonify({'success': False, 'error': 'No tasks to display'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/get_tasks', methods=['GET'])
@require_api_key
def get_tasks():
    generator = get_user_generator()
    tasks = [{
        'name': t['name'],
        'start': t['start'].strftime('%Y-%m-%d'),
        'time': t['start'].strftime('%H:%M'),
        'duration': t['duration_str']
    } for t in generator.tasks]
    return jsonify({'tasks': tasks})

@app.route('/update_task/<int:index>', methods=['PUT'])
@require_api_key
def update_task(index):
    try:
        generator = get_user_generator()
        if 0 <= index < len(generator.tasks):
            data = request.json
            name = data.get('name')
            start_date_str = data.get('start_date')
            start_time_str = data.get('start_time', '00:00')
            duration_str = data.get('duration')
            
            if not name or not start_date_str or not duration_str:
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            # Parse date and time
            datetime_str = f"{start_date_str} {start_time_str}"
            start_date = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            total_hours, formatted_duration = generator.parse_duration(duration_str)
            end_date = start_date + timedelta(hours=total_hours)
            
            # Update the task
            generator.tasks[index] = {
                'name': name,
                'start': start_date,
                'duration_hours': total_hours,
                'duration_str': formatted_duration,
                'end': end_date
            }
            
            # Recalculate sequence for all subsequent tasks if in progressive mode
            updated_count = 1
            if generator.progressive_mode and index < len(generator.tasks) - 1:
                sequence_updates = generator.recalculate_sequence(index + 1)
                updated_count += sequence_updates
            
            return jsonify({
                'success': True,
                'task': {
                    'name': name,
                    'start': start_date.strftime('%Y-%m-%d'),
                    'time': start_date.strftime('%H:%M'),
                    'duration': formatted_duration
                },
                'updated_count': updated_count
            })
        return jsonify({'success': False, 'error': 'Invalid task index'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/remove_task/<int:index>', methods=['DELETE'])
@require_api_key
def remove_task(index):
    try:
        generator = get_user_generator()
        if 0 <= index < len(generator.tasks):
            generator.tasks.pop(index)
            
            # Recalculate sequence for remaining tasks if in progressive mode
            updated_count = 0
            if generator.progressive_mode and index < len(generator.tasks):
                updated_count = generator.recalculate_sequence(index)
            
            return jsonify({
                'success': True, 
                'task_count': len(generator.tasks),
                'updated_count': updated_count
            })
        return jsonify({'success': False, 'error': 'Invalid index'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/clear_tasks', methods=['POST'])
@require_api_key
def clear_tasks():
    generator = get_user_generator()
    generator.tasks.clear()
    return jsonify({'success': True})

@app.route('/get_progressive_mode', methods=['GET'])
@require_api_key
def get_progressive_mode():
    generator = get_user_generator()
    return jsonify({'progressive_mode': generator.progressive_mode})

@app.route('/toggle_progressive_mode', methods=['POST'])
@require_api_key
def toggle_progressive_mode():
    generator = get_user_generator()
    generator.progressive_mode = not generator.progressive_mode
    
    # If turning ON progressive mode, recalculate all task sequences
    updated_count = 0
    if generator.progressive_mode and len(generator.tasks) > 1:
        updated_count = generator.recalculate_sequence(1)
    
    return jsonify({
        'success': True,
        'progressive_mode': generator.progressive_mode,
        'updated_count': updated_count
    })

@app.route('/download_chart', methods=['POST'])
@require_api_key
def download_chart():
    """Generate and download chart as PNG file"""
    try:
        generator = get_user_generator()
        data = request.json
        chart_type = data.get('chart_type', 'standard')
        color_scheme = data.get('color_scheme', 'corporate')
        if not generator.tasks:
            return jsonify({'success': False, 'error': 'No tasks to generate chart'}), 400
        
        img_base64 = generator.generate_chart(chart_type, color_scheme)
        filename = f'gantt_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        img_data = base64.b64decode(img_base64)
        with open(filepath, 'wb') as f:
            f.write(img_data)
        
        return jsonify({'success': True, 'filename': filename, 'download_url': f'/download/{filename}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/download/<filename>')
def download_file(filename):
    """Serve the download file"""
    return send_from_directory(DOWNLOADS_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    import os
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    
    # Get port from environment variable (for deployment) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print("\n" + "="*60)
    print("🚀 Gantt Chart Generator - Mobile App")
    print("="*60)
    print("\n📱 Access from mobile:")
    print(f"   http://YOUR_PHONE_IP:{port}")
    print("\n💻 Access from desktop:")
    print(f"   http://localhost:{port}")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
