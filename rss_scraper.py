"""
RSS-based news scraper for financial news
Much more reliable than HTML scraping as RSS feeds are designed for machine consumption
"""
import feedparser
import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
import hashlib
from dataclasses import dataclass
try:
    from config_free import Config
except ImportError:
    from config import Config

logger = logging.getLogger(__name__)

@dataclass
class RSSNewsArticle:
    """Represents a single news article from RSS feed"""
    title: str
    link: str
    published: str
    summary: str
    source: str
    article_id: str
    
    def __post_init__(self):
        # Generate unique ID based on title and link
        content = f"{self.title}_{self.link}"
        self.article_id = hashlib.md5(content.encode()).hexdigest()[:12]

class RSSNewsScraper:
    """RSS-based news scraper for multiple financial news sources"""
    
    def __init__(self):
        self.sources = Config.NEWS_SOURCES
        self.backup_sources = getattr(Config, 'BACKUP_SOURCES', {})
        self.session = None
        self.seen_articles = set()
        
    async def create_session(self):
        """Create aiohttp session for RSS requests"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def fetch_rss_feed(self, url: str, source_name: str) -> List[RSSNewsArticle]:
        """Fetch and parse RSS feed from a given URL with improved error handling"""
        try:
            await self.create_session()
            
            # Add proper headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
            
            logger.info(f"Fetching RSS feed from {source_name}: {url}")
            
            async with self.session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    content = await response.text()
                    articles = self._parse_rss_content(content, source_name)
                    logger.info(f"✅ {source_name}: Successfully fetched {len(articles)} articles")
                    return articles
                elif response.status == 404:
                    logger.warning(f"❌ {source_name}: Feed not found (404) - URL may be outdated")
                    return []
                elif response.status == 403:
                    logger.warning(f"❌ {source_name}: Access forbidden (403) - may need different headers or be blocked")
                    return []
                elif response.status == 429:
                    logger.warning(f"⏳ {source_name}: Rate limited (429) - too many requests")
                    return []
                else:
                    logger.warning(f"❌ {source_name}: HTTP {response.status} - {response.reason}")
                    return []
                    
        except asyncio.TimeoutError:
            logger.error(f"⏰ {source_name}: Request timeout - feed may be slow or unreachable")
            return []
        except aiohttp.ClientError as e:
            logger.error(f"🌐 {source_name}: Network error - {e}")
            return []
        except Exception as e:
            logger.error(f"💥 {source_name}: Unexpected error - {e}")
            return []
    
    def _parse_rss_content(self, content: str, source_name: str) -> List[RSSNewsArticle]:
        """Parse RSS content and extract articles"""
        try:
            feed = feedparser.parse(content)
            articles = []
            
            if feed.bozo:
                logger.warning(f"RSS feed from {source_name} has parsing issues")
            
            logger.info(f"Found {len(feed.entries)} entries in {source_name} feed")
            
            for entry in feed.entries:
                try:
                    # Extract article data
                    title = getattr(entry, 'title', 'No title')
                    link = getattr(entry, 'link', '')
                    summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
                    
                    # Handle published date
                    published = 'Unknown'
                    if hasattr(entry, 'published'):
                        published = entry.published
                    elif hasattr(entry, 'updated'):
                        published = entry.updated
                    elif hasattr(entry, 'pubDate'):
                        published = entry.pubDate
                    
                    # Clean up summary (remove HTML tags)
                    if summary:
                        import re
                        summary = re.sub(r'<[^>]+>', '', summary)
                        summary = summary.strip()
                    
                    # Create article object
                    article = RSSNewsArticle(
                        title=title.strip(),
                        link=link,
                        published=published,
                        summary=summary[:200] + "..." if len(summary) > 200 else summary,
                        source=source_name,
                        article_id=""  # Will be generated in __post_init__
                    )
                    
                    # Check for duplicates
                    if article.article_id not in self.seen_articles:
                        articles.append(article)
                        self.seen_articles.add(article.article_id)
                    
                except Exception as e:
                    logger.debug(f"Error parsing RSS entry: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(articles)} new articles from {source_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing RSS content from {source_name}: {e}")
            return []
    
    async def get_latest_news(self, max_articles: int = None) -> List[RSSNewsArticle]:
        """Get latest news from all configured sources"""
        max_articles = max_articles or Config.MAX_ARTICLES_PER_SCRAPE
        all_articles = []
        
        try:
            # Fetch from all sources concurrently
            tasks = []
            for source_name, url in self.sources.items():
                tasks.append(self.fetch_rss_feed(url, source_name))
            
            # Wait for all feeds to be fetched
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and track success/failure
            successful_sources = []
            failed_sources = []
            no_new_articles_sources = []
            
            for i, result in enumerate(results):
                source_name = list(self.sources.keys())[i]
                if isinstance(result, Exception):
                    logger.error(f"❌ {source_name}: Exception - {result}")
                    failed_sources.append(source_name)
                elif result:  # Got new articles
                    all_articles.extend(result)
                    successful_sources.append(f"{source_name}({len(result)})")
                else:  # No new articles (not a failure)
                    no_new_articles_sources.append(source_name)
            
            # Log summary of feed status
            if successful_sources:
                logger.info(f"✅ Sources with new articles: {', '.join(successful_sources)}")
            if no_new_articles_sources:
                logger.info(f"📰 Sources with no new articles: {', '.join(no_new_articles_sources)}")
            if failed_sources:
                logger.warning(f"❌ Actually failed sources: {', '.join(failed_sources)}")
            
            # If no new articles and we have backup sources, try them
            if not all_articles and self.backup_sources:
                logger.info("No new articles from main sources, trying backup sources...")
                
                backup_tasks = []
                for source_name, url in self.backup_sources.items():
                    backup_tasks.append(self.fetch_rss_feed(url, f"backup_{source_name}"))
                
                backup_results = await asyncio.gather(*backup_tasks, return_exceptions=True)
                
                backup_successful = []
                for i, result in enumerate(backup_results):
                    source_name = f"backup_{list(self.backup_sources.keys())[i]}"
                    if isinstance(result, Exception):
                        logger.error(f"❌ {source_name}: Exception - {result}")
                    elif result:
                        all_articles.extend(result)
                        backup_successful.append(f"{source_name}({len(result)})")
                
                if backup_successful:
                    logger.info(f"✅ Backup sources with articles: {', '.join(backup_successful)}")
            
            # Sort by source priority and limit results
            # Prioritize certain sources (updated list with working feeds)
            priority_sources = [
                'investing_economic',    # Economic data (highest priority)
                'investing_rss',        # General investing news
                'marketwatch',          # Real-time headlines
                'coindesk',             # Crypto news
                'cointelegraph',        # Crypto news
                'investing_crypto',     # Crypto news
                'investing_forex',      # Forex news
                'yahoo_finance_crypto', # Yahoo Finance
                'backup_benzinga_crypto', # Backup sources
                'backup_decrypt',
                'backup_the_block',
                'backup_crypto_news'
            ]
            
            def get_source_priority(article):
                try:
                    return priority_sources.index(article.source)
                except ValueError:
                    return 999
            
            all_articles.sort(key=get_source_priority)
            
            # Limit results
            limited_articles = all_articles[:max_articles]
            
            total_sources = len(self.sources) + (len(self.backup_sources) if len(all_articles) > len([a for a in all_articles if not a.source.startswith('backup_')]) else 0)
            logger.info(f"Retrieved {len(limited_articles)} articles from {total_sources} sources")
            return limited_articles
            
        except Exception as e:
            logger.error(f"Error getting latest news: {e}")
            return []
    
    def reset_seen_articles(self):
        """Reset the seen articles cache"""
        self.seen_articles.clear()
        logger.info("Reset seen articles cache")
    
    def should_reset_cache(self):
        """Check if we should reset the cache (if it gets too large)"""
        return len(self.seen_articles) > 500  # Reset when cache gets large
    
    def periodic_cache_cleanup(self):
        """Clean up old articles from cache to prevent it from growing indefinitely"""
        if self.should_reset_cache():
            # Keep only the most recent 200 articles
            if len(self.seen_articles) > 200:
                articles_list = list(self.seen_articles)
                self.seen_articles = set(articles_list[-200:])
                logger.info(f"Cleaned up seen articles cache, kept last 200 articles")

# Test function
async def test_rss_scraper():
    """Test the RSS scraper functionality"""
    scraper = RSSNewsScraper()
    
    try:
        print("Testing RSS scraper...")
        print(f"Configured sources: {list(scraper.sources.keys())}")
        
        articles = await scraper.get_latest_news(5)
        
        if articles:
            print(f"\n✅ Successfully retrieved {len(articles)} articles:")
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. {article.title}")
                print(f"   Source: {article.source}")
                print(f"   Link: {article.link}")
                print(f"   Published: {article.published}")
                if article.summary:
                    print(f"   Summary: {article.summary[:100]}...")
        else:
            print("❌ No articles retrieved")
            
    except Exception as e:
        print(f"❌ Error testing RSS scraper: {e}")
        
    finally:
        await scraper.close_session()

if __name__ == "__main__":
    asyncio.run(test_rss_scraper()) 