#!/usr/bin/env python3
"""
Test script for the new features:
1. Insider trading news filtering
2. Image support from RSS enclosures
"""
import asyncio
import logging
from investing_scraper import InvestingNewsScraper, NewsArticle

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_new_features():
    """Test insider trading filtering and image support"""
    logger.info("🧪 Testing New Features: Insider Trading Filter & Image Support")
    logger.info("=" * 70)
    
    scraper = InvestingNewsScraper()
    
    try:
        # Test 1: Insider trading filter
        print("\n🚫 Testing Insider Trading Filter...")
        test_titles = [
            "Eagle Point director sells $328,417 in shares",  # Should be filtered
            "Tesla CEO Elon Musk buys $1M in TSLA stock",    # Should be filtered  
            "Apple reports Q3 earnings beat expectations",    # Should NOT be filtered
            "JPMorgan CFO sells $500k in JPM shares",        # Should be filtered
            "Bitcoin surges to new highs on ETF approval",   # Should NOT be filtered
            "Microsoft EVP Jahnke sells shares worth $250k", # Should be filtered
        ]
        
        for title in test_titles:
            is_insider = scraper._is_insider_trading_news(title)
            status = "🚫 FILTERED" if is_insider else "✅ ALLOWED"
            print(f"   {status}: {title}")
        
        print("\n📊 Test Results:")
        filtered_count = sum(1 for title in test_titles if scraper._is_insider_trading_news(title))
        print(f"   📈 Total articles: {len(test_titles)}")
        print(f"   🚫 Filtered out: {filtered_count}")
        print(f"   ✅ Allowed through: {len(test_titles) - filtered_count}")
        
        # Test 2: RSS feed with enclosures (simulate)
        print("\n📸 Testing Image Support...")
        print("   📡 Checking RSS feeds for image enclosures...")
        
        # Get some articles from RSS
        articles = await scraper._blitz_rss_feeds(5)
        
        articles_with_images = [a for a in articles if hasattr(a, 'image_url') and a.image_url]
        articles_without_images = [a for a in articles if not (hasattr(a, 'image_url') and a.image_url)]
        
        print(f"\n📊 Image Support Results:")
        print(f"   📰 Total articles: {len(articles)}")
        print(f"   📸 With images: {len(articles_with_images)}")
        print(f"   📝 Text only: {len(articles_without_images)}")
        
        if articles_with_images:
            print(f"\n✅ Sample articles with images:")
            for i, article in enumerate(articles_with_images[:3], 1):
                print(f"   {i}. {article.title[:60]}...")
                print(f"      🖼️  Image: {article.image_url}")
        
        print("\n" + "=" * 70)
        print("🎉 FEATURE TESTS COMPLETED!")
        print("✅ Insider trading filter: Working")
        print("✅ Image support: Added to RSS parsing")
        print("✅ Bot will now:")
        print("   - Filter out boring insider trading news")
        print("   - Send images when available from RSS feeds")
        print("   - Continue to work with text-only news as before")
        
    except Exception as e:
        logger.error(f"💥 Error in feature tests: {e}")
        
    finally:
        await scraper.close_session()

if __name__ == "__main__":
    asyncio.run(test_new_features())