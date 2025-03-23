"""
YouTube Monitor for Samsung TV

This script integrates all modules to monitor YouTube content on a Samsung TV,
track watch time, and provide audio alerts when limits are exceeded.
"""

import os
import time
import json
import logging
from datetime import datetime

# Import custom modules
from tv_connection import TVConnection
from youtube_handler import YouTubeHandler
from theme_analyzer import ThemeAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Monitor")

class YouTubeMonitor:
    def __init__(self):
        """Initialize all components of the monitoring system."""
        # Create logs directory
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Set up file handler for logging
        file_handler = logging.FileHandler(os.path.join(self.logs_dir, "monitor.log"))
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        logger.info("Initializing YouTube Monitor...")
        
        # Initialize components
        logger.info("Initializing TV connection...")
        self.tv = TVConnection()
        
        logger.info("Initializing YouTube handler...")
        self.youtube = YouTubeHandler()
        
        logger.info("Initializing theme analyzer...")
        self.analyzer = ThemeAnalyzer()
        
        # Monitoring state
        self.current_video_id = None
        self.session_start = datetime.now()
        
        # Stats tracking
        self.videos_detected = 0
        self.alerts_triggered = 0
    
    def on_new_video(self, video_id, app_info):
        """
        Handle new video detection.
        
        Args:
            video_id (str): YouTube video ID
            app_info (dict): App information from TV
        """
        logger.info(f"New video detected: {video_id}")
        
        # End previous video if any
        if self.current_video_id:
            self.on_video_ended()
        
        # Record video start
        video_details = self.youtube.record_video_start(video_id)
        self.current_video_id = video_id
        
        # Update stats
        self.videos_detected += 1
        
        # Log details
        if video_details:
            logger.info(f"Now watching: \"{video_details['title']}\"")
            logger.info(f"Channel: {video_details['channel']}")
            logger.info(f"Category: {self.analyzer.get_category_name(video_details['category_id'])}")
            
            # Print to console
            print(f"\nNow watching: \"{video_details['title']}\"")
            print(f"Channel: {video_details['channel']}")
            print(f"Category: {self.analyzer.get_category_name(video_details['category_id'])}")
    
    def on_video_ended(self):
        """Handle video end event."""
        if not self.current_video_id:
            return
        
        # Record video end and get duration
        result = self.youtube.record_video_end()
        self.current_video_id = None
        
        if result:
            video = result["video"]
            duration = result["duration_seconds"]
            
            logger.info(f"Video ended: \"{video['title']}\"")
            logger.info(f"Watched for {duration:.2f} seconds")
            
            # Check if any time limits were exceeded
            alerts = self.analyzer.check_time_limits(video, duration)
            
            if alerts:
                logger.warning(f"Time limit alerts triggered: {len(alerts)}")
                self.alerts_triggered += len(alerts)
                
                # Play audio alerts
                self.analyzer.play_alerts(alerts)
    
    def print_stats(self):
        """Print monitoring statistics."""
        now = datetime.now()
        session_duration = (now - self.session_start).total_seconds()
        
        print("\n")
        print("=" * 60)
        print(" YOUTUBE MONITOR SESSION STATISTICS ".center(60, "="))
        print("=" * 60)
        
        # Session stats
        print(f"Session duration: {self._format_time(session_duration)}")
        print(f"Videos detected: {self.videos_detected}")
        print(f"Time limit alerts: {self.alerts_triggered}")
        
        # Get detailed watch stats
        stats = self.analyzer.get_stats_report()
        
        if "error" not in stats:
            # Print daily/weekly usage
            print("\nWatch Time Summary:")
            print(f"  Today: {stats['daily']['formatted']} / {self._format_time(stats['daily']['limit'])} " +
                  f"({stats['daily']['percent']:.1f}%)")
            print(f"  This week: {stats['weekly']['formatted']} / {self._format_time(stats['weekly']['limit'])} " +
                 f"({stats['weekly']['percent']:.1f}%)")
            print(f"  All time: {stats['total_time']['all_time_formatted']}")
            
            # Top categories
            print("\nTop Categories:")
            for category in stats["categories"][:5]:  # Top 5 categories
                daily_limit = category['daily']['limit']
                limit_str = f" / {self._format_time(daily_limit)}" if daily_limit > 0 else ""
                
                print(f"  {category['name']}: {category['daily']['formatted']}{limit_str} " +
                      f"(Videos: {category['video_count']})")
        
        print("=" * 60)
    
    def _format_time(self, seconds):
        """Format seconds as a readable time string."""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        
        minutes, seconds = divmod(seconds, 60)
        if minutes < 60:
            return f"{int(minutes)} minutes"
        
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours)}h {int(minutes)}m"
    
    def start_monitoring(self):
        """Start monitoring for YouTube videos."""
        logger.info("Starting YouTube monitoring...")
        
        try:
            # Print welcome message
            print("\n" + "=" * 60)
            print(" SAMSUNG TV YOUTUBE MONITOR ".center(60, "="))
            print("=" * 60)
            print("\nMonitoring for YouTube videos on your TV...")
            print("Press Ctrl+C to stop monitoring and view statistics\n")
            
            # Start monitoring
            self.tv.monitor_continuously(callback=self.on_new_video)
            
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            
            # If a video was playing, record it as ended
            if self.current_video_id:
                self.on_video_ended()
            
            # Print statistics
            self.print_stats()
            
        except Exception as e:
            logger.error(f"Error during monitoring: {e}")
            # If a video was playing, record it as ended
            if self.current_video_id:
                self.on_video_ended()
            raise

# Run the monitor if executed directly
if __name__ == "__main__":
    monitor = YouTubeMonitor()
    monitor.start_monitoring()
