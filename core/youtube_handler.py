"""
YouTube Handler Module

This module handles YouTube video data retrieval and logging.
"""

import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("YouTubeHandler")

class YouTubeHandler:
    def __init__(self):
        """Initialize YouTube handler with API key from environment."""
        # Load environment variables
        load_dotenv()
        
        # Get API key
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            logger.error("YouTube API key not found in environment variables")
            raise ValueError("YouTube API key not found. Please set YOUTUBE_API_KEY in .env file")
        
        # Video info endpoint
        self.video_info_url = "https://www.googleapis.com/youtube/v3/videos"
        
        # Create logs directory
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Video logs file
        self.videos_log_file = os.path.join(self.logs_dir, "youtube_videos.json")
        
        # Video watch time file
        self.watchtime_log_file = os.path.join(self.logs_dir, "watch_time.json")
        
        # Initialize logs
        self._initialize_logs()
        
        # Track current video
        self.current_video = None
        self.current_video_start_time = None
    
    def _initialize_logs(self):
        """Initialize log files if they don't exist."""
        # Initialize videos log
        if not os.path.exists(self.videos_log_file):
            with open(self.videos_log_file, "w") as f:
                json.dump({}, f)
        
        # Initialize watch time log
        if not os.path.exists(self.watchtime_log_file):
            with open(self.watchtime_log_file, "w") as f:
                json.dump({
                    "total_watch_time": 0,
                    "videos": {},
                    "categories": {}
                }, f, indent=2)
    
    def get_video_details(self, video_id):
        """
        Fetch video details from YouTube API.
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Video details or None if not found
        """
        if not video_id:
            return None
        
        try:
            # Check if we already have this video in our logs
            video_details = self._get_cached_video(video_id)
            if video_details:
                logger.info(f"Using cached data for video {video_id}")
                return video_details
            
            # Otherwise, fetch from API
            logger.info(f"Fetching data for video {video_id} from YouTube API")
            
            params = {
                "id": video_id,
                "key": self.api_key,
                "part": "snippet,contentDetails,statistics,status"
            }
            
            response = requests.get(self.video_info_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if we got video data
            if not data.get("items"):
                logger.warning(f"No data found for video ID: {video_id}")
                return None
            
            # Get the first (and only) item
            video_data = data["items"][0]
            
            # Extract relevant info
            snippet = video_data.get("snippet", {})
            content_details = video_data.get("contentDetails", {})
            statistics = video_data.get("statistics", {})
            
            # Format details
            video_details = {
                "video_id": video_id,
                "title": snippet.get("title", "Unknown"),
                "description": snippet.get("description", ""),
                "channel": snippet.get("channelTitle", "Unknown"),
                "published_at": snippet.get("publishedAt", ""),
                "category_id": snippet.get("categoryId", ""),
                "tags": snippet.get("tags", []),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "duration": content_details.get("duration", ""),
                "definition": content_details.get("definition", ""),
                "view_count": statistics.get("viewCount", "0"),
                "like_count": statistics.get("likeCount", "0"),
                "comment_count": statistics.get("commentCount", "0"),
                "first_detected": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "watches": []
            }
            
            # Save to logs
            self._save_video_to_logs(video_details)
            
            return video_details
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching video data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing video data: {e}")
            return None
    
    def _get_cached_video(self, video_id):
        """Get video from logs if available."""
        try:
            with open(self.videos_log_file, "r") as f:
                videos = json.load(f)
                return videos.get(video_id)
        except:
            return None
    
    def _save_video_to_logs(self, video_details):
        """Save video details to log file."""
        video_id = video_details["video_id"]
        
        try:
            # Load existing logs
            with open(self.videos_log_file, "r") as f:
                videos = json.load(f)
            
            # Add or update this video
            videos[video_id] = video_details
            
            # Save updated logs
            with open(self.videos_log_file, "w") as f:
                json.dump(videos, f, indent=2)
            
            logger.info(f"Saved video details for {video_id} - '{video_details['title']}'")
            return True
        
        except Exception as e:
            logger.error(f"Error saving video to logs: {e}")
            return False
    
    def record_video_start(self, video_id):
        """
        Record that a video has started playing.
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Video details or None if not found
        """
        # Get video details first
        video_details = self.get_video_details(video_id)
        
        if not video_details:
            logger.warning(f"Cannot record start for unknown video: {video_id}")
            return None
        
        # Record start time
        self.current_video = video_details
        self.current_video_start_time = datetime.now()
        
        logger.info(f"Started watching: {video_details['title']}")
        
        # Add this session to watches list
        try:
            with open(self.videos_log_file, "r") as f:
                videos = json.load(f)
            
            if video_id in videos:
                videos[video_id]["watches"].append({
                    "start_time": self.current_video_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": None,
                    "duration_seconds": None
                })
                
                with open(self.videos_log_file, "w") as f:
                    json.dump(videos, f, indent=2)
        except Exception as e:
            logger.error(f"Error recording video start: {e}")
        
        return video_details
    
    def record_video_end(self):
        """
        Record that the current video has ended.
        
        Returns:
            float: Duration watched in seconds or None if no video was playing
        """
        if not self.current_video or not self.current_video_start_time:
            return None
        
        # Calculate duration
        end_time = datetime.now()
        duration_seconds = (end_time - self.current_video_start_time).total_seconds()
        
        video_id = self.current_video["video_id"]
        title = self.current_video["title"]
        
        logger.info(f"Stopped watching: {title} (watched for {duration_seconds:.2f} seconds)")
        
        # Update watch log
        try:
            with open(self.videos_log_file, "r") as f:
                videos = json.load(f)
            
            if video_id in videos and videos[video_id]["watches"]:
                # Update the last watch entry
                last_watch = videos[video_id]["watches"][-1]
                if last_watch["end_time"] is None:
                    last_watch["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
                    last_watch["duration_seconds"] = duration_seconds
                
                with open(self.videos_log_file, "w") as f:
                    json.dump(videos, f, indent=2)
            
            # Update watchtime log
            self._update_watch_time(video_id, duration_seconds)
        
        except Exception as e:
            logger.error(f"Error recording video end: {e}")
        
        # Reset current video tracking
        current_video = self.current_video
        self.current_video = None
        self.current_video_start_time = None
        
        return {
            "video": current_video,
            "duration_seconds": duration_seconds
        }
    
    def _update_watch_time(self, video_id, duration_seconds):
        """Update watch time logs with this video session."""
        try:
            with open(self.watchtime_log_file, "r") as f:
                watch_data = json.load(f)
            
            # Update total watch time
            watch_data["total_watch_time"] += duration_seconds
            
            # Update for this specific video
            if video_id not in watch_data["videos"]:
                watch_data["videos"][video_id] = {
                    "total_time": 0,
                    "session_count": 0
                }
            
            watch_data["videos"][video_id]["total_time"] += duration_seconds
            watch_data["videos"][video_id]["session_count"] += 1
            
            # Get video details for category info
            with open(self.videos_log_file, "r") as f:
                videos = json.load(f)
            
            if video_id in videos:
                category = videos[video_id].get("category_id", "unknown")
                
                # Update category stats
                if category not in watch_data["categories"]:
                    watch_data["categories"][category] = {
                        "total_time": 0,
                        "video_count": 0
                    }
                
                watch_data["categories"][category]["total_time"] += duration_seconds
                
                # Only count unique videos per category
                if video_id not in watch_data["categories"][category].get("videos", []):
                    if "videos" not in watch_data["categories"][category]:
                        watch_data["categories"][category]["videos"] = []
                    
                    watch_data["categories"][category]["videos"].append(video_id)
                    watch_data["categories"][category]["video_count"] += 1
            
            # Save updated watch time data
            with open(self.watchtime_log_file, "w") as f:
                json.dump(watch_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error updating watch time: {e}")

# Test module if run directly
if __name__ == "__main__":
    # Set up file handler for logging
    file_handler = logging.FileHandler("logs/youtube_handler.log")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    # Create handler
    handler = YouTubeHandler()
    
    # Test with a sample video ID
    test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    print("\nYouTube Handler Test")
    print("===================\n")
    
    # Get video details
    print("Fetching video details...")
    video = handler.get_video_details(test_video_id)
    
    if video:
        print(f"Video Title: {video['title']}")
        print(f"Channel: {video['channel']}")
        print(f"View Count: {video['view_count']}")
        
        # Test tracking
        print("\nSimulating video watch session...")
        handler.record_video_start(test_video_id)
        print("Watching video for 5 seconds...")
        
        import time
        time.sleep(5)
        
        result = handler.record_video_end()
        if result:
            print(f"Watched for {result['duration_seconds']:.2f} seconds")
        
        print("\nCheck the logs directory for detailed logs")
    else:
        print("Failed to fetch video details")