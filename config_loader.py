"""
Configuration Loader

Loads configuration from config.json and overrides with environment variables.
"""

import os
import json
from dotenv import load_dotenv

def load_config(config_file="config.json"):
    """
    Load configuration from config.json and override with environment variables.
    
    Returns:
        dict: The configuration dictionary
    """
    # Load .env file
    load_dotenv()
    
    # Load base configuration from JSON
    with open(config_file, "r") as f:
        config = json.load(f)
    
    # Override with environment variables if they exist
    if os.getenv("TV_IP"):
        config["tv"]["ip"] = os.getenv("TV_IP")
        
    if os.getenv("YOUTUBE_API_KEY"):
        config["api_keys"]["youtube"] = os.getenv("YOUTUBE_API_KEY")
        
    if os.getenv("OPENAI_API_KEY"):
        config["api_keys"]["openai"] = os.getenv("OPENAI_API_KEY")
    
    # Add additional environment variable overrides as needed
    
    return config