"""
Configuration management for the Telegram News Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the bot"""
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = "7452324631:AAHFMFgb5s2Ef5YRTRDNxFNcb4ik-ETz_Tc"
    TELEGRAM_CHANNEL_ID = "-1002294392721"  # Note: Channel IDs need -100 prefix
    
    # Webhook Configuration
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PATH = "/webhook"
    WEBHOOK_PORT = 8443
    
    # Scraping Configuration - Using RSS feeds for better reliability
    NEWS_SOURCES = {
        'yahoo_finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
        'marketwatch': 'https://feeds.marketwatch.com/marketwatch/realtimeheadlines/',
        'investing_rss': 'https://www.investing.com/rss/news.rss',
        'reuters_business': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'
    }
    SCRAPE_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", "60"))
    MAX_ARTICLES_PER_SCRAPE = int(os.getenv("MAX_ARTICLES_PER_SCRAPE", "10"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/bot.log"
    
    # Headers for web scraping (to avoid being blocked)
    REQUEST_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True) 