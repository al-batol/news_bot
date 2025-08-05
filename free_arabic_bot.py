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
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import pytz

# Import enhanced modules
from config_free import Config
from deep_translator import GoogleTranslator
from ai_translator import AITranslator
from crypto_arabic_formatter import CryptoArabicFormatter
from investing_scraper import InvestingNewsScraper, EconomicEvent
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
        self.scraper = InvestingNewsScraper()
        self.rss_scraper = RSSNewsScraper()  # NEW: RSS scraper for CoinDesk + Cointelegraph
        self.database = ArticleDatabase('production_seen_articles.json')  # Use production database
        self.formatter = CryptoArabicFormatter()
        
        # Economic calendar DISABLED per user request
        # self.pending_events = []
        # self.last_calendar_check = None
        
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
        
        # 🕐 CONDITIONAL: Set timezone based on SCRAPING_MODE
        # if Config.SCRAPING_MODE == 2:  # CoinDesk only
        #     saudi_tz = pytz.timezone('Asia/Riyadh')
        #     self.startup_time = datetime.now(timezone.utc)
        #     logger.info(f"🪙 CoinDesk Mode: Bot started at {self.startup_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (UTC timezone)")
        # elif Config.SCRAPING_MODE == 3:  # Both sources  
        #     saudi_tz = pytz.timezone('Asia/Riyadh')
        #     self.startup_time = datetime.now(saudi_tz)
        #     logger.info(f"🌐 Mixed Mode: Bot started at {self.startup_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (KSA timezone for CoinDesk only)")
        # else:  # Mode 1: Investing.com only
        self.startup_time = datetime.now(timezone.utc)
        logger.info(f"📰 Investing Mode: Bot started at {self.startup_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (original timing)")
        
        # Performance tracking
        self.stats = {
            'messages_sent': 0,
            'articles_processed': 0,
            'translation_successes': 0,
            'start_time': self.startup_time
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
    
    def _get_section_emoji(self, section: str) -> str:
        """🎨 Get emoji based on article section"""
        section = section.upper()
        
        if 'CRYPTO' in section:
            return '₿'
        elif 'FOREX' in section:
            return '💱'
        elif 'STOCK' in section:
            return '📈'
        elif 'ECONOMIC' in section:
            return '🏛️'
        elif 'COMMODITIES' in section:
            return '🛢️'
        elif 'BREAKING' in section:
            return '🚨'
        else:
            return '📰'
    
    def is_relevant_news(self, title: str, summary: str = "") -> bool:
        """🎯 STRICT: Financial markets content ONLY - NO world news, politics, or wars"""
        content = f"{title} {summary}".lower()
        
        # ✅ REQUIRED: Must contain financial market keywords
        crypto_score = 0
        for keyword in Config.CRYPTO_KEYWORDS:
            if keyword.lower() in content:
                crypto_score += 2  # Higher weight for crypto
        
        # ✅ EXPANDED FINANCIAL KEYWORDS: Comprehensive coverage for all financial content
        financial_keywords = [
            # Core Financial
            'stock', 'share', 'market', 'trading', 'investor', 'investment', 'portfolio', 'dividend',
            'earnings', 'revenue', 'profit', 'loss', 'ipo', 'merger', 'acquisition', 'buyback',
            
            # Economic Indicators  
            'fed', 'federal reserve', 'interest rate', 'inflation', 'gdp', 'unemployment', 'job',
            'consumer price', 'ppi', 'cpi', 'retail sales', 'housing', 'manufacturing',
            
            # Forex & Currencies
            'dollar', 'euro', 'yen', 'pound', 'currency', 'forex', 'exchange rate', 'devaluation',
            'central bank', 'monetary policy', 'quantitative easing',
            
            # Commodities & Energy
            'oil', 'crude', 'gold', 'silver', 'copper', 'wheat', 'corn', 'natural gas', 'commodity',
            'opec', 'energy', 'mining', 'metals', 'agriculture',
            
            # Crypto (additional)
            'blockchain', 'defi', 'nft', 'stablecoin', 'altcoin', 'binance', 'coinbase',
            
            # 🔥 EXPANDED: Major Companies & Financial Terms
            'apple', 'tesla', 'microsoft', 'google', 'amazon', 'meta', 'nvidia', 'berkshire',
            'ceo', 'cfo', 'president', 'company', 'corporation', 'firm', 'business', 'financial',
            'bank', 'banking', 'credit', 'loan', 'reserves', 'fund', 'finance', 'capital',
            'imf', 'world bank', 'economic', 'economy', 'tariff', 'trade', 'export', 'import',
            'sales', 'growth', 'decline', 'billion', 'million', 'lawsuit', 'jury', 'settlement',
            'regulatory', 'regulation', 'policy', 'announcement', 'guidance', 'forecast'
        ]
        
        financial_score = 0
        for keyword in financial_keywords:
            if keyword in content:
                financial_score += 1
        
        total_score = crypto_score + financial_score
        
        # 🎯 STRICT REQUIREMENT: Must be financial markets content
        if total_score >= 1:
            logger.debug(f"✅ APPROVED: Score {total_score} - '{title[:50]}...'")
            return True
        else:
            logger.debug(f"🚫 EXCLUDED (not financial): Score {total_score} - '{title[:50]}...'")
            return False
    
    def is_text_arabic(self, text: str) -> bool:
        """Check if text is already in Arabic"""
        if not text:
            return False
        
        # Count Arabic characters
        arabic_chars = 0
        total_letters = 0
        
        for char in text:
            if char.isalpha():
                total_letters += 1
                # Arabic Unicode range: U+0600 to U+06FF
                if '\u0600' <= char <= '\u06FF':
                    arabic_chars += 1
        
        if total_letters == 0:
            return False
        
        # If more than 70% of letters are Arabic, consider it Arabic text
        arabic_ratio = arabic_chars / total_letters
        return arabic_ratio > 0.7

    async def translate_to_arabic(self, text: str, context: str = "crypto news") -> str:
        """Translate text to Arabic using AI or Google Translate (optimized)"""
        
        # Skip translation for very short text
        if len(text.strip()) < 10:
            return text
        
        # NEW: Skip translation if text is already in Arabic
        if self.is_text_arabic(text):
            logger.info("Text is already in Arabic, skipping translation")
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
    
    async def send_message(self, text: str, image_url: str = None) -> bool:
        """Send message to Telegram channel with optional image"""
        try:
            # Add retry logic for network issues
            for attempt in range(Config.MAX_RETRIES):
                try:
                    async with aiohttp.ClientSession() as session:
                        # 📸 NEW: Send with image if available
                        if image_url:
                            # Send as photo with caption
                            data = {
                                'chat_id': self.channel_id,
                                'photo': image_url,
                                'caption': text,
                                'parse_mode': 'HTML'
                            }
                            endpoint = f"{self.base_url}/sendPhoto"
                            logger.info(f"📸 Sending message with image: {image_url}")
                        else:
                            # Send as text message (as before)
                            data = {
                                'chat_id': self.channel_id,
                                'text': text,
                                'disable_web_page_preview': True
                            }
                            endpoint = f"{self.base_url}/sendMessage"
                        
                        async with session.post(endpoint, json=data, timeout=10) as response:
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
        """🌍 FLEXIBLE: Format article as Arabic (if enabled) or English financial message"""
        try:
            # 🚀 CHECK CONFIG: Skip Arabic translation if disabled
            if not Config.ENABLE_ARABIC:
                # 🇺🇸 ENGLISH ONLY MODE: Send news directly without translation
                section_emoji = self._get_section_emoji(getattr(article, 'section', ''))
                flag = self.detect_country_flag(article.title, getattr(article, 'summary', ''))
                
                message = f"🚨 {section_emoji} {flag} BREAKING: {article.title}\n\n"
                
                # Only add description if it exists and is meaningful (not empty)
                if hasattr(article, 'summary') and article.summary and article.summary.strip():
                    message += f"📝 {article.summary}\n\n"
                
                # message += f"📊 Section: {getattr(article, 'section', 'Financial News')}\n"
                # message += f"⏰ {getattr(article, 'published', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'))}\n\n"
                message += "📈 Follow us: @news_crypto_911"
                
                return message
            
            # 🇸🇦 ARABIC MODE: Original Arabic translation flow
            # Determine context for better translation
            content = f"{article.title} {getattr(article, 'summary', '')}"
            context = "cryptocurrency news" if any(crypto in content.lower() for crypto in ['bitcoin', 'crypto', 'ethereum']) else "financial news"
            
            # Translate title to Arabic
            arabic_title = await self.translate_to_arabic(article.title, context)
            
            # Simple market analysis (no API calls for efficiency)
            market_analysis = {'impact': 'محايد', 'currency': 'الدولار الأمريكي'}
            
            # Use enhanced formatter for professional-style messages
            message = await self.formatter.format_enhanced_arabic_news(
                article, arabic_title, market_analysis
            )
            
            return message
            
        except Exception as e:
            logger.error(f"💥 Error formatting message: {e}")
            # 🛡️ ROBUST FALLBACK: Based on config setting
            flag = self.detect_country_flag(article.title, getattr(article, 'summary', ''))
            section_emoji = self._get_section_emoji(getattr(article, 'section', ''))
            
            if Config.ENABLE_ARABIC:
                return f"عاجل: {section_emoji} {flag} {article.title}\n\nتابعنا لكل جديد : @news_crypto_911"
            else:
                return f"🚨 {section_emoji} {flag} BREAKING: {article.title}\n\nFollow us: @news_crypto_911"
    
    async def post_articles(self, articles):
        """Post filtered articles to Telegram channel"""
        posted_count = 0
        
        # 🚀 CONDITIONAL TIMING: Apply different logic based on SCRAPING_MODE and source
        fresh_articles = []
        for article in articles:
            try:
                # 🚫 SKIP: Already seen articles (early filtering)
                if self.database.is_article_seen(article.article_id):
                    continue
                
                # 🎯 SMART FILTERING: Only apply advanced timezone filtering for specific modes
                should_apply_timezone_filter = self._should_apply_timezone_filtering(article)
                
                if not should_apply_timezone_filter:
                    # 📰 ORIGINAL LOGIC: No timezone filtering (Mode 1 or Investing.com in Mode 3)
                    fresh_articles.append(article)
                    continue
                
                # Parse article publish time (for timezone filtering)
                if hasattr(article, 'published') and article.published:
                    # Handle different date formats
                    published_time = None
                    if isinstance(article.published, str):
                        # Try different datetime formats (CoinDesk uses RFC 2822 format)
                        date_formats = [
                            '%a, %d %b %Y %H:%M:%S %z',    # CoinDesk format: "Sat, 02 Aug 2025 16:43:51 +0000"
                            '%Y-%m-%d %H:%M:%S %z',
                            '%Y-%m-%d %H:%M:%S', 
                            '%Y-%m-%d %H:%M', 
                            '%a, %d %b %Y %H:%M:%S %Z',
                            '%a, %d %b %Y %H:%M:%S'         # Fallback without timezone
                        ]
                        
                        for fmt in date_formats:
                            try:
                                published_time = datetime.strptime(article.published, fmt)
                                if published_time.tzinfo is None:
                                    published_time = published_time.replace(tzinfo=timezone.utc)
                                logger.debug(f"🕒 Parsed time: {published_time} from format {fmt}")
                                break
                            except ValueError:
                                continue
                    
                    # If we couldn't parse time, include the article (better safe than sorry)
                    if published_time is None:
                        fresh_articles.append(article)
                        continue
                    
                    # ✅ FIXED: Saudi Arabia timezone filtering with proper tolerance
                    saudi_tz = pytz.timezone('Asia/Riyadh')
                    current_time = datetime.now(saudi_tz)
                    time_tolerance = timedelta(hours=3)  # Increased tolerance for fresh news
                    max_future_time = current_time + timedelta(minutes=30)  # Allow 30 min future articles
                    
                    # Convert published_time to Saudi timezone for comparison
                    if published_time.tzinfo is not None:
                        published_time_saudi = published_time.astimezone(saudi_tz)
                    else:
                        # If no timezone info, assume UTC and convert
                        published_time = published_time.replace(tzinfo=timezone.utc)
                        published_time_saudi = published_time.astimezone(saudi_tz)
                    
                    logger.debug(f"🇸🇦 TIME COMPARISON: Article: {published_time_saudi} vs Current: {current_time}")
                    
                    # ✅ SIMPLIFIED: Check if article is within the last 3 hours (fresh news)
                    min_time = current_time - time_tolerance  # 3 hours back
                    is_fresh = min_time <= published_time_saudi <= max_future_time
                    
                    # 🪙 Special handling for crypto news (more lenient)
                    if hasattr(article, 'section') and 'CRYPTO' in article.section.upper():
                        crypto_tolerance = timedelta(hours=4)  # 4 hours for crypto
                        crypto_min_time = current_time - crypto_tolerance
                        is_fresh = crypto_min_time <= published_time_saudi <= max_future_time
                        logger.debug(f"🪙 CRYPTO: {article.title[:40]}... ({published_time_saudi.strftime('%H:%M')} KSA) - {'✅ FRESH' if is_fresh else '❌ OLD'}")
                    else:
                        logger.debug(f"📰 NEWS: {article.title[:40]}... ({published_time_saudi.strftime('%H:%M')} KSA) - {'✅ FRESH' if is_fresh else '❌ OLD'}")
                    
                    if is_fresh:
                        fresh_articles.append(article)
                        logger.debug(f"✅ FRESH: {article.title[:50]}... (published: {published_time_saudi})")
                    elif published_time_saudi > max_future_time:
                        logger.debug(f"🔮 FUTURE: Skipping {article.title[:50]}... (published: {published_time_saudi}) - too far in future")
                    else:
                        logger.debug(f"⏰ OLD: Skipping {article.title[:50]}... (published: {published_time_saudi})")
                else:
                    # No publish time, include it
                    fresh_articles.append(article)
            except Exception as e:
                logger.debug(f"Error parsing article time: {e}")
                # If error parsing time, include the article
                fresh_articles.append(article)
        
        relevant_articles = fresh_articles
         
        # 📊 SMART LOGGING: Show different messages based on filtering mode
        if Config.SCRAPING_MODE == 1:
            logger.info(f"📰 INVESTING ONLY: Using {len(relevant_articles)} articles from {len(articles)} total (original timing)")
        elif Config.SCRAPING_MODE == 2:
            logger.info(f"🪙 COINDESK ONLY: Using {len(relevant_articles)} fresh articles from {len(articles)} total (KSA timezone: {self.startup_time.strftime('%H:%M:%S %Z')})")
        else:
            logger.info(f"🌐 MIXED SOURCES: Using {len(relevant_articles)} articles from {len(articles)} total (conditional timing)")
        
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
                
                # Send message with image if available  
                success = await self.send_message(message, article.image_url if hasattr(article, 'image_url') else None)
                
                if success:
                    # Mark as seen in database
                    self.database.mark_article_seen(
                        article.article_id,
                        article.title,
                        article.link,
                        getattr(article, 'published', datetime.now(pytz.timezone('Asia/Riyadh')).isoformat())
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
    
    # DISABLED: Economic calendar functionality removed per user request
    async def check_economic_calendar_DISABLED(self):
        """Check for upcoming and released economic events - DISABLED"""
        return  # Economic calendar disabled
        try:
            logger.info("Checking economic calendar...")
            
            # Get economic events
            events = await self.scraper.scrape_economic_calendar()
            
            # 📅 FILTER: Only process events that are relevant for today
            today_events = self._filter_today_events(events)
            logger.info(f"📅 Found {len(today_events)} events for today out of {len(events)} total")
            
            for event in today_events:
                try:
                    # Create different keys for before/after event states with date
                    current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                    event_base_key = f"{event.event_name}_{event.time}_{event.country}_{current_date}"
                    upcoming_key = f"{event_base_key}_upcoming"
                    released_key = f"{event_base_key}_released"
                    
                    # Check if event is current (time-based logic)
                    is_event_released = self._is_event_released(event)
                    
                    if is_event_released and event.actual and event.actual not in ["", "--", "TBD"]:
                        # Event has been released with actual data - send "صدر الآن" message
                        if self.database.is_article_seen(released_key):
                            continue  # Already sent release message
                            
                        message = await self.formatter.format_economic_data_release(
                            event_name_arabic=event.event_name_arabic,
                            country="أمريكا" if "US" in event.country.upper() else event.country,
                            country_flag=self.scraper.get_country_flag(event.country),
                            previous=event.previous,
                            forecast=event.forecast,
                            actual=event.actual,
                            impact_analysis=self._analyze_economic_impact(event)
                        )
                        event_key = released_key
                        
                    else:
                        # Upcoming event - send "ترقبوا اليوم" message (ONLY if today)
                        if self.database.is_article_seen(upcoming_key):
                            continue  # Already sent upcoming message
                        
                        # 📅 CHECK: Only send if event is TODAY
                        current_date = datetime.now(timezone.utc).date()
                        is_today = True  # For simulated events, assume today
                        
                        # For real events, check if they're actually today
                        if hasattr(event, 'event_date') and event.event_date:
                            try:
                                if isinstance(event.event_date, str):
                                    event_date = datetime.strptime(event.event_date, '%Y-%m-%d').date()
                                else:
                                    event_date = event.event_date
                                is_today = (event_date == current_date)
                            except:
                                is_today = True  # Default to today if can't parse
                        
                        message = await self.formatter.format_economic_announcement(
                            event_name_english=event.event_name,  # 🇬🇧 Original English title
                            event_name_arabic=event.event_name_arabic,  # 🇸🇦 Arabic translation
                            country_flag=self.scraper.get_country_flag(event.country),
                            event_time=event.time,
                            is_today=is_today,  # ✅ Only show TODAY events
                            previous=event.previous,  # 📈 Previous value
                            forecast=event.forecast   # 🔮 Forecast value
                        )
                        
                        # Skip if message is None (not today)
                        if not message:
                            continue
                            
                        event_key = upcoming_key
                    
                    # Send message with image if available
                    success = await self.send_message(message, event.image_url if hasattr(event, 'image_url') else None)
                    
                    if success:
                        # Mark as seen
                        self.database.mark_article_seen(
                            event_key,
                            event.event_name,
                            f"economic_calendar_{event.event_name}",
                            datetime.now(timezone.utc).isoformat()
                        )
                        logger.info(f"Posted economic event: {event.event_name}")
                        
                        # Add delay between posts
                        await asyncio.sleep(Config.MESSAGE_DELAY_SECONDS)
                    
                except Exception as e:
                    logger.error(f"Error posting economic event: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error checking economic calendar: {e}")
    
    def _analyze_economic_impact(self, event: EconomicEvent) -> str:
        """Analyze the impact of economic event on USD"""
        try:
            if not event.actual or not event.forecast:
                return "كما هو متوقع للدولار الأمريكي"
            
            # Clean and compare values
            def clean_value(val):
                if not val:
                    return None
                try:
                    return float(re.sub(r'[^\d.-]', '', str(val)))
                except:
                    return None
            
            actual_val = clean_value(event.actual)
            forecast_val = clean_value(event.forecast)
            
            if actual_val is None or forecast_val is None:
                return "كما هو متوقع للدولار الأمريكي"
            
            event_lower = event.event_name.lower()
            
            # Employment indicators (higher = better for USD)
            if any(keyword in event_lower for keyword in ['payroll', 'jobs', 'employment']):
                if actual_val > forecast_val:
                    return "إيجابي للدولار الأمريكي"
                elif actual_val < forecast_val:
                    return "سلبي للدولار الأمريكي"
            
            # Unemployment (lower = better for USD)
            elif 'unemployment' in event_lower:
                if actual_val < forecast_val:
                    return "إيجابي للدولار الأمريكي"
                elif actual_val > forecast_val:
                    return "سلبي للدولار الأمريكي"
            
            # PMI (higher = better for USD)
            elif 'pmi' in event_lower:
                if actual_val > forecast_val:
                    return "إيجابي للدولار الأمريكي"
                elif actual_val < forecast_val:
                    return "سلبي للدولار الأمريكي"
            
            return "كما هو متوقع للدولار الأمريكي"
            
        except Exception as e:
            logger.error(f"Error analyzing economic impact: {e}")
            return "كما هو متوقع للدولار الأمريكي"
    
    def _filter_today_events(self, events: List[EconomicEvent]) -> List[EconomicEvent]:
        """📅 Filter events to only include those relevant for today and translate properly"""
        today_events = []
        current_date = datetime.now(timezone.utc).date()
        
        for event in events:
            try:
                # 🌍 TRANSLATE: Properly translate event names using scraper's dictionary
                translated_name = self.scraper._get_arabic_event_name(event.event_name)
                # Update the event with proper Arabic translation
                event.event_name_arabic = translated_name
                
                # For simulated events (no specific date), always include
                if not hasattr(event, 'event_date') or not event.event_date:
                    today_events.append(event)
                    continue
                
                # For real calendar events, check if they're for today
                if hasattr(event, 'event_date') and event.event_date:
                    try:
                        # Parse event date (could be various formats)
                        if isinstance(event.event_date, str):
                            event_date = datetime.strptime(event.event_date, '%Y-%m-%d').date()
                        elif hasattr(event.event_date, 'date'):
                            event_date = event.event_date.date()
                        else:
                            event_date = event.event_date
                        
                        # Only include events for today
                        if event_date == current_date:
                            today_events.append(event)
                        else:
                            logger.debug(f"📅 Skipping event for {event_date}: {event.event_name}")
                            
                    except Exception as e:
                        logger.debug(f"📅 Error parsing event date: {e}, including event anyway")
                        today_events.append(event)
                        
            except Exception as e:
                logger.debug(f"📅 Error filtering event: {e}, including event anyway")
                today_events.append(event)
        
        return today_events
    
    def _should_apply_timezone_filtering(self, article) -> bool:
         """🎯 Determine if timezone filtering should be applied based on SCRAPING_MODE and source"""
         
         # Mode 1: Investing.com only - NO timezone filtering (original logic)
         if Config.SCRAPING_MODE == 1:
             return False
             
         # Mode 2: CoinDesk only - APPLY timezone filtering
         elif Config.SCRAPING_MODE == 2:
             return True
             
         # Mode 3: Both sources - Apply timezone filtering ONLY to CoinDesk articles
         elif Config.SCRAPING_MODE == 3:
             # Check if article is from CoinDesk
             is_coindesk = False
             
             # Check by section
             if hasattr(article, 'section') and 'COINDESK' in article.section.upper():
                 is_coindesk = True
             
             # Check by link domain
             if hasattr(article, 'link') and 'coindesk.com' in article.link.lower():
                 is_coindesk = True
                 
             # Only apply timezone filtering to CoinDesk articles
             return is_coindesk
             
         # Default: no filtering
         return False
    
    def _is_event_released(self, event: EconomicEvent) -> bool:
        """Check if economic event has been released based on time and actual data"""
        try:
            # If event has actual data, it's definitely released
            if event.actual and event.actual not in ["", "--", "TBD", None]:
                return True
            
            # If no time specified, consider it not released yet
            if not event.time or event.time in ["TBD", "All Day", ""]:
                return False
            
            current_time = datetime.now(timezone.utc)
            current_hour = current_time.hour
            current_minute = current_time.minute
            
            # Parse event time
            if ':' in event.time:
                event_hour, event_minute = map(int, event.time.split(':'))
            else:
                event_hour = int(event.time) if event.time.isdigit() else 13
                event_minute = 30
            
            # Check if current time has passed the event time (give 5 minutes grace period)
            if current_hour > event_hour:
                return True
            elif current_hour == event_hour and current_minute >= (event_minute + 5):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking event release time: {e}")
            return bool(event.actual)  # Fallback to checking actual data existence
    
    async def check_for_news(self):
        """🚀 ENHANCED: Check for new articles with configurable scraping modes (NEWS ONLY - every 3 minutes)"""
        try:
            logger.info(f"📰 PROFESSIONAL: Checking for news (Mode: {Config.SCRAPING_MODE})...")
            
            # 🚀 ENHANCED: Get new articles based on SCRAPING_MODE configuration
            articles = []
            
            # Mode 1: Investing.com only
            if Config.SCRAPING_MODE == 1:
                logger.info("🏛️ INVESTING.COM ONLY MODE")
                articles = await self._fetch_investing_articles()
            
            # Mode 2: CoinDesk only
            elif Config.SCRAPING_MODE == 2:
                logger.info("🪙 COINDESK ONLY MODE")
                articles = await self._fetch_coindesk_articles()
            
            # Mode 3: Both sources (Investing.com + CoinDesk)
            elif Config.SCRAPING_MODE == 3:
                logger.info("🌐 BOTH SOURCES MODE")
                investing_articles = await self._fetch_investing_articles()
                coindesk_articles = await self._fetch_coindesk_articles()
                articles = investing_articles + coindesk_articles
                logger.info(f"📊 COMBINED: {len(investing_articles)} from Investing.com + {len(coindesk_articles)} from CoinDesk")
            
            # Mode 4: RSS sources (CoinDesk + Cointelegraph)
            elif Config.SCRAPING_MODE == 4:
                logger.info("📡 RSS SOURCES MODE (CoinDesk + Cointelegraph)")
                articles = await self._fetch_rss_articles()
            
            # Mode 5: Cointelegraph only (Arabic if enabled) - NEW MODE
            elif Config.SCRAPING_MODE == 5:
                if Config.ENABLE_ARABIC:
                    logger.info("🇦🇪 COINTELEGRAPH ARABIC ONLY MODE")
                    articles = await self._fetch_cointelegraph_arabic_articles()
                else:
                    logger.info("📰 COINTELEGRAPH ONLY MODE")
                    articles = await self._fetch_cointelegraph_only_articles()
            
            else:
                logger.error(f"❌ Invalid SCRAPING_MODE: {Config.SCRAPING_MODE}. Using default (Cointelegraph only)")
                if Config.ENABLE_ARABIC:
                    articles = await self._fetch_cointelegraph_arabic_articles()
                else:
                    articles = await self._fetch_cointelegraph_only_articles()
            
            if articles:
                posted_count_before = self.stats['messages_sent']
                await self.post_articles(articles)
                posted_count_after = self.stats['messages_sent']
                new_articles_posted = posted_count_after - posted_count_before
                
                logger.info(f"✅ Posted {new_articles_posted} new Arabic articles from {len(articles)} found")
                
                # 📊 IMPROVED: Only show newly posted articles (not repeated ones)
                if new_articles_posted > 0:
                    logger.info(f"🆕 NEW ARTICLES POSTED:")
                    # Count how many articles were actually posted and only show those
                    posted_articles = [a for a in articles if not self.database.is_article_seen(a.article_id)][:new_articles_posted]
                    for article in posted_articles:
                        logger.info(f"   🔥 {article.section}: {article.title[:60]}...")
                else:
                    logger.info(f"♻️  All {len(articles)} articles were duplicates (already seen)")
            else:
                logger.info("ℹ️ No new articles found")
                
            # Cleanup database if it gets too large  
            if self.database.get_article_count() > Config.MAX_DATABASE_SIZE:
                self.database.cleanup_old_articles(Config.MAX_DATABASE_SIZE // 2)
            
            # Cleanup scraper cache to save memory
            self.scraper.cleanup_cache()
                
        except Exception as e:
            logger.error(f"💥 Error checking for news: {e}")

    async def _fetch_investing_articles(self) -> List:
        """🏛️ Fetch articles from Investing.com with retry logic"""
        articles = []
        for attempt in range(Config.MAX_RETRIES):
            try:
                # 🎯 USE ENHANCED FEATURES: Breaking news priority + more articles
                raw_articles = await self.scraper.scrape_investing_news(
                    max_articles=Config.MAX_ARTICLES_PER_SCRAPE * 2,  # Get more for better selection
                    breaking_news_priority=True  # 🔥 Prioritize breaking news
                )
                
                if raw_articles:
                    # 🧠 SMART CLASSIFICATION: Fix article sections using URL + content analysis
                    articles = self.scraper.fix_article_sections(raw_articles)
                    
                    # 📊 PROFESSIONAL: Report section coverage
                    coverage = self.scraper.verify_section_coverage(articles)
                    covered_sections = [section for section, count in coverage.items() if count > 0]
                    logger.info(f"📊 INVESTING COVERAGE: {len(covered_sections)}/6 sections - {', '.join(covered_sections)}")
                    
                    break
            except Exception as e:
                logger.error(f"⚠️ Investing.com fetch attempt {attempt + 1} failed: {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    await asyncio.sleep(10)
        
        return articles

    async def _fetch_coindesk_articles(self) -> List:
        """🪙 Fetch articles from CoinDesk with retry logic"""
        articles = []
        for attempt in range(Config.MAX_RETRIES):
            try:
                # 🪙 Fetch CoinDesk articles
                coindesk_articles = await self.scraper.scrape_coindesk_news(
                    max_articles=Config.MAX_ARTICLES_PER_SCRAPE
                )
                
                if coindesk_articles:
                    articles = coindesk_articles
                    logger.info(f"🪙 COINDESK SUCCESS: Retrieved {len(articles)} crypto articles")
                    break
                    
            except Exception as e:
                logger.error(f"⚠️ CoinDesk fetch attempt {attempt + 1} failed: {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    await asyncio.sleep(10)
        
        return articles

    async def _fetch_rss_articles(self) -> List:
        """📡 Fetch articles from RSS sources (CoinDesk + Cointelegraph) with retry logic"""
        articles = []
        for attempt in range(Config.MAX_RETRIES):
            try:
                # 📡 Fetch RSS articles from both CoinDesk and Cointelegraph
                rss_articles = await self.rss_scraper.get_latest_news(
                    max_articles=Config.MAX_ARTICLES_PER_SCRAPE
                )
                
                if rss_articles:
                    # Convert RSS articles to the format expected by the bot
                    converted_articles = []
                    for rss_article in rss_articles:
                        # Create a compatible article object
                        article = type('Article', (), {
                            'title': rss_article.title,
                            'link': rss_article.link,
                            'published': rss_article.published,
                            'summary': rss_article.summary,
                            'section': rss_article.source.upper(),  # Use source as section
                            'article_id': rss_article.article_id,
                            'image_url': getattr(rss_article, 'image_url', None)
                        })()
                        converted_articles.append(article)
                    
                    articles = converted_articles
                    source_counts = {}
                    for article in articles:
                        source_counts[article.section] = source_counts.get(article.section, 0) + 1
                    
                    sources_summary = ', '.join([f"{source}({count})" for source, count in source_counts.items()])
                    logger.info(f"📡 RSS SUCCESS: Retrieved {len(articles)} articles from {sources_summary}")
                    break
                    
            except Exception as e:
                logger.error(f"⚠️ RSS fetch attempt {attempt + 1} failed: {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    await asyncio.sleep(10)
        
        return articles

    async def _fetch_cointelegraph_only_articles(self) -> List:
        """📰 Fetch articles from Cointelegraph only (English) with retry logic"""
        articles = []
        for attempt in range(Config.MAX_RETRIES):
            try:
                # 📰 Create RSS scraper with Cointelegraph only sources
                cointelegraph_scraper = RSSNewsScraper(custom_sources=Config.COINTELEGRAPH_SOURCES)
                
                # Fetch Cointelegraph articles only
                rss_articles = await cointelegraph_scraper.get_latest_news(
                    max_articles=Config.MAX_ARTICLES_PER_SCRAPE
                )
                
                if rss_articles:
                    # Convert RSS articles to the format expected by the bot
                    converted_articles = []
                    for rss_article in rss_articles:
                        # Create a compatible article object
                        article = type('Article', (), {
                            'title': rss_article.title,
                            'link': rss_article.link,
                            'published': rss_article.published,
                            'summary': rss_article.summary,
                            'section': 'COINTELEGRAPH',  # Use consistent section name
                            'article_id': rss_article.article_id,
                            'image_url': getattr(rss_article, 'image_url', None)
                        })()
                        converted_articles.append(article)
                    
                    articles = converted_articles
                    logger.info(f"📰 COINTELEGRAPH SUCCESS: Retrieved {len(articles)} English articles")
                    await cointelegraph_scraper.close_session()
                    break
                    
                await cointelegraph_scraper.close_session()
                    
            except Exception as e:
                logger.error(f"⚠️ Cointelegraph fetch attempt {attempt + 1} failed: {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    await asyncio.sleep(10)
        
        return articles

    async def _fetch_cointelegraph_arabic_articles(self) -> List:
        """🇦🇪 Fetch articles from Arabic Cointelegraph RSS with retry logic"""
        articles = []
        for attempt in range(Config.MAX_RETRIES):
            try:
                # 🇦🇪 Create RSS scraper with Arabic Cointelegraph source
                arabic_scraper = RSSNewsScraper(custom_sources=Config.COINTELEGRAPH_ARABIC_SOURCES)
                
                # Fetch Arabic Cointelegraph articles
                rss_articles = await arabic_scraper.get_latest_news(
                    max_articles=Config.MAX_ARTICLES_PER_SCRAPE
                )
                
                if rss_articles:
                    # Convert RSS articles to the format expected by the bot
                    converted_articles = []
                    for rss_article in rss_articles:
                        # Create a compatible article object
                        article = type('Article', (), {
                            'title': rss_article.title,
                            'link': rss_article.link,
                            'published': rss_article.published,
                            'summary': rss_article.summary,
                            'section': 'COINTELEGRAPH_ARABIC',  # Use Arabic section name
                            'article_id': rss_article.article_id,
                            'image_url': getattr(rss_article, 'image_url', None)
                        })()
                        converted_articles.append(article)
                    
                    articles = converted_articles
                    logger.info(f"🇦🇪 COINTELEGRAPH ARABIC SUCCESS: Retrieved {len(articles)} Arabic articles")
                    await arabic_scraper.close_session()
                    break
                    
                await arabic_scraper.close_session()
                    
            except Exception as e:
                logger.error(f"⚠️ Arabic Cointelegraph fetch attempt {attempt + 1} failed: {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    await asyncio.sleep(10)
        
        return articles
    

    # DISABLED: Economic calendar task removed per user request
    async def economic_calendar_task_DISABLED(self):
        """📊 SEPARATE TASK: Economic calendar checker (every 1 hour 2 minutes) - DISABLED"""
        return  # Economic calendar disabled
        while self.running:
            try:
                logger.info("📊 ECONOMIC CALENDAR: Checking for economic events...")
                await self.check_economic_calendar_DISABLED()
                
                # Wait 1 hour 2 minutes for next economic calendar check
                economic_wait = 3720  # 1 hour 2 minutes
                logger.info(f"📊 ECONOMIC CALENDAR: Waiting {economic_wait} seconds (1h 2m) until next economic calendar check...")
                await asyncio.sleep(economic_wait)
                
            except Exception as e:
                logger.error(f"💥 Error in economic calendar task: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
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
            
            # Send startup message based on language mode
            if Config.ENABLE_ARABIC:
                startup_message = (
                    f"🚀 بوت الأخبار المالية العربي!\n\n"
                    f"تابعنا لكل جديد : @news_crypto_911"
                )
            else:
                startup_message = (
                    f"🚀 Financial News Bot Started!\n\n"
                    f"📈 Real-time financial market updates\n"
                    f"🔥 Breaking news priority\n"
                    f"🎯 Professional market analysis\n\n"
                    f"Follow us for real-time updates: @news_crypto_911"
                )
            
            # Try to send startup message
            startup_sent = await self.send_message(startup_message)
            if startup_sent:
                logger.info("Startup message sent successfully")
            else:
                logger.warning("Failed to send startup message - continuing anyway")
            
            # DISABLED: Economic calendar task removed per user request
            # economic_task = asyncio.create_task(self.economic_calendar_task())
            # logger.info("📊 ECONOMIC CALENDAR: Started separate task (1h 2m intervals) - REAL EVENTS ONLY")
            
            # Main loop for NEWS (every 3 minutes as before)
            while self.running:
                try:
                    await self.check_for_news()
                    
                    # Wait for next NEWS cycle (3 minutes as before)
                    news_wait = 180  # 3 minutes for news (as requested by user)
                    logger.info(f"📰 NEWS: Waiting {news_wait} seconds (3m) until next news check...")
                    await asyncio.sleep(news_wait)
                    
                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    # Economic task disabled
                    # if 'economic_task' in locals():
                    #     economic_task.cancel()  # Cancel economic task
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
    setup_logging(Config.LOG_LEVEL, Config.LOG_FILE)
    
    language_mode = "🇸🇦 Arabic" if Config.ENABLE_ARABIC else "🇺🇸 English"
    print(f"🤖 FREE Financial News Bot ({language_mode})")
    print("=" * 60)
    print("🤖 AI-Powered Translation (Groq - FREE)" if Config.ENABLE_ARABIC else "🚀 Direct English News (No Translation)")
    print("💎 Enhanced Financial Market Focus")
    print("📊 Professional News Formatting")
    print("🔥 Real-time Market Impact Analysis")
    print(f"🌍 Language: {language_mode}")
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