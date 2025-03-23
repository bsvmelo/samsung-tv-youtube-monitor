"""
YouTube Data Module

This module fetches video information from the YouTube API
and stores the data in a structured JSON log file.
"""

import os
import json
import requests
from datetime import datetime

class YouTubeData:
    def __init__(self, config_file="config.json"):
        """Initialize YouTube data handler with API key from config."""
        # Load configuration
        with open(config_file, "r") as f:
            self.config = json.load(f)
        
        self.api_key = self.config["api_keys"]["youtube"]
        self.logs_dir = self.config["system"]["logs_dir"]
        
        # Create logs directory if it doesn't exist
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Log file path
        self.video_log_file = os.path.join(self.logs_dir, "youtube_videos.json")
        
        # API endpoints
        self.video_info_url = "https://www.googleapis.com/youtube/v3/videos"
    
    def fetch_video_details(self, video_id):
        """Fetch video details from YouTube API using the video ID."""
        if not video_id:
            return None
        
        try:
            # Request parameters
            params = {
                "id": video_id,
                "key": self.api_key,
                "part": "snippet,contentDetails,statistics"
            }
            
            # Make API request
            response = requests.get(self.video_info_url, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            data = response.json()
            
            # Check if video data is returned
            if "items" not in data or len(data["items"]) == 0:
                print(f"No data found for video ID: {video_id}")
                return None
            
            # Extract relevant information
            video_data = data["items"][0]
            snippet = video_data["snippet"]
            
            # Format video details
            video_details = {
                "video_id": video_id,
                "title": snippet.get("title", "Unknown"),
                "description": snippet.get("description", ""),
                "channel": snippet.get("channelTitle", "Unknown"),
                "published_at": snippet.get("publishedAt", ""),
                "category_id": snippet.get("categoryId", ""),
                "tags": snippet.get("tags", []),
                "duration": video_data.get("contentDetails", {}).get("duration", ""),
                "view_count": video_data.get("statistics", {}).get("viewCount", ""),
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": None,
                "theme": None  # Will be filled by the theme classifier
            }
            
            return video_details
        
        except requests.exceptions.RequestException as e:
            print(f"API error fetching video data: {e}")
            return None
        except Exception as e:
            print(f"Error processing video data: {e}")
            return None
    
    def log_video_data(self, video_data):
        """Store video details in JSON log file."""
        if not video_data:
            return False
        
        try:
            # Load existing log or create new one
            if os.path.exists(self.video_log_file):
                with open(self.video_log_file, "r") as f:
                    logs = json.load(f)
            else:
                logs = {}
            
            # Add or update video data
            logs[video_data["video_id"]] = video_data
            
            # Save updated log
            with open(self.video_log_file, "w") as f:
                json.dump(logs, f, indent=4)
            
            return True
        
        except Exception as e:
            print(f"Error logging video data: {e}")
            return False
    
    def update_video_end_time(self, video_id):
        """Update the end time of a video in the log."""
        if not video_id:
            return False
        
        try:
            # Load existing log
            if not os.path.exists(self.video_log_file):
                return False
            
            with open(self.video_log_file, "r") as f:
                logs = json.load(f)
            
            # Update end time if video exists in log
            if video_id in logs:
                logs[video_id]["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Save updated log
                with open(self.video_log_file, "w") as f:
                    json.dump(logs, f, indent=4)
                
                return True
            
            return False
        
        except Exception as e:
            print(f"Error updating video end time: {e}")
            return False

# Test module if run directly
if __name__ == "__main__":
    youtube_data = YouTubeData()
    
    # Test with a sample video ID
    test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    # Fetch and log video details
    video_details = youtube_data.fetch_video_details(test_video_id)
    if video_details:
        print(f"Successfully fetched details for: {video_details['title']}")
        youtube_data.log_video_data(video_details)
        print(f"Data saved to {youtube_data.video_log_file}")