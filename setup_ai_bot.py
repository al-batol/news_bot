#!/usr/bin/env python3
"""
Setup script for Enhanced Arabic Crypto News Bot
Helps users configure their AI-powered bot with free APIs
"""
import os
import sys
import asyncio
from pathlib import Path

def print_header():
    print("🚀 Enhanced Arabic Crypto News Bot Setup")
    print("=" * 60)
    print("✨ AI-powered translation with Groq (FREE)")
    print("💎 Crypto market focus")
    print("📊 Professional Arabic formatting")
    print("🔥 Real-time market impact analysis")
    print("=" * 60)

def check_requirements():
    print("\n📦 Checking requirements...")
    
    required_packages = [
        'groq', 'feedparser', 'aiohttp', 'deep-translator'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements_free.txt")
        return False
    
    print("\n✅ All requirements satisfied!")
    return True

def setup_env_file():
    print("\n🔧 Setting up environment variables...")
    
    env_file = Path('.env')
    
    # Get API keys
    groq_key = input("\n🤖 Enter your Groq API key (get free at console.groq.com): ").strip()
    if not groq_key:
        print("⚠️  Groq API key is required for AI translation!")
        return False
    
    telegram_token = input("📱 Enter your Telegram Bot Token: ").strip()
    if not telegram_token:
        print("⚠️  Telegram Bot Token is required!")
        return False
    
    channel_id = input("📢 Enter your Telegram Channel ID (e.g., -1001234567890): ").strip()
    if not channel_id:
        print("⚠️  Telegram Channel ID is required!")
        return False
    
    # Create .env file
    env_content = f"""# Enhanced Arabic Crypto News Bot Configuration

# Groq AI Translation (FREE)
GROQ_API_KEY={groq_key}

# Telegram Configuration
TELEGRAM_BOT_TOKEN={telegram_token}
TELEGRAM_CHANNEL_ID={channel_id}

# Bot Settings
SCRAPE_INTERVAL_SECONDS=180
MAX_ARTICLES_PER_SCRAPE=5
MESSAGE_DELAY_SECONDS=3
LOG_LEVEL=INFO
ENVIRONMENT=enhanced_crypto
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Environment file created: {env_file}")
    return True

async def test_setup():
    print("\n🧪 Testing setup...")
    
    try:
        # Test AI translator
        print("  Testing AI translation...")
        from ai_translator import AITranslator
        
        translator = AITranslator()
        if translator.client:
            test_text = "Bitcoin reaches new high"
            result = await translator.translate_to_arabic(test_text, "crypto news")
            print(f"  ✅ AI Translation: {result[:50]}...")
        else:
            print("  ❌ AI Translation failed - check GROQ_API_KEY")
            return False
        
        # Test formatter
        print("  Testing Arabic formatter...")
        from crypto_arabic_formatter import CryptoArabicFormatter
        formatter = CryptoArabicFormatter()
        print("  ✅ Arabic formatter initialized")
        
        # Test RSS scraper
        print("  Testing RSS scraper...")
        from rss_scraper import RSSNewsScraper
        scraper = RSSNewsScraper()
        articles = await scraper.get_latest_news(2)  # Test with 2 articles
        await scraper.close_session()
        
        if articles:
            print(f"  ✅ RSS Scraper: Found {len(articles)} articles")
        else:
            print("  ⚠️  RSS Scraper: No articles found (may be normal)")
        
        print("\n🎉 Setup test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Setup test failed: {e}")
        return False

def show_next_steps():
    print("\n🚀 Next Steps:")
    print("1. Run the bot: python free_arabic_bot.py")
    print("2. Monitor logs in: logs/bot.log")
    print("3. Check your Telegram channel for crypto news!")
    print("\n📚 Features:")
    print("  • AI-powered Arabic translation")
    print("  • Real-time crypto market analysis")
    print("  • Professional Arabic formatting")
    print("  • Smart crypto news filtering")
    print("\n💡 Tips:")
    print("  • Bot focuses on crypto and financial news")
    print("  • Groq API provides fast, free AI translation")
    print("  • Adjust SCRAPE_INTERVAL_SECONDS for frequency")

async def main():
    print_header()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup environment
    if not setup_env_file():
        sys.exit(1)
    
    # Test setup
    if not await test_setup():
        print("\n⚠️  Setup has issues. Check your configuration.")
        sys.exit(1)
    
    show_next_steps()
    print("\n✨ Enhanced Arabic Crypto News Bot is ready!")

if __name__ == "__main__":
    asyncio.run(main())