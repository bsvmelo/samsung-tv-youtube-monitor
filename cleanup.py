"""
Cleanup script to organize the project file structure
"""

import os
import shutil
from datetime import datetime

def create_backup():
    """Create a backup of all files first"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"📦 Creating backup in {backup_dir}/")
    
    # Copy all python and json files to backup
    for file in os.listdir():
        if file.endswith((".py", ".json", ".md", ".txt")) and file != "cleanup.py":
            shutil.copy2(file, os.path.join(backup_dir, file))
    
    print(f"✅ Backup created with {len(os.listdir(backup_dir))} files")
    return backup_dir

def organize_files():
    """Organize files into appropriate directories"""
    
    # Define directories
    dirs = {
        "core": "Current implementation files",
        "config": "Configuration files",
        "utils": "Utility scripts",
        "old_implementation": "Original implementation files",
        "temp": "Temporary and fix files"
    }
    
    # Create directories
    for dir_name, description in dirs.items():
        os.makedirs(dir_name, exist_ok=True)
        print(f"📁 Created {dir_name}/ - {description}")
    
    # Define which files go where
    file_groups = {
        "core": [
            "tv_connection.py",
            "youtube_handler.py", 
            "theme_analyzer.py",
            "monitor.py"
        ],
        "config": [
            "theme_limits.json",
            ".env",
            ".env.example",
            "requirements.txt"
        ],
        "utils": [
            "test_connections.py",
            "init_logs.py"
        ],
        "old_implementation": [
            "main.py",
            "config.json",
            "config.json.example",
            "theme_classifier.py",
            "watch_time_tracker.py", 
            "youtube_data.py",
            "config_loader.py"
        ],
        "temp": [
            "tv_connection.py.bak",
            "tv_connection.py.bak2",
            "tv_connection_fix.py",
            "tv_connection_update.py"
        ]
    }
    
    # Move files to appropriate directories
    for group, files in file_groups.items():
        for file in files:
            if os.path.exists(file):
                try:
                    # For config files, create copies instead of moving them
                    if group == "config" and file in [".env", "theme_limits.json", "requirements.txt"]:
                        shutil.copy2(file, os.path.join(group, file))
                        print(f"📄 Copied {file} to {group}/")
                    else:
                        shutil.move(file, os.path.join(group, file))
                        print(f"📄 Moved {file} to {group}/")
                except Exception as e:
                    print(f"❌ Error moving {file}: {e}")
    
    # Create a launch script in the main directory
    with open("run_monitor.py", "w") as f:
        f.write("""'''
YouTube Monitor for Samsung TV - Launch Script

This script adds the necessary paths and runs the monitor
'''

import sys
import os

# Add the core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

# Import and run the monitor
from monitor import YouTubeMonitor

if __name__ == "__main__":
    print("Starting Samsung TV YouTube Monitor...")
    monitor = YouTubeMonitor()
    monitor.start_monitoring()
""")
    
    print("✅ Created run_monitor.py launch script")
    
    # Create a README in the main directory
    with open("README.md", "w") as f:
        f.write("""# Samsung TV YouTube Monitor

## Directory Structure

- **core/** - Main application files
- **config/** - Configuration files
- **utils/** - Utility scripts
- **logs/** - Log files (created when the app runs)
- **old_implementation/** - Original implementation (not used)
- **temp/** - Temporary files (can be deleted)

## Quick Start

1. Make sure your configuration is set up:
   - Check that `config/.env` has your TV IP and YouTube API key
   - Review watch time limits in `config/theme_limits.json`

2. Run the monitor:
   ```
   python run_monitor.py
   ```

3. To test connections first:
   ```
   python utils/test_connections.py
   ```

## Logs

All logs are stored in the `logs/` directory:
- **youtube_videos.json** - Details of detected videos
- **watch_time.json** - Watch time statistics
- **tv_connection.log** - TV connection log
- **monitor.log** - General monitoring log
""")
    
    print("✅ Created README.md")

if __name__ == "__main__":
    print("🧹 Starting project cleanup...")
    backup_dir = create_backup()
    organize_files()
    print(f"\n✅ Cleanup complete! A backup was created in {backup_dir}/")
    print("🚀 You can now run the monitor using: python run_monitor.py")