"""
Samsung TV YouTube Monitor - Connection Test Script

This script tests the essential connections required for the application:
1. Samsung TV connection
2. YouTube API functionality

Run this before setting up the main application to verify your configuration.
"""

import os
import sys
import time
import json
import requests
from dotenv import load_dotenv

# Try to import the Samsung TV library
try:
    from samsungtvws import SamsungTVWS
except ImportError:
    print("ERROR: samsungtvws package not installed.")
    print("Please run: pip install samsungtvws")
    sys.exit(1)

def check_environment():
    """Check if all required environment variables are set."""
    load_dotenv()
    
    required_vars = ["TV_IP", "YOUTUBE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("\n❌ ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file.")
        return False
    
    print("✅ All required environment variables are set.")
    return True

def test_tv_connection():
    """Test the connection to the Samsung TV."""
    print("\n--- Testing Samsung TV Connection ---")
    
    tv_ip = os.getenv("TV_IP")
    token_file = os.getenv("TOKEN_FILE", "tv_token.txt")
    
    print(f"Attempting to connect to Samsung TV at {tv_ip}...")
    
    try:
        # Initialize TV connection
        tv = SamsungTVWS(host=tv_ip, token_file=token_file)
        
        # Try to get TV info
        info = tv.rest_device_info()
        
        # If we get here without an exception, connection was successful
        print(f"✅ Successfully connected to Samsung TV!")
        print(f"TV Name: {info.get('name', 'Unknown')}")
        print(f"Model: {info.get('model', 'Unknown')}")
        
        # Try to check if TV is on
        try:
            power_state = tv.rest_power()
            print(f"Power State: {'On' if power_state else 'Off or Standby'}")
        except Exception:
            print("Note: Could not determine power state, but connection was successful.")
        
        # Check for open apps
        try:
            app_status = tv.rest_app_status()
            if app_status and 'app' in app_status and 'name' in app_status['app']:
                print(f"Current App: {app_status['app']['name']}")
        except Exception:
            print("Note: Could not determine current app, but connection was successful.")
            
        return True
    
    except Exception as e:
        print(f"❌ Error connecting to Samsung TV: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure your TV is turned on")
        print("2. Verify the TV_IP address in your .env file")
        print("3. Ensure your computer and TV are on the same network")
        print("4. Check if your TV supports network control")
        print("5. Look for any confirmation prompts on your TV screen")
        return False

def test_youtube_api():
    """Test the connection to YouTube API."""
    print("\n--- Testing YouTube API Connection ---")
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    
    print(f"Attempting to fetch data for test video (ID: {test_video_id})...")
    
    try:
        # API endpoint
        url = "https://www.googleapis.com/youtube/v3/videos"
        
        # Parameters
        params = {
            "id": test_video_id,
            "key": api_key,
            "part": "snippet"
        }
        
        # Make API request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        
        # Check if video data is returned
        if "items" not in data or len(data["items"]) == 0:
            print("❌ API responded but no video data was returned.")
            return False
        
        # Get video details
        video = data["items"][0]["snippet"]
        title = video.get("title", "Unknown")
        channel = video.get("channelTitle", "Unknown")
        
        print(f"✅ Successfully connected to YouTube API!")
        print(f"Video Title: {title}")
        print(f"Channel: {channel}")
        
        return True
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error from YouTube API: {e}")
        
        # Check for specific error codes
        if response.status_code == 400:
            print("This may indicate a malformed request or invalid parameters.")
        elif response.status_code == 403:
            print("This may indicate an invalid or restricted API key.")
        elif response.status_code == 404:
            print("This may indicate the API endpoint or resource was not found.")
        
        print("\nTroubleshooting steps:")
        print("1. Verify your YOUTUBE_API_KEY in the .env file")
        print("2. Make sure the YouTube Data API v3 is enabled in your Google Cloud Console")
        print("3. Check if you've reached your API quota limit")
        return False
    
    except Exception as e:
        print(f"❌ Error connecting to YouTube API: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Verify your YOUTUBE_API_KEY in the .env file")
        print("3. Make sure the YouTube Data API v3 is enabled in your Google Cloud Console")
        return False

def run_all_tests():
    """Run all connection tests."""
    print("\n=================================================")
    print("  SAMSUNG TV YOUTUBE MONITOR - CONNECTION TEST")
    print("=================================================")
    
    # Check environment variables
    if not check_environment():
        return False
    
    # Test TV connection
    tv_success = test_tv_connection()
    
    # Test YouTube API
    youtube_success = test_youtube_api()
    
    # Overall result
    print("\n=================================================")
    print("  TEST RESULTS")
    print("=================================================")
    print(f"Environment Variables: {'✅ PASSED' if check_environment() else '❌ FAILED'}")
    print(f"Samsung TV Connection: {'✅ PASSED' if tv_success else '❌ FAILED'}")
    print(f"YouTube API: {'✅ PASSED' if youtube_success else '❌ FAILED'}")
    
    if tv_success and youtube_success:
        print("\n✅ ALL TESTS PASSED!")
        print("You're ready to use the Samsung TV YouTube Monitor.")
        print("Run 'python main.py' to start the application.")
        return True
    else:
        print("\n❌ SOME TESTS FAILED.")
        print("Please fix the issues above before running the main application.")
        return False

if __name__ == "__main__":
    run_all_tests()