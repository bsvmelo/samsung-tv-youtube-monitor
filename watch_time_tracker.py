"""
Watch Time Tracker Module

This module tracks watch time per theme, checks against limits,
and triggers audio notifications when thresholds are exceeded.
"""

import os
import json
import time
from datetime import datetime, timedelta
import pyttsx3

class WatchTimeTracker:
    def __init__(self, config_file="config.json"):
        """Initialize watch time tracker with config values."""
        # Load configuration
        with open(config_file, "r") as f:
            self.config = json.load(f)
        
        self.watch_time_limits = self.config["watch_time_limits"]
        self.logs_dir = self.config["system"]["logs_dir"]
        self.reset_interval = self.config["system"]["reset_interval"]
        
        # Create logs directory if it doesn't exist
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Watch time log file
        self.watch_log_file = os.path.join(self.logs_dir, "watch_time.json")
        
        # Last reset timestamp file
        self.reset_file = os.path.join(self.logs_dir, "last_reset.txt")
        
        # Load existing watch time data or create new
        self.load_watch_time()
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
    
    def load_watch_time(self):
        """Load watch time data from log file."""
        # Check if we need to reset first
        self.check_reset_needed()
        
        try:
            if os.path.exists(self.watch_log_file):
                with open(self.watch_log_file, "r") as f:
                    self.watch_time = json.load(f)
            else:
                self.watch_time = {}
        except Exception as e:
            print(f"Error loading watch time data: {e}")
            self.watch_time = {}
    
    def save_watch_time(self):
        """Save watch time data to log file."""
        try:
            with open(self.watch_log_file, "w") as f:
                json.dump(self.watch_time, f, indent=4)
        except Exception as e:
            print(f"Error saving watch time data: {e}")
    
    def check_reset_needed(self):
        """Check if watch time should be reset based on reset interval."""
        try:
            now = datetime.now()
            
            # Get last reset time
            if os.path.exists(self.reset_file):
                with open(self.reset_file, "r") as f:
                    last_reset_str = f.read().strip()
                    last_reset = datetime.fromisoformat(last_reset_str)
            else:
                # If no reset file, create one and return (no reset needed)
                with open(self.reset_file, "w") as f:
                    f.write(now.isoformat())
                return
            
            # Check if reset is needed based on interval
            if self.reset_interval == "daily":
                # Reset if it's a new day
                if now.date() > last_reset.date():
                    self.reset_watch_time()
                    with open(self.reset_file, "w") as f:
                        f.write(now.isoformat())
            
            elif self.reset_interval == "weekly":
                # Reset if it's been a week
                if now - last_reset >= timedelta(days=7):
                    self.reset_watch_time()
                    with open(self.reset_file, "w") as f:
                        f.write(now.isoformat())
            
            # Add more intervals as needed
        
        except Exception as e:
            print(f"Error checking reset interval: {e}")
    
    def reset_watch_time(self):
        """Reset all watch time data."""
        print(f"Resetting watch time data ({self.reset_interval} reset)")
        self.watch_time = {}
        self.save_watch_time()
    
    def update_watch_time(self, theme, duration_seconds):
        """
        Update watch time for a theme and check against limits.
        
        Args:
            theme: Video theme category
            duration_seconds: Watch duration in seconds
        """
        if not theme:
            return
        
        # Initialize theme if not exists
        if theme not in self.watch_time:
            self.watch_time[theme] = 0
        
        # Update watch time
        self.watch_time[theme] += duration_seconds
        
        print(f"Updated watch time for '{theme}': {self.format_time(self.watch_time[theme])}")
        
        # Save updated data
        self.save_watch_time()
        
        # Check if limit exceeded
        if theme in self.watch_time_limits:
            limit = self.watch_time_limits[theme]
            if self.watch_time[theme] > limit and self.watch_time[theme] - duration_seconds <= limit:
                # Only alert if this update caused the threshold to be crossed
                self.alert_user(theme)
    
    def format_time(self, seconds):
        """Format seconds as hours:minutes:seconds."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def alert_user(self, theme):
        """
        Send an audio alert when watch time exceeds the limit.
        
        Args:
            theme: Theme that exceeded the limit
        """
        limit_formatted = self.format_time(self.watch_time_limits[theme])
        alert_message = f"Alert! You have exceeded your {limit_formatted} watch time limit for {theme} videos!"
        
        print("\n" + "!" * 50)
        print(alert_message)
        print("!" * 50 + "\n")
        
        try:
            # Set voice properties
            self.tts_engine.setProperty('rate', 150)  # Adjust speed (150 words per minute)
            self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Speak the alert
            self.tts_engine.say(alert_message)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error generating audio alert: {e}")
    
    def get_theme_statistics(self):
        """Get statistics about watch time for all themes."""
        stats = {
            "total_watch_time": sum(self.watch_time.values()),
            "themes": {}
        }
        
        # Add data for each theme
        for theme, seconds in self.watch_time.items():
            limit = self.watch_time_limits.get(theme, float("inf"))
            percentage = (seconds / limit * 100) if limit != float("inf") else 0
            
            stats["themes"][theme] = {
                "watch_time": seconds,
                "formatted_time": self.format_time(seconds),
                "limit": limit if limit != float("inf") else None,
                "percentage_of_limit": round(percentage, 1),
                "exceeded": seconds > limit
            }
        
        return stats

# Test module if run directly
if __name__ == "__main__":
    tracker = WatchTimeTracker()
    
    # Test with sample data
    tracker.update_watch_time("baseball", 300)  # 5 minutes
    tracker.update_watch_time("gaming", 600)    # 10 minutes
    
    # Print statistics
    stats = tracker.get_theme_statistics()
    print("\nWatch Time Statistics:")
    print(f"Total watch time: {tracker.format_time(stats['total_watch_time'])}")
    
    for theme, data in stats["themes"].items():
        limit_str = f"/{tracker.format_time(data['limit'])}" if data['limit'] else ""
        print(f"  {theme}: {data['formatted_time']}{limit_str} ({data['percentage_of_limit']}%)")