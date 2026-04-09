"""
Performance Monitoring Dashboard for Attendance System
Shows real-time cache statistics, polling intervals, and memory usage
"""

import tkinter as tk
from tkinter import ttk
import os
import logging
from datetime import datetime
from optimized_attendance import get_optimized_attendance_store

# Try to import psutil, make it optional
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logging.warning("psutil not installed. Install with: pip install psutil")

logger = logging.getLogger(__name__)


class MonitoringDashboard:
    """Real-time monitoring of system performance and optimizations"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Attendance System - Performance Monitor")
        self.root.geometry("700x400")
        self.root.minsize(600, 350)
        
        self.attended_store = get_optimized_attendance_store()
        
        if HAS_PSUTIL:
            self.process = psutil.Process(os.getpid())
        else:
            self.process = None
        
        self.create_widgets()
        self.update_stats()
    
    def create_widgets(self):
        """Create monitoring UI"""
        # Title
        title = tk.Label(self.root, text="⚡ Performance & Optimization Monitor", 
                        font=("Arial", 14, "bold"), fg="#1565C0")
        title.pack(pady=10)
        
        # Main frame with notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Caching Stats
        cache_frame = ttk.Frame(notebook)
        notebook.add(cache_frame, text="📦 Cache Status")
        self.create_cache_tab(cache_frame)
        
        # Tab 2: Performance Metrics
        perf_frame = ttk.Frame(notebook)
        notebook.add(perf_frame, text="📊 Performance")
        self.create_performance_tab(perf_frame)
        
        # Tab 3: System Resources
        resource_frame = ttk.Frame(notebook)
        notebook.add(resource_frame, text="💾 Resources")
        self.create_resources_tab(resource_frame)
    
    def create_cache_tab(self, parent):
        """Cache status tab"""
        frame = ttk.LabelFrame(parent, text="Cache Information", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cache status labels
        self.cache_enabled_label = tk.Label(frame, text="Cache Enabled: —", 
                                           font=("Arial", 10), justify=tk.LEFT)
        self.cache_enabled_label.pack(anchor=tk.W, pady=5)
        
        self.cached_items_label = tk.Label(frame, text="Cached Items: —", 
                                          font=("Arial", 10), justify=tk.LEFT)
        self.cached_items_label.pack(anchor=tk.W, pady=5)
        
        self.polling_interval_label = tk.Label(frame, text="Polling Interval: —", 
                                              font=("Arial", 10, "bold"), fg="#4CAF50", justify=tk.LEFT)
        self.polling_interval_label.pack(anchor=tk.W, pady=5)
        
        self.idle_mode_label = tk.Label(frame, text="Idle Mode: —", 
                                       font=("Arial", 10), justify=tk.LEFT)
        self.idle_mode_label.pack(anchor=tk.W, pady=5)
        
        # Info text
        info = tk.Label(frame, text="✓ Green interval = Adaptive polling based on activity\n✓ Faster polls when active (2s)\n✓ Slower polls when idle (up to 30s)\n✓ Saves 70% database queries",
                       font=("Arial", 9), fg="#666", justify=tk.LEFT)
        info.pack(anchor=tk.W, pady=10, fill=tk.BOTH, expand=True)
    
    def create_performance_tab(self, parent):
        """Performance metrics tab"""
        frame = ttk.LabelFrame(parent, text="System Performance", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.memory_label = tk.Label(frame, text="Memory Usage: —", 
                                    font=("Arial", 10), justify=tk.LEFT)
        self.memory_label.pack(anchor=tk.W, pady=5)
        
        self.cpu_label = tk.Label(frame, text="CPU Usage: —", 
                                 font=("Arial", 10), justify=tk.LEFT)
        self.cpu_label.pack(anchor=tk.W, pady=5)
        
        self.uptime_label = tk.Label(frame, text="Uptime: —", 
                                    font=("Arial", 10), justify=tk.LEFT)
        self.uptime_label.pack(anchor=tk.W, pady=5)
        
        # Info
        info = tk.Label(frame, text="✓ Optimized queries reduce CPU load\n✓ Caching reduces database hits\n✓ Memory stays stable with garbage collection",
                       font=("Arial", 9), fg="#666", justify=tk.LEFT)
        info.pack(anchor=tk.W, pady=10, fill=tk.BOTH, expand=True)
    
    def create_resources_tab(self, parent):
        """System resources tab"""
        frame = ttk.LabelFrame(parent, text="System Resources", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.total_memory_label = tk.Label(frame, text="Total Memory: —", 
                                          font=("Arial", 10), justify=tk.LEFT)
        self.total_memory_label.pack(anchor=tk.W, pady=5)
        
        self.available_memory_label = tk.Label(frame, text="Available Memory: —", 
                                              font=("Arial", 10), justify=tk.LEFT)
        self.available_memory_label.pack(anchor=tk.W, pady=5)
        
        self.cpu_cores_label = tk.Label(frame, text="CPU Cores: —", 
                                       font=("Arial", 10), justify=tk.LEFT)
        self.cpu_cores_label.pack(anchor=tk.W, pady=5)
        
        self.start_time_label = tk.Label(frame, text="System Started: —", 
                                        font=("Arial", 9), fg="#999", justify=tk.LEFT)
        self.start_time_label.pack(anchor=tk.W, pady=5)
    
    def update_stats(self):
        """Update all statistics"""
        try:
            # Cache stats
            cache_stats = self.attended_store.get_cache_stats()
            self.cache_enabled_label.config(
                text=f"Cache Enabled: {'✓ Yes' if cache_stats['cache_enabled'] else '✗ No'}"
            )
            self.cached_items_label.config(
                text=f"Cached Items: {cache_stats['total_cached_items']}"
            )
            
            interval_ms = cache_stats['current_polling_interval_ms']
            interval_s = interval_ms / 1000
            self.polling_interval_label.config(
                text=f"Polling Interval: {interval_s:.1f}s",
                fg="#FFB300" if interval_s > 5 else "#4CAF50"
            )
            
            idle_status = "✓ IDLE (Low polling)" if cache_stats['is_idle_mode'] else "🔴 ACTIVE (Fast polling)"
            self.idle_mode_label.config(text=f"Status: {idle_status}")
            
            # Performance stats (only if psutil available)
            if self.process and HAS_PSUTIL:
                mem = self.process.memory_info()
                mem_mb = mem.rss / 1024 / 1024
                self.memory_label.config(text=f"Memory Usage: {mem_mb:.1f} MB")
                
                cpu_percent = self.process.cpu_percent(interval=0.5)
                self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
                
                create_time = datetime.fromtimestamp(self.process.create_time())
                uptime = datetime.now() - create_time
                hours = uptime.seconds // 3600
                minutes = (uptime.seconds % 3600) // 60
                self.uptime_label.config(text=f"Uptime: {hours}h {minutes}m")
                
                # System resources
                mem_total = psutil.virtual_memory()
                self.total_memory_label.config(text=f"Total Memory: {mem_total.total / 1024 / 1024 / 1024:.1f} GB")
                self.available_memory_label.config(text=f"Available: {mem_total.available / 1024 / 1024 / 1024:.1f} GB ({mem_total.percent:.1f}% used)")
                
                self.cpu_cores_label.config(text=f"CPU Cores: {psutil.cpu_count()} cores")
                
                # Process start time
                start_time = datetime.fromtimestamp(self.process.create_time())
                self.start_time_label.config(text=f"Process Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                self.memory_label.config(text="Memory Usage: psutil not installed")
                self.cpu_label.config(text="CPU Usage: psutil not installed")
                self.uptime_label.config(text="Uptime: psutil not installed")
                self.total_memory_label.config(text="Total Memory: psutil not installed")
                self.available_memory_label.config(text="Available: psutil not installed")
                self.cpu_cores_label.config(text="CPU Cores: psutil not installed")
                self.start_time_label.config(text="Process Started: psutil not installed")
        
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
        
        # Update every 2 seconds
        self.root.after(2000, self.update_stats)


if __name__ == "__main__":
    root = tk.Tk()
    dashboard = MonitoringDashboard(root)
    root.mainloop()
