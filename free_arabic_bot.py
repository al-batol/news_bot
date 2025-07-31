#!/usr/bin/env python3
"""
FREE Arabic Financial News Bot
No API keys required except Telegram Bot Token
"""
import asyncio
import aiohttp
import logging
import json
import re
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# Import enhanced modules
from config_free import Config
from deep_translator import GoogleTranslator
from ai_translator import AITranslator
from crypto_arabic_formatter import CryptoArabicFormatter
from rss_scraper import RSSNewsScraper
from database import ArticleDatabase
from error_handler import setup_logging

logger = logging.getLogger(__name__)

class FreeArabicNewsBot:
    """Enhanced Arabic crypto news bot with AI translation"""
    
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.channel_id = Config.TELEGRAM_CHANNEL_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.running = False
        
        # Initialize components
        self.scraper = RSSNewsScraper()
        self.database = ArticleDatabase(Config.DATABASE_FILE)
        self.formatter = CryptoArabicFormatter()
        
        # Initialize AI translator (FREE)
        if Config.USE_AI_TRANSLATION:
            try:
                self.ai_translator = AITranslator(Config.GROQ_API_KEY)
                logger.info("AI Translator initialized with Groq API (FREE)")
            except Exception as e:
                logger.error(f"Failed to initialize AI translator: {e}")
                self.ai_translator = None
        else:
            self.ai_translator = None
        
        # Fallback Google Translator
        try:
            self.translator = GoogleTranslator(source='en', target='ar')
            logger.info("Google Translator initialized as fallback")
        except Exception as e:
            logger.error(f"Failed to initialize Google translator: {e}")
            self.translator = None
        
        # Enhanced country/asset detection for flags  
        self.country_flags = {
            # Crypto assets (priority)
            'bitcoin': '₿', 'btc': '₿', 'crypto': '🪙', 'cryptocurrency': '🪙',
            'ethereum': '🔷', 'eth': '🔷', 'defi': '🏗️', 'nft': '🎨',
            'binance': '🔸', 'coinbase': '🔵', 'blockchain': '⛓️',
            
            # Countries
            'united states': '🇺🇸', 'us': '🇺🇸', 'usa': '🇺🇸', 'america': '🇺🇸', 'american': '🇺🇸',
            'federal reserve': '🏦', 'fed': '🏦', 'nasdaq': '🇺🇸', 'nyse': '🇺🇸', 'dow': '🇺🇸',
            'china': '🇨🇳', 'chinese': '🇨🇳', 'europe': '🇪🇺', 'european': '🇪🇺',
            'uk': '🇬🇧', 'britain': '🇬🇧', 'japan': '🇯🇵', 'japanese': '🇯🇵',
            
            # Commodities
            'oil': '🛢️', 'gold': '🥇', 'silver': '🥈', 'copper': '🟫',
        }
        
        # Performance tracking
        self.stats = {
            'messages_sent': 0,
            'articles_processed': 0,
            'translation_successes': 0,
            'start_time': datetime.now(timezone.utc)
        }
        
        logger.info("Free Arabic News Bot initialized")
    
    def detect_country_flag(self, title: str, summary: str = "") -> str:
        """Detect appropriate flag emoji based on content with crypto priority"""
        content = f"{title} {summary}".lower()
        
        # Check crypto assets first (higher priority)
        crypto_flags = ['₿', '🪙', '🔷', '🔸', '🔵', '⛓️', '🏗️', '🎨']
        for keyword, flag in self.country_flags.items():
            if keyword in content and flag in crypto_flags:
                return flag
        
        # Check other flags
        for keyword, flag in self.country_flags.items():
            if keyword in content:
                return flag
        
        return '🪙'  # Default to crypto emoji for crypto-focused bot
    
    def is_relevant_news(self, title: str, summary: str = "") -> bool:
        """Enhanced relevance check with crypto priority"""
        content = f"{title} {summary}".lower()
        
        # Prioritize crypto content (higher relevance)
        crypto_score = 0
        for keyword in Config.CRYPTO_KEYWORDS:
            if keyword.lower() in content:
                crypto_score += 2  # Higher weight for crypto
        
        # Check financial/market keywords
        financial_score = 0
        for keyword in Config.STOCK_KEYWORDS + Config.MARKET_IMPACT_KEYWORDS:
            if keyword.lower() in content:
                financial_score += 1
        
        total_score = crypto_score + financial_score
        
        # Strong exclusions
        exclusions = [
            'sports', 'entertainment', 'celebrity', 'weather', 'music', 'game',
            'fashion', 'travel', 'food', 'recipe', 'movie', 'tv show', 'netflix',
            'health tips', 'diet', 'exercise', 'workout', 'beauty', 'lifestyle'
        ]
        
        for exclusion in exclusions:
            if exclusion in content:
                return False
        
        # Crypto news gets priority (score >= 2)
        # Financial news needs score >= 1
        # General economic news with high impact gets through
        return total_score >= 1
    
    async def translate_to_arabic(self, text: str, context: str = "crypto news") -> str:
        """Translate text to Arabic using AI or Google Translate (optimized)"""
        
        # Skip translation for very short text
        if len(text.strip()) < 10:
            return text
        
        # Try AI translation first if available (with quick timeout)
        if self.ai_translator and self.ai_translator.client:
            try:
                translation = await self.ai_translator.translate_to_arabic(text, context)
                if translation and translation != text:  # Check if translation actually worked
                    self.stats['translation_successes'] += 1
                    logger.info("AI translation successful")
                    return translation
            except Exception as e:
                logger.warning(f"AI translation failed quickly, using Google fallback: {e}")
        
        # Fallback to Google Translate (faster and more reliable)
        if self.translator:
            try:
                # Clean text
                text = re.sub(r'<[^>]+>', '', text)  # Remove HTML
                text = re.sub(r'\s+', ' ', text).strip()  # Clean whitespace
                
                if len(text) > 800:
                    text = text[:800] + "..."
                
                # Translate
                translation = self.translator.translate(text)
                self.stats['translation_successes'] += 1
                logger.info("Google translation successful")
                return translation
                
            except Exception as e:
                logger.error(f"Google translation failed: {e}")
        
        return text  # Return original if all translation fails
    
    async def send_message(self, text: str) -> bool:
        """Send message to Telegram channel"""
        try:
            # Add retry logic for network issues
            for attempt in range(Config.MAX_RETRIES):
                try:
                    async with aiohttp.ClientSession() as session:
                        data = {
                            'chat_id': self.channel_id,
                            'text': text,
                            'disable_web_page_preview': True
                        }
                        
                        async with session.post(f"{self.base_url}/sendMessage", json=data, timeout=10) as response:
                            if response.status == 200:
                                result = await response.json()
                                if result.get('ok'):
                                    self.stats['messages_sent'] += 1
                                    logger.info("Message sent successfully")
                                    return True
                                else:
                                    logger.error(f"Telegram API error: {result.get('description')}")
                                    return False
                            else:
                                logger.error(f"HTTP error: {response.status}")
                                if attempt < Config.MAX_RETRIES - 1:
                                    await asyncio.sleep(5)  # Wait before retry
                                    continue
                                return False
                                
                except aiohttp.ClientError as e:
                    logger.error(f"Network error (attempt {attempt + 1}): {e}")
                    if attempt < Config.MAX_RETRIES - 1:
                        await asyncio.sleep(10)  # Wait longer for network issues
                        continue
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def format_arabic_message(self, article) -> str:
        """Format article as enhanced Arabic crypto/financial message (OPTIMIZED)"""
        try:
            # Determine context for better translation
            content = f"{article.title} {getattr(article, 'summary', '')}"
            context = "cryptocurrency news" if any(crypto in content.lower() for crypto in ['bitcoin', 'crypto', 'ethereum']) else "financial news"
            
            # Check if this is economic data first (to avoid unnecessary translation)
            economic_data = self.formatter.extract_economic_data(article.title, getattr(article, 'summary', ''))
            
            # Only translate if not economic data (economic data uses Arabic names already)
            if economic_data and economic_data.get('has_data'):
                # For economic data, use the Arabic name directly
                arabic_title = economic_data.get('arabic_name', article.title)
                # Skip market analysis API call for economic data - use built-in logic
                market_analysis = {'impact': 'محايد', 'currency': 'الدولار الأمريكي'}
            else:
                # For non-economic news, translate normally
                arabic_title = await self.translate_to_arabic(article.title, context)
                # Skip market analysis for non-economic news to save API calls
                market_analysis = {'impact': 'محايد', 'currency': 'السوق'}
            
            # Use enhanced formatter for professional-style messages
            message = await self.formatter.format_enhanced_arabic_news(
                article, arabic_title, market_analysis
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting enhanced Arabic message: {e}")
            # Fallback to simple format
            flag = self.detect_country_flag(article.title, getattr(article, 'summary', ''))
            return f"عاجل: {flag} {article.title}\n\nتابعنا لكل جديد : @news_news127"
    
    async def post_articles(self, articles):
        """Post filtered articles to Telegram channel"""
        posted_count = 0
        
        # Filter articles for relevance
        relevant_articles = []
        for article in articles:
            if self.is_relevant_news(article.title, getattr(article, 'summary', '')):
                relevant_articles.append(article)
        
        logger.info(f"Found {len(relevant_articles)} relevant articles from {len(articles)} total")
        
        # Limit to max articles per scrape
        relevant_articles = relevant_articles[:Config.MAX_ARTICLES_PER_SCRAPE]
        
        for article in relevant_articles:
            try:
                # Check if already posted
                if self.database.is_article_seen(article.article_id):
                    continue
                
                self.stats['articles_processed'] += 1
                
                # Format Arabic message
                message = await self.format_arabic_message(article)
                
                # Send message
                success = await self.send_message(message)
                
                if success:
                    # Mark as seen in database
                    self.database.mark_article_seen(
                        article.article_id,
                        article.title,
                        article.link,
                        getattr(article, 'published', datetime.now(timezone.utc).isoformat())
                    )
                    
                    posted_count += 1
                    logger.info(f"Posted Arabic article: {article.title[:50]}...")
                    
                    # Add delay between posts
                    await asyncio.sleep(Config.MESSAGE_DELAY_SECONDS)
                else:
                    logger.error(f"Failed to post Arabic article: {article.title[:50]}...")
                    
            except Exception as e:
                logger.error(f"Error posting Arabic article: {e}")
                continue
        
        return posted_count
    
    async def check_for_news(self):
        """Check for new articles and post them"""
        try:
            logger.info("Checking for new financial news...")
            
            # Get new articles from RSS sources with retry logic
            articles = []
            for attempt in range(Config.MAX_RETRIES):
                try:
                    articles = await self.scraper.get_latest_news()
                    if articles:
                        break
                except Exception as e:
                    logger.error(f"RSS fetch attempt {attempt + 1} failed: {e}")
                    if attempt < Config.MAX_RETRIES - 1:
                        await asyncio.sleep(10)
            
            if articles:
                posted = await self.post_articles(articles)
                logger.info(f"Posted {posted} new Arabic articles from {len(articles)} found")
            else:
                logger.info("No new articles found (network or RSS issues)")
                
            # Cleanup database if it gets too large
            if self.database.get_article_count() > Config.MAX_DATABASE_SIZE:
                self.database.cleanup_old_articles(Config.MAX_DATABASE_SIZE // 2)
            
            # Periodic cleanup of RSS scraper cache to ensure fresh content
            self.scraper.periodic_cache_cleanup()
                
        except Exception as e:
            logger.error(f"Error checking for news: {e}")
    
    async def run(self):
        """Main run loop"""
        try:
            self.running = True
            logger.info("Starting FREE Arabic Financial News Bot...")
            
            # Validate configuration
            config_errors = Config.validate_config()
            if config_errors:
                for error in config_errors:
                    logger.error(f"Configuration error: {error}")
                return
            
            # Log configuration summary
            config_summary = Config.get_config_summary()
            logger.info(f"Bot configuration: {config_summary}")
            
            # Send startup message
            startup_message = (
                f"🚀 بوت الأخبار المالية العربي!\n\n"
                f"تابعنا لكل جديد : @news_news127"
            )
            
            # Try to send startup message
            startup_sent = await self.send_message(startup_message)
            if startup_sent:
                logger.info("Startup message sent successfully")
            else:
                logger.warning("Failed to send startup message - continuing anyway")
            
            # Main loop
            while self.running:
                try:
                    await self.check_for_news()
                    
                    # Wait for next cycle
                    logger.info(f"Waiting {Config.SCRAPE_INTERVAL_SECONDS} seconds until next check...")
                    await asyncio.sleep(Config.SCRAPE_INTERVAL_SECONDS)
                    
                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    # Wait before retrying
                    await asyncio.sleep(30)
                    
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.running = False
            if self.scraper:
                await self.scraper.close_session()
            logger.info("Free Arabic bot stopped")

async def main():
    """Main function"""
    # Set up logging
    setup_logging(Config.LOG_LEVEL)
    
    print("🇸🇦 🤖 FREE Arabic Financial News Bot")
    print("=" * 60)
    print("🤖 AI-Powered Translation (Groq - FREE)")
    print("💎 Enhanced Crypto Market Focus")
    print("📊 Professional Arabic Formatting")
    print("🔥 Real-time Market Impact Analysis")
    print(f"📱 Channel: {Config.TELEGRAM_CHANNEL_ID}")
    print(f"⏱️  Update Interval: {Config.SCRAPE_INTERVAL_SECONDS} seconds")
    print(f"🌍 Environment: {Config.ENVIRONMENT}")
    print("=" * 60)
    
    bot = FreeArabicNewsBot()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 وداعاً! (Goodbye!)")
    except Exception as e:
        print(f"\n💥 خطأ فادح: {e}")
        logger.error(f"Fatal error: {e}")
    print("🔚 انتهى!") 