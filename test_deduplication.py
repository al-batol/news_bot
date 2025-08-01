#!/usr/bin/env python3
"""
Test the enhanced deduplication logic with the duplicate news examples
"""
import asyncio
import sys
from investing_scraper import InvestingNewsScraper, NewsArticle

async def test_deduplication():
    """Test deduplication with real duplicate examples"""
    print("🧪 Testing Enhanced Deduplication Logic")
    print("=" * 60)
    
    scraper = InvestingNewsScraper()
    
    # Create test articles based on the duplicates you found
    test_articles = [
        NewsArticle(
            title="Eagle Point sells ACRES commercial realty (ACR) stock for $328,417",
            link="https://www.investing.com/news/insider-trading-news/eagle-point-sells-acres-commercial-realty-corp-acr-stock-for-328417-93CH-4166793",
            published="2025-08-01 22:44",
            summary="Eagle Point transaction details...",
            section="HEADLINES-BLITZ",
            article_id="ca59f9f76729"
        ),
        NewsArticle(
            title="Eagle Point sells acres Commercial Realty Corp (ACR) stock for $328,417",
            link="https://www.investing.com/news/insider-trading-news/eagle-point-sells-acres-commercial-realty-corp-acr-stock-for-328417-93CH-4166792",
            published="2025-08-01 22:44",
            summary="Eagle Point transaction details...",
            section="HEADLINES-BLITZ", 
            article_id="dd95e95130"
        ),
        NewsArticle(
            title="Apple reports Q3 earnings beat expectations",
            link="https://www.investing.com/news/earnings/apple-q3-earnings-beat",
            published="2025-08-01 22:45",
            summary="Apple earnings...",
            section="HEADLINES-BLITZ",
            article_id="unique1"
        ),
        NewsArticle(
            title="Microsoft director buys $50,000 in shares",
            link="https://www.investing.com/news/insider-trading/microsoft-director-buys-shares",
            published="2025-08-01 22:46", 
            summary="Microsoft insider trading...",
            section="HEADLINES-BLITZ",
            article_id="unique2"
        )
    ]
    
    print(f"📥 INPUT: {len(test_articles)} articles")
    print("Articles:")
    for i, article in enumerate(test_articles, 1):
        print(f"  {i}. {article.title}")
    
    print("\n" + "=" * 60)
    print("🧹 RUNNING DEDUPLICATION...")
    
    # Test the enhanced deduplication
    unique_articles = scraper._stealth_deduplicate(test_articles)
    
    print(f"📤 OUTPUT: {len(unique_articles)} unique articles")
    print("Unique articles:")
    for i, article in enumerate(unique_articles, 1):
        print(f"  {i}. {article.title}")
    
    print("\n" + "=" * 60)
    
    # Check if it caught the duplicates
    titles = [article.title for article in unique_articles]
    eagle_point_count = sum(1 for title in titles if "eagle point" in title.lower())
    
    if eagle_point_count == 1:
        print("✅ SUCCESS: Duplicate Eagle Point articles were merged!")
        print("✅ DEDUPLICATION WORKING CORRECTLY")
    else:
        print("❌ FAILED: Duplicate Eagle Point articles were not caught")
        print(f"❌ Found {eagle_point_count} Eagle Point articles (should be 1)")
    
    if len(unique_articles) == 3:  # Should be 3 unique articles total
        print("✅ SUCCESS: Correct number of unique articles")
    else:
        print(f"❌ FAILED: Expected 3 unique articles, got {len(unique_articles)}")
    
    await scraper.close_session()

if __name__ == "__main__":
    asyncio.run(test_deduplication())