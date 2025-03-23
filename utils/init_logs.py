"""
Initialize all log files for the YouTube Monitor
"""

import os
import logging
import json
from datetime import datetime

def initialize_logs():
    """Create all necessary log files"""
    # Create logs directory
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Initialize all text log files
    log_files = [
        "monitor.log",
        "tv_connection.log",
        "youtube_handler.log",
        "theme_analyzer.log",
        "detected_videos.log"
    ]
    
    print("Initializing log files...")
    
    for log_file in log_files:
        file_path = os.path.join(logs_dir, log_file)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(f"Log initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            print(f"  Created: {log_file}")
        else:
            print(f"  Already exists: {log_file}")
    
    # Initialize JSON data files if they don't exist
    json_files = {
        "youtube_videos.json": {},
        "watch_time.json": {
            "total_watch_time": 0,
            "videos": {},
            "categories": {},
            "reset_points": {
                "daily": {"total_time": 0, "categories": {}},
                "weekly": {"total_time": 0, "categories": {}}
            }
        },
        "categories.json": {
            "1": "Film & Animation",
            "2": "Autos & Vehicles",
            "10": "Music",
            "15": "Pets & Animals",
            "17": "Sports",
            "18": "Short Movies",
            "19": "Travel & Events",
            "20": "Gaming",
            "22": "People & Blogs",
            "23": "Comedy",
            "24": "Entertainment",
            "25": "News & Politics",
            "26": "Howto & Style",
            "27": "Education",
            "28": "Science & Technology",
            "29": "Nonprofits & Activism",
            "30": "Movies"
        },
        "last_reset.json": {
            "daily": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "weekly": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    print("\nInitializing data files...")
    
    for filename, default_data in json_files.items():
        file_path = os.path.join(logs_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump(default_data, f, indent=2)
            print(f"  Created: {filename}")
        else:
            print(f"  Already exists: {filename}")
    
    print("\nAll log files initialized successfully.")
    print(f"Log directory: {os.path.abspath(logs_dir)}")

if __name__ == "__main__":
    initialize_logs()