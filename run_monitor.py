'''
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
