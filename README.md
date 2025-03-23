# Samsung TV YouTube Monitor

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
