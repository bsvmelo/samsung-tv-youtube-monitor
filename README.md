# Samsung TV YouTube Monitor

A smart monitoring system that tracks YouTube viewing habits on your Samsung TV, categorizes content using AI, and helps manage screen time with customizable alerts.

![Project Banner](https://via.placeholder.com/800x400?text=Samsung+TV+YouTube+Monitor)

## 📌 Overview

This application connects to your Samsung TV over your local network to monitor YouTube viewing activity. It uses AI (OpenAI) to classify videos by theme, tracks watch time per category, and provides voice alerts when you exceed your predefined time limits.

Perfect for:
- Parents managing their children's screen time
- Individuals looking to balance their media consumption
- Anyone wanting insights into their YouTube viewing patterns

## ✨ Features

- **Smart TV Integration**: Seamlessly connects to Samsung TVs via network API
- **AI-Powered Classification**: Uses OpenAI to categorize videos by theme (sports, news, gaming, etc.)
- **Custom Time Limits**: Set different time limits for different content categories
- **Voice Alerts**: Receive spoken notifications when time limits are exceeded
- **Watch Time Analytics**: Track and analyze your viewing habits over time
- **Daily/Weekly Resets**: Automatically reset watch time counters on your schedule
- **Detailed Logging**: Maintains comprehensive logs of all watched content

## 🛠️ Requirements

- Python 3.8+
- Samsung TV with network connectivity (2016 model or newer recommended)
- Computer or Raspberry Pi on the same network as your TV
- Internet connection for YouTube API and OpenAI API access
- API keys for YouTube Data API and OpenAI

## 📋 Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/samsung-tv-youtube-monitor.git
cd samsung-tv-youtube-monitor
```

### Create a Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Activate it (macOS/Linux)
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configuration

1. Create a `.env` file with your API keys:

```
YOUTUBE_API_KEY=your_youtube_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
TV_IP=192.168.1.X
```

2. Customize watch time limits in `config.json`:

```json
{
    "watch_time_limits": {
        "baseball": 1800,  // 30 minutes
        "gaming": 3600,    // 1 hour
        "news": 1200       // 20 minutes
    }
}
```

## 🚀 Usage

### Starting the Monitor

Run the main application:

```bash
python main.py
```

On first run, your TV may prompt you to accept the connection.

### Monitoring Process

The system will:
1. Connect to your Samsung TV
2. Monitor for YouTube videos being played
3. Classify videos by theme using AI
4. Track watch time for each theme
5. Play voice alerts when time limits are exceeded

### Viewing Statistics

Press `Ctrl+C` to stop monitoring and view your watch time statistics.

## 📊 Watch Time Analytics

The application tracks:
- Total watch time per theme
- Percentage of limit used
- Viewing patterns over time

Example statistics output:
```
===============================
WATCH TIME STATISTICS
===============================
Total watch time: 1h 45m 22s

Watch time by theme:
  baseball: 25m 10s/30m (83.9%)
  gaming: 45m 30s/1h (75.8%)
  news: 34m 42s/20m (EXCEEDED)
===============================
```

## 📁 Project Structure

```
samsung-tv-youtube-monitor/
├── config.json             # Configuration settings
├── config_loader.py        # Loads config with env variables
├── main.py                 # Main controller script
├── tv_connection.py        # Samsung TV connection module
├── youtube_data.py         # YouTube API integration
├── theme_classifier.py     # AI theme classification
├── watch_time_tracker.py   # Time tracking and alerts
├── .env                    # API keys (not committed to git)
└── logs/                   # Directory for all system logs
    ├── youtube_videos.json # Details of all videos
    ├── watch_time.json     # Current watch time stats
    ├── theme_cache.json    # Cached theme classifications
    └── session.log         # Session activity log
```

## 🔧 Troubleshooting

### TV Connection Issues

- **TV Not Detected**: Ensure your TV and computer are on the same network
- **Connection Refused**: Verify the TV IP address is correct in your .env file
- **Authorization Required**: Accept any connection prompts on your TV
- **Unsupported TV**: This application works best with Samsung TVs from 2016 onwards

### API Issues

- **API Errors**: Verify your API keys are correct and have the necessary permissions
- **Rate Limiting**: The free tier of OpenAI API has usage limits
- **YouTube API Quota**: Be aware of YouTube API quota limits (daily requests)

## 🛡️ Privacy & Data

All data is stored locally on your computer. No viewing data is sent to external servers except:
- Video IDs sent to YouTube API to fetch metadata
- Video titles/descriptions sent to OpenAI for classification

## 🔄 Extending the System

The modular architecture makes it easy to:

- **Replace OpenAI**: Swap the theme classifier with a local model
- **Add More Alerts**: Extend the notification system with SMS or mobile alerts
- **Custom Analytics**: Build your own reports on viewing habits

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [samsungtvws](https://github.com/xchwarze/samsung-tv-ws-api) for Samsung TV communication
- OpenAI for theme classification
- YouTube Data API for video metadata

## 📣 Feedback and Contributions

Feedback and contributions are welcome! Please feel free to submit a pull request or open an issue.
