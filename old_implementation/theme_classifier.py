"""
Theme Classification Module

This module uses OpenAI's LLM to classify YouTube videos
into themes based on their title and description.
"""

import os
import json
import time
from openai import OpenAI

class ThemeClassifier:
    def __init__(self, config_file="config.json"):
        """Initialize theme classifier with OpenAI API key from config."""
        # Load configuration
        with open(config_file, "r") as f:
            self.config = json.load(f)
        
        # Initialize OpenAI client
        self.api_key = self.config["api_keys"]["openai"]
        self.client = OpenAI(api_key=self.api_key)
        
        # Set up cache for theme classification
        self.logs_dir = self.config["system"]["logs_dir"]
        os.makedirs(self.logs_dir, exist_ok=True)
        self.cache_file = os.path.join(self.logs_dir, "theme_cache.json")
        self.load_cache()
    
    def load_cache(self):
        """Load cached theme classifications from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            print(f"Error loading theme cache: {e}")
            self.cache = {}
    
    def save_cache(self):
        """Save theme classifications to cache file."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=4)
        except Exception as e:
            print(f"Error saving theme cache: {e}")
    
    def classify_video_theme(self, title, description, retry_attempts=3):
        """
        Classify video into a theme using OpenAI's model.
        
        Args:
            title: Video title
            description: Video description
            retry_attempts: Number of retries on API failure
            
        Returns:
            Theme as a lowercase string (e.g., "sports", "gaming", "news")
        """
        # Create cache key from title and description
        cache_key = f"{title}:{description[:100]}"  # Truncate description for key
        
        # Check if theme is in cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Prepare prompt for OpenAI
        prompt = (
            "Analyze the following YouTube video and classify it into a single specific theme category.\n\n"
            f"Title: {title}\n"
            f"Description: {description[:500]}\n\n"  # Truncate description if too long
            "Respond with just one word representing the theme category. "
            "Choose from themes like: sports, baseball, football, basketball, gaming, news, politics, "
            "music, cooking, tech, science, movies, education, finance, travel, etc. "
            "Be specific where possible (e.g., use 'baseball' instead of just 'sports' if it's clearly about baseball)."
        )
        
        # Try to get classification with retries
        for attempt in range(retry_attempts):
            try:
                # Call OpenAI API
                response = self.client.chat.completions.create(
                    model="gpt-4-turbo",  # Use the latest model
                    messages=[
                        {"role": "system", "content": "You are a video theme classifier that responds with a single theme word."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Low temperature for more consistent results
                    max_tokens=20  # We only need a short response
                )
                
                # Extract theme from response
                theme = response.choices[0].message.content.strip().lower()
                
                # Clean up theme (remove punctuation, etc.)
                theme = theme.replace(".", "").replace(",", "").replace("!", "").replace("?", "")
                
                # Store in cache
                self.cache[cache_key] = theme
                self.save_cache()
                
                return theme
            
            except Exception as e:
                print(f"Error classifying theme (attempt {attempt+1}/{retry_attempts}): {e}")
                
                if attempt < retry_attempts - 1:
                    # Wait before retrying (exponential backoff)
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # Return a default theme on final failure
                    return "other"

# Test module if run directly
if __name__ == "__main__":
    classifier = ThemeClassifier()
    
    # Test with sample video data
    test_cases = [
        {
            "title": "Top 10 Home Runs of All Time!",
            "description": "A compilation of the greatest baseball home runs in history."
        },
        {
            "title": "Breaking News: Stock Market Update",
            "description": "Latest updates on the financial markets and economic trends."
        },
        {
            "title": "How to Make Perfect Pasta Carbonara",
            "description": "Learn the authentic Italian recipe for this classic dish."
        }
    ]
    
    for i, test in enumerate(test_cases):
        theme = classifier.classify_video_theme(test["title"], test["description"])
        print(f"Test {i+1}:")
        print(f"  Title: {test['title']}")
        print(f"  Description: {test['description'][:50]}...")
        print(f"  Classified Theme: {theme}")
        print()