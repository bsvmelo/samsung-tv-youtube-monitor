"""
Configuration Loader

Loads configuration from config.json and required environment variables.
"""

import os
import json
import sys
from dotenv import load_dotenv

def load_config(config_file="config.json"):
    """
    Load configuration from config.json and required environment variables.
    
    Returns:
        dict: The configuration dictionary
        
    Raises:
        SystemExit: If required environment variables are missing
    """
    # Load .env file
    load_dotenv()
    
    # Check for required environment variables
    required_env_vars = ["TV_IP", "YOUTUBE_API_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("ERROR: The following required environment variables are missing:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease add them to your .env file or environment and try again.")
        print("Example .env file format:")
        print("TV_IP=192.168.1.X")
        print("YOUTUBE_API_KEY=your_youtube_api_key")
        print("OPENAI_API_KEY=your_openai_api_key")
        sys.exit(1)
    
    # Load base configuration from JSON
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file '{config_file}' not found.")
        print("Please create it using the config.json.example template.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON format in '{config_file}'.")
        sys.exit(1)
    
    # Ensure the required config sections exist
    if "tv" not in config:
        config["tv"] = {}
    if "api_keys" not in config:
        config["api_keys"] = {}
    
    # Add environment variables to configuration
    config["tv"]["ip"] = os.getenv("TV_IP")
    config["tv"]["token_file"] = os.getenv("TOKEN_FILE", "tv_token.txt")
    
    config["api_keys"]["youtube"] = os.getenv("YOUTUBE_API_KEY")
    config["api_keys"]["openai"] = os.getenv("OPENAI_API_KEY")
    
    return config