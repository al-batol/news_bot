#!/usr/bin/env python3
"""
FREE Configuration for Arabic Financial News Bot
No API keys required except Telegram Bot Token
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Free configuration - no external API keys needed"""
    
    # Telegram Configuration (ONLY REQUIRED)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7452324631:AAHFMFgb5s2Ef5YRTRDNxFNcb4ik-ETz_Tc')
    TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '-1001870604395')
    
    # AI TRANSLATION WITH GROQ (FREE API)
    USE_AI_TRANSLATION = True   # Enable Groq API for better Arabic translation
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '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')  # Free Groq API key
    ENABLE_ARABIC = True        # Enable/disable Arabic translation (True=Arabic, False=English only)
    USE_IMAGES = False         # FREE: No images, text only
    
    # Not needed for free version
    OPENAI_API_KEY = ''
    UNSPLASH_ACCESS_KEY = ''
    
    # SCRAPING MODE CONFIGURATION
    # 1 = Scrape only investing.com (all related RSS)
    # 2 = Scrape only CoinDesk
    # 3 = Scrape both investing.com and CoinDesk
    # 4 = Scrape RSS sources (CoinDesk + Cointelegraph)
    # 5 = Scrape only Cointelegraph (Arabic if ENABLE_ARABIC is True) - NEW MODE
    SCRAPING_MODE = int(os.getenv('SCRAPING_MODE', '5'))  # Default: Cointelegraph only (with Arabic support)
    
    # Investing.com scraping configuration (replaces RSS feeds)
    INVESTING_NEWS_SECTIONS = [
        'headlines',
        'economic-indicators', 
        'forex-news',
        'commodities-news',
        'stock-market-news',
        'cryptocurrency-news'
    ]
    
    # RSS News Sources Configuration - Both CoinDesk and Cointelegraph
    NEWS_SOURCES = {
        'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'cointelegraph': 'https://cointelegraph.com/rss'
    }
    
    # Arabic Cointelegraph RSS URL (used when ENABLE_ARABIC is True)
    COINTELEGRAPH_ARABIC_RSS_URL = 'https://ar.cointelegraph.com/feed'
    
    # Cointelegraph only sources (for mode 5)
    COINTELEGRAPH_SOURCES = {
        'cointelegraph': 'https://cointelegraph.com/rss'
    }
    
    # Arabic Cointelegraph only sources (for mode 5 with Arabic enabled)
    COINTELEGRAPH_ARABIC_SOURCES = {
        'cointelegraph_arabic': 'https://ar.cointelegraph.com/feed'
    }
    
    # Legacy CoinDesk RSS configuration (for compatibility)
    COINDESK_RSS_URL = 'https://www.coindesk.com/arc/outboundfeeds/rss/'
    
    # Resource optimization settings for 400MB RAM, better performance
    SCRAPER_CONFIG = {
        'max_concurrent_requests': 5,  # Increased concurrent connections
        'request_delay_min': 2,        # Minimum delay between requests (anti-ban)
        'request_delay_max': 4,        # Maximum delay between requests
        'max_articles_per_section': 4, # More articles per section
        'memory_cleanup_threshold': 200, # Higher cache threshold
    }
    
    # Enhanced News Filtering Keywords - Financial Focus
    STOCK_KEYWORDS = [
        'stock', 'shares', 'equity', 'nasdaq', 'nyse', 'dow jones', 'sp500', 's&p 500',
        'earnings', 'dividend', 'ipo', 'market cap', 'trading', 'bull market', 'bear market',
        'apple', 'microsoft', 'google', 'tesla', 'amazon', 'meta', 'nvidia', 'berkshire'
    ]
    
    CRYPTO_KEYWORDS = [
        'bitcoin', 'ethereum', 'crypto', 'cryptocurrency', 'blockchain', 'defi', 'nft',
        'binance', 'coinbase', 'solana', 'cardano', 'dogecoin', 'ripple', 'xrp', 'btc', 'eth'
    ]
    
    MARKET_IMPACT_KEYWORDS = [
        'federal reserve', 'fed', 'interest rate', 'inflation', 'recession', 'gdp',
        'unemployment', 'jobs report', 'trump', 'tariff', 'trade war', 'china trade',
        'jerome powell', 'janet yellen', 'oil price', 'war', 'ukraine', 'russia'
    ]
    
    # All relevant keywords combined
    RELEVANT_KEYWORDS = STOCK_KEYWORDS + CRYPTO_KEYWORDS + MARKET_IMPACT_KEYWORDS
    
    # Bot Configuration - Performance optimized (400MB RAM allowed)
    SCRAPE_INTERVAL_SECONDS = int(os.getenv('SCRAPE_INTERVAL_SECONDS', '180'))  # 3 minutes for faster updates
    MAX_ARTICLES_PER_SCRAPE = int(os.getenv('MAX_ARTICLES_PER_SCRAPE', '8'))   # Increased for better coverage
    MAX_ECONOMIC_EVENTS = int(os.getenv('MAX_ECONOMIC_EVENTS', '5'))           # More economic events
    
    # Request Headers
    REQUEST_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/free_bot.log')
    
    # Environment Settings
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'free')
    DEBUG = bool(os.getenv('DEBUG', 'False'))
    
    # Database Settings - Production optimized for better performance
    DATABASE_FILE = os.getenv('DATABASE_FILE', 'production_seen_articles.json')
    MAX_DATABASE_SIZE = int(os.getenv('MAX_DATABASE_SIZE', '3000'))  # Increased for better performance
    
    # Rate Limiting - Anti-ban optimization
    MESSAGE_DELAY_SECONDS = int(os.getenv('MESSAGE_DELAY_SECONDS', '6'))  # Slower to avoid Telegram limits
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '2'))  # Reduced retries to save resources
    
    # Memory optimization settings - Performance mode
    ENABLE_MEMORY_OPTIMIZATION = True
    MAX_MEMORY_CACHE_SIZE = 150  # Increased cache for better performance (400MB RAM)
    CLEANUP_INTERVAL = 15        # Less frequent cleanup for better performance
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration"""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN or cls.TELEGRAM_BOT_TOKEN == 'your_bot_token_here':
            errors.append("TELEGRAM_BOT_TOKEN not properly configured")
            
        if not cls.TELEGRAM_CHANNEL_ID:
            errors.append("TELEGRAM_CHANNEL_ID not configured")
            
        return errors
    
    @classmethod
    def get_config_summary(cls):
        """Get a summary of current configuration"""
        return {
            'environment': cls.ENVIRONMENT,
            'channel_id': cls.TELEGRAM_CHANNEL_ID,
            'scrape_interval': cls.SCRAPE_INTERVAL_SECONDS,
            'ai_translation': cls.USE_AI_TRANSLATION,
            'images_enabled': cls.USE_IMAGES,
            'max_articles': cls.MAX_ARTICLES_PER_SCRAPE,
            'investing_sections': len(cls.INVESTING_NEWS_SECTIONS),
            'relevant_keywords': len(cls.RELEVANT_KEYWORDS),
            'memory_optimization': cls.ENABLE_MEMORY_OPTIMIZATION
        } 