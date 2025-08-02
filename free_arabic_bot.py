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

# Import enhanced modules
from config_free import Config
from deep_translator import GoogleTranslator
from ai_translator import AITranslator
from crypto_arabic_formatter import CryptoArabicFormatter
from investing_scraper import InvestingNewsScraper, EconomicEvent
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
        self.database = ArticleDatabase('production_seen_articles.json')  # Use production database
        self.formatter = CryptoArabicFormatter()
        
        # Economic calendar for upcoming events
        self.pending_events = []
        self.last_calendar_check = None
        
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
        
        # 🕐 Bot startup time for filtering fresh news only
        self.startup_time = datetime.now(timezone.utc)
        
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
                
                if hasattr(article, 'summary') and article.summary:
                    message += f"📝 {article.summary}\n\n"
                
                # message += f"📊 Section: {getattr(article, 'section', 'Financial News')}\n"
                # message += f"⏰ {getattr(article, 'published', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'))}\n\n"
                message += "📈 Follow us: @news_news127"
                
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
                return f"عاجل: {section_emoji} {flag} {article.title}\n\nتابعنا لكل جديد : @news_news127"
            else:
                return f"🚨 {section_emoji} {flag} BREAKING: {article.title}\n\nFollow us: @news_news127"
    
    async def post_articles(self, articles):
        """Post filtered articles to Telegram channel"""
        posted_count = 0
        
        # 🚀 NO CONTENT FILTERING: Trust our professional RSS endpoints!
        # But filter by time: only get fresh news after bot startup
        fresh_articles = []
        for article in articles:
            try:
                # Parse article publish time
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
                    
                    # Flexible time filtering with different rules for different sources
                    current_time = datetime.now(timezone.utc)
                    time_tolerance = timedelta(hours=12)  # Allow future articles (timezone issues)
                    max_future_time = current_time + time_tolerance
                    
                    # For CoinDesk crypto news, be more lenient (allow articles up to 6 hours old)
                    if hasattr(article, 'section') and article.section == 'CRYPTOCURRENCY':
                        min_time = current_time - timedelta(hours=6)  # 6 hours back for crypto
                        is_fresh = min_time <= published_time <= max_future_time
                        logger.debug(f"🪙 CRYPTO CHECK: {article.title[:30]}... time: {published_time}, range: {min_time} to {max_future_time}")
                    else:
                        # For other news, use bot startup time as minimum
                        is_fresh = self.startup_time <= published_time <= max_future_time
                        logger.debug(f"📰 NEWS CHECK: {article.title[:30]}... time: {published_time}, startup: {self.startup_time}")
                    
                    if is_fresh:
                        fresh_articles.append(article)
                        logger.debug(f"✅ FRESH: {article.title[:50]}... (published: {published_time})")
                    elif published_time > max_future_time:
                        logger.debug(f"🔮 FUTURE: Skipping {article.title[:50]}... (published: {published_time}) - too far in future")
                    else:
                        logger.debug(f"⏰ OLD: Skipping {article.title[:50]}... (published: {published_time})")
                else:
                    # No publish time, include it
                    fresh_articles.append(article)
            except Exception as e:
                logger.debug(f"Error parsing article time: {e}")
                # If error parsing time, include the article
                fresh_articles.append(article)
        
        relevant_articles = fresh_articles
        logger.info(f"📰 FRESH NEWS: Using {len(relevant_articles)} fresh articles from {len(articles)} total (after startup: {self.startup_time.strftime('%H:%M:%S')})")
        
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
    
    async def check_economic_calendar(self):
        """Check for upcoming and released economic events"""
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
            else:
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
            
            # Mode 3: Both sources
            elif Config.SCRAPING_MODE == 3:
                logger.info("🌐 BOTH SOURCES MODE")
                investing_articles = await self._fetch_investing_articles()
                coindesk_articles = await self._fetch_coindesk_articles()
                articles = investing_articles + coindesk_articles
                logger.info(f"📊 COMBINED: {len(investing_articles)} from Investing.com + {len(coindesk_articles)} from CoinDesk")
            
            else:
                logger.error(f"❌ Invalid SCRAPING_MODE: {Config.SCRAPING_MODE}. Using default (both sources)")
                investing_articles = await self._fetch_investing_articles()
                coindesk_articles = await self._fetch_coindesk_articles()
                articles = investing_articles + coindesk_articles
            
            if articles:
                posted = await self.post_articles(articles)
                logger.info(f"✅ Posted {posted} new Arabic articles from {len(articles)} found")
                
                # 🎯 Log top breaking news for monitoring
                for article in articles[:3]:
                    logger.info(f"🔥 {article.section}: {article.title[:60]}...")
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
    

    async def economic_calendar_task(self):
        """📊 SEPARATE TASK: Economic calendar checker (every 1 hour 2 minutes)"""
        while self.running:
            try:
                logger.info("📊 ECONOMIC CALENDAR: Checking for economic events...")
                await self.check_economic_calendar()
                
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
                    f"تابعنا لكل جديد : @news_news127"
                )
            else:
                startup_message = (
                    f"🚀 Financial News Bot Started!\n\n"
                    f"📈 Real-time financial market updates\n"
                    f"🔥 Breaking news priority\n"
                    f"🎯 Professional market analysis\n\n"
                    f"Follow us for real-time updates: @news_news127"
                )
            
            # Try to send startup message
            startup_sent = await self.send_message(startup_message)
            if startup_sent:
                logger.info("Startup message sent successfully")
            else:
                logger.warning("Failed to send startup message - continuing anyway")
            
            # Start economic calendar task separately
            economic_task = asyncio.create_task(self.economic_calendar_task())
            logger.info("📊 ECONOMIC CALENDAR: Started separate task (1h 2m intervals)")
            
            # Start economic calendar task separately (1h 2m intervals)
            economic_task = asyncio.create_task(self.economic_calendar_task())
            logger.info("📊 ECONOMIC CALENDAR: Started separate task (1h 2m intervals)")
            
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
                    if 'economic_task' in locals():
                        economic_task.cancel()  # Cancel economic task
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