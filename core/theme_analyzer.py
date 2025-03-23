"""
Theme Analyzer Module

This module analyzes YouTube videos to determine their theme/category
and checks if watch time limits have been exceeded.
"""

import os
import json
import logging
from datetime import datetime, timedelta
import pyttsx3
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ThemeAnalyzer")

class ThemeAnalyzer:
    def __init__(self):
        """Initialize theme analyzer."""
        # Load environment variables
        load_dotenv()
        
        # Create logs directory
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Categories file maps YouTube category IDs to readable names
        self.categories_file = os.path.join(self.logs_dir, "categories.json")
        self._initialize_categories()
        
        # Theme watch time limits file
        self.limits_file = "theme_limits.json"
        self._initialize_limits()
        
        # Watch time log file
        self.watchtime_log_file = os.path.join(self.logs_dir, "watch_time.json")
        
        # Initialize TTS engine for alerts
        self.tts_engine = pyttsx3.init()
        
        # Track daily and weekly reset timestamps
        self.reset_file = os.path.join(self.logs_dir, "last_reset.json")
        self._initialize_reset_file()
        self._check_reset_needed()
    
    def _initialize_categories(self):
        """Initialize YouTube category mapping file."""
        # Default YouTube category mapping
        default_categories = {
            "1": "Film & Animation",
            "2": "Autos & Vehicles",
            "10": "Music",
            "15": "Pets & Animals",
            "17": "Sports",
            "18": "Short Movies",
            "19": "Travel & Events",
            "20": "Gaming",
            "21": "Videoblogging",
            "22": "People & Blogs",
            "23": "Comedy",
            "24": "Entertainment",
            "25": "News & Politics",
            "26": "Howto & Style",
            "27": "Education",
            "28": "Science & Technology",
            "29": "Nonprofits & Activism",
            "30": "Movies",
            "31": "Anime/Animation",
            "32": "Action/Adventure",
            "33": "Classics",
            "34": "Comedy",
            "35": "Documentary",
            "36": "Drama",
            "37": "Family",
            "38": "Foreign",
            "39": "Horror",
            "40": "Sci-Fi/Fantasy",
            "41": "Thriller",
            "42": "Shorts",
            "43": "Shows",
            "44": "Trailers"
        }
        
        if not os.path.exists(self.categories_file):
            with open(self.categories_file, "w") as f:
                json.dump(default_categories, f, indent=2)
    
    def _initialize_limits(self):
        """Initialize watch time limits file if it doesn't exist."""
        if not os.path.exists(self.limits_file):
            # Default limits (30 minutes for each category)
            default_limits = {
                "daily": {
                    "total": 7200,  # 2 hours total per day
                    "categories": {
                        "10": 1800,  # 30 min for Music
                        "17": 1800,  # 30 min for Sports
                        "20": 1800,  # 30 min for Gaming
                        "24": 1800,  # 30 min for Entertainment
                        "25": 1800,  # 30 min for News & Politics
                        "28": 3600   # 1 hour for Science & Technology
                    }
                },
                "weekly": {
                    "total": 28800,  # 8 hours total per week
                    "categories": {
                        "20": 7200   # 2 hours for Gaming per week
                    }
                }
            }
            
            with open(self.limits_file, "w") as f:
                json.dump(default_limits, f, indent=2)
    
    def _initialize_reset_file(self):
        """Initialize the reset timestamp file."""
        if not os.path.exists(self.reset_file):
            now = datetime.now()
            
            reset_data = {
                "daily": now.strftime("%Y-%m-%d %H:%M:%S"),
                "weekly": now.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.reset_file, "w") as f:
                json.dump(reset_data, f, indent=2)
    
    def _check_reset_needed(self):
        """Check if watch time needs to be reset (daily/weekly)."""
        try:
            # Get current time
            now = datetime.now()
            
            # Load reset timestamps
            with open(self.reset_file, "r") as f:
                reset_data = json.load(f)
            
            # Parse timestamps
            daily_reset = datetime.strptime(reset_data["daily"], "%Y-%m-%d %H:%M:%S")
            weekly_reset = datetime.strptime(reset_data["weekly"], "%Y-%m-%d %H:%M:%S")
            
            # Check daily reset (if it's a new day)
            if now.date() > daily_reset.date():
                logger.info("Performing daily watch time reset")
                self._reset_watch_time("daily")
                reset_data["daily"] = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # Check weekly reset (if it's been a week)
            if now - weekly_reset >= timedelta(days=7):
                logger.info("Performing weekly watch time reset")
                self._reset_watch_time("weekly")
                reset_data["weekly"] = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # Save updated reset timestamps
            with open(self.reset_file, "w") as f:
                json.dump(reset_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error checking reset status: {e}")
    
    def _reset_watch_time(self, reset_type):
        """
        Reset watch time statistics.
        
        Args:
            reset_type (str): 'daily' or 'weekly'
        """
        try:
            if not os.path.exists(self.watchtime_log_file):
                return
            
            with open(self.watchtime_log_file, "r") as f:
                watch_data = json.load(f)
            
            # Create reset points if they don't exist
            if "reset_points" not in watch_data:
                watch_data["reset_points"] = {
                    "daily": {
                        "total_time": 0,
                        "categories": {}
                    },
                    "weekly": {
                        "total_time": 0,
                        "categories": {}
                    }
                }
            
            # Store current stats as reset point
            watch_data["reset_points"][reset_type]["total_time"] = watch_data["total_watch_time"]
            
            # Reset category counters
            for category, data in watch_data.get("categories", {}).items():
                watch_data["reset_points"][reset_type]["categories"][category] = data["total_time"]
            
            # Save updated watch data
            with open(self.watchtime_log_file, "w") as f:
                json.dump(watch_data, f, indent=2)
            
            logger.info(f"Reset {reset_type} watch time counters")
        
        except Exception as e:
            logger.error(f"Error resetting watch time: {e}")
    
    def get_category_name(self, category_id):
        """
        Get readable name for a category ID.
        
        Args:
            category_id (str): YouTube category ID
            
        Returns:
            str: Category name or 'Unknown'
        """
        try:
            with open(self.categories_file, "r") as f:
                categories = json.load(f)
            
            return categories.get(str(category_id), "Unknown")
        except:
            return "Unknown"
    
    def check_time_limits(self, video_details, duration_seconds):
        """
        Check if this video exceeds any watch time limits.
        
        Args:
            video_details (dict): Video details dictionary
            duration_seconds (float): Duration watched in seconds
            
        Returns:
            list: List of limit alerts, empty if no limits exceeded
        """
        if not video_details or duration_seconds <= 0:
            return []
        
        # Get category ID
        category_id = str(video_details.get("category_id", "0"))
        
        try:
            # Load watch time data
            if not os.path.exists(self.watchtime_log_file):
                return []
            
            with open(self.watchtime_log_file, "r") as f:
                watch_data = json.load(f)
            
            # Load limits
            with open(self.limits_file, "r") as f:
                limits = json.load(f)
            
            alerts = []
            
            # Check total daily limit
            daily_total_limit = limits.get("daily", {}).get("total")
            if daily_total_limit:
                daily_reset_point = watch_data.get("reset_points", {}).get("daily", {}).get("total_time", 0)
                current_daily_total = watch_data["total_watch_time"] - daily_reset_point
                
                # Check if this video pushed us over the limit
                if current_daily_total > daily_total_limit and (current_daily_total - duration_seconds) <= daily_total_limit:
                    alerts.append({
                        "type": "daily_total",
                        "limit": daily_total_limit,
                        "current": current_daily_total,
                        "message": f"You have exceeded your daily total watch time limit of {self._format_time(daily_total_limit)}"
                    })
            
            # Check category daily limit
            daily_category_limit = limits.get("daily", {}).get("categories", {}).get(category_id)
            if daily_category_limit:
                daily_category_reset = watch_data.get("reset_points", {}).get("daily", {}).get("categories", {}).get(category_id, 0)
                
                category_total = watch_data.get("categories", {}).get(category_id, {}).get("total_time", 0)
                current_daily_category = category_total - daily_category_reset
                
                category_name = self.get_category_name(category_id)
                
                # Check if this video pushed us over the limit
                if current_daily_category > daily_category_limit and (current_daily_category - duration_seconds) <= daily_category_limit:
                    alerts.append({
                        "type": "daily_category",
                        "category_id": category_id,
                        "category_name": category_name,
                        "limit": daily_category_limit,
                        "current": current_daily_category,
                        "message": f"You have exceeded your daily limit of {self._format_time(daily_category_limit)} for {category_name} videos"
                    })
            
            # Check weekly limits (similar logic)
            weekly_total_limit = limits.get("weekly", {}).get("total")
            if weekly_total_limit:
                weekly_reset_point = watch_data.get("reset_points", {}).get("weekly", {}).get("total_time", 0)
                current_weekly_total = watch_data["total_watch_time"] - weekly_reset_point
                
                if current_weekly_total > weekly_total_limit and (current_weekly_total - duration_seconds) <= weekly_total_limit:
                    alerts.append({
                        "type": "weekly_total",
                        "limit": weekly_total_limit,
                        "current": current_weekly_total,
                        "message": f"You have exceeded your weekly total watch time limit of {self._format_time(weekly_total_limit)}"
                    })
            
            # Check category weekly limit
            weekly_category_limit = limits.get("weekly", {}).get("categories", {}).get(category_id)
            if weekly_category_limit:
                weekly_category_reset = watch_data.get("reset_points", {}).get("weekly", {}).get("categories", {}).get(category_id, 0)
                
                category_total = watch_data.get("categories", {}).get(category_id, {}).get("total_time", 0)
                current_weekly_category = category_total - weekly_category_reset
                
                category_name = self.get_category_name(category_id)
                
                if current_weekly_category > weekly_category_limit and (current_weekly_category - duration_seconds) <= weekly_category_limit:
                    alerts.append({
                        "type": "weekly_category",
                        "category_id": category_id,
                        "category_name": category_name,
                        "limit": weekly_category_limit,
                        "current": current_weekly_category,
                        "message": f"You have exceeded your weekly limit of {self._format_time(weekly_category_limit)} for {category_name} videos"
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking time limits: {e}")
            return []
    
    def play_alerts(self, alerts):
        """
        Play text-to-speech alerts for time limit violations.
        
        Args:
            alerts (list): List of alert dictionaries
        """
        if not alerts:
            return
        
        try:
            # Configure TTS engine
            self.tts_engine.setProperty('rate', 150)    # Speaking rate
            self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Log alerts
            for alert in alerts:
                logger.warning(f"ALERT: {alert['message']}")
                print("\n" + "!" * 60)
                print(f"ALERT: {alert['message']}")
                print("!" * 60 + "\n")
            
            # Build combined alert message
            if len(alerts) == 1:
                alert_message = alerts[0]['message']
            else:
                alert_message = "Multiple watch time limits exceeded: "
                for i, alert in enumerate(alerts):
                    if i > 0:
                        alert_message += ". Also, "
                    alert_message += alert['message']
            
            # Speak the alert
            self.tts_engine.say(alert_message)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            logger.error(f"Error playing alerts: {e}")
    
    def _format_time(self, seconds):
        """Format seconds as a readable time string."""
        if seconds < 60:
            return f"{seconds} seconds"
        
        minutes, seconds = divmod(seconds, 60)
        if minutes < 60:
            return f"{minutes} minutes" if seconds == 0 else f"{minutes} minutes, {seconds} seconds"
        
        hours, minutes = divmod(minutes, 60)
        if hours == 1:
            return f"{hours} hour" if minutes == 0 else f"{hours} hour, {minutes} minutes"
        else:
            return f"{hours} hours" if minutes == 0 else f"{hours} hours, {minutes} minutes"
    
    def get_stats_report(self):
        """
        Generate a statistics report of watch time.
        
        Returns:
            dict: Statistics report
        """
        try:
            if not os.path.exists(self.watchtime_log_file):
                return {"error": "No watch time data available"}
            
            with open(self.watchtime_log_file, "r") as f:
                watch_data = json.load(f)
            
            # Load limits
            with open(self.limits_file, "r") as f:
                limits = json.load(f)
            
            # Get reset points
            daily_reset = watch_data.get("reset_points", {}).get("daily", {}).get("total_time", 0)
            weekly_reset = watch_data.get("reset_points", {}).get("weekly", {}).get("total_time", 0)
            
            # Calculate current periods
            total_time = watch_data.get("total_watch_time", 0)
            daily_total = total_time - daily_reset
            weekly_total = total_time - weekly_reset
            
            # Daily limits
            daily_limit = limits.get("daily", {}).get("total", 0)
            daily_percent = (daily_total / daily_limit * 100) if daily_limit > 0 else 0
            
            # Weekly limits
            weekly_limit = limits.get("weekly", {}).get("total", 0)
            weekly_percent = (weekly_total / weekly_limit * 100) if weekly_limit > 0 else 0
            
            # Category stats
            categories = []
            for category_id, data in watch_data.get("categories", {}).items():
                category_name = self.get_category_name(category_id)
                category_total = data.get("total_time", 0)
                
                # Get daily/weekly category totals
                daily_category_reset = watch_data.get("reset_points", {}).get("daily", {}).get("categories", {}).get(category_id, 0)
                weekly_category_reset = watch_data.get("reset_points", {}).get("weekly", {}).get("categories", {}).get(category_id, 0)
                
                daily_category = category_total - daily_category_reset
                weekly_category = category_total - weekly_category_reset
                
                # Get limits
                daily_category_limit = limits.get("daily", {}).get("categories", {}).get(category_id, 0)
                weekly_category_limit = limits.get("weekly", {}).get("categories", {}).get(category_id, 0)
                
                # Calculate percentages
                daily_category_percent = (daily_category / daily_category_limit * 100) if daily_category_limit > 0 else 0
                weekly_category_percent = (weekly_category / weekly_category_limit * 100) if weekly_category_limit > 0 else 0
                
                categories.append({
                    "id": category_id,
                    "name": category_name,
                    "total_time": category_total,
                    "daily": {
                        "time": daily_category,
                        "limit": daily_category_limit,
                        "percent": daily_category_percent,
                        "formatted": self._format_time(daily_category)
                    },
                    "weekly": {
                        "time": weekly_category,
                        "limit": weekly_category_limit,
                        "percent": weekly_category_percent,
                        "formatted": self._format_time(weekly_category)
                    },
                    "video_count": data.get("video_count", 0)
                })
            
            # Sort categories by watch time
            categories.sort(key=lambda x: x["total_time"], reverse=True)
            
            # Build report
            report = {
                "total_time": {
                    "all_time": total_time,
                    "all_time_formatted": self._format_time(total_time)
                },
                "daily": {
                    "time": daily_total,
                    "limit": daily_limit,
                    "percent": daily_percent,
                    "formatted": self._format_time(daily_total)
                },
                "weekly": {
                    "time": weekly_total,
                    "limit": weekly_limit,
                    "percent": weekly_percent,
                    "formatted": self._format_time(weekly_total)
                },
                "categories": categories,
                "video_count": len(watch_data.get("videos", {}))
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating stats report: {e}")
            return {"error": str(e)}

# Test module if run directly
if __name__ == "__main__":
    # Set up file handler for logging
    file_handler = logging.FileHandler("logs/theme_analyzer.log")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    # Create analyzer
    analyzer = ThemeAnalyzer()
    
    print("\nTheme Analyzer Test")
    print("==================\n")
    
    # Get a category name
    print("Category ID 10 =", analyzer.get_category_name("10"))
    
    # Print stats report
    print("\nGenerating watch time statistics...")
    stats = analyzer.get_stats_report()
    
    if "error" not in stats:
        print(f"\nTotal watch time: {stats['total_time']['all_time_formatted']}")
        print(f"Daily watch time: {stats['daily']['formatted']} (Limit: {analyzer._format_time(stats['daily']['limit'])})")
        print(f"Weekly watch time: {stats['weekly']['formatted']} (Limit: {analyzer._format_time(stats['weekly']['limit'])})")
        
        print("\nTop categories:")
        for category in stats["categories"][:3]:  # Top 3 categories
            print(f"- {category['name']}: {analyzer._format_time(category['total_time'])}")
    else:
        print(f"Error: {stats['error']}")
    
    print("\nTime limit test:")
    mock_video = {
        "category_id": "20",  # Gaming
        "title": "Test Video"
    }
    
    # Test time limit alerts
    alerts = analyzer.check_time_limits(mock_video, 60)
    if alerts:
        print("Alerts triggered:")
        for alert in alerts:
            print(f"- {alert['message']}")
        
        print("\nPlaying alert...")
        analyzer.play_alerts(alerts)
    else:
        print("No time limits exceeded in test")