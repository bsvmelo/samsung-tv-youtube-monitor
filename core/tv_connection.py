"""
Samsung TV Connection Module - Enhanced for Samsung The Frame TVs

This module connects to a Samsung The Frame TV and attempts to detect YouTube videos.
"""

import os
import json
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from samsungtvws import SamsungTVWS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SamsungTV")

# Add file handler
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/tv_connection.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class TVConnection:
    def __init__(self):
        """Initialize connection with Samsung TV using environment variables."""
        # Load environment variables
        load_dotenv()
        
        # Get TV IP from environment
        self.tv_ip = os.getenv("TV_IP")
        self.token_file = os.getenv("TOKEN_FILE", "tv_token.txt")
        self.polling_interval = int(os.getenv("POLLING_INTERVAL", "5"))  # Default 5 seconds
        
        # Initialize connection
        self.tv = None
        self.is_connected = False
        self.current_app = None
        self.power_state = False
        
        # Initialize state tracking
        self.last_check_time = datetime.now()
        self.last_status = {
            "app": None,
            "power": False
        }
        
        # Connect to TV
        self.connect()
    
    def connect(self):
        """Establish connection to the Samsung TV."""
        try:
            logger.info(f"Connecting to Samsung TV at {self.tv_ip}")
            self.tv = SamsungTVWS(host=self.tv_ip, token_file=self.token_file)
            
            # Try to get basic TV info to confirm connection
            try:
                info = self.tv.rest_device_info()
                if info:
                    tv_name = info.get('name', 'Unknown')
                    tv_model = info.get('model', 'Unknown')
                    logger.info(f"Connected to: {tv_name} - {tv_model}")
                    self.is_connected = True
                    return True
            except Exception as e:
                logger.error(f"Could not get TV info: {e}")
                
            # If we got here without returning, something went wrong
            logger.warning("Connection established but couldn't verify TV info")
            self.is_connected = False
            return False
                
        except Exception as e:
            logger.error(f"Error connecting to TV: {e}")
            self.is_connected = False
            return False
    
    def check_power_state(self):
        """Check if the TV is powered on."""
        if not self.is_connected:
            return False
        
        # For The Frame TV, we'll assume the TV is on if we have a connection
        # This avoids using the unsupported rest_power() method
        try:
            # Try getting device info to confirm connection is active
            info = self.tv.rest_device_info()
            if info:
                # If we can get device info, TV is probably on
                self.power_state = True
                return True
        except Exception:
            pass
            
        # If we couldn't confirm it's on, assume it might be off
        self.power_state = False
        return False
    
    def get_running_app(self):
        """Get information about currently running app."""
        if not self.is_connected:
            return None
        
        # Different methods to try, in order of preference
        methods = [
            self._try_get_app_via_app_status,
            self._try_get_app_via_browser
        ]
        
        for method in methods:
            try:
                app_info = method()
                if app_info:
                    return app_info
            except Exception as e:
                logger.debug(f"App detection method failed: {str(e)}")
        
        return None
    
    def _try_get_app_via_app_status(self):
        """Try to get current app using app_status APIs."""
        try:
            # This might not work on all TVs
            app_status = self.tv.rest_app_status()
            logger.debug(f"App status response: {app_status}")
            
            if app_status and "app" in app_status:
                return app_status["app"]
            
            return None
        except Exception as e:
            logger.debug(f"Could not get app via app_status: {e}")
            return None
    
    def _try_get_app_via_browser(self):
        """Try to get current app via browser URL if available."""
        try:
            # This is specific to some TV models
            browser_url = self.tv.browser_url()
            if browser_url:
                return {
                    "name": "Browser",
                    "url": browser_url
                }
            return None
        except Exception as e:
            logger.debug(f"Could not get browser URL: {e}")
            return None
    
    def is_youtube_running(self):
        """
        Check if YouTube app is running.
        
        Returns:
            (bool, dict): (is_youtube, app_data)
        """
        app_info = self.get_running_app()
        
        if not app_info:
            return False, None
        
        # Log the app info for debugging
        logger.debug(f"Current app info: {app_info}")
        
        # Check if app name contains YouTube
        app_name = app_info.get("name", "")
        if "youtube" in app_name.lower():
            return True, app_info
        
        # Also check URL if available
        app_url = app_info.get("url", "")
        if "youtube.com" in app_url.lower():
            return True, app_info
        
        return False, app_info
    
    def extract_video_id(self, app_info):
        """
        Extract YouTube video ID from app info if possible.
        
        Args:
            app_info (dict): App information dictionary
            
        Returns:
            str or None: YouTube video ID if found
        """
        if not app_info:
            return None
        
        url = app_info.get("url", "")
        
        # Standard YouTube URL
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[-1].split("&")[0]
        
        # Shortened YouTube URL
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[-1].split("?")[0]
        
        # YouTube TV app may use different URL formats
        elif "youtube.com" in url:
            logger.debug(f"Found YouTube URL but couldn't extract video ID: {url}")
        
        return None
    
    def get_current_video_id(self):
        """
        Attempt to extract a YouTube video ID from the currently running app.
        
        Returns:
            str or None: YouTube video ID if found
        """
        if not self.is_connected:
            if not self.connect():
                return None
        
        # First check if the TV is on
        if not self.check_power_state():
            logger.debug("TV appears to be off or in standby")
            return None
        
        # Check if YouTube is running
        youtube_running, app_info = self.is_youtube_running()
        
        if youtube_running:
            logger.info("YouTube app is running")
            
            # Try to extract video ID
            video_id = self.extract_video_id(app_info)
            if video_id:
                logger.info(f"Detected YouTube video: {video_id}")
                return video_id
            else:
                logger.debug("YouTube is running but couldn't get video ID")
                
        elif app_info:
            logger.debug(f"Different app is running: {app_info.get('name', 'Unknown')}")
        
        return None

    def monitor_continuously(self, callback=None):
        """
        Monitor TV continuously for YouTube videos.
        
        Args:
            callback (callable): Function to call when a new video is detected
                                 with signature callback(video_id, app_info)
        """
        logger.info("Starting continuous monitoring...")
        last_video_id = None
        
        try:
            while True:
                # Record check time
                check_time = datetime.now()
                time_diff = (check_time - self.last_check_time).total_seconds()
                self.last_check_time = check_time
                
                # Check power state
                power_state = self.check_power_state()
                if power_state != self.last_status["power"]:
                    if power_state:
                        logger.info("TV powered on")
                    else:
                        logger.info("TV powered off or in standby")
                    self.last_status["power"] = power_state
                
                if power_state:
                    # Check for YouTube videos
                    video_id = self.get_current_video_id()
                    
                    # If we have a new video ID
                    if video_id and video_id != last_video_id:
                        logger.info(f"New YouTube video detected: {video_id}")
                        
                        # Call the callback if provided
                        if callback and callable(callback):
                            youtube_running, app_info = self.is_youtube_running()
                            callback(video_id, app_info)
                            
                            # Also log to detected_videos.log
                            try:
                                with open("logs/detected_videos.log", "a") as f:
                                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    f.write(f"[{timestamp}] Video ID: {video_id}\n")
                            except Exception as e:
                                logger.error(f"Error writing to detected_videos.log: {e}")
                        
                        last_video_id = video_id
                
                # Wait before next check
                time.sleep(self.polling_interval)
        
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error during monitoring: {e}")
            raise

# Example usage when run directly
if __name__ == "__main__":
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Set up file handler for logging to file
    file_handler = logging.FileHandler("logs/tv_connection.log")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    # Function to call when a new video is detected
    def on_new_video(video_id, app_info):
        print(f"\n{'='*50}")
        print(f"NEW VIDEO DETECTED: {video_id}")
        print(f"App Info: {json.dumps(app_info, indent=2)}")
        print(f"{'='*50}\n")
        
        # Log to a special file
        with open("logs/detected_videos.log", "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Video ID: {video_id}\n")
    
    # Create TV connection
    tv_conn = TVConnection()
    
    print("\nSamsung The Frame TV YouTube Monitor")
    print("====================================")
    print("This monitor will detect YouTube videos playing on your TV")
    print("Press Ctrl+C to stop monitoring\n")
    
    # Start monitoring
    tv_conn.monitor_continuously(callback=on_new_video)