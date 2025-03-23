"""
Samsung TV Connection Module

This module connects to a Samsung TV via the network API
and extracts information about YouTube videos playing on the TV.
"""

import json
import time
from samsungtvws import SamsungTVWS

class TVConnection:
    def __init__(self, config_file="config.json"):
        """Initialize connection with Samsung TV using config values."""
        # Load configuration
        with open(config_file, "r") as f:
            self.config = json.load(f)
        
        tv_config = self.config["tv"]
        self.tv_ip = tv_config["ip"]
        self.token_file = tv_config["token_file"]
        self.polling_interval = tv_config["polling_interval"]
        
        # Initialize connection
        self.tv = None
        self.connect()
    
    def connect(self):
        """Establish connection to the Samsung TV."""
        try:
            self.tv = SamsungTVWS(host=self.tv_ip, token_file=self.token_file)
            print(f"Successfully connected to Samsung TV at {self.tv_ip}")
        except Exception as e:
            print(f"Error connecting to TV: {e}")
    
    def get_current_video_id(self):
        """Extract the currently playing YouTube video ID from the TV."""
        if not self.tv:
            print("TV connection not established")
            return None
        
        try:
            app_status = self.tv.rest_app_status()
            
            # Check if YouTube app is running
            if "YouTube" in app_status.get("app", {}).get("title", ""):
                url = app_status.get("app", {}).get("url", "")
                
                # Extract video ID from YouTube URL
                if "youtube.com/watch?v=" in url:
                    video_id = url.split("v=")[-1].split("&")[0]
                    return video_id
                
                # Handle shortened YouTube URLs
                elif "youtu.be/" in url:
                    video_id = url.split("youtu.be/")[-1].split("?")[0]
                    return video_id
            
            return None
        except Exception as e:
            print(f"Error retrieving video ID: {e}")
            # Try to reconnect if connection is lost
            self.connect()
            return None

# Test module if run directly
if __name__ == "__main__":
    tv_conn = TVConnection()
    
    print("Monitoring YouTube videos...")
    prev_video_id = None
    
    while True:
        video_id = tv_conn.get_current_video_id()
        if video_id and video_id != prev_video_id:
            print(f"New YouTube video detected! ID: {video_id}")
            prev_video_id = video_id
        
        time.sleep(tv_conn.polling_interval)