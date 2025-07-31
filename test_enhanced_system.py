#!/usr/bin/env python3
"""
Test Enhanced Arabic Financial News System
Demonstrates the new Groq AI translation and TradingView-style formatting
"""
import asyncio
import logging
from crypto_arabic_formatter import CryptoArabicFormatter
from ai_translator import AITranslator
from config_free import Config
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockArticle:
    """Mock article for testing"""
    def __init__(self, title, summary="", link=""):
        self.title = title
        self.summary = summary
        self.link = link
        self.article_id = "test_123"

async def test_enhanced_system():
    """Test the enhanced system with economic data examples"""
    
    print("🧪 Testing Enhanced Arabic Financial News System")
    print("=" * 60)
    
    # Initialize components
    formatter = CryptoArabicFormatter()
    ai_translator = AITranslator(Config.GROQ_API_KEY)
    
    # Test cases that match the user's desired format
    test_cases = [
        {
            'title': "US Non-Farm Payrolls: 7.437M vs 7.5M expected, Previous 7.769M",
            'summary': "US employment data came in below expectations with 7.437M jobs added compared to forecast of 7.5M. Previous month was 7.769M.",
            'expected_format': "Economic data with Previous/Forecast/Actual format"
        },
        {
            'title': "Chicago PMI: 47.1 vs 41.9 expected, Previous 40.4", 
            'summary': "Chicago Purchasing Managers Index rose to 47.1, beating expectations of 41.9. Previous reading was 40.4.",
            'expected_format': "PMI data with USD impact analysis"
        },
        {
            'title': "US Unemployment Claims: 218K vs 222K expected, Previous 217K",
            'summary': "Weekly unemployment claims fell to 218K, better than 222K forecast. Previous week was 217K claims.",
            'expected_format': "Weekly claims data with USD impact"
        },
        {
            'title': "ISM Manufacturing PMI falls to 47.8 vs 48.0 expected",
            'summary': "US manufacturing activity contracted more than expected in latest PMI reading.",
            'expected_format': "Manufacturing data"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test Case {i}: {test_case['expected_format']}")
        print("-" * 40)
        print(f"Original Title: {test_case['title']}")
        
        try:
            # Create mock article
            article = MockArticle(test_case['title'], test_case['summary'])
            
            # Test economic data extraction
            economic_data = formatter.extract_economic_data(article.title, article.summary)
            print(f"\n🔍 Economic Data Detected: {economic_data is not None}")
            
            if economic_data:
                print(f"   - Indicator: {economic_data.get('indicator')}")
                print(f"   - Arabic Name: {economic_data.get('arabic_name')}")
                print(f"   - Values: {economic_data.get('values')}")
                print(f"   - Raw Numbers: {economic_data.get('raw_numbers')}")
            
            # Test AI translation (if available)
            if ai_translator.client:
                print(f"\n🤖 AI Translation Test...")
                translation = await ai_translator.translate_to_arabic(
                    article.title, "economic news"
                )
                print(f"Arabic Translation: {translation}")
                
                # Test market analysis
                market_analysis = await ai_translator.analyze_market_impact(
                    article.title, article.summary
                )
                print(f"Market Analysis: {market_analysis}")
            else:
                print(f"\n⚠️  AI Translation not available (need GROQ_API_KEY)")
                translation = "ترجمة تجريبية"
                market_analysis = {'impact': 'سلبي', 'currency': 'الدولار الأمريكي'}
            
            # Test enhanced formatting
            print(f"\n📱 Enhanced Arabic Formatting:")
            print("-" * 30)
            
            if economic_data and economic_data['has_data']:
                # Test sentiment analysis
                sentiment = formatter.analyze_market_sentiment(article.title, article.summary)
                
                # Format as economic data release
                formatted_message = await formatter._format_economic_data_release(
                    translation, economic_data, market_analysis, sentiment
                )
                print(formatted_message)
            else:
                print("📝 Not recognized as economic data - would use general formatting")
                
        except Exception as e:
            print(f"❌ Error in test case {i}: {e}")
            
        print("\n" + "="*60)
    
    # Configuration summary
    print(f"\n⚙️  System Configuration:")
    print(f"   - AI Translation: {'✅ Enabled' if ai_translator.client else '❌ Disabled (set GROQ_API_KEY)'}")
    print(f"   - Enhanced Formatter: ✅ Enabled")
    print(f"   - Economic Data Detection: ✅ Enhanced")
    print(f"   - USD Impact Analysis: ✅ Enabled")
    
    print(f"\n📋 To use this system:")
    print(f"   1. Set your GROQ_API_KEY environment variable")
    print(f"   2. Run: python free_arabic_bot.py")
    print(f"   3. The bot will automatically detect and format economic news")

if __name__ == "__main__":
    asyncio.run(test_enhanced_system())