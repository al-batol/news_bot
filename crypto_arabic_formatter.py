#!/usr/bin/env python3
"""
Enhanced Arabic formatter for crypto and financial news
Creates detailed market analysis format like professional trading channels
"""
import re
import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone
import asyncio

from config_free import Config

logger = logging.getLogger(__name__)

class CryptoArabicFormatter:
    """Enhanced Arabic formatter for crypto-focused financial news"""
    
    def __init__(self):
        # Centralized translation dictionary
        self.translations = {
            'wait_for_event': {
                'ar': "⏰ ترقبوا اليوم سيصدر",
                'en': "⏰ Wait for today's event to be released"
            },
            'date_in_saudi': {
                'ar': "🕐 الموعد بتوقيت السعودية:",
                'en': "🕐 Date in Saudi Arabia:"
            },
            'previous': {
                'ar': "📈 السابق:",
                'en': "📈 Previous:"
            },
            'forecast': {
                'ar': "🔮 المتوقع:",
                'en': "🔮 Forecast:"
            },
            'results_notice': {
                'ar': "💡 سنقوم بنشر النتائج فور صدورها",
                'en': "💡 We will post the results as soon as they are released"
            },
            'released_now': {
                'ar': "🚨 صدر الآن :",
                'en': "🚨 Released now :"
            },
            'previous_short': {
                'ar': "⏮️ السابق :",
                'en': "⏮️ Previous :"
            },
            'estimate': {
                'ar': "🎯 التقدير :",
                'en': "🎯 Estimate :"
            },
            'current': {
                'ar': "✨ الحالي :",
                'en': "✨ Current :"
            },
            'result': {
                'ar': "النتيجة :",
                'en': "The result :"
            },
            'positive_for_usd': {
                'ar': "إيجابي للدولار الأمريكي",
                'en': "Positive for the US dollar"
            },
            'negative_for_usd': {
                'ar': "سلبي للدولار الأمريكي",
                'en': "Negative for the US dollar"
            },
            'as_expected_for_usd': {
                'ar': "كما هو متوقع للدولار الأمريكي",
                'en': "As expected for the US dollar"
            },
            'follow_us_analysis': {
                'ar': "📊 تابعونا لتحليل الأسواق @news_crypto_911",
                'en': "📊 Follow us for market analysis @news_crypto_911"
            },
            'america': {
                'ar': "أمريكا",
                'en': "America"
            },
            'breaking_news': {
                'ar': "عاجل:",
                'en': "Breaking:"
            },
            'follow_us_updates': {
                'ar': "تابعنا لكل جديد : @news_crypto_911",
                'en': "Follow us for updates : @news_crypto_911"
            }
        }
        
        # Enhanced emoji mapping for crypto and financial content
        self.market_emojis = {
            # Market direction
            'positive': '🟢',
            'negative': '🟥', 
            'neutral': '🟡',
            'strong_positive': '✅',
            'strong_negative': '❌',
            
            # Assets
            'bitcoin': '₿',
            'crypto': '🪙',
            'dollar': '💵',
            'gold': '🥇',
            'oil': '🛢️',
            'stocks': '📈',
            
            # News types
            'breaking': '🚨',
            'released': '📊',
            'economic_data': '📋',
            'fed': '🏦',
            'important': '⚡',
        }
        
        # Enhanced economic data terms in Arabic (matching TradingView style)
        self.economic_terms = {
            # Employment indicators
            'unemployment': 'معدل البطالة',
            'unemployment rate': 'معدل البطالة',
            'jobless claims': 'طلبات إعانة البطالة',
            'unemployment claims': 'طلبات إعانة البطالة',
            'non farm payroll': 'فرص العمل الأمريكية',
            'nonfarm payrolls': 'فرص العمل الأمريكية',
            'jobs report': 'تقرير الوظائف الأمريكي',
            'employment': 'التوظيف',
            
            # Inflation and prices
            'inflation': 'التضخم',
            'cpi': 'مؤشر أسعار المستهلك',
            'core cpi': 'مؤشر أسعار المستهلك الأساسي',
            'ppi': 'مؤشر أسعار المنتجين',
            'pcr': 'مؤشر أسعار الإنفاق الاستهلاكي',
            
            # GDP and growth
            'gdp': 'الناتج المحلي الإجمالي',
            'economic growth': 'النمو الاقتصادي',
            
            # Manufacturing and business
            'pmi': 'مؤشر مديري المشتريات',
            'manufacturing pmi': 'مؤشر مديري المشتريات التصنيعي',
            'ism manufacturing': 'مؤشر مديري المشتريات الصناعي',
            'chicago pmi': 'مؤشر مديري المشتريات من شيكاغو',
            'business activity': 'النشاط التجاري',
            
            # Sales and consumption
            'retail sales': 'مبيعات التجزئة',
            'consumer spending': 'الإنفاق الاستهلاكي',
            'housing starts': 'بدء البناء السكني',
            
            # Fed and monetary policy
            'interest rate': 'أسعار الفائدة',
            'fed rate': 'أسعار الفائدة الفيدرالية',
            'fomc': 'لجنة السوق المفتوحة الفيدرالية',
            'federal reserve': 'الاحتياطي الفيدرالي',
            'monetary policy': 'السياسة النقدية',
            
            # Trade and international
            'trade balance': 'الميزان التجاري',
            'current account': 'الحساب الجاري',
            'exports': 'الصادرات',
            'imports': 'الواردات',
        }
        
        # Market impact phrases
        self.impact_phrases = {
            'positive_dollar': 'إيجابي للدولار الأمريكي',
            'negative_dollar': 'سلبي للدولار الأمريكي', 
            'positive_crypto': 'إيجابي للعملات المشفرة',
            'negative_crypto': 'سلبي للعملات المشفرة',
            'positive_gold': 'إيجابي للذهب',
            'negative_gold': 'سلبي للذهب',
            'mixed': 'تأثير مختلط على الأسواق',
            'neutral': 'تأثير محايد على الأسواق'
        }
    
    def get_text(self, key: str) -> str:
        """
        Get translated text based on current language setting
        """
        if key not in self.translations:
            logger.warning(f"Translation key '{key}' not found")
            return key
        
        lang = 'ar' if Config.ENABLE_ARABIC else 'en'
        return self.translations[key].get(lang, key)
    
    # NOTE: This method has been replaced by investing_scraper.py economic calendar functionality
    # Keeping for backward compatibility only
    
    def detect_crypto_asset(self, title: str, summary: str = "") -> str:
        """
        Detect which crypto asset is the main focus
        """
        content = f"{title} {summary}".lower()
        
        crypto_assets = {
            'bitcoin': ['bitcoin', 'btc', 'بيتكوين'],
            'ethereum': ['ethereum', 'eth', 'إيثريوم'], 
            'crypto_general': ['crypto', 'cryptocurrency', 'altcoin', 'العملات المشفرة']
        }
        
        for asset, keywords in crypto_assets.items():
            for keyword in keywords:
                if keyword in content:
                    return asset
        
        return 'crypto_general'
    
    def analyze_market_sentiment(self, title: str, summary: str = "") -> Dict:
        """
        Analyze market sentiment and direction from news content
        """
        content = f"{title} {summary}".lower()
        
        # Positive indicators
        positive_words = [
            'rise', 'up', 'gain', 'high', 'surge', 'boost', 'strong', 'growth',
            'bullish', 'rally', 'increase', 'record', 'all-time high', 'ath'
        ]
        
        # Negative indicators  
        negative_words = [
            'fall', 'down', 'drop', 'decline', 'crash', 'dump', 'weak', 'loss',
            'bearish', 'decrease', 'low', 'correction', 'sell-off', 'plunge'
        ]
        
        positive_score = sum(1 for word in positive_words if word in content)
        negative_score = sum(1 for word in negative_words if word in content)
        
        if positive_score > negative_score:
            return {
                'sentiment': 'positive',
                'strength': 'strong' if positive_score >= 3 else 'moderate',
                'direction': 'bullish'
            }
        elif negative_score > positive_score:
            return {
                'sentiment': 'negative', 
                'strength': 'strong' if negative_score >= 3 else 'moderate',
                'direction': 'bearish'
            }
        else:
            return {
                'sentiment': 'neutral',
                'strength': 'moderate',
                'direction': 'sideways'
            }
    
    async def format_enhanced_arabic_news(self, article, translation: str, market_analysis: Dict) -> str:
        """
        Create enhanced Arabic news format like professional trading channels
        """
        try:
            # Detect crypto asset and sentiment
            crypto_asset = self.detect_crypto_asset(article.title, getattr(article, 'summary', ''))
            sentiment_analysis = self.analyze_market_sentiment(article.title, getattr(article, 'summary', ''))
            
            # Format as general crypto/market news (economic data now handled separately)
            return await self._format_crypto_market_news(
                translation, crypto_asset, market_analysis, sentiment_analysis
            )
                
        except Exception as e:
            logger.error(f"Error in enhanced formatting: {e}")
            # Fallback to simple format
            return await self._format_simple_news(translation, market_analysis)
    
    async def format_economic_announcement(self, event_name_english: str, event_name_arabic: str, country_flag: str = "🇺🇸", event_time: str = None, is_today: bool = False, previous: str = None, forecast: str = None) -> str:
        """
        Format upcoming economic event announcement with enhanced emojis
        Shows both English original title and Arabic translation
        Only show if event is TODAY
        """
        # 📅 Only show events that are TODAY
        if not is_today:
            return None  # Don't send events that are not today
        
        # Enhanced emojis for different event types
        if 'بطالة' in event_name_arabic:
            emoji = "💼"  # Briefcase for unemployment
        elif 'وظائف' in event_name_arabic or 'توظيف' in event_name_arabic:
            emoji = "🏢"  # Office building for jobs
        elif 'تضخم' in event_name_arabic or 'أسعار المستهلك' in event_name_arabic:
            emoji = "📊"  # Chart for inflation
        elif 'مشتريات' in event_name_arabic:
            emoji = "🏭"  # Factory for PMI
        elif 'فائدة' in event_name_arabic:
            emoji = "🏦"  # Bank for interest rates
        elif 'تجزئة' in event_name_arabic:
            emoji = "🛍️"  # Shopping for retail
        else:
            emoji = "📈"  # Default economic chart
        
        # Convert time to Saudi Arabia timezone if provided
        saudi_time = None
        if event_time and event_time not in ["TBD", "All Day", ""]:
            saudi_time = self._convert_to_saudi_time(event_time)
        
        # Build announcement message - TODAY events only
        message = self.get_text('wait_for_event') + f" {emoji}\n\n"
        message += f"{country_flag} {event_name_english}\n"
        if Config.ENABLE_ARABIC:
            message += f"📊 {event_name_arabic}"
        
        if saudi_time:
            message += f"\n{self.get_text('date_in_saudi')} {saudi_time}"
        
        # Add Previous and Forecast if available
        if previous:
            message += f"\n{self.get_text('previous')} {previous}"
        if forecast:
            message += f"\n{self.get_text('forecast')} {forecast}"
        
        message += f"\n\n{self.get_text('results_notice')}"
        
        return message
    
    def _convert_to_saudi_time(self, utc_time_str: str) -> str:
        """Convert UTC time to Saudi Arabia time (UTC+3)"""
        try:
            from datetime import datetime, timezone, timedelta
            
            # Parse the time string
            if ':' in utc_time_str:
                hour, minute = map(int, utc_time_str.split(':'))
            else:
                hour = int(utc_time_str) if utc_time_str.isdigit() else 13
                minute = 0
            
            # Create UTC datetime for today
            utc_dt = datetime.now(timezone.utc).replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Convert to Saudi time (UTC+3)
            saudi_tz = timezone(timedelta(hours=3))
            saudi_dt = utc_dt.astimezone(saudi_tz)
            
            # Format as HH:MM
            return saudi_dt.strftime('%H:%M')
            
        except Exception as e:
            # Fallback to original time
            return utc_time_str
    
    async def format_economic_data_release(self, event_name_arabic: str, country: str, country_flag: str, 
                                         previous: str = None, forecast: str = None, actual: str = None,
                                         impact_analysis: str = None) -> str:
        """
        Format economic data release with improved emojis and visual appeal
        """
        # Enhanced header with flash emoji for urgent news
        message = f"{self.get_text('released_now')}\n\n"
        
        # Country and event name with enhanced emoji
        message += f"{country} - {country_flag}\n"
        
        # Choose emoji based on event type for better visual context
        if 'بطالة' in event_name_arabic:
            event_emoji = "💼"  # Briefcase for unemployment
        elif 'وظائف' in event_name_arabic or 'توظيف' in event_name_arabic:
            event_emoji = "🏢"  # Office building for jobs
        elif 'تضخم' in event_name_arabic or 'أسعار المستهلك' in event_name_arabic:
            event_emoji = "📊"  # Chart for inflation
        elif 'مشتريات' in event_name_arabic:
            event_emoji = "🏭"  # Factory for PMI
        elif 'فائدة' in event_name_arabic:
            event_emoji = "🏦"  # Bank for interest rates
        elif 'تجزئة' in event_name_arabic:
            event_emoji = "🛍️"  # Shopping for retail
        else:
            event_emoji = "📈"  # Default economic chart
            
        message += f"{event_emoji} {event_name_arabic}\n\n"
        
        # Data points with enhanced formatting and emojis
        if previous:
            message += f"{self.get_text('previous_short')} {previous}\n"
        if forecast:
            message += f"{self.get_text('estimate')} {forecast}\n"
        if actual:
            message += f"{self.get_text('current')} {actual}\n"
        
        # Add separator line for better readability
        message += "\n" + "➖" * 25 + "\n\n"
        
        # Result analysis with appropriate emoji based on impact
        if impact_analysis:
            if 'إيجابي' in impact_analysis or 'Positive' in impact_analysis:
                result_emoji = "✅"  # Green check for positive
            elif 'سلبي' in impact_analysis or 'Negative' in impact_analysis:
                result_emoji = "❌"  # Red X for negative
            else:
                result_emoji = "⚖️"  # Scale for neutral
            message += f"{result_emoji} {self.get_text('result')} {impact_analysis}"
        else:
            message += f"⚖️ {self.get_text('result')} {self.get_text('as_expected_for_usd')}"
        
        # Add footer for engagement
        message += f"\n\n{self.get_text('follow_us_analysis')}"
        
        return message
    
    async def _format_economic_data_release(self, translation: str, data: Dict, analysis: Dict, sentiment: Dict) -> str:
        """
        Legacy method - now redirects to new format_economic_data_release
        """
        # Get the Arabic name for the indicator
        indicator_arabic = data.get('arabic_name', data.get('indicator', 'البيانات الاقتصادية'))
        
        # Extract structured data values
        data_values = data.get('values', [])
        previous_val = None
        forecast_val = None
        actual_val = None
        
        # Parse the structured data
        for value_type, value in data_values:
            if value_type == 'previous':
                previous_val = value
            elif value_type == 'forecast':
                forecast_val = value
            elif value_type == 'actual':
                actual_val = value
        
        # If we don't have structured data, try to use raw numbers in order
        if not any([previous_val, forecast_val, actual_val]) and data.get('raw_numbers'):
            numbers = data['raw_numbers']
            if len(numbers) >= 3:
                # Assume order: previous, forecast, actual (most common in economic news)
                previous_val = numbers[0] if len(numbers) > 0 else None
                forecast_val = numbers[1] if len(numbers) > 1 else None
                actual_val = numbers[2] if len(numbers) > 2 else None
            elif len(numbers) == 2:
                # Usually actual vs forecast
                actual_val = numbers[0]
                forecast_val = numbers[1]
        
        # Determine USD impact based on indicator type and sentiment
        usd_impact = self._analyze_usd_impact(data, sentiment, previous_val, forecast_val, actual_val)
        
        # Format the result analysis
        if usd_impact == 'positive':
            impact_analysis = self.get_text('positive_for_usd')
        elif usd_impact == 'negative':
            impact_analysis = self.get_text('negative_for_usd')
        else:
            impact_analysis = self.get_text('as_expected_for_usd')
        
        # Use new formatting method
        return await self.format_economic_data_release(
            event_name_arabic=indicator_arabic,
            country=self.get_text('america'),
            country_flag="🇺🇸",
            previous=previous_val,
            forecast=forecast_val,
            actual=actual_val,
            impact_analysis=impact_analysis
        )
    
    def _analyze_usd_impact(self, data: Dict, sentiment: Dict, previous_val: str = None, forecast_val: str = None, actual_val: str = None) -> str:
        """
        Analyze USD impact based on economic indicator type and values
        """
        indicator = data.get('indicator', '').lower()
        
        # Convert values to float for comparison (remove letters like M, K, %)
        def clean_number(val):
            if not val:
                return None
            try:
                # Remove common suffixes and convert
                clean_val = re.sub(r'[mkb%]', '', str(val).lower())
                return float(clean_val)
            except:
                return None
        
        actual_num = clean_number(actual_val)
        forecast_num = clean_number(forecast_val) 
        previous_num = clean_number(previous_val)
        
        # Employment indicators (higher jobs = stronger USD)
        if any(keyword in indicator for keyword in ['payroll', 'jobs', 'employment']):
            if actual_num and forecast_num:
                return 'positive' if actual_num > forecast_num else 'negative'
            elif actual_num and previous_num:
                return 'positive' if actual_num > previous_num else 'negative'
        
        # Unemployment (lower unemployment = stronger USD)
        elif 'unemployment' in indicator:
            if actual_num and forecast_num:
                return 'positive' if actual_num < forecast_num else 'negative'
            elif actual_num and previous_num:
                return 'positive' if actual_num < previous_num else 'negative'
                
        # PMI (higher PMI = stronger USD)
        elif 'pmi' in indicator:
            if actual_num and forecast_num:
                return 'positive' if actual_num > forecast_num else 'negative'
            elif actual_num and previous_num:
                return 'positive' if actual_num > previous_num else 'negative'
        
        # Inflation (moderate inflation good, too high or low bad)
        elif any(keyword in indicator for keyword in ['cpi', 'inflation', 'ppi']):
            if actual_num and forecast_num:
                # This is complex, but generally meeting expectations is positive
                return 'positive' if abs(actual_num - forecast_num) < 0.2 else 'negative'
        
        # Default fallback based on sentiment
        return sentiment.get('sentiment', 'neutral') if sentiment.get('sentiment') in ['positive', 'negative'] else 'neutral'
    
    async def _format_crypto_market_news(self, translation: str, asset: str, analysis: Dict, sentiment: Dict) -> str:
        """
        Format general crypto market news (NO impact analysis for non-economic news)
        """
        # Choose emoji based on asset
        asset_emoji = self.market_emojis.get(asset, self.market_emojis['crypto'])
        
        # Build simple message without impact analysis
        message = f"{self.market_emojis['breaking']} {self.get_text('breaking_news')} {asset_emoji}\n\n"
        message += f"{translation}\n\n"
        message += f"{self.get_text('follow_us_updates')}"
        
        return message
    
    async def _format_simple_news(self, translation: str, analysis: Dict) -> str:
        """
        Simple fallback format
        """
        message = f"{self.market_emojis['breaking']} {self.get_text('breaking_news')} {self.market_emojis['crypto']} {translation}\n\n"
        message += f"{self.get_text('follow_us_updates')}"
        return message

# Test function
async def test_formatter():
    """Test the crypto Arabic formatter"""
    formatter = CryptoArabicFormatter()
    
    # Mock article
    class MockArticle:
        def __init__(self, title, summary=""):
            self.title = title
            self.summary = summary
    
    # Test cases
    test_cases = [
        {
            'article': MockArticle("Bitcoin reaches new all-time high above $100,000", "Strong institutional demand drives crypto rally"),
            'translation': "البيتكوين يصل إلى أعلى مستوى جديد فوق 100 ألف دولار",
            'analysis': {'impact': 'إيجابي', 'currency': 'العملات المشفرة'}
        },
        {
            'article': MockArticle("US unemployment rate falls to 3.7% vs 3.8% expected", "Non-farm payrolls exceed expectations"),
            'translation': "معدل البطالة الأمريكي ينخفض إلى 3.7% مقابل 3.8% متوقع",
            'analysis': {'impact': 'إيجابي', 'currency': 'الدولار الأمريكي'}
        }
    ]
    
    print("Testing Crypto Arabic Formatter:")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        formatted = await formatter.format_enhanced_arabic_news(
            test['article'], 
            test['translation'], 
            test['analysis']
        )
        print(formatted)
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_formatter())