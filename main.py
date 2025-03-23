"""
Samsung TV YouTube Monitor - Main Controller

This script integrates all modules to monitor YouTube content on a Samsung TV,
classify videos by theme, track watch time, and provide audio alerts when limits are exceeded.
"""

import os
import time
import json
from datetime import datetime

# Import custom modules
from tv_connection import TVConnection
from youtube_data import YouTubeData
from theme_classifier import ThemeClassifier
from watch_time_tracker import WatchTimeTracker
from config_loader import load_config

class YouTubeMonitor:
    def __init__(self, config_file="config.json"):
        """Initialize all components of the monitoring system."""
        # Load config with environment variable overrides
        self.config = load_config(config_file)
        
        # Initialize components
        print("Initializing TV connection...")
        self.tv = TVConnection(config_file)
        
        print("Initializing YouTube data handler...")
        self.youtube = YouTubeData(config_file)
        
        print("Initializing theme classifier...")
        self.classifier = ThemeClassifier(config_file)
        
        print("Initializing watch time tracker...")
        self.tracker = WatchTimeTracker(config_file)
        
        # Monitoring state
        self.current_video_id = None
        self.video_start_time = None
        self.polling_interval = self.config["tv"]["polling_interval"]
        
        # Create logs directory
        self.logs_dir = self.config["system"]["logs_dir"]
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Initialize session log
        self.session_log_file = os.path.join(self.logs_dir, "session.log")
        self.log_message("Session started")
    
    def log_message(self, message):
        """Log a message with timestamp to the session log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        print(log_entry)
        
        try:
            with open(self.session_log_file, "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Error writing to session log: {e}")
    
    def calculate_duration(self, start_time):
        """Calculate duration in seconds from start_time to now."""
        if not start_time:
            return 0
        
        now = datetime.now()
        return (now - start_time).total_seconds()
    
    def start_monitoring(self):
        """Main monitoring loop to detect and process YouTube videos."""
        self.log_message("Starting YouTube monitoring...")
        
        try:
            while True:
                # Get current video ID
                video_id = self.tv.get_current_video_id()
                
                # New video detected
                if video_id and video_id != self.current_video_id:
                    self.process_new_video(video_id)
                
                # Previous video ended (no video currently playing)
                elif not video_id and self.current_video_id:
                    self.process_video_ended()
                
                # Wait before next check
                time.sleep(self.polling_interval)
        
        except KeyboardInterrupt:
            self.log_message("Monitoring stopped by user")
            # Process last video if any
            if self.current_video_id:
                self.process_video_ended()
        
        except Exception as e:
            self.log_message(f"Error in monitoring loop: {e}")
            # Process last video if any
            if self.current_video_id:
                self.process_video_ended()
    
    def process_new_video(self, video_id):
        """Process a newly detected video."""
        # First, end previous video if any
        if self.current_video_id:
            self.process_video_ended()
        
        # Log new video
        self.log_message(f"New video detected: {video_id}")
        
        # Fetch video details
        video_data = self.youtube.fetch_video_details(video_id)
        
        if video_data:
            # Classify video theme
            theme = self.classifier.classify_video_theme(
                video_data["title"], 
                video_data["description"]
            )
            
            # Add theme to video data
            video_data["theme"] = theme
            
            # Log video data
            self.youtube.log_video_data(video_data)
            
            # Update state
            self.current_video_id = video_id
            self.video_start_time = datetime.now()
            
            # Log detection
            self.log_message(f"Now watching: \"{video_data['title']}\" (Theme: {theme})")
        else:
            self.log_message(f"Failed to fetch details for video: {video_id}")
    
    def process_video_ended(self):
        """Process the end of the current video."""
        if not self.current_video_id or not self.video_start_time:
            return
        
        # Calculate watch duration
        duration = self.calculate_duration(self.video_start_time)
        
        # Update video end time in log
        self.youtube.update_video_end_time(self.current_video_id)
        
        # Get video theme from logs
        video_theme = None
        try:
            with open(self.youtube.video_log_file, "r") as f:
                logs = json.load(f)
                if self.current_video_id in logs:
                    video_theme = logs[self.current_video_id]["theme"]
        except Exception as e:
            self.log_message(f"Error retrieving video theme: {e}")
        
        # Update watch time for theme
        if video_theme:
            self.tracker.update_watch_time(video_theme, duration)
            
            self.log_message(
                f"Video ended: {self.current_video_id} - " +
                f"Watched for {self.tracker.format_time(duration)} - " +
                f"Theme: {video_theme}"
            )
        
        # Reset state
        self.current_video_id = None
        self.video_start_time = None
    
    def print_statistics(self):
        """Print current watch time statistics."""
        stats = self.tracker.get_theme_statistics()
        
        print("\n" + "=" * 50)
        print(f"WATCH TIME STATISTICS")
        print("=" * 50)
        
        print(f"Total watch time: {self.tracker.format_time(stats['total_watch_time'])}")
        print("\nWatch time by theme:")
        
        for theme, data in stats["themes"].items():
            limit_str = f"/{self.tracker.format_time(data['limit'])}" if data['limit'] else ""
            status = "EXCEEDED" if data["exceeded"] else f"{data['percentage_of_limit']}%"
            print(f"  {theme}: {data['formatted_time']}{limit_str} ({status})")
        
        print("=" * 50 + "\n")

# Run the monitor if executed directly
if __name__ == "__main__":
    monitor = YouTubeMonitor()
    
    try:
        # Print instructions
        print("\n" + "*" * 60)
        print("SAMSUNG TV YOUTUBE MONITOR".center(60))
        print("*" * 60)
        print("\nPress Ctrl+C to stop monitoring and view statistics\n")
        
        # Start monitoring
        monitor.start_monitoring()
    
    except KeyboardInterrupt:
        # Print statistics before exit
        monitor.print_statistics()