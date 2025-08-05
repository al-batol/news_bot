# Telegram Financial News Bot

A real-time Telegram bot that scrapes financial news from Investing.com and posts updates to a Telegram channel.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Bot
Update the credentials in `config.py`:
```python
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHANNEL_ID = "your_channel_id_here"  
```

### 3. Test Setup
```bash
# Test scraping functionality
python run_bot.py --scrape-test

# Run complete test suite  
python run_bot.py --test
```

### 4. Run Bot
```bash
# Simple polling mode (recommended for testing)
python run_bot.py --polling

# Webhook mode with ngrok (for production)
python run_bot.py --webhook
```

### 5. Bot Commands
- `/start` - Initialize bot
- `/status` - Check bot health  
- `/test` - Manual scraping test
- `/reset` - Reset seen articles database

## Development Environment Setup

### Prerequisites

1. **Python 3.8+** - Required for async/await support and modern libraries
2. **pip** - Python package manager
3. **Git** - Version control (optional but recommended)
4. **Ngrok account** - For webhook tunneling (free tier available)

### Required Libraries

```bash
pip install requests
pip install beautifulsoup4
pip install python-telegram-bot
pip install aiohttp
pip install apscheduler
pip install python-dotenv
pip install lxml
```

### Development Tools

1. **BeautifulSoup4** - HTML parsing for web scraping
2. **requests/aiohttp** - HTTP client libraries (requests for sync, aiohttp for async)
3. **python-telegram-bot** - Modern Telegram Bot API wrapper with async support
4. **APScheduler** - Advanced Python Scheduler for periodic tasks
5. **python-dotenv** - Environment variable management
6. **lxml** - Fast XML/HTML parser (optional, for better performance)

### Project Structure

```
news_scraping/
├── requirements.txt
├── .env
├── main.py                 # Main bot application
├── scraper.py             # News scraping logic
├── config.py              # Configuration management
├── database.py            # Simple file-based storage for seen articles
├── webhook_handler.py     # Webhook endpoint handler
└── logs/                  # Application logs
```

### Setup Steps

1. Install Python 3.8+ and pip
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file with bot credentials
6. Install and setup Ngrok for webhook testing
7. Test scraping functionality independently
8. Test Telegram bot integration
9. Deploy with webhook configuration

### Environment Variables Required

- `TELEGRAM_BOT_TOKEN` - Bot token from BotFather
- `TELEGRAM_CHANNEL_ID` - Target channel ID
- `NGROK_AUTHTOKEN` - Ngrok authentication token (optional)
- `WEBHOOK_URL` - Ngrok tunnel URL for webhooks
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR) 