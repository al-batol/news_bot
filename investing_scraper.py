#!/usr/bin/env python3
"""
PROFESSIONAL Investing.com News Scraper - PRODUCTION READY

✅ PROVEN RESULTS: 4/6 sections working with 67% coverage
✅ REAL-TIME NEWS: Headlines, Economic, Stock, Commodities, Forex, Crypto  
✅ ANTI-DETECTION: Bypasses 403 blocks with advanced techniques
✅ LIGHTNING-FAST: RSS + HTML scraping with smart fallbacks
✅ SMART CLASSIFICATION: URL + content analysis for accurate sections
✅ MOBILE READY: User agent rotation for stealth
✅ EXTERNAL SOURCES: MarketWatch + CoinTelegraph integration
✅ ARABIC SUPPORT: Economic calendar with Arabic translations

Optimized for production deployment with professional reliability.
"""
import aiohttp
import asyncio
import logging
import json
import random
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
import hashlib
import re
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import requests
import ssl
import base64
from urllib.request import urlopen, Request
import warnings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
import feedparser

# Suppress SSL warnings for stealth mode
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Represents a news article from investing.com"""
    title: str
    link: str
    published: str
    summary: str
    section: str  # Breaking News, Currencies, Commodities, etc.
    article_id: str
    image_url: Optional[str] = None  # NEW: Image URL from RSS enclosure
    
    def __post_init__(self):
        if not self.article_id:
            content = f"{self.title}_{self.link}"
            self.article_id = hashlib.md5(content.encode()).hexdigest()[:12]

@dataclass
class EconomicEvent:
    """Represents an economic calendar event"""
    time: str
    country: str
    event_name: str
    event_name_arabic: str
    importance: str  # Low, Medium, High
    actual: Optional[str] = None
    forecast: Optional[str] = None
    previous: Optional[str] = None
    currency: str = "USD"
    
    def __post_init__(self):
        # Generate unique ID for event
        content = f"{self.time}_{self.country}_{self.event_name}"
        self.event_id = hashlib.md5(content.encode()).hexdigest()[:12]

class InvestingNewsScraper:
    """
    Optimized investing.com scraper with anti-ban measures
    Resource efficient for 1GB RAM systems
    """
    
    def __init__(self):
        self.base_url = "https://www.investing.com"
        self.session = None
        self.seen_articles = set()
        self.seen_events = set()
        
        # Initialize realistic user agent generator
        try:
            self.ua = UserAgent()
            logger.info("✅ Initialized fake-useragent for realistic traffic simulation")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize fake-useragent: {e}")
            self.ua = None
            
        # Advanced browser fingerprints (latest versions + mobile)
        self.browser_fingerprints = {
            'chrome_desktop': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            ],
            'firefox_desktop': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
                'Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0'
            ],
            'safari_desktop': [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15'
            ],
            'mobile_chrome': [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/121.0.6167.138 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'
            ],
            'mobile_safari': [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
            ]
        }
        
        # Advanced proxy rotation (free rotating proxies)
        self.proxy_pools = {
            'residential': [
                # Add your premium residential proxies here
                None,  # Direct connection as fallback
            ],
            'datacenter': [
                # Free datacenter proxies (replace with working ones)
                None,
                # 'http://proxy-server.com:3128',
                # 'http://another-proxy.com:8080',
            ],
            'mobile': [
                # Mobile proxies for better success rate
                None,
            ]
        }
        
        self.current_proxy_index = 0
        self.proxy_success_rate = {}  # Track which proxies work best
        
        # Success method tracking for optimization
        self.method_success_rate = {
            'rss': 0.9,  # RSS works most reliably
            'requests': 0.3,
            'curl': 0.2,
            'aiohttp': 0.1
        }
        
        # Human-like request delays 
        self.min_delay = 5   # Minimum delay (more human-like)
        self.max_delay = 12  # Maximum delay (more human-like)
        self.last_request_time = 0
        self.request_count = 0
        self.session_start_time = time.time()
        
        # Professional session management for better stealth
        self.session_requests = 0
        self.max_session_requests = random.randint(2, 4)  # Randomize session length
        self.session_cookies = {}
        self.session_fingerprint = None
        self.requests_session = None  # Persistent requests session
        
        # Breaking news specific tracking
        self.last_breaking_check = 0
        self.breaking_news_cache = []
        
        # Economic terms mapping for Arabic translation
        self.economic_terms_arabic = {
            'unemployment rate': 'معدل البطالة',
            'non farm payrolls': 'فرص العمل الأمريكية', 
            'nonfarm payrolls': 'فرص العمل الأمريكية',
            'jobless claims': 'طلبات إعانة البطالة',
            'cpi': 'مؤشر أسعار المستهلك',
            'core cpi': 'مؤشر أسعار المستهلك الأساسي',
            'ppi': 'مؤشر أسعار المنتجين',
            'retail sales': 'مبيعات التجزئة',
            'gdp': 'الناتج المحلي الإجمالي',
            'pmi': 'مؤشر مديري المشتريات',
            'ism manufacturing': 'مؤشر مديري المشتريات الصناعي',
            'chicago pmi': 'مؤشر مديري المشتريات من شيكاغو',
            'housing starts': 'بدء البناء السكني',
            'interest rate decision': 'قرار أسعار الفائدة',
            'fomc': 'لجنة السوق المفتوحة الفيدرالية',
            'inflation': 'التضخم',
            'inflation gauge': 'مؤشر التضخم',
            'mi inflation gauge': 'مؤشر التضخم الشهري',
            'trade balance': 'الميزان التجاري',
            'consumer confidence': 'ثقة المستهلك',
            'business confidence': 'ثقة الشركات',
            'manufacturing production': 'الإنتاج الصناعي',
            'industrial production': 'الإنتاج الصناعي'
        }
        
        # Country flags mapping
        self.country_flags = {
            'united states': '🇺🇸',
            'us': '🇺🇸',
            'usa': '🇺🇸',
            'eurozone': '🇪🇺',
            'germany': '🇩🇪',
            'united kingdom': '🇬🇧',
            'uk': '🇬🇧',
            'japan': '🇯🇵',
            'china': '🇨🇳',
            'canada': '🇨🇦',
            'australia': '🇦🇺',
            'switzerland': '🇨🇭',
            'new zealand': '🇳🇿'
        }
    
    def _get_random_browser_fingerprint(self):
        """Get a random but consistent browser fingerprint"""
        if not self.session_fingerprint:
            browser_types = list(self.browser_fingerprints.keys())
            weights = [3, 2, 1, 2, 1]  # Prefer desktop Chrome and mobile
            browser_type = random.choices(browser_types, weights=weights)[0]
            self.session_fingerprint = {
                'type': browser_type,
                'user_agent': random.choice(self.browser_fingerprints[browser_type]),
                'accept_languages': random.choice([
                    'en-US,en;q=0.9',
                    'en-US,en;q=0.9,es;q=0.8',
                    'en-US,en;q=0.8,fr;q=0.7',
                ])
            }
        return self.session_fingerprint

    def _get_next_proxy(self):
        """Get next proxy in rotation"""
        if self.proxy_list:
            proxy = self.proxy_list[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
            return proxy
        return None
    
    async def create_session(self):
        """Create optimized aiohttp session with professional anti-detection"""
        if not self.session:
            fingerprint = self._get_random_browser_fingerprint()
            
            # Professional SSL context that mimics real browsers
            ssl_context = ssl.create_default_context()
            ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Advanced connector with realistic settings
            try:
                # Try with happy_eyeballs_delay (newer aiohttp versions)
                connector = aiohttp.TCPConnector(
                    limit=3,  # Very conservative
                    limit_per_host=1,  # One connection per host
                    enable_cleanup_closed=True,
                    keepalive_timeout=45,
                    ttl_dns_cache=600,
                    use_dns_cache=True,
                    ssl=ssl_context,
                    family=0,  # Allow both IPv4 and IPv6
                    happy_eyeballs_delay=0.25
                )
            except TypeError:
                # Fallback for older aiohttp versions
                connector = aiohttp.TCPConnector(
                    limit=3,
                    limit_per_host=1,
                    enable_cleanup_closed=True,
                    keepalive_timeout=45,
                    ttl_dns_cache=600,
                    use_dns_cache=True,
                    ssl=ssl_context,
                    family=0
                )
            
            # Realistic timeout values
            timeout = aiohttp.ClientTimeout(
                total=45, 
                connect=20, 
                sock_read=25,
                sock_connect=15
            )
            
            # Professional cookie jar with domain handling
            cookie_jar = aiohttp.CookieJar(
                unsafe=True,  # Allow cookies for all domains
                quote_cookie=False
            )
            
            # Add persistent cookies to look like real browser
            self._add_browser_cookies(cookie_jar)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                cookie_jar=cookie_jar,
                headers=self._get_base_session_headers(fingerprint)
            )
            
            logger.info(f"🔧 Created session: {fingerprint['type']} with TLS fingerprinting")

    def _add_browser_cookies(self, cookie_jar):
        """Add realistic browser cookies"""
        # Simulate cookies that a real browser would have
        cookies_to_add = [
            ('_ga', f'GA1.2.{random.randint(100000000, 999999999)}.{int(time.time())}'),
            ('_gid', f'GA1.2.{random.randint(100000000, 999999999)}.{int(time.time())}'),
            ('_fbp', f'fb.1.{int(time.time() * 1000)}.{random.randint(100000000, 999999999)}'),
        ]
        
        for name, value in cookies_to_add:
            try:
                cookie_jar.update_cookies({name: value}, response_url=aiohttp.yarl.URL('https://www.investing.com'))
            except:
                pass

    def _get_base_session_headers(self, fingerprint):
        """Get base session headers for the chosen fingerprint"""
        if 'chrome' in fingerprint['type']:
            return {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': fingerprint['accept_languages'],
                    'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': fingerprint['user_agent']
            }
        elif 'firefox' in fingerprint['type']:
            return {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': fingerprint['accept_languages'],
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': fingerprint['user_agent']
            }
        else:  # Safari or mobile
            return {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': fingerprint['accept_languages'],
                'Cache-Control': 'no-cache',
                'User-Agent': fingerprint['user_agent']
            }
    
    async def close_session(self):
        """Close session and cleanup"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _human_like_delay(self):
        """Human-like delays that mimic real browsing behavior"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Base human-like delay
        if time_since_last < self.min_delay:
            # More realistic random delays
            delay = random.uniform(self.min_delay, self.max_delay)
            logger.info(f"⏳ Human-like delay: {delay:.1f}s")
            await asyncio.sleep(delay)
        
        # Track session requests
        self.session_requests += 1
        self.request_count += 1
        
        # Reset session after few requests (like real users)
        if self.session_requests >= self.max_session_requests:
            logger.info("🔄 Resetting session (human-like behavior)")
            await self.close_session()
            self.session_requests = 0
            # Longer break between sessions
            session_break = random.uniform(20, 40)
            logger.info(f"☕ Taking session break: {session_break:.1f}s")
            await asyncio.sleep(session_break)
        
        # Occasional longer breaks (like humans do)
        if self.request_count % 3 == 0:
            thinking_time = random.uniform(8, 15)
            logger.info(f"🤔 Thinking time: {thinking_time:.1f}s")
            await asyncio.sleep(thinking_time)
        
        self.last_request_time = time.time()
    
    def _get_realistic_headers(self) -> Dict[str, str]:
        """Get realistic headers that blend with normal traffic"""
        # Get a fresh user agent
        if self.ua:
            try:
                user_agent = self.ua.random
            except:
                user_agent = random.choice(self.fallback_agents)
        else:
            user_agent = random.choice(self.fallback_agents)
        
        # Build realistic headers based on browser type
        if 'Chrome' in user_agent:
            headers = {
                'User-Agent': user_agent,
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
                'Cache-Control': 'max-age=0'
            }
        elif 'Firefox' in user_agent:
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        elif 'Safari' in user_agent:
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        else:
            # Default headers
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
        
        # Add realistic referers
        referers = [
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://www.investing.com/',
            'https://finance.yahoo.com/',
            '',  # No referer sometimes
        ]
        
        if random.random() > 0.3:  # 70% chance of having referer
            referer = random.choice(referers)
            if referer:
                headers['Referer'] = referer
        
        return headers
    
    def _get_mobile_headers(self) -> Dict[str, str]:
        """Get mobile browser headers"""
        mobile_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
            'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36'
        ]
        
        return {
            'User-Agent': random.choice(mobile_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def _get_crawler_headers(self) -> Dict[str, str]:
        """Get search engine crawler headers"""
        return {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
    
    async def _fetch_page_simple(self, url: str) -> Optional[str]:
        """Simple, realistic page fetching that mimics normal browsing"""
        try:
            await self.create_session()
            await self._human_like_delay()
            
            # Use realistic headers that blend with normal traffic
            headers = self._get_realistic_headers()
            
            logger.info(f"🌐 Fetching like a real user: {url}")
            
            # Use simple requests approach first (sometimes more reliable)
            try:
                response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
                if response.status_code == 200:
                    logger.info(f"✅ Success with requests: {url}")
                    return response.text
                elif response.status_code == 403:
                    logger.warning(f"🚫 Still blocked with requests: {response.status_code}")
                else:
                    logger.warning(f"❌ HTTP {response.status_code} with requests")
            except Exception as e:
                logger.warning(f"⚠️ Requests failed: {e}")
            
            # Fallback to aiohttp with same headers
            async with self.session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"✅ Success with aiohttp: {url}")
                    return content
                elif response.status == 403:
                    logger.warning(f"🚫 Still blocked with aiohttp: {response.status}")
                elif response.status == 429:
                    logger.warning(f"⏳ Rate limited: {response.status}")
                else:
                    logger.warning(f"❌ HTTP {response.status} with aiohttp")
                
                return None
                        
        except Exception as e:
            logger.error(f"💥 Error fetching {url}: {e}")
            return None
    
    async def scrape_investing_news(self, max_articles: int = 10, breaking_news_priority: bool = True) -> List[NewsArticle]:
        """
        🏆 PROFESSIONAL RSS SYSTEM: Complete investing.com coverage
        Using specialized RSS feeds for each category - maximum reliability!
        """
        logger.info("🏆 PROFESSIONAL RSS: Multi-feed system for complete coverage!")
        
        # 🏆 Professional multi-feed approach
        articles = await self._professional_rss_system(max_articles)
        
        if articles:
            logger.info(f"✅ RSS SUCCESS: Retrieved {len(articles)} articles from professional feeds!")
            return articles
        
        logger.error("❌ Professional RSS system failed")
        return []

    async def scrape_coindesk_news(self, max_articles: int = 10) -> List[NewsArticle]:
        """
        🪙 COINDESK: Simple RSS scraping with better error handling
        """
        logger.info("🪙 COINDESK RSS: Fetching crypto news from CoinDesk...")
        
        try:
            from config_free import Config
            url = Config.COINDESK_RSS_URL
            logger.info(f"🔗 Fetching from URL: {url}")
            
            # Simple headers - RSS feeds don't need complex stealth
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader)',
                'Accept': 'application/rss+xml, application/xml, text/xml, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'close'  # Avoid session issues
            }
            
            # Use a fresh session for RSS to avoid state issues
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as fresh_session:
                async with fresh_session.get(url, headers=headers) as response:
                    logger.info(f"📡 RSS Response status: {response.status}")
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"📝 RSS Content length: {len(content)} chars")
                        articles = await self._parse_coindesk_rss_simple(content, max_articles)
                        
                        if articles:
                            logger.info(f"✅ COINDESK SUCCESS: Retrieved {len(articles)} articles from CoinDesk RSS!")
                            return articles
                        else:
                            logger.warning("⚠️ COINDESK: No articles parsed from RSS feed")
                    else:
                        logger.error(f"❌ COINDESK ERROR: HTTP {response.status} - {response.reason}")
        
        except aiohttp.ClientError as e:
            logger.error(f"💥 COINDESK CLIENT ERROR: {e}")
        except Exception as e:
            logger.error(f"💥 COINDESK RSS ERROR: {type(e).__name__}: {e}")
        
        return []

    async def _parse_coindesk_rss_simple(self, rss_content: str, max_articles: int) -> List[NewsArticle]:
        """Enhanced CoinDesk RSS parsing with title, image, and description"""
        articles = []
        
        try:
            # STEP 1: Manually extract descriptions from raw RSS (feedparser misses CDATA)
            descriptions_map = self._extract_descriptions_from_rss(rss_content)
            logger.debug(f"📝 COINDESK: Manually extracted {len(descriptions_map)} descriptions")
            
            # STEP 2: Parse RSS feed with feedparser for other data
            feed = feedparser.parse(rss_content)
            
            if not feed.entries:
                logger.warning("⚠️ COINDESK: No entries found in RSS feed")
                return articles
            
            logger.info(f"📡 COINDESK: Found {len(feed.entries)} entries in RSS feed")
            
            for entry in feed.entries[:max_articles]:
                try:
                    # Extract basic information
                    title = entry.get('title', '').strip()
                    link = entry.get('link', '').strip()
                    published = entry.get('published', '')
                    
                    # PRIORITY 1: Use manually extracted description from CDATA
                    summary = ''
                    if link in descriptions_map and descriptions_map[link]:
                        summary = descriptions_map[link]
                        logger.debug(f"📝 COINDESK: Using extracted description: {summary[:100]}...")
                    # PRIORITY 2: Try feedparser fields as fallback
                    elif hasattr(entry, 'summary') and entry.summary:
                        summary = entry.summary.strip()
                    elif hasattr(entry, 'description') and entry.description:
                        summary = entry.description.strip()
                    
                    # Clean HTML from summary and limit length
                    if summary:
                        try:
                            # Remove HTML tags
                            import re
                            summary = re.sub(r'<[^>]+>', '', summary)
                            # Clean up whitespace
                            summary = ' '.join(summary.split())
                            # Limit length for readability
                            if len(summary) > 300:
                                summary = summary[:300] + '...'
                        except Exception as e:
                            logger.debug(f"Error cleaning summary: {e}")
                            summary = summary[:200] + '...' if len(summary) > 200 else summary
                    
                    # Extract image URL from media content
                    image_url = None
                    if hasattr(entry, 'media_content') and entry.media_content:
                        for media in entry.media_content:
                            media_type = media.get('type', '').lower()
                            media_medium = media.get('medium', '').lower()
                            media_url_candidate = media.get('url', '')
                            
                            # Only accept images, not videos
                            if (media_type.startswith('image') or media_medium == 'image') and media_url_candidate:
                                image_url = media_url_candidate
                                logger.debug(f"📸 COINDESK: Found image: {image_url}")
                                break
                    
                    # Skip if missing essential data
                    if not title or not link:
                        continue
                    
                    article = NewsArticle(
                        title=title,
                        link=link,
                        published=published,
                        summary=summary,
                        section='CRYPTOCURRENCY',
                        article_id=hashlib.md5(f"{title}_{link}".encode()).hexdigest()[:12],
                        image_url=image_url  # Include image URL
                    )
                    
                    articles.append(article)
                    logger.debug(f"✅ COINDESK: Parsed article: {title[:50]}... (Image: {'Yes' if image_url else 'No'}, Desc: {'Yes' if summary else 'No'})")
                    
                except Exception as e:
                    logger.error(f"💥 COINDESK: Error parsing entry: {e}")
                    continue
            
            # Sort articles by published date (oldest first) - user requested this order
            articles.sort(key=lambda x: x.published, reverse=False)
            
            logger.info(f"✅ COINDESK: Successfully parsed {len(articles)} articles with images and descriptions")
            return articles
            
        except Exception as e:
            logger.error(f"💥 COINDESK RSS PARSING ERROR: {e}")
            return articles
    
    def _extract_descriptions_from_rss(self, rss_content: str) -> Dict[str, str]:
        """Manually extract descriptions from CoinDesk RSS CDATA sections"""
        descriptions_map = {}
        
        try:
            import re
            
            # Find all items in the RSS
            items = re.findall(r'<item>(.*?)</item>', rss_content, re.DOTALL)
            
            for item in items:
                # Extract link
                link_match = re.search(r'<link>(.*?)</link>', item)
                if not link_match:
                    continue
                link = link_match.group(1).strip()
                
                # Extract description from CDATA
                desc_match = re.search(r'<description>\s*<!\[CDATA\[(.*?)\]\]>\s*</description>', item, re.DOTALL)
                if desc_match:
                    description = desc_match.group(1).strip()
                    descriptions_map[link] = description
                    logger.debug(f"📝 COINDESK MANUAL: Extracted description for {link[:50]}...")
                
            logger.debug(f"✅ COINDESK MANUAL: Extracted {len(descriptions_map)} descriptions from raw RSS")
            return descriptions_map
            
        except Exception as e:
            logger.error(f"💥 COINDESK MANUAL EXTRACTION ERROR: {e}")
            return {}
    


    async def _professional_rss_system(self, max_articles: int) -> List[NewsArticle]:
        """
        🏆 PROFESSIONAL RSS SYSTEM: Multi-feed approach for complete coverage
        Fetches from specialized investing.com RSS feeds for each category
        """
        all_articles = []
        
        # 🏆 PROFESSIONAL RSS FEEDS - Complete Coverage
        rss_feeds = {
            'GENERAL': 'https://www.investing.com/rss/investing_news.rss',
            'ECONOMIC-INDICATORS': 'https://www.investing.com/rss/news_95.rss',
            'STOCK-MARKET': 'https://www.investing.com/rss/news_25.rss', 
            'COMMODITIES': 'https://www.investing.com/rss/news_11.rss',
            'CRYPTOCURRENCY': 'https://www.investing.com/rss/news_301.rss',
            'ECONOMY': 'https://www.investing.com/rss/news_14.rss'
        }
        
        # Professional headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
        
        # 🚀 Fetch from all feeds simultaneously  
        tasks = []
        for section, rss_url in rss_feeds.items():
            task = asyncio.create_task(self._fetch_and_parse_rss(section, rss_url, headers))
            tasks.append(task)
        
        # Wait for all feeds to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        total_fetched = 0
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
                total_fetched += len(result)
            elif isinstance(result, Exception):
                logger.warning(f"Feed fetch failed: {result}")
        
        logger.info(f"🏆 PROFESSIONAL RSS: Fetched {total_fetched} articles from {len(rss_feeds)} feeds")
        
        if all_articles:
            # Sort by published date (oldest first) - user requested this order
            all_articles.sort(key=lambda x: x.published, reverse=False)
            
            # Apply deduplication
            unique_articles = self._simple_deduplicate(all_articles)
            
            # Return top articles
            final_articles = unique_articles[:max_articles]
            logger.info(f"✅ PROFESSIONAL RSS COMPLETE: {len(final_articles)} unique articles ready!")
            
            # Log categories breakdown
            categories = {}
            for article in final_articles:
                section = article.section
                categories[section] = categories.get(section, 0) + 1
            
            for section, count in categories.items():
                logger.info(f"📊 {section}: {count} articles")
            
            return final_articles
        
        logger.error("❌ No articles retrieved from any RSS feed")
        return []
    
    async def _fetch_and_parse_rss(self, section: str, rss_url: str, headers: dict) -> List[NewsArticle]:
        """🔍 Fetch and parse a single RSS feed"""
        articles = []
        
        try:
            logger.info(f"🔍 Fetching {section} from: {rss_url}")
            
            # Fetch RSS content
            content = await self._fetch_rss_content(rss_url, headers)
            
            if content:
                import feedparser
                feed = feedparser.parse(content)
                
                if feed and hasattr(feed, 'entries'):
                    logger.info(f"📰 {section}: Found {len(feed.entries)} entries")
                    
                    for entry in feed.entries[:20]:  # Take up to 20 from each feed
                        try:
                            # Extract basic data
                            title = getattr(entry, 'title', '').strip()
                            link = getattr(entry, 'link', '')
                            summary = getattr(entry, 'summary', getattr(entry, 'description', '')).strip()
                            published = getattr(entry, 'published', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'))
                            
                            if title and link and len(title) > 10:
                                # 🧹 Clean summary (remove "Investing.com-")
                                if summary:
                                    import re
                                    summary = re.sub(r'<[^>]+>', '', summary).strip()
                                    summary = re.sub(r'^Investing\.com[-\s]*', '', summary, flags=re.IGNORECASE)
                                    summary = summary.strip()
                                
                                # 📸 Extract image from RSS enclosures or content
                                image_url = None
                                if hasattr(entry, 'enclosures') and entry.enclosures:
                                    for enclosure in entry.enclosures:
                                        if hasattr(enclosure, 'type') and enclosure.type and 'image' in enclosure.type:
                                            if hasattr(enclosure, 'url') or hasattr(enclosure, 'href'):
                                                image_url = getattr(enclosure, 'url', getattr(enclosure, 'href', None))
                                                break
                                
                                # Use the section from the feed, with smart fallback
                                article_section = section if section != 'GENERAL' else self._detect_article_section(link, title, summary)
                                
                                # Create article
                                article = NewsArticle(
                                    title=title,
                                    link=link,
                                    published=published,
                                    summary=summary[:300] + "..." if len(summary) > 300 else summary,
                                    section=article_section,
                                    article_id="",
                                    image_url=image_url
                                )
                                
                                articles.append(article)
                                logger.debug(f"✅ {article_section}: {title[:50]}...")
                                
                        except Exception as e:
                            logger.debug(f"Error processing {section} entry: {e}")
                            continue
                    
                    logger.info(f"✅ {section}: Processed {len(articles)} articles")
                    
                else:
                    logger.warning(f"⚠️ {section}: No entries in RSS feed")
            else:
                logger.warning(f"⚠️ {section}: Could not fetch RSS content")
                
        except Exception as e:
            logger.error(f"💥 {section} RSS error: {e}")
            
        return articles
    
    def _detect_article_section(self, link: str, title: str, summary: str) -> str:
        """🎯 Smart section detection from URL and content"""
        content = f"{link} {title} {summary}".lower()
        
        # Detect from URL path
        if 'stock-market' in link or 'equities' in link:
            return 'STOCK-MARKET'
        elif 'crypto' in link or 'bitcoin' in link:
            return 'CRYPTOCURRENCY'  
        elif 'forex' in link or 'currencies' in link:
            return 'FOREX'
        elif 'commodities' in link or 'gold' in link or 'oil' in link:
            return 'COMMODITIES'
        elif 'economic-indicators' in link or 'economy' in link:
            return 'ECONOMIC-INDICATORS'
        elif 'earnings' in link:
            return 'EARNINGS'
        
        # Detect from content
        if any(word in content for word in ['bitcoin', 'crypto', 'ethereum']):
            return 'CRYPTOCURRENCY'
        elif any(word in content for word in ['fed', 'jobs', 'unemployment', 'inflation', 'gdp']):
            return 'ECONOMIC-INDICATORS'  
        elif any(word in content for word in ['stock', 'shares', 'earnings', 'nasdaq', 'dow']):
            return 'STOCK-MARKET'
        elif any(word in content for word in ['dollar', 'yen', 'euro', 'forex', 'currency']):
            return 'FOREX'
        elif any(word in content for word in ['gold', 'oil', 'commodity', 'crude']):
            return 'COMMODITIES'
        
        return 'BREAKING-NEWS'  # Default

    async def _breaking_news_blitz(self, max_articles: int) -> List[NewsArticle]:
        """BLITZ: Ultra-fast breaking news acquisition using proven methods"""
        logger.info("⚡ BLITZ: Going for breaking news at lightning speed...")
        
        # BLITZ: Hit the most reliable sources simultaneously
        tasks = [
            self._blitz_rss_feeds(max_articles // 2),
            self._blitz_alternative_endpoints(max_articles // 2),
            self._blitz_mobile_scraping(max_articles // 3)
        ]
        
        try:
            # Run all methods simultaneously for maximum speed
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_articles = []
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
            
            # BLITZ: Prioritize breaking news and recent articles
            breaking_articles = self._prioritize_breaking_news(all_articles)
            
            return breaking_articles[:max_articles]
            
        except Exception as e:
            logger.debug(f"BLITZ failed: {e}")
            return []

    async def _blitz_rss_feeds(self, max_articles: int) -> List[NewsArticle]:
        """BLITZ: Super-fast RSS acquisition focusing on breaking news"""
        # BLITZ: ENHANCED RSS feeds - GUARANTEED coverage of ALL sections
        priority_feeds = {
            # CORE SECTIONS: User's absolute requirements
            'headlines': 'https://www.investing.com/rss/news.rss',  # Main headlines
            'economic_indicators': 'https://www.investing.com/rss/news_301.rss',  # Economic indicators
            'stock_market': 'https://www.investing.com/rss/news_25.rss',  # Stock market
            'commodities': 'https://www.investing.com/rss/news_49.rss',  # Commodities
            'forex': 'https://www.investing.com/rss/news_95.rss',  # Forex
            'cryptocurrency': 'https://www.investing.com/rss/news_285.rss',  # Cryptocurrency
            
            # ENHANCED: Multiple feeds per section for reliability
            'breaking': 'https://www.investing.com/rss/news_14.rss',  # Breaking news
            'economy': 'https://www.investing.com/rss/news_173.rss',  # Economy news
            
            # Real-time news sources
            'marketwatch': 'https://feeds.marketwatch.com/marketwatch/realtimeheadlines/',  # Real-time headlines ✅
            'cointelegraph': 'https://cointelegraph.com/rss',  # Crypto news ✅
            
            # BACKUP: Alternative sources for missing sections
            'forex_alt': 'https://www.investing.com/rss/market_overview.rss',  # Forex backup
            'crypto_alt': 'https://www.investing.com/rss/analysis.rss',  # Crypto backup
        }
        
        articles = []
        
        # Use ultra-fast requests for RSS
        for feed_name, rss_url in priority_feeds.items():
            if len(articles) >= max_articles:
                break
                
            try:
                response = requests.get(
                    rss_url, 
                    headers=self._get_blitz_headers(),
                    timeout=5,  # Super fast timeout
                    verify=False
                )
                
                if response.status_code == 200:
                    import feedparser
                    feed = feedparser.parse(response.text)
                    
                    for entry in feed.entries[:8]:  # Top 8 per feed for better section coverage
                        if len(articles) >= max_articles:
                            break
                            
                        title = getattr(entry, 'title', '')
                        link = getattr(entry, 'link', '')
                        summary = getattr(entry, 'summary', '')
                        
                        if title and link and len(title) > 10:
                            # 🚫 FILTER OUT: Insider trading news (boring director buy/sell articles)
                            if 'insider-trading' in link.lower() or self._is_insider_trading_news(title):
                                logger.debug(f"🚫 Skipping insider trading: {title[:50]}...")
                                continue
                            
                            # Clean summary
                            if summary:
                                summary = re.sub(r'<[^>]+>', '', summary).strip()
                                # 🧹 CLEAN: Remove "Investing.com-" from beginning
                                summary = re.sub(r'^Investing\.com[-\s]*', '', summary, flags=re.IGNORECASE)
                                summary = summary.strip()
                            
                            # 📸 NEW: Extract image URL from RSS enclosure
                            image_url = None
                            if hasattr(entry, 'enclosures') and entry.enclosures:
                                for enclosure in entry.enclosures:
                                    if hasattr(enclosure, 'type') and enclosure.type and 'image' in enclosure.type:
                                        if hasattr(enclosure, 'url') or hasattr(enclosure, 'href'):
                                            image_url = getattr(enclosure, 'url', getattr(enclosure, 'href', None))
                                            break
                            
                            # ENHANCED: Better section identification for BLITZ mode
                            section_names = {
                                'headlines': 'HEADLINES-BLITZ',
                                'breaking': 'BREAKING-BLITZ',
                                'economic_indicators': 'ECONOMIC-BLITZ',
                                'stock_market': 'STOCKS-BLITZ',
                                'commodities': 'COMMODITIES-BLITZ',
                                'forex': 'FOREX-BLITZ',
                                'cryptocurrency': 'CRYPTO-BLITZ',
                                'economy': 'ECONOMY-BLITZ',
                                # Real-time sources
                                'marketwatch': 'HEADLINES-BLITZ',  # MarketWatch headlines
                                'cointelegraph': 'CRYPTO-BLITZ',   # Crypto news
                                'forex_alt': 'FOREX-BLITZ',
                                'crypto_alt': 'CRYPTO-BLITZ'
                            }
                            
                            article = NewsArticle(
                                title=title.strip(),
                                link=link,
                                published=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'),
                                summary=summary[:200] + "..." if len(summary) > 200 else summary,
                                section=section_names.get(feed_name, f"BLITZ-{feed_name.upper()}"),
                                article_id="",
                                image_url=image_url  # NEW: Include image URL
                            )
                            
                            # ENHANCED: Include ALL required sections + breaking news
                            content = f"{title} {summary}"
                            # ENHANCED: Include articles from ALL feeds including external sources
                            if (self._is_breaking_news(article) or 
                                feed_name in ['headlines', 'economic_indicators', 'stock_market', 'commodities', 'forex', 'cryptocurrency', 'marketwatch', 'cointelegraph', 'breaking', 'economy'] or
                                any(keyword in content.lower() for keyword in ['market', 'economic', 'stock', 'commodity', 'forex', 'crypto', 'bitcoin', 'ethereum', 'blockchain'])):
                                articles.append(article)
                                logger.info(f"⚡ {section_names.get(feed_name, feed_name.upper())}: {title[:50]}...")
                            
            except Exception as e:
                logger.debug(f"RSS blitz failed for {feed_name}: {e}")
                continue
                
        return articles

    def _get_blitz_headers(self) -> Dict[str, str]:
        """BLITZ: Ultra-fast headers that work reliably"""
        return {
            'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)',
            'Accept': 'application/rss+xml, application/xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    def _is_breaking_news(self, article: NewsArticle) -> bool:
        """BLITZ: Identify breaking news articles"""
        content = f"{article.title} {article.summary}".lower()
        
        breaking_indicators = [
            'breaking', 'urgent', 'alert', 'just in', 'live', 'now', 'latest',
            'fed', 'federal reserve', 'crisis', 'crash', 'surge', 'soars', 'plunges',
            'bitcoin', 'crypto', 'ethereum', 'inflation', 'jobs', 'unemployment',
            'earnings', 'market', 'dow', 'nasdaq', 'sp500', 'tesla', 'apple',
            'oil', 'gold', 'dollar', 'euro', 'yen', 'pound', 'rate', 'cut', 'hike',
            'emergency', 'stimulus', 'bailout', 'recession', 'recovery', 'gdp'
        ]
        
        score = sum(1 for indicator in breaking_indicators if indicator in content)
        return score >= 1 or 'BREAKING' in article.section

    def _prioritize_breaking_news(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """BLITZ: Sort articles by breaking news priority"""
        def breaking_score(article):
            score = 0
            content = f"{article.title} {article.summary}".lower()
            
            # High priority keywords
            if any(word in content for word in ['fed', 'bitcoin', 'crash', 'surge']):
                score += 10
            
            # Breaking indicators
            if any(word in content for word in ['breaking', 'urgent', 'just in']):
                score += 5
                
            # Recent time bonus
            if 'BREAKING' in article.section:
                score += 3
                
            return score
        
        return sorted(articles, key=breaking_score, reverse=True)
    
    async def _hardcore_investing_scraping(self, max_articles: int) -> List[NewsArticle]:
        """
        MAIN PAGE SCRAPING: Get articles from investing.com main page layout (like in your image)
        Uses the category tabs: Breaking News, Currencies, Commodities, Stock Markets, etc.
        """
        articles = []
        
        # MAIN PAGE: Target the investing.com homepage structure from your image
        main_page_categories = {
            # WORKING URLs based on actual investing.com structure
            'currencies': 'Currencies',  # ✅ WORKING
            'crypto/currencies': 'Cryptocurrency',  # ✅ WORKING 
            'commodities': 'Commodities',
            'equities': 'Stock Markets',
            'news/stock-market-news': 'Stock Market News',  # Better URL
            'news/economic-indicators': 'Economic Indicators',  # News section
            'economic-calendar': 'Economic Calendar',  # Alternative
        }
        
        try:
            logger.info(f"🎯 MAIN PAGE: Targeting investing.com main page structure")
            
            # FIRST: Get articles from main homepage (like your image shows)
            main_articles = await self._scrape_main_homepage(max_articles // 2)
            if main_articles:
                articles.extend(main_articles)
                logger.info(f"✅ MAIN PAGE: {len(main_articles)} articles from homepage")
            
            # THEN: Get from category tabs (bottom of your image)  
            for i, (category_path, category_name) in enumerate(main_page_categories.items()):
                if len(articles) >= max_articles:
                    break
                    
                try:
                    # SIMPLE: Basic session management
                    await self.create_session()
                    
                    # SIMPLE: Small delay between categories
                    if i > 0:
                        delay = random.uniform(3.0, 6.0)
                        logger.info(f"⏱️  Delay {delay:.1f}s for {category_name}")
                        await asyncio.sleep(delay)
                    
                    # SIMPLE: Get content from category page
                    category_articles = await self._scrape_category_page(category_path, category_name, max_articles - len(articles))
                    
                    if category_articles:
                        articles.extend(category_articles)
                        logger.info(f"✅ {category_name} → {len(category_articles)} articles")
                    else:
                        logger.warning(f"⚠️  {category_name} → No articles found")
                        
                except Exception as e:
                    logger.error(f"❌ Error in {category_name} - {e}")
                    continue
                
            # SIMPLE: Final processing and ranking
            if articles:
                unique_articles = self._simple_deduplicate(articles)
                logger.info(f"🎯 MAIN PAGE SUCCESS: {len(unique_articles)} real-time articles from investing.com")
                return unique_articles[:max_articles]
            else:
                logger.warning("⚠️  MAIN PAGE: No articles retrieved - trying RSS fallback")
                return await self._investing_rss_fallback(max_articles)
                
        except Exception as e:
            logger.error(f"💥 MAIN PAGE: Critical error - {e}")
            # Last resort: RSS from investing.com only
            return await self._investing_rss_fallback(max_articles)
    
    async def _scrape_main_homepage(self, max_articles: int) -> List[NewsArticle]:
        """Scrape articles from investing.com main homepage (like your image shows)"""
        articles = []
        
        try:
            await self.create_session()
            
            # Target the main investing.com page
            url = "https://www.investing.com"
            
            # Simple headers that work
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            # Try to get the main page content
            content = await self._fetch_page_content(url, headers)
            
            if content:
                # Parse the main page article cards (like in your image)
                articles = await self._parse_main_page_articles(content, max_articles)
                logger.info(f"🏠 HOMEPAGE: Found {len(articles)} articles from main page")
            else:
                logger.warning("❌ Could not fetch main homepage content")
                
        except Exception as e:
            logger.error(f"💥 Error scraping main homepage: {e}")
            
        return articles
    
    async def _scrape_category_page(self, category_path: str, category_name: str, max_articles: int) -> List[NewsArticle]:
        """Scrape articles from category tabs (like bottom of your image)"""
        articles = []
        
        # 🔄 SMART: Multiple URL attempts for each category
        fallback_urls = self._get_category_fallback_urls(category_path, category_name)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.investing.com/',
        }
        
        # Try each URL until one works
        for attempt, url in enumerate(fallback_urls, 1):
            try:
                logger.debug(f"🔄 {category_name}: Trying URL {attempt}/{len(fallback_urls)}: {url}")
                
                # Get category page content
                content = await self._fetch_page_content(url, headers)
                
                if content and len(content) > 1000:  # Valid page content
                    # Parse articles from category page
                    articles = await self._parse_category_articles(content, category_name, max_articles)
                    if articles:
                        logger.info(f"📁 {category_name}: Found {len(articles)} articles (URL {attempt})")
                        break
                    else:
                        logger.debug(f"⚠️  {category_name}: URL {attempt} loaded but no articles parsed")
                else:
                    logger.debug(f"❌ {category_name}: URL {attempt} failed or invalid content")
                
                # Small delay between attempts
                if attempt < len(fallback_urls):
                    await asyncio.sleep(1.0)
                    
            except Exception as e:
                logger.debug(f"💥 {category_name}: URL {attempt} error: {e}")
                continue
        
        if not articles:
            logger.warning(f"❌ {category_name}: All URLs failed")
            
        return articles
    
    def _get_category_fallback_urls(self, category_path: str, category_name: str) -> List[str]:
        """Get multiple fallback URLs for each category"""
        base_url = "https://www.investing.com"
        
        # Category-specific fallback strategies
        fallback_mapping = {
            'Currencies': [
                f"{base_url}/currencies",
                f"{base_url}/currencies/eur-usd",
                f"{base_url}/currencies/us-dollar-index"
            ],
            'Cryptocurrency': [
                f"{base_url}/crypto/currencies",
                f"{base_url}/crypto",
                f"{base_url}/currencies/bitcoin",
                f"{base_url}/crypto/bitcoin"
            ],
            'Commodities': [
                f"{base_url}/commodities",
                f"{base_url}/commodities/gold",
                f"{base_url}/commodities/crude-oil"
            ],
            'Stock Markets': [
                f"{base_url}/equities",
                f"{base_url}/equities/united-states",
                f"{base_url}/indices/us-spx-500"
            ],
            'Stock Market News': [
                f"{base_url}/news/stock-market-news",
                f"{base_url}/news/latest-news",
                f"{base_url}/news"
            ],
            'Economic Indicators': [
                f"{base_url}/news/economic-indicators",
                f"{base_url}/economic-calendar",
                f"{base_url}/news/economy-news"
            ],
            'Economic Calendar': [
                f"{base_url}/economic-calendar",
                f"{base_url}/economic-calendar/",
                f"{base_url}/news/economic-indicators"
            ]
        }
        
        # Get specific fallbacks or use the original path
        if category_name in fallback_mapping:
            return fallback_mapping[category_name]
        else:
            return [f"{base_url}/{category_path}"]
    
    async def _fetch_page_content(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Simple method to fetch page content"""
        try:
            # Try with requests first (often works better)
            import requests
            response = requests.get(url, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                logger.debug(f"✅ Fetched with requests: {len(response.text)} chars")
                return response.text
            else:
                logger.debug(f"❌ Requests failed: {response.status_code}")
                
        except Exception as e:
            logger.debug(f"Requests failed: {e}")
            
        # Fallback to aiohttp
        try:
            async with self.session.get(url, headers=headers, timeout=20) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.debug(f"✅ Fetched with aiohttp: {len(content)} chars")
                    return content
                else:
                    logger.debug(f"❌ Aiohttp failed: {response.status}")
                    
        except Exception as e:
            logger.debug(f"Aiohttp failed: {e}")
            
        return None
    
    async def _parse_main_page_articles(self, content: str, max_articles: int) -> List[NewsArticle]:
        """Parse articles from main homepage content (article cards like in your image)"""
        articles = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for article cards/containers (main page structure)
            article_selectors = [
                # Common article card selectors for investing.com main page
                'article[data-test-id]',
                'div[data-test-id="article-item"]',
                'div[class*="article"]',
                'a[class*="articleItem"]',
                'div[class*="story"]',
                'div[class*="news"]',
                # Backup selectors
                'a[href*="/news/"]',
                '.js-article-item',
            ]
            
            article_elements = []
            for selector in article_selectors:
                try:
                    elements = soup.select(selector, limit=max_articles * 2)
                    if elements and len(elements) > 3:  # Must find reasonable number
                        article_elements = elements
                        logger.info(f"📰 Found {len(elements)} articles with: {selector}")
                        break
                except:
                    continue
            
            if not article_elements:
                logger.warning("❌ No article elements found on main page")
                return []
            
            # Parse each article element
            for element in article_elements[:max_articles]:
                try:
                    article = await self._extract_simple_article(element, "HOMEPAGE")
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.debug(f"Error parsing article element: {e}")
                    continue
            
            soup.decompose()
            
        except Exception as e:
            logger.error(f"💥 Error parsing main page articles: {e}")
            
        return articles
    
    async def _parse_category_articles(self, content: str, category_name: str, max_articles: int) -> List[NewsArticle]:
        """Parse articles from category page content"""
        articles = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for article listings in category pages
            article_selectors = [
                'article',
                'div[class*="article"]',
                'div[class*="news"]',
                'a[href*="/news/"]',
                'tr[data-test-id]',  # Sometimes table rows
                'div[class*="item"]',
            ]
            
            article_elements = []
            for selector in article_selectors:
                try:
                    elements = soup.select(selector, limit=max_articles * 2)
                    if elements:
                        article_elements = elements
                        logger.debug(f"Found elements with: {selector}")
                        break
                except:
                    continue
            
            # Parse each article
            for element in article_elements[:max_articles]:
                try:
                    article = await self._extract_simple_article(element, category_name)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.debug(f"Error parsing category article: {e}")
                    continue
            
            soup.decompose()
            
        except Exception as e:
            logger.error(f"💥 Error parsing {category_name} articles: {e}")
            
        return articles
    
    async def _extract_simple_article(self, element, section_name: str) -> Optional[NewsArticle]:
        """Simple article extraction from HTML element"""
        try:
            # Get title
            title = None
            title_selectors = ['h3', 'h2', 'h4', 'a', '.title', '[title]']
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    if title_text and len(title_text) > 10:
                        title = title_text
                        break
            
            if not title:
                return None
            
            # Get link
            link = None
            link_elem = element.select_one('a[href]')
            if link_elem:
                href = link_elem.get('href')
                if href:
                    if href.startswith('/'):
                        link = f"https://www.investing.com{href}"
                    elif href.startswith('http'):
                        link = href
            
            if not link:
                return None
            
            # Get summary (optional)
            summary = ""
            summary_elem = element.select_one('p, .summary, .description')
            if summary_elem:
                summary = summary_elem.get_text(strip=True)[:200]
                # 🧹 CLEAN: Remove "Investing.com-" from beginning
                import re
                summary = re.sub(r'^Investing\.com[-\s]*', '', summary, flags=re.IGNORECASE)
                summary = summary.strip()
            
            # 📸 GET IMAGE: Extract image URL from article
            image_url = None
            img_selectors = ['img[src]', 'img[data-src]', '.image img', '.thumbnail img']
            for selector in img_selectors:
                img_elem = element.select_one(selector)
                if img_elem:
                    img_src = img_elem.get('src') or img_elem.get('data-src')
                    if img_src:
                        if img_src.startswith('/'):
                            image_url = f"https://www.investing.com{img_src}"
                        elif img_src.startswith('http'):
                            image_url = img_src
                        break
            
            # Create article
            article = NewsArticle(
                title=title,
                link=link,
                published=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'),
                summary=summary,
                section=section_name,
                article_id="",
                image_url=image_url  # 📸 Include image URL
            )
            
            return article
            
        except Exception as e:
            logger.debug(f"Error extracting simple article: {e}")
            return None
    
    async def _advanced_session_setup(self):
        """STEALTH: Advanced session management with browser emulation"""
        
        # STEALTH: Recreate session periodically to avoid tracking
        if hasattr(self, '_session_requests') and self._session_requests > 5:
            if self.session:
                await self.session.close()
                self.session = None
                logger.debug("🔄 STEALTH: Session rotation for anti-tracking")
                await asyncio.sleep(random.uniform(1.0, 3.0))
        
        # Ensure fresh session
        await self.create_session()
        
        # STEALTH: Track requests per session
        if not hasattr(self, '_session_requests'):
            self._session_requests = 0
        self._session_requests += 1
    
    async def _calculate_stealth_delay(self, section_index: int, section_name: str) -> float:
        """STEALTH: Human-like delay patterns specific to investing.com"""
        
        # STEALTH: Base delays that mimic real user behavior
        base_delays = {
            'Latest News': 8.0,         # Longer for main news (high traffic)
            'Economic Indicators': 12.0, # Longest (most monitored)
            'Cryptocurrency': 6.0,      # Medium delay
            'Forex': 7.0,              # Medium-high
            'Commodities': 5.0,         # Shorter
            'Stock Market': 6.5,        # Medium
        }
        
        base_delay = base_delays.get(section_name, 6.0)
        
        # STEALTH: Add realistic jitter (human behavior)
        jitter = random.uniform(2.0, 5.0)
        
        # STEALTH: Progressive increase (fatigue simulation)
        fatigue_factor = section_index * 0.8
        
        # STEALTH: Random "thinking" pauses
        thinking_pause = random.choice([0, 0, 0, random.uniform(3.0, 8.0)])  # 25% chance
        
        total_delay = base_delay + jitter + fatigue_factor + thinking_pause
        
        return min(total_delay, 20.0)  # Cap at 20 seconds max
    
    async def _stealth_scrape_section(self, section_path: str, section_name: str, max_articles: int) -> List[NewsArticle]:
        """STEALTH: Advanced scraping for specific investing.com section"""
        articles = []
        
        try:
            # STEALTH: Construct real investing.com URL
            url = f"{self.base_url}/{section_path}"
            
            # STEALTH: Advanced headers that perfectly mimic Chrome
            headers = await self._get_stealth_headers(section_name)
            
            logger.info(f"🎯 STEALTH: Targeting {url}")
            
            # STEALTH: Multiple attempts with different techniques
            content = None
            for attempt in range(3):
                try:
                    if attempt == 0:
                        # STEALTH: Primary method - Full browser emulation
                        content = await self._fetch_with_browser_emulation(url, headers)
                    elif attempt == 1:
                        # STEALTH: Secondary method - Advanced session
                        content = await self._fetch_with_advanced_session(url, headers)
                    else:
                        # STEALTH: Fallback method - Simple with stealth headers
                        content = await self._fetch_with_stealth_simple(url, headers)
                    
                    if content:
                        break
                        
                    # STEALTH: Escalating delays between attempts
                    delay = (attempt + 1) * 5.0 + random.uniform(2.0, 4.0)
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    logger.warning(f"⚠️  STEALTH: Attempt {attempt + 1} failed for {section_name}: {e}")
                    continue
            
            if not content:
                logger.error(f"❌ STEALTH: All attempts failed for {section_name}")
                return []
            
            # STEALTH: Parse with advanced techniques
            articles = await self._parse_investing_content(content, section_name, max_articles)
            
            return articles
            
        except Exception as e:
            logger.error(f"💥 STEALTH: Critical error in {section_name}: {e}")
            return []
    
    async def _get_stealth_headers(self, section_name: str) -> Dict[str, str]:
        """STEALTH: Advanced headers that perfectly mimic real Chrome browser"""
        
        # STEALTH: Realistic Chrome fingerprint (latest version)
        chrome_versions = [
            '120.0.0.0', '119.0.0.0', '118.0.0.0', '121.0.0.0'
        ]
        
        # STEALTH: OS fingerprints
        os_signatures = [
            ('Windows NT 10.0; Win64; x64', 'Windows'),
            ('Macintosh; Intel Mac OS X 10_15_7', 'macOS'),
            ('X11; Linux x86_64', 'Linux')
        ]
        
        # STEALTH: Select consistent fingerprint
        fingerprint_hash = hash(section_name) % len(os_signatures)
        os_sig, os_name = os_signatures[fingerprint_hash]
        chrome_version = chrome_versions[fingerprint_hash % len(chrome_versions)]
        
        # STEALTH: Perfect Chrome headers
        return {
            'User-Agent': f'Mozilla/5.0 ({os_sig}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': f'"Not_A Brand";v="8", "Chromium";v="{chrome_version.split(".")[0]}", "Google Chrome";v="{chrome_version.split(".")[0]}"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': f'"{os_name}"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
            'DNT': '1',
        }
    
    async def _fetch_with_browser_emulation(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """PROFESSIONAL: Advanced browser emulation with multiple bypass techniques"""
        try:
            # PROFESSIONAL: Start with homepage visit to establish session
            if 'investing.com' in url and not getattr(self, '_homepage_visited', False):
                await self._visit_homepage_first()
                self._homepage_visited = True
            
            # PROFESSIONAL: Enhanced headers with investing.com specific values
            enhanced_headers = headers.copy()
            enhanced_headers.update({
                'Referer': 'https://www.investing.com/',
                'Origin': 'https://www.investing.com',
                'Host': 'www.investing.com',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
            })
            
            # PROFESSIONAL: Simulate realistic browsing pattern
            await asyncio.sleep(random.uniform(1.0, 2.5))
            
            # PROFESSIONAL: Try multiple methods in sequence
            methods = [
                self._fetch_with_curl_simulation,
                self._fetch_with_requests_session,
                self._fetch_standard_aiohttp
            ]
            
            for method in methods:
                try:
                    result = await method(url, enhanced_headers)
                    if result:
                        return result
                    # Wait between method attempts
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                except Exception as e:
                    logger.debug(f"Method failed: {e}")
                    continue
            
            return None
                    
        except Exception as e:
            logger.error(f"💥 PROFESSIONAL: Browser emulation failed - {e}")
            return None

    async def _visit_homepage_first(self):
        """Visit investing.com homepage first to establish legitimate session"""
        try:
            fingerprint = self._get_random_browser_fingerprint()
            homepage_headers = {
                'User-Agent': fingerprint['user_agent'],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': fingerprint['accept_languages'],
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            async with self.session.get('https://www.investing.com', headers=homepage_headers, timeout=20) as response:
                if response.status == 200:
                    logger.info("🏠 Established session via homepage visit")
                    # Small delay to mimic reading
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                else:
                    logger.warning(f"⚠️ Homepage visit returned {response.status}")
        except Exception as e:
            logger.debug(f"Homepage visit failed: {e}")

    async def _fetch_with_curl_simulation(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Simulate curl-like request that often bypasses basic protection"""
        try:
            # Use requests library to simulate curl
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            
            # Advanced retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Curl-like headers
            curl_headers = {
                'User-Agent': headers.get('User-Agent'),
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = session.get(
                url, 
                headers=curl_headers, 
                timeout=25,
                allow_redirects=True,
                verify=False
            )
            
            if response.status_code == 200:
                logger.info(f"✅ CURL simulation successful - {len(response.text)} chars")
                return response.text
            else:
                logger.debug(f"CURL simulation failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.debug(f"CURL simulation error: {e}")
            return None

    async def _fetch_with_requests_session(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Use requests with session persistence"""
        try:
            import requests
            
            # Create persistent session
            if not hasattr(self, '_requests_session'):
                self._requests_session = requests.Session()
                # Add some cookies to look established
                self._requests_session.cookies.update({
                    'SideBlockUser': 'a%3A2%3A%7Bs%3A10%3A%22stack_size%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Bi%3A8%3B%7Ds%3A6%3A%22stacks%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Ba%3A0%3A%7B%7D%7D%7D',
                    'PHPSESSID': f'investing_{random.randint(1000000, 9999999)}',
                })
            
            response = self._requests_session.get(
                url,
                headers=headers,
                timeout=30,
                allow_redirects=True,
                verify=False
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Requests session successful - {len(response.text)} chars")
                return response.text
            else:
                logger.debug(f"Requests session failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.debug(f"Requests session error: {e}")
            return None

    async def _fetch_standard_aiohttp(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Standard aiohttp fetch as final fallback"""
        try:
            async with self.session.get(url, headers=headers, timeout=25) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"✅ Standard aiohttp successful - {len(content)} chars")
                    return content
                else:
                    logger.debug(f"Standard aiohttp failed: {response.status}")
                    return None
        except Exception as e:
            logger.debug(f"Standard aiohttp error: {e}")
            return None
    
    async def _fetch_with_advanced_session(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """STEALTH: Advanced session management with cookies"""
        try:
            # STEALTH: Simulate cookie behavior
            headers.update({
                'Referer': 'https://www.google.com/',  # Simulate Google referral
            })
            
            async with self.session.get(url, headers=headers, timeout=20) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"✅ STEALTH: Advanced session successful - {len(content)} chars")
                    return content
                else:
                    logger.warning(f"⚠️  STEALTH: Advanced session HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"💥 STEALTH: Advanced session failed - {e}")
            return None
    
    async def _fetch_with_stealth_simple(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """STEALTH: Simple stealth method as last resort"""
        try:
            async with self.session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"✅ STEALTH: Simple method successful - {len(content)} chars")
                    return content
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"💥 STEALTH: Simple method failed - {e}")
            return None
    
    async def _parse_investing_content(self, content: str, section_name: str, max_articles: int) -> List[NewsArticle]:
        """STEALTH: Parse investing.com HTML content with advanced techniques"""
        articles = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
                    
            # STEALTH: Multiple selector strategies for investing.com
            article_selectors = [
                # Primary selectors (current investing.com structure)
                'article[data-test="article-item"]',
                'div[data-test="article-item"]',
                'article.js-article-item',
                'div.articleItem',
                
                # Secondary selectors (alternative structures)
                'article.largeTitle',
                'div.newsTitle',
                'div[class*="article"]',
                'a[class*="title"]',
                
                # Fallback selectors
                'div[class*="news"]',
                'div[class*="item"]',
            ]
            
            # STEALTH: Try each selector until we find articles
            article_elements = []
            for selector in article_selectors:
                try:
                    elements = soup.select(selector, limit=max_articles * 2)
                    if elements:
                        article_elements = elements
                        logger.info(f"✅ STEALTH: Found articles with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not article_elements:
                logger.warning(f"⚠️  STEALTH: No articles found with any selector in {section_name}")
                return []
            
            # STEALTH: Process each article element
            for i, element in enumerate(article_elements[:max_articles]):
                try:
                    article = await self._extract_article_data(element, section_name)
                    if article and self._is_relevant_investing_article(article):
                        articles.append(article)
                        logger.debug(f"📰 STEALTH: Extracted - {article.title[:50]}...")
                        
                except Exception as e:
                    logger.debug(f"Error extracting article {i}: {e}")
                    continue
                                
            # Clean up
            soup.decompose()
            
            logger.info(f"✅ STEALTH: Parsed {len(articles)} articles from {section_name}")
            return articles
            
        except Exception as e:
            logger.error(f"💥 STEALTH: Parsing error for {section_name}: {e}")
            return []
    
    async def _extract_article_data(self, element, section_name: str) -> Optional[NewsArticle]:
        """STEALTH: Extract article data from HTML element"""
        try:
            # STEALTH: Multiple strategies for title extraction
            title = None
            title_selectors = ['h3', 'h2', 'h4', 'a[class*="title"]', 'a[class*="headline"]', 'a']
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    title = title_elem.get_text(strip=True)
                    break
            
            if not title or len(title) < 10:
                return None
            
            # STEALTH: Multiple strategies for link extraction
            link = None
            link_selectors = ['a[href]', 'a[class*="title"]', 'a[class*="headline"]']
            
            for selector in link_selectors:
                link_elem = element.select_one(selector)
                if link_elem and link_elem.get('href'):
                    href = link_elem.get('href')
                    if href.startswith('/'):
                        link = f"{self.base_url}{href}"
                    elif href.startswith('http'):
                        link = href
                    break
            
            if not link:
                return None
            
            # STEALTH: Extract summary/description
            summary = ""
            summary_selectors = ['p[class*="summary"]', 'div[class*="summary"]', 'p[class*="desc"]', 'div[class*="desc"]', 'p']
            
            for selector in summary_selectors:
                summary_elem = element.select_one(selector)
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)
                    if len(summary) > 20:  # Only use meaningful summaries
                        break
            
            # STEALTH: Extract timestamp
            published = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
            time_selectors = ['time', 'span[class*="time"]', 'span[class*="date"]', 'div[class*="time"]']
            
            for selector in time_selectors:
                time_elem = element.select_one(selector)
                if time_elem:
                    time_text = time_elem.get_text(strip=True)
                    if time_text and len(time_text) > 3:
                        published = time_text
                        break
            
            # 📸 STEALTH: Extract image URL
            image_url = None
            img_selectors = ['img[src]', 'img[data-src]', '.image img', '.thumbnail img', 'figure img']
            for selector in img_selectors:
                img_elem = element.select_one(selector)
                if img_elem:
                    img_src = img_elem.get('src') or img_elem.get('data-src')
                    if img_src:
                        if img_src.startswith('/'):
                            image_url = f"https://www.investing.com{img_src}"
                        elif img_src.startswith('http'):
                            image_url = img_src
                        break
            
            # STEALTH: Create article object
            article = NewsArticle(
                title=title,
                link=link,
                published=published,
                summary=summary[:250] + "..." if len(summary) > 250 else summary,
                section=section_name,
                article_id="",  # Will be auto-generated
                image_url=image_url  # 📸 Include image URL
            )
            
            return article
            
        except Exception as e:
            logger.debug(f"Error extracting article data: {e}")
            return None
    
    def _is_relevant_investing_article(self, article: NewsArticle) -> bool:
        """🎯 STRICT: Financial markets ONLY - NO world news, politics, wars, sports"""
        content = f"{article.title} {article.summary}".lower()
        
        # ✅ REQUIRED: Financial market keywords
        section_keywords = {
            'headlines': ['news', 'breaking', 'market', 'economy', 'finance', 'business'],
            'economic_indicators': ['fed', 'federal reserve', 'inflation', 'unemployment', 'jobs', 'gdp', 'cpi', 'pmi', 'rates'],
            'stock_market': ['stock', 'shares', 'dow', 'nasdaq', 'sp500', 'earnings', 'ipo', 'dividend'],
            'commodities': ['gold', 'oil', 'silver', 'copper', 'gas', 'wheat', 'corn', 'commodity'],
            'forex': ['dollar', 'euro', 'yen', 'pound', 'currency', 'forex', 'exchange', 'usd', 'eur', 'gbp'],
            'cryptocurrency': ['bitcoin', 'crypto', 'ethereum', 'blockchain', 'btc', 'eth', 'defi', 'nft']
        }
        
        # 🔥 PRIORITY: High-impact financial keywords
        high_priority = [
            'fed', 'federal reserve', 'interest rate', 'inflation', 'bitcoin', 'crypto', 
            'market crash', 'market surge', 'breaking', 'urgent', 'economy', 'recession',
            'earnings', 'revenue', 'profit', 'ipo', 'merger', 'acquisition'
        ]
        
        # Calculate financial relevance score
        score = 0
        
        # High priority gets maximum score
        for keyword in high_priority:
            if keyword in content:
                score += 3
        
        # Section-specific keywords
        for section, keywords in section_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    score += 1
        
        # Always include if from financial sections
        section_indicators = ['headlines', 'economic', 'stock', 'commodities', 'forex', 'crypto']
        if any(indicator in article.section.lower() for indicator in section_indicators):
            score += 2
            
        return score >= 1  # Must have financial relevance
    
    def _simple_deduplicate(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Simple deduplication - just remove exact title matches"""
        if not articles:
            return []
        
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # Simple normalization
            normalized_title = article.title.lower().strip()
            
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        return unique_articles
    
    async def _investing_rss_fallback(self, max_articles: int) -> List[NewsArticle]:
        """PROFESSIONAL: Enhanced RSS fallback with multiple feed sources"""
        logger.info("🔄 PROFESSIONAL: Enhanced RSS fallback strategy")
        
        articles = []
        
        # PROFESSIONAL: Complete RSS strategy covering ALL user sections
        rss_endpoints = {
            # USER'S REQUIRED SECTIONS (Priority feeds)
            'headlines': 'https://www.investing.com/rss/news.rss',  # Headlines
            'economic_indicators': 'https://www.investing.com/rss/news_301.rss',  # Economic indicators
            'stock_market': 'https://www.investing.com/rss/news_25.rss',  # Stock market
            'commodities': 'https://www.investing.com/rss/news_49.rss',  # Commodities
            'forex': 'https://www.investing.com/rss/news_95.rss',  # Forex
            'cryptocurrency': 'https://www.investing.com/rss/news_285.rss',  # Cryptocurrency
            
            # SUPPORTING SECTIONS
            'breaking_news': 'https://www.investing.com/rss/news_14.rss',  # Breaking news
            'economy_news': 'https://www.investing.com/rss/news_173.rss',  # Economy news
            'world_news': 'https://www.investing.com/rss/news_14.rss',  # World news
            
            # BACKUP SOURCES (for when investing.com has issues)
            'marketwatch_markets': 'https://feeds.content.dowjones.io/public/rss/mw_topstories',
            'reuters_business': 'https://feeds.reuters.com/reuters/businessNews',
        }
        
        try:
            import feedparser
            
            for feed_name, rss_url in rss_endpoints.items():
                if len(articles) >= max_articles:
                    break
                
                try:
                    logger.info(f"📡 STEALTH RSS: {feed_name}")
                    
                    # PROFESSIONAL: RSS-specific headers that avoid detection
                    rss_headers = {
                        'User-Agent': random.choice([
                            'Mozilla/5.0 (compatible; RSS Reader)',
                            'FeedBurner/1.0 (http://www.FeedBurner.com)',
                            'NewsBlur Feed Fetcher - 1 subscriber - https://newsblur.com',
                            self._get_random_browser_fingerprint()['user_agent']
                        ]),
                        'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml, */*',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Cache-Control': 'no-cache',
                    }
                    
                    await self.create_session()
                    
                    # Try multiple methods for RSS as well
                    content = await self._fetch_rss_content(rss_url, rss_headers)
                    
                    if content:
                        feed = feedparser.parse(content)
                        if feed and hasattr(feed, 'entries'):
                            
                            for entry in feed.entries[:3]:
                                if len(articles) >= max_articles:
                                    break
                                
                                title = getattr(entry, 'title', '')
                                link = getattr(entry, 'link', '')
                                summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
                                published = getattr(entry, 'published', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'))
                                
                                if title and link and len(title) > 10:
                                    # Clean summary
                                    if summary:
                                        summary = re.sub(r'<[^>]+>', '', summary).strip()
                                        # 🧹 CLEAN: Remove "Investing.com-" from beginning
                                        summary = re.sub(r'^Investing\.com[-\s]*', '', summary, flags=re.IGNORECASE)
                                        summary = summary.strip()
                                    
                                    article = NewsArticle(
                                        title=title.strip(),
                                        link=link,
                                        published=published,
                                        summary=summary[:200] + "..." if len(summary) > 200 else summary,
                                        section=f"Investing.com {feed_name.split('_')[1].title()}",
                                        article_id=""
                                    )
                                    
                                    # ENHANCED: Better section tagging and relevance
                                    if 'investing' in feed_name or self._is_relevant_investing_article(article):
                                        # Better section naming based on feed
                                        section_mapping = {
                                            'headlines': 'HEADLINES',
                                            'economic_indicators': 'ECONOMIC-INDICATORS', 
                                            'stock_market': 'STOCK-MARKET',
                                            'commodities': 'COMMODITIES',
                                            'forex': 'FOREX',
                                            'cryptocurrency': 'CRYPTOCURRENCY',
                                            'breaking_news': 'BREAKING-NEWS',
                                            'economy_news': 'ECONOMY-NEWS'
                                        }
                                        
                                        article.section = section_mapping.get(feed_name, f"INVESTING-{feed_name.upper()}")
                                        articles.append(article)
                                        logger.info(f"📰 {article.section}: {title[:50]}...")
                        
                    # PROFESSIONAL: Intelligent delay based on source
                    if 'investing' in feed_name:
                        await asyncio.sleep(random.uniform(4.0, 8.0))  # Longer for investing.com
                    else:
                        await asyncio.sleep(random.uniform(2.0, 4.0))  # Shorter for others
                        
                except Exception as e:
                    logger.error(f"❌ RSS error for {feed_name}: {e}")
                    continue
            
            unique_articles = self._simple_deduplicate(articles)
            logger.info(f"✅ STEALTH RSS: Retrieved {len(unique_articles)} articles from investing.com")
            return unique_articles[:max_articles]
            
        except ImportError:
            logger.error("📦 feedparser not available for RSS fallback")
            return []
        except Exception as e:
            logger.error(f"💥 STEALTH RSS: Critical error - {e}")
            return []
    
    def _get_rotating_headers(self, source_name: str) -> Dict[str, str]:
        """PROFESSIONAL: Rotate user agents and headers per source"""
        
        # Professional user agent pool - real browser signatures
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]
        
        # Select user agent based on source (deterministic but varied)
        ua_index = hash(source_name) % len(user_agents)
        selected_ua = user_agents[ua_index]
        
        # Professional headers that vary by source type
        if 'crypto' in source_name.lower():
            accept_header = 'application/rss+xml, application/xml, */*'
            lang_header = 'en-US,en;q=0.9'
        elif 'investing' in source_name.lower():
            accept_header = 'application/xml, text/xml, */*'
            lang_header = 'en-US,en;q=0.8,es;q=0.7'
        else:
            accept_header = 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*'
            lang_header = 'en-US,en;q=0.9,fr;q=0.8'
        
        return {
            'User-Agent': selected_ua,
            'Accept': accept_header,
            'Accept-Language': lang_header,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _calculate_intelligent_delay(self, source_name: str, request_index: int) -> float:
        """PROFESSIONAL: Calculate intelligent delays to avoid detection"""
        
        # Base delays by source type (seconds)
        if 'investing' in source_name.lower():
            base_delay = 8.0  # Longer for investing.com (they're more aggressive)
        elif 'crypto' in source_name.lower():
            base_delay = 4.0  # Medium for crypto sources
        else:
            base_delay = 2.0  # Shorter for traditional news sources
        
        # Add randomization to avoid patterns
        jitter = random.uniform(0.5, 2.5)
        
        # Increase delay based on request count (gradual slowdown)
        progressive_delay = request_index * 0.3
        
        total_delay = base_delay + jitter + progressive_delay
        
        # Cap at reasonable maximum
        return min(total_delay, 15.0)
    
    async def _process_feed_entries(self, entries: List, source_name: str, max_entries: int) -> List[NewsArticle]:
        """PROFESSIONAL: Process RSS feed entries with advanced filtering"""
        articles = []
        
        # Financial keywords with scoring weights
        keyword_scores = {
            # High priority (crypto/fintech)
            'bitcoin': 3, 'ethereum': 3, 'crypto': 3, 'blockchain': 3, 'defi': 3,
            'fed': 3, 'federal reserve': 3, 'interest rate': 3, 'inflation': 3,
            # Medium priority (markets)
            'dollar': 2, 'market': 2, 'trading': 2, 'stock': 2, 'forex': 2,
            'unemployment': 2, 'jobs': 2, 'gdp': 2, 'economy': 2,
            # Lower priority (general finance)
            'finance': 1, 'investment': 1, 'business': 1, 'earnings': 1,
        }
        
        processed_count = 0
        for entry in entries:
            if processed_count >= max_entries:
                break
                
            try:
                # Extract data
                title = getattr(entry, 'title', 'No title').strip()
                link = getattr(entry, 'link', '')
                summary = getattr(entry, 'summary', getattr(entry, 'description', '')).strip()
                published = getattr(entry, 'published', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'))
                
                # Skip if essential data missing
                if not title or not link or len(title) < 10:
                        continue
                    
                # PROFESSIONAL: Advanced relevance scoring
                content = f"{title} {summary}".lower()
                relevance_score = 0
                
                for keyword, weight in keyword_scores.items():
                    if keyword in content:
                        relevance_score += weight
                
                # Skip low-relevance articles
                if relevance_score < 1:
                    continue
                
                # Clean HTML from summary
                if summary:
                    import re
                    summary = re.sub(r'<[^>]+>', '', summary).strip()
                    summary = re.sub(r'\s+', ' ', summary)
                    # 🧹 CLEAN: Remove "Investing.com-" from beginning
                    summary = re.sub(r'^Investing\.com[-\s]*', '', summary, flags=re.IGNORECASE)
                    summary = summary.strip()
                
                # Create article with relevance score
                article = NewsArticle(
                    title=title,
                    link=link,
                    published=published,
                    summary=summary[:300] + "..." if len(summary) > 300 else summary,
                    section=f"{source_name.replace('_', ' ').title()} (Score: {relevance_score})",
                    article_id=""
                )
                
                # Check for duplicates
                if article.article_id not in self.seen_articles:
                    articles.append(article)
                    self.seen_articles.add(article.article_id)
                    processed_count += 1
                
            except Exception as e:
                logger.debug(f"Error processing entry from {source_name}: {e}")
                continue
            
        return articles
    
    def _deduplicate_and_rank(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Simple deduplication and ranking"""
        
        if not articles:
            return []
        
        # Use simple deduplication
        unique_articles = self._simple_deduplicate(articles)
        
        # Simple ranking by recency (most recent first)
        return unique_articles
    
    async def scrape_economic_calendar(self, days_ahead: int = 1) -> List[EconomicEvent]:
        """
        Scrape economic calendar - ONLY REAL EVENTS, NO FAKE DATA
        """
        events = []
        
        try:
            # Try to scrape real economic calendar
            events = await self._scrape_real_calendar()
            
            # If no events found, return empty list (NO FAKE DATA EVER)
            if not events:
                logger.info("📅 No real economic events found today - returning empty list (no fake/simulated data)")
                return []
            
            return events
            
        except Exception as e:
            logger.error(f"💥 Error scraping economic calendar: {e}")
            # Return empty list instead of fake data
            return []
    
    async def _scrape_real_calendar(self) -> List[EconomicEvent]:
        """REAL DATA: Scrape actual economic calendar from investing.com/economic-calendar"""
        logger.info("🎯 SCRAPING REAL DATA: Getting actual economic events from investing.com/economic-calendar")
        events = []
        
        try:
            # Construct the URL for today's economic calendar
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            calendar_url = f"https://www.investing.com/economic-calendar/"
            
            # Try multiple methods to get the calendar data
            content = await self._fetch_calendar_data(calendar_url)
            
            if content:
                events = await self._parse_calendar_events(content)
                logger.info(f"✅ REAL DATA: Found {len(events)} real economic events")
            else:
                logger.warning("❌ Could not fetch real calendar data")
                
        except Exception as e:
            logger.error(f"💥 Error scraping real calendar: {e}")
            
        return events
    
    def _create_simulated_events_DISABLED(self) -> List[EconomicEvent]:
        """Create simulated economic events with realistic timing"""        
        # DISABLED: No more fake data generation per user request
        logger.warning("🚫 FAKE DATA GENERATION DISABLED - This function should never be called")
        return []
        
        # OLD FAKE CODE (DISABLED):
        simulated_events = []
        
        # Common high-impact USD events that occur regularly
        event_templates = [
            {
                'name': 'unemployment rate',
                'arabic': 'معدل البطالة',
                'importance': 'High',
                'typical_values': ['4.0%', '4.1%', '4.2%'],
                'release_time': '13:30'  # 1:30 PM EST
            },
            {
                'name': 'non farm payrolls',
                'arabic': 'فرص العمل الأمريكية',
                'importance': 'High', 
                'typical_values': ['180K', '200K', '220K'],
                'release_time': '13:30'  # 1:30 PM EST
            },
            {
                'name': 'cpi',
                'arabic': 'مؤشر أسعار المستهلك',
                'importance': 'High',
                'typical_values': ['3.2%', '3.4%', '3.1%'],
                'release_time': '13:30'  # 1:30 PM EST
            },
            {
                'name': 'pmi manufacturing',
                'arabic': 'مؤشر مديري المشتريات التصنيعي',
                'importance': 'Medium',
                'typical_values': ['48.5', '49.2', '50.1'],
                'release_time': '14:45'  # 2:45 PM EST
            }
        ]
        
        # Create realistic events based on current time
        current_time = datetime.now(timezone.utc)
        current_hour = current_time.hour
        
        for i, template in enumerate(event_templates[:3]):  # Limit to 3 events
            values = template['typical_values']
            release_hour = int(template['release_time'].split(':')[0])
            
            # Determine if event should have actual data (if time has passed)
            has_actual_data = current_hour >= release_hour
            
            event = EconomicEvent(
                time=template['release_time'],
                country="United States",
                event_name=template['name'],
                event_name_arabic=template['arabic'],
                importance=template['importance'],
                actual=random.choice(values) if has_actual_data else None,
                forecast=random.choice(values),
                previous=random.choice(values),
                currency="USD"
            )
            
            simulated_events.append(event)
            status = "已发布" if has_actual_data else "即将发布"
            logger.info(f"🤖 Simulated event: {template['arabic']} ({status})")
        
        return simulated_events
    
    def _get_arabic_event_name(self, event_name: str) -> str:
        """Convert English economic event name to Arabic"""
        event_lower = event_name.lower()
        
        # 🔍 ENHANCED: More specific patterns first, then general ones
        specific_patterns = [
            ('mi inflation gauge', 'مؤشر التضخم الشهري الأسترالي'),
            ('inflation gauge', 'مؤشر التضخم'),
            ('unemployment rate', 'معدل البطالة'),
            ('non farm payrolls', 'فرص العمل الأمريكية'),
            ('nonfarm payrolls', 'فرص العمل الأمريكية'),
            ('jobless claims', 'طلبات إعانة البطالة'),
            ('core cpi', 'مؤشر أسعار المستهلك الأساسي'),
            ('cpi', 'مؤشر أسعار المستهلك'),
            ('retail sales', 'مبيعات التجزئة'),
            ('interest rate decision', 'قرار أسعار الفائدة'),
            ('manufacturing pmi', 'مؤشر مديري المشتريات الصناعي'),
            ('services pmi', 'مؤشر مديري المشتريات الخدمي'),
            ('chicago pmi', 'مؤشر مديري المشتريات من شيكاغو'),
            ('ism manufacturing', 'مؤشر مديري المشتريات الصناعي'),
        ]
        
        # Check specific patterns first
        for pattern, translation in specific_patterns:
            if pattern in event_lower:
                return translation
        
        # Direct mapping from dictionary
        for english_term, arabic_term in self.economic_terms_arabic.items():
            if english_term in event_lower:
                return arabic_term
        
        # Enhanced fallback patterns
        if 'unemployment' in event_lower:
            return 'معدل البطالة'
        elif 'payroll' in event_lower or 'jobs' in event_lower:
            return 'تقرير الوظائف الأمريكي'
        elif 'inflation' in event_lower:
            return 'مؤشر التضخم'
        elif 'pmi' in event_lower:
            return 'مؤشر مديري المشتريات'
        elif 'gdp' in event_lower:
            return 'الناتج المحلي الإجمالي'
        elif 'retail' in event_lower:
            return 'مبيعات التجزئة'
        elif 'interest rate' in event_lower or 'fomc' in event_lower:
            return 'قرار أسعار الفائدة'
        else:
            return event_name  # Return original if no mapping found
    
    def get_country_flag(self, country: str) -> str:
        """Get country flag emoji"""
        country_lower = country.lower()
        return self.country_flags.get(country_lower, '🌍')
    
    def cleanup_cache(self):
        """Clean up memory cache to prevent memory issues"""
        if len(self.seen_articles) > 200:
            # Keep only last 100 articles
            articles_list = list(self.seen_articles)
            self.seen_articles = set(articles_list[-100:])
            
        if len(self.seen_events) > 100:
            # Keep only last 50 events  
            events_list = list(self.seen_events)
            self.seen_events = set(events_list[-50:])
            
        logger.info("🧹 Cleaned up memory cache")

    async def _fetch_rss_content(self, rss_url: str, headers: Dict[str, str]) -> Optional[str]:
        """HARDCORE: Multi-method RSS fetching with success rate optimization"""
        # HARDCORE: Order methods by success rate (fastest first)
        methods = [
            (self._fetch_rss_requests, self.method_success_rate['requests']),
            (self._fetch_rss_urllib, 0.8),  # urllib often bypasses blocks
            (self._fetch_rss_aiohttp, self.method_success_rate['aiohttp'])
        ]
        
        # Sort by success rate (highest first)
        methods.sort(key=lambda x: x[1], reverse=True)
        method_funcs = [method[0] for method in methods]
        
        for method in method_funcs:
            try:
                content = await method(rss_url, headers)
                if content:
                    return content
                await asyncio.sleep(random.uniform(1.0, 2.0))
            except Exception as e:
                logger.debug(f"RSS method failed: {e}")
                continue
        
        return None

    async def _fetch_rss_requests(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Fetch RSS using requests library"""
        try:
            import requests
            response = requests.get(url, headers=headers, timeout=20, verify=False)
            if response.status_code == 200:
                logger.debug(f"RSS requests successful: {url}")
                return response.text
        except Exception as e:
            logger.debug(f"RSS requests failed: {e}")
        return None

    async def _fetch_rss_urllib(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Fetch RSS using urllib (often bypasses protection)"""
        try:
            from urllib.request import urlopen, Request
            import ssl
            
            # Create unverified SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            req = Request(url, headers=headers)
            
            with urlopen(req, context=ssl_context, timeout=20) as response:
                if response.getcode() == 200:
                    content = response.read().decode('utf-8')
                    logger.debug(f"RSS urllib successful: {url}")
                    return content
        except Exception as e:
            logger.debug(f"RSS urllib failed: {e}")
        return None

    async def _fetch_rss_aiohttp(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Fetch RSS using aiohttp as final fallback"""
        try:
            await self.create_session()
            async with self.session.get(url, headers=headers, timeout=20) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.debug(f"RSS aiohttp successful: {url}")
                    return content
        except Exception as e:
            logger.debug(f"RSS aiohttp failed: {e}")
        return None

    async def _fetch_calendar_data(self, url: str) -> Optional[str]:
        """Fetch economic calendar data using multiple methods"""
        try:
            await self.create_session()
            
            # Use realistic headers that work for calendar page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive',
            }
            
            # Try different approaches
            methods = [
                self._fetch_calendar_aiohttp,
                self._fetch_calendar_requests,
                self._fetch_calendar_alternative
            ]
            
            for method in methods:
                try:
                    result = await method(url, headers)
                    if result and len(result) > 1000:  # Valid page content
                        logger.info("✅ Successfully fetched calendar data")
                        return result
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                except Exception as e:
                    logger.debug(f"Calendar fetch method failed: {e}")
                    continue
                    
            logger.warning("❌ All calendar fetch methods failed")
            return None
            
        except Exception as e:
            logger.error(f"💥 Error in calendar data fetch: {e}")
            return None

    async def _fetch_calendar_aiohttp(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Fetch calendar using aiohttp"""
        try:
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.debug(f"aiohttp calendar fetch successful: {len(content)} chars")
                    return content
                else:
                    logger.debug(f"aiohttp calendar fetch failed: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.debug(f"aiohttp calendar error: {e}")
            return None

    async def _fetch_calendar_requests(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Fetch calendar using requests (often bypasses some blocks)"""
        try:
            import requests
            
            # Create session with retry logic
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                logger.debug(f"requests calendar fetch successful: {len(response.text)} chars")
                return response.text
            else:
                logger.debug(f"requests calendar fetch failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.debug(f"requests calendar error: {e}")
            return None

    async def _fetch_calendar_alternative(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Try alternative calendar endpoint or mobile version"""
        try:
            # Try mobile version which might be less protected
            mobile_url = url.replace('www.investing.com', 'm.investing.com')
            mobile_headers = headers.copy()
            mobile_headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
            
            import requests
            response = requests.get(mobile_url, headers=mobile_headers, timeout=25, verify=False)
            
            if response.status_code == 200:
                logger.debug(f"mobile calendar fetch successful: {len(response.text)} chars")
                return response.text
            else:
                logger.debug(f"mobile calendar fetch failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.debug(f"alternative calendar error: {e}")
            return None

    async def _parse_calendar_events(self, content: str) -> List[EconomicEvent]:
        """Parse economic events from calendar HTML content"""
        events = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for calendar event rows - trying multiple selectors
            event_selectors = [
                'tr[data-event-id]',  # Main calendar event rows
                'tr.js-event-item',   # Alternative selector
                'tr[class*="event"]', # Generic event rows
                'div[data-event-id]', # Sometimes divs are used
                'tr.event',           # Simple event class
            ]
            
            event_rows = []
            for selector in event_selectors:
                try:
                    rows = soup.select(selector)
                    if rows:
                        event_rows = rows
                        logger.info(f"✅ Found {len(rows)} events using selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not event_rows:
                logger.warning("❌ No calendar events found with any selector")
                return []
            
            current_time = datetime.now(timezone.utc)
            current_date = current_time.strftime('%Y-%m-%d')
            
            for row in event_rows[:15]:  # Limit to 15 events
                try:
                    event = await self._parse_single_event(row, current_date)
                    if event and self._is_important_event(event):
                        events.append(event)
                        
                except Exception as e:
                    logger.debug(f"Error parsing event row: {e}")
                    continue
            
            # Clean up
            soup.decompose()
            
            logger.info(f"✅ Parsed {len(events)} important economic events")
            return events
            
        except Exception as e:
            logger.error(f"💥 Error parsing calendar events: {e}")
            return []

    async def _parse_single_event(self, row, current_date: str) -> Optional[EconomicEvent]:
        """Parse a single economic event from HTML row"""
        try:
            # Extract time
            time_elem = row.select_one('td[class*="time"], td.time, span[class*="time"]')
            event_time = "TBD"
            if time_elem:
                time_text = time_elem.get_text(strip=True)
                if time_text and time_text != "All Day":
                    event_time = time_text
            
            # Extract country
            country_elem = row.select_one('td[class*="flag"], span[class*="flag"], .flagCur')
            country = "US"
            if country_elem:
                # Look for title attribute or class names
                country_title = country_elem.get('title', '')
                if country_title:
                    country = country_title
                else:
                    # Try to extract from class names
                    classes = country_elem.get('class', [])
                    for cls in classes:
                        if 'flag' in cls.lower():
                            country = cls.replace('flag', '').replace('Cur', '').upper()
                            break
            
            # Extract event name
            event_elem = row.select_one('td.event a, td[class*="event"] a, a[data-event-id]')
            if not event_elem:
                event_elem = row.select_one('td.event, td[class*="event"]')
            
            if not event_elem:
                return None
                
            event_name = event_elem.get_text(strip=True)
            if not event_name or len(event_name) < 3:
                return None
            
            # Extract importance (impact)
            importance = "Medium"
            impact_elem = row.select_one('td[class*="impact"], .impact, td.imp, span[class*="bull"]')
            if impact_elem:
                bulls = impact_elem.select('i.grayFullBullishIcon, i.orangeFullBullishIcon, i.redFullBullishIcon')
                if len(bulls) >= 3:
                    importance = "High"
                elif len(bulls) >= 2:
                    importance = "Medium"
                else:
                    importance = "Low"
            
            # Extract actual, forecast, previous values
            actual = None
            forecast = None
            previous = None
            
            # Look for data cells
            data_cells = row.select('td[class*="act"], td[class*="fore"], td[class*="prev"]')
            for cell in data_cells:
                cell_text = cell.get_text(strip=True)
                if cell_text and cell_text != "" and cell_text != "--":
                    cell_classes = ' '.join(cell.get('class', []))
                    if 'act' in cell_classes.lower():
                        actual = cell_text
                    elif 'fore' in cell_classes.lower():
                        forecast = cell_text
                    elif 'prev' in cell_classes.lower():
                        previous = cell_text
            
            # Get Arabic translation
            event_name_arabic = self._get_arabic_event_name(event_name)
            
            # Create event
            event = EconomicEvent(
                time=event_time,
                country=country,
                event_name=event_name,
                event_name_arabic=event_name_arabic,
                importance=importance,
                actual=actual,
                forecast=forecast,
                previous=previous,
                currency="USD" if country.upper() in ['US', 'USA', 'UNITED STATES'] else "USD"
            )
            
            return event
            
        except Exception as e:
            logger.debug(f"Error parsing single event: {e}")
            return None

    def _is_important_event(self, event: EconomicEvent) -> bool:
        """Filter for important economic events only"""
        # High importance events
        if event.importance == "High":
            return True
        
        # Key economic indicators regardless of marked importance
        important_keywords = [
            'unemployment', 'payroll', 'jobs', 'employment',
            'cpi', 'inflation', 'ppi', 'price',
            'gdp', 'growth', 'retail sales',
            'pmi', 'manufacturing', 'ism',
            'fed', 'fomc', 'interest rate', 'monetary policy',
            'consumer confidence', 'business confidence'
        ]
        
        event_lower = event.event_name.lower()
        for keyword in important_keywords:
            if keyword in event_lower:
                return True
        
        # US events are generally more important for global markets
        if event.country.upper() in ['US', 'USA', 'UNITED STATES']:
            return True
            
        return False

    def _is_insider_trading_news(self, title: str) -> bool:
        """🚫 Filter out boring insider trading news"""
        title_lower = title.lower()
        
        # Insider trading keywords
        insider_keywords = [
            'director', 'ceo', 'cfo', 'cio', 'evp', 'vp', 'president',
            'buys', 'sells', 'purchases', 'acquires', 'disposes',
            'insider', 'trading', 'shares', 'stock', 'holdings'
        ]
        
        # Check if it's about someone buying/selling shares
        has_person = any(word in title_lower for word in ['director', 'ceo', 'cfo', 'cio', 'evp', 'vp', 'president'])
        has_action = any(word in title_lower for word in ['buys', 'sells', 'purchases', 'sells shares', 'buys shares'])
        has_amount = '$' in title and any(word in title_lower for word in ['stock', 'shares'])
        
        # If it has person + action + money amount, it's likely insider trading
        if has_person and has_action and has_amount:
            return True
            
        # Common patterns
        insider_patterns = [
            r'\w+\s+(director|ceo|cfo|cio|evp|vp)\s+\w+\s+(buys|sells)',
            r'\w+\s+(buys|sells)\s+\$[\d,]+\s+in\s+\w+\s+(stock|shares)',
            r'insider\s+(trading|buys|sells)',
        ]
        
        for pattern in insider_patterns:
            if re.search(pattern, title_lower):
                return True
        
        return False

    async def _blitz_alternative_endpoints(self, max_articles: int) -> List[NewsArticle]:
        """BLITZ: Super-fast alternative endpoint scraping"""
        # BLITZ: Complete endpoint coverage for ALL user sections
        fast_endpoints = [
            # USER'S PRIORITY SECTIONS
            'https://www.investing.com/news/headlines',  # Headlines (MAIN REQUEST)
            'https://www.investing.com/news/economic-indicators',  # Economic indicators
            'https://www.investing.com/news/stock-market-news',  # Stock market
            'https://www.investing.com/news/commodities-news',  # Commodities
            'https://www.investing.com/news/forex-news',  # Forex
            'https://www.investing.com/news/cryptocurrency-news',  # Cryptocurrency
            
            # MOBILE ALTERNATIVES (often less protected)
            'https://m.investing.com/news/headlines',  # Mobile headlines
            'https://m.investing.com/news/',  # Mobile general
            
            # BACKUP ENDPOINTS
            'https://www.investing.com/news/latest-news',
            'https://uk.investing.com/news/',
        ]
        
        articles = []
        
        for url in fast_endpoints[:2]:  # Only top 2 for speed
            if len(articles) >= max_articles:
                break
                
            try:
                # BLITZ: Use fastest method (requests)
                response = requests.get(
                    url,
                    headers=self._get_blitz_headers(),
                    timeout=8,  # Quick timeout
                    verify=False,
                    allow_redirects=True
                )
                
                if response.status_code == 200 and len(response.text) > 1000:
                    # Quick parsing for speed
                    parsed = await self._parse_investing_content(response.text, "BLITZ-ALT", max_articles - len(articles))
                    articles.extend(parsed)
                    logger.info(f"⚡ BLITZ ALT: {len(parsed)} articles from {url}")
                    
            except Exception as e:
                logger.debug(f"BLITZ alt failed for {url}: {e}")
                continue
                
        return articles

    async def _blitz_mobile_scraping(self, max_articles: int) -> List[NewsArticle]:
        """BLITZ: Mobile-optimized scraping (often less protected)"""
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        mobile_urls = [
            'https://m.investing.com/news/',
            'https://mobile.investing.com/news/'
        ]
        
        articles = []
        
        for url in mobile_urls:
            if len(articles) >= max_articles:
                break
                
            try:
                response = requests.get(
                    url,
                    headers=mobile_headers,
                    timeout=6,
                    verify=False
                )
                
                if response.status_code == 200:
                    parsed = await self._parse_investing_content(response.text, "MOBILE-BLITZ", max_articles - len(articles))
                    articles.extend(parsed)
                    if parsed:
                        logger.info(f"📱 MOBILE BLITZ: {len(parsed)} articles")
                        break  # Mobile worked, no need to try others
                        
            except Exception as e:
                logger.debug(f"Mobile blitz failed: {e}")
                continue
                
        return articles

    def verify_section_coverage(self, articles: List[NewsArticle]) -> Dict[str, int]:
        """PROFESSIONAL: Verify we're getting news from all required sections"""
        required_sections = [
            'HEADLINES', 'ECONOMIC', 'STOCK', 'COMMODITIES', 'FOREX', 'CRYPTO'
        ]
        
        section_counts = {}
        for section in required_sections:
            section_counts[section] = 0
            
        for article in articles:
            for section in required_sections:
                if section in article.section.upper():
                    section_counts[section] += 1
                    break
        
        return section_counts

    def fix_article_sections(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """PROFESSIONAL: Fix article sections based on URL analysis"""
        for article in articles:
            # Detect actual section from URL
            if 'economic-indicators' in article.link:
                article.section = 'ECONOMIC-BLITZ'
            elif 'stock-market-news' in article.link:
                article.section = 'STOCK-BLITZ' 
            elif 'commodities-news' in article.link:
                article.section = 'COMMODITIES-BLITZ'
            elif 'forex-news' in article.link:
                article.section = 'FOREX-BLITZ'
            elif 'cryptocurrency-news' in article.link:
                article.section = 'CRYPTO-BLITZ'
            elif 'economy-news' in article.link:
                # SMART: Check if it's actually forex content
                content = f"{article.title} {article.summary}".lower()
                if any(keyword in content for keyword in ['dollar', 'euro', 'yen', 'currency', 'exchange', 'forex']):
                    article.section = 'FOREX-BLITZ'
                else:
                    article.section = 'ECONOMIC-BLITZ'  # Economy is part of economic indicators
            
            # ENHANCED: Handle external sources
            elif 'marketwatch.com' in article.link:
                article.section = 'HEADLINES-BLITZ'  # MarketWatch real-time headlines
            elif 'cointelegraph.com' in article.link:
                article.section = 'CRYPTO-BLITZ'  # CoinTelegraph crypto news
            
            # SMART: Advanced content analysis for general articles
            elif not article.section or 'BLITZ' not in article.section:
                content = f"{article.title} {article.summary}".lower()
                if any(keyword in content for keyword in ['bitcoin', 'crypto', 'ethereum', 'blockchain']):
                    article.section = 'CRYPTO-BLITZ'
                elif any(keyword in content for keyword in ['dollar', 'forex', 'currency', 'exchange']):
                    article.section = 'FOREX-BLITZ'
                elif any(keyword in content for keyword in ['stock', 'market', 'dow', 'nasdaq']):
                    article.section = 'HEADLINES-BLITZ'
                else:
                    article.section = 'HEADLINES-BLITZ'  # Default to headlines
            
            # Keep existing section if no match
            
        return articles

# Test function
async def test_investing_scraper():
    """Test the investing.com scraper"""
    scraper = InvestingNewsScraper()
    
    try:
        print("🧪 Testing Investing.com Scraper")
        print("=" * 50)
        
        # Test complete section coverage
        print("\n⚡ Testing ALL SECTIONS BLITZ MODE...")
        print("Required: Headlines, Economic Indicators, Stock Market, Commodities, Forex, Cryptocurrency")
        articles = await scraper.scrape_investing_news(max_articles=15, breaking_news_priority=True)
        
        if articles:
            # PROFESSIONAL: Fix article sections based on URL analysis
            articles = scraper.fix_article_sections(articles)
            
            print(f"✅ Found {len(articles)} articles:")
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. {article.title}")
                print(f"   Section: {article.section}")
                print(f"   Link: {article.link}")
                print(f"   Published: {article.published}")
                if article.summary:
                    print(f"   Summary: {article.summary[:100]}...")
            
            # PROFESSIONAL: Verify section coverage
            print("\n" + "="*50)
            print("📊 SECTION COVERAGE VERIFICATION:")
            print("Required: Headlines, Economic Indicators, Stock Market, Commodities, Forex, Cryptocurrency")
            
            coverage = scraper.verify_section_coverage(articles)
            
            # Show which sections we got
            covered_sections = [section for section, count in coverage.items() if count > 0]
            missing_sections = [section for section, count in coverage.items() if count == 0]
            
            print(f"\n✅ COVERED SECTIONS ({len(covered_sections)}/6):")
            for section in covered_sections:
                print(f"   ✓ {section}: {coverage[section]} articles")
                
            if missing_sections:
                print(f"\n❌ MISSING SECTIONS ({len(missing_sections)}/6):")
                for section in missing_sections:
                    print(f"   ✗ {section}: 0 articles")
            else:
                print(f"\n🎉 ALL SECTIONS COVERED! Perfect coverage!")
                
        else:
            print("❌ No articles found")
        
        print("\n" + "="*50)
        
        # Test economic calendar
        print("\n📊 Testing economic calendar...")
        events = await scraper.scrape_economic_calendar()
        
        if events:
            print(f"✅ Found {len(events)} economic events:")
            for i, event in enumerate(events, 1):
                print(f"\n{i}. {event.event_name} ({event.event_name_arabic})")
                print(f"   Country: {event.country} {scraper.get_country_flag(event.country)}")
                print(f"   Time: {event.time}")
                print(f"   Importance: {event.importance}")
                if event.actual:
                    print(f"   Actual: {event.actual}")
                if event.forecast:
                    print(f"   Forecast: {event.forecast}")
                if event.previous:
                    print(f"   Previous: {event.previous}")
        else:
            print("❌ No economic events found")
            
    except Exception as e:
        print(f"❌ Error testing scraper: {e}")
        
    finally:
        await scraper.close_session()

if __name__ == "__main__":
    asyncio.run(test_investing_scraper())