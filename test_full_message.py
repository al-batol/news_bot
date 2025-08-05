#!/usr/bin/env python3
"""Test script to verify description extraction and message formatting"""

import asyncio
import sys
sys.path.append('.')

from investing_scraper import InvestingNewsScraper

async def test_description_extraction():
    scraper = InvestingNewsScraper()
    
    print("🧪 Testing CoinDesk RSS parsing with descriptions...")
    articles = await scraper.scrape_coindesk_news(max_articles=3)
    
    if articles:
        print(f"✅ Found {len(articles)} articles")
        for i, article in enumerate(articles, 1):
            print(f"\n📰 Article {i}:")
            print(f"Title: {article.title}")
            print(f"Summary: {article.summary[:200] if article.summary else 'NO SUMMARY'}...")
            print(f"Image: {'Yes' if article.image_url else 'No'}")
            print(f"Link: {article.link}")
            print("-" * 80)
    else:
        print("❌ No articles found")
    
    await scraper.close_session()

if __name__ == "__main__":
    asyncio.run(test_description_extraction())