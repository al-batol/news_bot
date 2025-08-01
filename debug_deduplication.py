#!/usr/bin/env python3
"""
Debug deduplication to see why Microsoft article is being removed
"""
import asyncio
import re
from investing_scraper import InvestingNewsScraper, NewsArticle

async def debug_deduplication():
    """Debug deduplication with detailed logging"""
    print("🔍 Debugging Deduplication Logic")
    print("=" * 60)
    
    scraper = InvestingNewsScraper()
    
    # Create test articles 
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
        ),
        NewsArticle(
            title="Eagle Point sells acres Commercial Realty Corp (ACR) stock for $328,417",
            link="https://www.investing.com/news/insider-trading-news/eagle-point-sells-acres-commercial-realty-corp-acr-stock-for-328417-93CH-4166792",
            published="2025-08-01 22:44",
            summary="Eagle Point transaction details...",
            section="HEADLINES-BLITZ", 
            article_id="dd95e95130"
        ),
    ]
    
    print("📥 Testing each article pair for similarity...")
    
    # Test each pair manually
    for i, article1 in enumerate(test_articles):
        for j, article2 in enumerate(test_articles[i+1:], i+1):
            print(f"\n🔍 Comparing Article {i+1} vs Article {j+1}:")
            print(f"  A{i+1}: {article1.title}")
            print(f"  A{j+1}: {article2.title}")
            
            # Test word similarity
            title1_norm = re.sub(r'[^\w\s]', '', article1.title.lower()).strip()
            title2_norm = re.sub(r'[^\w\s]', '', article2.title.lower()).strip()
            words1 = set(title1_norm.split())
            words2 = set(title2_norm.split())
            
            if len(words1) > 0 and len(words2) > 0:
                intersection = len(words1 & words2)
                union = len(words1 | words2)
                word_sim = intersection / union
                print(f"    📊 Word similarity: {word_sim:.3f} ({'DUPLICATE' if word_sim > 0.75 else 'UNIQUE'})")
            
            # Test financial signature
            amount1 = re.search(r'\$[\d,]+', article1.title)
            amount2 = re.search(r'\$[\d,]+', article2.title)
            company1 = re.search(r'([A-Z]{2,5})\s+', article1.title)
            company2 = re.search(r'([A-Z]{2,5})\s+', article2.title)
            
            sig1 = ""
            if amount1: sig1 += amount1.group(0)
            if company1: sig1 += company1.group(1)
            
            sig2 = ""
            if amount2: sig2 += amount2.group(0)
            if company2: sig2 += company2.group(1)
            
            if sig1 and sig2 and len(sig1) > 3 and len(sig2) > 3:
                print(f"    💰 Financial signatures: '{sig1}' vs '{sig2}' ({'DUPLICATE' if sig1 == sig2 else 'UNIQUE'})")
            
            # Test URL similarity
            if hasattr(article1, 'link') and hasattr(article2, 'link'):
                clean_url1 = re.sub(r'-\d+$', '', article1.link.split('/')[-1])
                clean_url2 = re.sub(r'-\d+$', '', article2.link.split('/')[-1])
                print(f"    🔗 URL similarity: '{clean_url1}' vs '{clean_url2}' ({'DUPLICATE' if clean_url1 == clean_url2 and len(clean_url1) > 10 else 'UNIQUE'})")
            
            # Test character similarity
            if len(title1_norm) > 20 and len(title2_norm) > 20:
                if abs(len(title1_norm) - len(title2_norm)) < 5:
                    shorter = min(len(title1_norm), len(title2_norm))
                    longer = max(len(title1_norm), len(title2_norm))
                    char_sim = shorter / longer if longer > 0 else 0
                    print(f"    📝 Character similarity: {char_sim:.3f} ({'DUPLICATE' if char_sim > 0.85 else 'UNIQUE'})")
    
    await scraper.close_session()

if __name__ == "__main__":
    asyncio.run(debug_deduplication())