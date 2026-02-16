import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GanttChartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gantt Chart Generator")
        self.root.geometry("1200x800")
        
        self.tasks = []
        
        # Main container with two columns
        main_container = tk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Input form
        left_panel = tk.Frame(main_container, relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        
        # Title
        title_label = tk.Label(left_panel, text="Add New Task", font=("Arial", 14, "bold"), bg="#2196F3", fg="white", pady=10)
        title_label.pack(fill=tk.X)
        
        # Form frame
        form_frame = tk.Frame(left_panel, padx=15, pady=15)
        form_frame.pack(fill=tk.BOTH, expand=False)
        
        # Task Name
        tk.Label(form_frame, text="Task Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.task_name_entry = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.task_name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Start Date
        tk.Label(form_frame, text="Start Date:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.start_date_entry = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.start_date_entry.grid(row=1, column=1, pady=5, padx=5)
        self.start_date_entry.insert(0, "2026-02-05")
        tk.Label(form_frame, text="(YYYY-MM-DD)", font=("Arial", 8), fg="gray").grid(row=1, column=2, sticky="w")
        
        # Duration
        tk.Label(form_frame, text="Duration:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.duration_entry = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.duration_entry.grid(row=2, column=1, pady=5, padx=5)
        tk.Label(form_frame, text="(e.g., 5d, 3h, 2d 4h, 90m)", font=("Arial", 8), fg="gray").grid(row=2, column=2, sticky="w")
        
        # Buttons for task management
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=15)
        
        self.add_btn = tk.Button(button_frame, text="Add Task", command=self.add_task, 
                                bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.remove_btn = tk.Button(button_frame, text="Remove Selected", command=self.remove_task,
                                    bg="#FF9800", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5)
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Task list with scrollbar
        list_frame = tk.Frame(left_panel, padx=15)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="Task List:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Treeview for task list
        tree_scroll = tk.Scrollbar(list_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_tree = ttk.Treeview(list_frame, columns=("Name", "Start", "Duration"), 
                                      show="headings", height=10, yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.task_tree.yview)
        
        self.task_tree.heading("Name", text="Task Name")
        self.task_tree.heading("Start", text="Start Date")
        self.task_tree.heading("Duration", text="Duration")
        
        self.task_tree.column("Name", width=150)
        self.task_tree.column("Start", width=100)
        self.task_tree.column("Duration", width=80)
        
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons at bottom
        action_frame = tk.Frame(left_panel, padx=15, pady=15)
        action_frame.pack(fill=tk.X)
        
        # Progressive mode checkbox
        self.progressive_mode = tk.BooleanVar(value=True)
        progressive_cb = tk.Checkbutton(action_frame, text="Progressive Mode (Tasks Run Sequentially)", 
                                       variable=self.progressive_mode, font=("Arial", 10, "bold"),
                                       command=self.toggle_progressive_mode)
        progressive_cb.pack(anchor="w", pady=(0, 10))
        
        # Chart type selection
        tk.Label(action_frame, text="Chart Type:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.chart_type = tk.StringVar(value="standard")
        
        chart_types = [
            ("Standard Gantt", "standard"),
            ("Timeline View", "timeline"),
            ("Milestone View", "milestone"),
            ("Compact View", "compact"),
            ("Waterfall View", "waterfall"),
            ("Progress Tracker", "progress"),
            ("Dependency View", "dependency"),
            ("Resource Allocation", "resource"),
            ("Burndown Chart", "burndown"),
            ("Calendar View", "calendar"),
            ("Kanban Board", "kanban")
        ]
        
        for text, value in chart_types:
            rb = tk.Radiobutton(action_frame, text=text, variable=self.chart_type, 
                               value=value, font=("Arial", 9))
            rb.pack(anchor="w", padx=10)
        
        self.generate_btn = tk.Button(action_frame, text="Generate Gantt Chart", command=self.generate_chart,
                                      bg="#2196F3", fg="white", font=("Arial", 11, "bold"), padx=20, pady=8)
        self.generate_btn.pack(fill=tk.X, pady=(10, 5))
        
        self.clear_all_btn = tk.Button(action_frame, text="Clear All Tasks", command=self.clear_all,
                                       bg="#f44336", fg="white", font=("Arial", 11, "bold"), padx=20, pady=8)
        self.clear_all_btn.pack(fill=tk.X, pady=5)
        
        # Right panel - Chart display
        right_panel = tk.Frame(main_container, relief=tk.SUNKEN, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        chart_title = tk.Label(right_panel, text="Gantt Chart", font=("Arial", 14, "bold"), bg="#FF9800", fg="white", pady=10)
        chart_title.pack(fill=tk.X)
        
        self.chart_frame = tk.Frame(right_panel)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add sample tasks
        self.add_sample_tasks()
        
    def add_sample_tasks(self):
        """Add sample tasks to demonstrate the app"""
        # Progressive sample tasks - each starts after previous
        sample_tasks = [
            ("Project Planning", "2026-02-01", "5d"),
            ("Design Phase", "2026-02-06", "10d"),
            ("Development", "2026-02-16", "20d"),
            ("Testing", "2026-03-08", "1d 12h"),
            ("Deployment", "2026-03-10", "8h")
        ]
        
        for task_name, start_date, duration in sample_tasks:
            self.task_name_entry.delete(0, tk.END)
            self.task_name_entry.insert(0, task_name)
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, start_date)
            self.duration_entry.delete(0, tk.END)
            self.duration_entry.insert(0, duration)
            self.add_task()
    
    def parse_duration(self, duration_str):
        """Parse duration string and return total hours and formatted string"""
        import re
        
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
    
    def toggle_progressive_mode(self):
        """Handle progressive mode toggle"""
        if self.progressive_mode.get() and self.tasks:
            # Recalculate all task dates to be sequential
            self.make_tasks_progressive()
    
    def make_tasks_progressive(self):
        """Recalculate task start dates to be sequential"""
        if not self.tasks:
            return
        
        # Keep first task's start date, adjust all others
        for i in range(1, len(self.tasks)):
            prev_task = self.tasks[i-1]
            self.tasks[i]['start'] = prev_task['end']
            self.tasks[i]['end'] = self.tasks[i]['start'] + timedelta(hours=self.tasks[i]['duration_hours'])
        
        # Update treeview
        self.refresh_treeview()
    
    def refresh_treeview(self):
        """Refresh the treeview with current task data"""
        # Clear treeview
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Repopulate
        for task in self.tasks:
            self.task_tree.insert("", tk.END, values=(
                task['name'], 
                task['start'].strftime('%Y-%m-%d'), 
                task['duration_str']
            ))
    
    def add_task(self):
        """Add a task to the list"""
        task_name = self.task_name_entry.get().strip()
        start_date_str = self.start_date_entry.get().strip()
        duration_str = self.duration_entry.get().strip()
        
        # Validation
        if not task_name:
            messagebox.showwarning("Input Error", "Please enter a task name.")
            return
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Date Error", "Invalid date format. Use YYYY-MM-DD.")
            return
        
        try:
            total_hours, formatted_duration = self.parse_duration(duration_str)
        except (ValueError, AttributeError):
            messagebox.showerror("Duration Error", 
                               "Invalid duration format. Use format like: 5d, 3h, 2d 4h, 90m")
            return
        
        # If progressive mode is on and there are existing tasks, start after the last task
        if self.progressive_mode.get() and self.tasks:
            last_task = self.tasks[-1]
            start_date = last_task['end']
            start_date_str = start_date.strftime('%Y-%m-%d')
            # Update the entry field to show the calculated date
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, start_date_str)
        
        # Add to task list
        end_date = start_date + timedelta(hours=total_hours)
        task = {
            'name': task_name,
            'start': start_date,
            'duration_hours': total_hours,
            'duration_str': formatted_duration,
            'end': end_date
        }
        self.tasks.append(task)
        
        # Add to treeview
        self.task_tree.insert("", tk.END, values=(task_name, start_date_str, formatted_duration))
        
        # Clear input fields
        self.task_name_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)
    
    def remove_task(self):
        """Remove selected task from the list"""
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a task to remove.")
            return
        
        # Get index and remove
        index = self.task_tree.index(selected_item[0])
        self.task_tree.delete(selected_item[0])
        self.tasks.pop(index)
    
    def clear_all(self):
        """Clear all tasks"""
        if not self.tasks:
            return
        
        response = messagebox.askyesno("Confirm", "Are you sure you want to clear all tasks?")
        if response:
            self.tasks.clear()
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)
            
            # Clear chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
    
    def generate_chart(self):
        """Generate and display the Gantt chart"""
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        try:
            if not self.tasks:
                messagebox.showwarning("No Tasks", "Please add at least one task.")
                return
            
            chart_type = self.chart_type.get()
            
            if chart_type == "standard":
                self.generate_standard_chart()
            elif chart_type == "timeline":
                self.generate_timeline_chart()
            elif chart_type == "milestone":
                self.generate_milestone_chart()
            elif chart_type == "compact":
                self.generate_compact_chart()
            elif chart_type == "waterfall":
                self.generate_waterfall_chart()
            elif chart_type == "progress":
                self.generate_progress_tracker_chart()
            elif chart_type == "dependency":
                self.generate_dependency_chart()
            elif chart_type == "resource":
                self.generate_resource_chart()
            elif chart_type == "burndown":
                self.generate_burndown_chart()
            elif chart_type == "calendar":
                self.generate_calendar_chart()
            elif chart_type == "kanban":
                self.generate_kanban_chart()
            
            messagebox.showinfo("Success", "Gantt chart generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def generate_standard_chart(self):
        """Generate standard Gantt chart"""
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # Colors for different tasks
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                 '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788']
        
        # Plot each task
        for idx, task in enumerate(self.tasks):
            color = colors[idx % len(colors)]
            duration_days = task['duration_hours'] / 24
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.5, color=color, edgecolor='black', linewidth=1.5, alpha=0.8)
            
            # Add duration label
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, task['duration_str'], 
                   ha='center', va='center', fontweight='bold', fontsize=9, 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        ax.invert_yaxis()
        self._format_and_display_chart(ax, fig, 'Standard Gantt Chart')
    
    def generate_timeline_chart(self):
        """Generate timeline view with dates"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            # Single color scheme for timeline
            ax.barh(idx, duration_days, left=task['start'], 
                   height=0.3, color='#3498db', edgecolor='#2c3e50', linewidth=2, alpha=0.7)
            
            # Add task name inside bar
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, task['name'], 
                   ha='center', va='center', fontweight='bold', fontsize=8, color='white')
            
            # Add start and end dates
            ax.text(task['start'], idx, task['start'].strftime('%m/%d'), 
                   ha='right', va='center', fontsize=7, color='black', 
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.5))
            ax.text(task['end'], idx, task['end'].strftime('%m/%d'), 
                   ha='left', va='center', fontsize=7, color='black',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='lightgreen', alpha=0.5))
        
        ax.set_yticks([])
        self._format_and_display_chart(ax, fig, 'Timeline View')
    
    def generate_milestone_chart(self):
        """Generate milestone chart with markers"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        
        for idx, task in enumerate(self.tasks):
            # Start marker
            ax.plot(task['start'], idx, marker='o', markersize=12, 
                   color=colors[idx % len(colors)], zorder=3)
            
            # End marker (diamond)
            ax.plot(task['end'], idx, marker='D', markersize=12, 
                   color=colors[idx % len(colors)], zorder=3)
            
            # Connecting line
            ax.plot([task['start'], task['end']], [idx, idx], 
                   color=colors[idx % len(colors)], linewidth=3, alpha=0.5)
            
            # Task name
            mid_point = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(mid_point, idx - 0.15, task['name'], 
                   ha='center', fontsize=9, fontweight='bold')
            
            # Duration below
            ax.text(mid_point, idx + 0.15, task['duration_str'], 
                   ha='center', fontsize=7, style='italic', color='gray')
        
        ax.set_yticks([])
        self._format_and_display_chart(ax, fig, 'Milestone Chart')
    
    def generate_compact_chart(self):
        """Generate compact view"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        gradient_colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.7, color=gradient_colors[idx % len(gradient_colors)], 
                   edgecolor='white', linewidth=2, alpha=0.85)
            
            # Minimal label - just duration
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, task['duration_str'], 
                   ha='center', va='center', fontweight='bold', fontsize=8, color='white')
        
        ax.invert_yaxis()
        self._format_and_display_chart(ax, fig, 'Compact View')
    
    def generate_waterfall_chart(self):
        """Generate waterfall/cascade view"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            # Create cascading effect with transparency
            alpha = 0.4 + (idx * 0.1)
            color_intensity = 255 - (idx * 30)
            color = f'#{max(100, color_intensity - 50):02x}{max(150, color_intensity):02x}ff'
            
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.6, color=color, edgecolor='navy', linewidth=1.5, 
                   alpha=min(alpha, 0.9))
            
            # Progress indicator (assuming 50% for demo)
            progress = duration_days * 0.5
            ax.barh(task['name'], progress, left=task['start'], 
                   height=0.6, color='green', alpha=0.3)
            
            # Label with percentage
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, f"{task['duration_str']}\n(50%)", 
                   ha='center', va='center', fontweight='bold', fontsize=8)
        
        ax.invert_yaxis()
        self._format_and_display_chart(ax, fig, 'Waterfall View (with Progress)')
    
    def generate_progress_tracker_chart(self):
        """Generate progress tracker with completion percentages"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            
            # Background bar (total duration)
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.6, color='#E0E0E0', edgecolor='black', linewidth=1)
            
            # Progress bar (simulated progress based on position)
            progress_pct = min(0.3 + (idx * 0.15), 0.95)  # Simulate varying progress
            progress_days = duration_days * progress_pct
            ax.barh(task['name'], progress_days, left=task['start'], 
                   height=0.6, color=colors[idx % len(colors)], alpha=0.8)
            
            # Add percentage label
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, f"{int(progress_pct * 100)}%", 
                   ha='center', va='center', fontweight='bold', fontsize=10, 
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='black', linewidth=2))
            
            # Add status indicator
            if progress_pct >= 0.9:
                status = "✓ Complete"
                status_color = 'green'
            elif progress_pct >= 0.5:
                status = "◐ In Progress"
                status_color = 'orange'
            else:
                status = "○ Starting"
                status_color = 'red'
            
            ax.text(task['end'], idx, f"  {status}", ha='left', va='center', 
                   fontsize=8, color=status_color, fontweight='bold')
        
        ax.invert_yaxis()
        self._format_and_display_chart(ax, fig, 'Progress Tracker')
    
    def generate_dependency_chart(self):
        """Generate dependency chart showing task relationships"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        colors = ['#8E44AD', '#3498DB', '#E74C3C', '#F39C12', '#16A085']
        
        for idx, task in enumerate(self.tasks):
            duration_days = task['duration_hours'] / 24
            color = colors[idx % len(colors)]
            
            # Draw task bar
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.5, color=color, edgecolor='black', linewidth=2, alpha=0.7)
            
            # Draw dependency arrow to next task
            if idx < len(self.tasks) - 1:
                next_task = self.tasks[idx + 1]
                ax.annotate('', xy=(next_task['start'], idx + 1), 
                          xytext=(task['end'], idx),
                          arrowprops=dict(arrowstyle='->', lw=2, color='red', 
                                        connectionstyle="arc3,rad=0.3"))
                
                # Add dependency label
                mid_y = (idx + idx + 1) / 2
                ax.text(task['end'], mid_y, 'Depends', fontsize=7, 
                       style='italic', color='red', ha='center',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
            
            # Add task number
            ax.text(task['start'], idx, f" #{idx+1}", ha='right', va='center', 
                   fontsize=9, fontweight='bold', color='navy')
        
        ax.invert_yaxis()
        self._format_and_display_chart(ax, fig, 'Dependency Chain')
    
    def generate_resource_chart(self):
        """Generate resource allocation chart"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # Simulate resource types
        resources = ['Dev Team', 'QA Team', 'Design Team', 'Ops Team', 'Management']
        resource_colors = ['#3498DB', '#E74C3C', '#9B59B6', '#F39C12', '#1ABC9C']
        
        for idx, task in enumerate(self.tasks):
            resource = resources[idx % len(resources)]
            color = resource_colors[idx % len(resource_colors)]
            duration_days = task['duration_hours'] / 24
            
            # Draw bar with resource info
            ax.barh(task['name'], duration_days, left=task['start'], 
                   height=0.6, color=color, edgecolor='white', linewidth=2, alpha=0.75)
            
            # Add resource label
            label_position = task['start'] + timedelta(hours=task['duration_hours']/2)
            ax.text(label_position, idx, f"{resource}\n{task['duration_str']}", 
                   ha='center', va='center', fontweight='bold', fontsize=8, 
                   color='white', bbox=dict(boxstyle='round,pad=0.3', 
                   facecolor='black', alpha=0.5))
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=resource_colors[i], label=resources[i]) 
                          for i in range(len(resources))]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=8)
        
        ax.invert_yaxis()
        self._format_and_display_chart(ax, fig, 'Resource Allocation')
    
    def generate_burndown_chart(self):
        """Generate burndown chart showing work completion over time"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # Calculate cumulative work hours
        total_hours = sum(task['duration_hours'] for task in self.tasks)
        
        # Generate ideal burndown line
        if self.tasks:
            start_date = min(task['start'] for task in self.tasks)
            end_date = max(task['end'] for task in self.tasks)
            
            # Ideal line
            ax.plot([start_date, end_date], [total_hours, 0], 
                   'g--', linewidth=3, label='Ideal Burndown', alpha=0.7)
            
            # Actual burndown (simulated)
            dates = []
            remaining_hours = []
            current_date = start_date
            current_hours = total_hours
            
            for task in self.tasks:
                dates.append(task['start'])
                remaining_hours.append(current_hours)
                dates.append(task['end'])
                current_hours -= task['duration_hours']
                remaining_hours.append(current_hours)
            
            ax.plot(dates, remaining_hours, 'b-o', linewidth=2.5, 
                   markersize=8, label='Actual Burndown', alpha=0.8)
            
            # Fill area under actual curve
            ax.fill_between(dates, remaining_hours, alpha=0.2, color='blue')
            
            # Add task completion markers
            for idx, task in enumerate(self.tasks):
                ax.annotate(task['name'], xy=(task['end'], remaining_hours[(idx+1)*2]), 
                          xytext=(10, 10), textcoords='offset points',
                          fontsize=8, bbox=dict(boxstyle='round,pad=0.3', 
                          facecolor='yellow', alpha=0.7),
                          arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2'))
            
            ax.set_ylabel('Remaining Hours', fontsize=11, fontweight='bold')
            ax.set_title('Project Burndown Chart', fontsize=13, fontweight='bold', pad=15)
            ax.legend(loc='upper right', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
        
        # Embed the chart
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def generate_calendar_chart(self):
        """Generate calendar-style view"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # Get date range
        if self.tasks:
            all_dates = []
            for task in self.tasks:
                current = task['start']
                while current <= task['end']:
                    all_dates.append(current.date())
                    current += timedelta(days=1)
            
            unique_dates = sorted(set(all_dates))
            date_to_idx = {date: idx for idx, date in enumerate(unique_dates)}
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                     '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788']
            
            # Plot each task as blocks
            for task_idx, task in enumerate(self.tasks):
                current = task['start']
                while current <= task['end']:
                    date = current.date()
                    if date in date_to_idx:
                        day_idx = date_to_idx[date]
                        ax.barh(task['name'], 0.9, left=day_idx, 
                               height=0.8, color=colors[task_idx % len(colors)], 
                               edgecolor='white', linewidth=2, alpha=0.8)
                    current += timedelta(days=1)
                
                # Add task label
                mid_idx = date_to_idx[task['start'].date()] + \
                         (date_to_idx[task['end'].date()] - date_to_idx[task['start'].date()]) / 2
                ax.text(mid_idx, task_idx, task['duration_str'], 
                       ha='center', va='center', fontweight='bold', fontsize=8, 
                       color='white', bbox=dict(boxstyle='round,pad=0.3', 
                       facecolor='black', alpha=0.6))
            
            # Set x-axis to show dates
            ax.set_xticks(range(len(unique_dates)))
            ax.set_xticklabels([d.strftime('%m/%d') for d in unique_dates], rotation=45, ha='right')
            ax.set_xlabel('Date', fontsize=11, fontweight='bold')
            ax.set_ylabel('Tasks', fontsize=11, fontweight='bold')
            ax.set_title('Calendar View', fontsize=13, fontweight='bold', pad=15)
            ax.invert_yaxis()
            ax.grid(True, axis='x', alpha=0.3)
            
            plt.tight_layout()
        
        # Embed the chart
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def generate_kanban_chart(self):
        """Generate Kanban board style chart"""
        fig, ax = plt.subplots(figsize=(9, 6))
        
        # Define kanban columns based on progress
        columns = ['To Do', 'In Progress', 'Review', 'Done']
        col_width = 0.8
        col_positions = list(range(len(columns)))
        
        # Simulate task states
        task_states = []
        for idx in range(len(self.tasks)):
            if idx < len(self.tasks) * 0.25:
                task_states.append('Done')
            elif idx < len(self.tasks) * 0.5:
                task_states.append('Review')
            elif idx < len(self.tasks) * 0.75:
                task_states.append('In Progress')
            else:
                task_states.append('To Do')
        
        # Count tasks in each column
        col_counts = {col: 0 for col in columns}
        
        colors = ['#E74C3C', '#F39C12', '#3498DB', '#2ECC71']
        col_colors = {columns[i]: colors[i] for i in range(len(columns))}
        
        # Plot tasks in their columns
        for task_idx, task in enumerate(self.tasks):
            state = task_states[task_idx]
            col_idx = columns.index(state)
            y_pos = col_counts[state]
            
            # Draw card
            rect = plt.Rectangle((col_idx - col_width/2, y_pos), col_width, 0.8,
                                facecolor=col_colors[state], edgecolor='black', 
                                linewidth=2, alpha=0.7)
            ax.add_patch(rect)
            
            # Add task info
            ax.text(col_idx, y_pos + 0.4, f"{task['name']}\n{task['duration_str']}",
                   ha='center', va='center', fontsize=8, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            col_counts[state] += 1
        
        # Set up axes
        ax.set_xlim(-0.5, len(columns) - 0.5)
        ax.set_ylim(-0.5, max(col_counts.values()) + 0.5)
        ax.set_xticks(col_positions)
        ax.set_xticklabels(columns, fontsize=11, fontweight='bold')
        ax.set_yticks([])
        ax.set_title('Kanban Board View', fontsize=13, fontweight='bold', pad=15)
        
        # Draw column separators
        for i in range(1, len(columns)):
            ax.axvline(x=i - 0.5, color='gray', linestyle='--', linewidth=2, alpha=0.5)
        
        # Add column headers background
        for i, col in enumerate(columns):
            rect = plt.Rectangle((i - 0.5, max(col_counts.values())), 1, 0.5,
                                facecolor=col_colors[col], alpha=0.3)
            ax.add_patch(rect)
        
        ax.invert_yaxis()
        ax.grid(False)
        plt.tight_layout()
        
        # Embed the chart
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _format_and_display_chart(self, ax, fig, title):
        """Common formatting and display for all chart types"""
        # Format the chart - adjust based on task durations
        max_duration_hours = max(task['duration_hours'] for task in self.tasks)
        
        if max_duration_hours <= 48:  # Less than 2 days, show hours
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, int(max_duration_hours // 10))))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(self.tasks) // 2)))
        
        plt.xticks(rotation=45, ha='right')
        
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')
        if 'Timeline' not in title and 'Milestone' not in title:
            ax.set_ylabel('Tasks', fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
        
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        
        # Embed the chart in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def main():
    root = tk.Tk()
    app = GanttChartApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
