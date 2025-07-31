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

logger = logging.getLogger(__name__)

class CryptoArabicFormatter:
    """Enhanced Arabic formatter for crypto-focused financial news"""
    
    def __init__(self):
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
    
    def extract_economic_data(self, title: str, summary: str = "") -> Optional[Dict]:
        """
        Enhanced economic data extraction for trading-style news
        """
        content = f"{title} {summary}".lower()
        
        # Enhanced number patterns to catch all formats
        # Matches: 7.5M, 3.2%, 218K, 0.155, +0.16%, etc.
        number_patterns = re.findall(r'([+-]?\d+\.?\d*[kmb%]?)', content, re.IGNORECASE)
        
        # Enhanced economic indicators with priority order
        economic_indicators = {
            # Employment (highest priority for USD impact)
            'non-farm payroll': 'فرص العمل الأمريكية',
            'non farm payroll': 'فرص العمل الأمريكية',
            'nonfarm payrolls': 'فرص العمل الأمريكية', 
            'payrolls': 'فرص العمل الأمريكية',
            'jobs report': 'تقرير الوظائف الأمريكي',
            'unemployment rate': 'معدل البطالة الأمريكي',
            'unemployment claims': 'معدلات الشكاوى من البطالة',
            'jobless claims': 'طلبات إعانة البطالة',
            
            # Manufacturing and PMI
            'chicago pmi': 'مؤشر مديري المشتريات من شيكاغو',
            'ism manufacturing': 'مؤشر مديري المشتريات الصناعي',
            'manufacturing pmi': 'مؤشر مديري المشتريات التصنيعي',
            'pmi': 'مؤشر مديري المشتريات',
            
            # Inflation
            'cpi': 'مؤشر أسعار المستهلك',
            'core cpi': 'مؤشر أسعار المستهلك الأساسي',
            'inflation': 'التضخم',
            'ppi': 'مؤشر أسعار المنتجين',
            
            # Other indicators
            'retail sales': 'مبيعات التجزئة',
            'gdp': 'الناتج المحلي الإجمالي',
            'housing starts': 'بدء البناء السكني'
        }
        
        # Find the most specific indicator
        found_indicator = None
        found_arabic_name = None
        
        for indicator, arabic_name in economic_indicators.items():
            if indicator in content:
                found_indicator = indicator
                found_arabic_name = arabic_name
                break
        
        # Look for previous/forecast/actual patterns
        prev_pattern = re.search(r'(?:previous|prev|prior|last)[:\s]*([+-]?\d+\.?\d*[kmb%]?)', content, re.IGNORECASE)
        forecast_pattern = re.search(r'(?:forecast|est|expected|estimate)[:\s]*([+-]?\d+\.?\d*[kmb%]?)', content, re.IGNORECASE)
        actual_pattern = re.search(r'(?:actual|current|latest|came in at)[:\s]*([+-]?\d+\.?\d*[kmb%]?)', content, re.IGNORECASE)
        
        # Extract vs pattern (common in economic news)
        vs_pattern = re.search(r'(\d+\.?\d*[kmb%]?)\s*(?:vs|versus|against)\s*(\d+\.?\d*[kmb%]?)', content, re.IGNORECASE)
        
        if found_indicator and (number_patterns or prev_pattern or forecast_pattern or actual_pattern):
            data_values = []
            
            # Try to extract structured data
            if prev_pattern:
                data_values.append(('previous', prev_pattern.group(1)))
            if forecast_pattern:
                data_values.append(('forecast', forecast_pattern.group(1)))
            if actual_pattern:
                data_values.append(('actual', actual_pattern.group(1)))
            elif vs_pattern:
                # Handle "X vs Y expected" format
                data_values.append(('actual', vs_pattern.group(1)))
                data_values.append(('forecast', vs_pattern.group(2)))
            
            # If no structured data, use all numbers found
            if not data_values and number_patterns:
                for num in number_patterns[:3]:  # Take first 3 numbers
                    data_values.append(('value', num))
            
            return {
                'indicator': found_indicator,
                'arabic_name': found_arabic_name,
                'values': data_values,
                'raw_numbers': number_patterns,
                'has_data': True,
                'is_economic_data': True
            }
        
        return None
    
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
            
            # Try to extract economic data
            economic_data = self.extract_economic_data(article.title, getattr(article, 'summary', ''))
            
            if economic_data and economic_data['has_data']:
                # Format as economic data release
                return await self._format_economic_data_release(
                    translation, economic_data, market_analysis, sentiment_analysis
                )
            else:
                # Format as general crypto/market news
                return await self._format_crypto_market_news(
                    translation, crypto_asset, market_analysis, sentiment_analysis
                )
                
        except Exception as e:
            logger.error(f"Error in enhanced formatting: {e}")
            # Fallback to simple format
            return await self._format_simple_news(translation, market_analysis)
    
    async def _format_economic_data_release(self, translation: str, data: Dict, analysis: Dict, sentiment: Dict) -> str:
        """
        Format economic data release in TradingView style exactly like user's example
        """
        # Get the Arabic name for the indicator
        indicator_arabic = data.get('arabic_name', data.get('indicator', 'البيانات الاقتصادية'))
        
        # Build the header with red square for "صدر الآن"
        message = f"🟥 صدر الآن :- {indicator_arabic}\n\n"
        
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
        
        # Format the data points with green circles
        if previous_val:
            message += f"🟢 السابق: {previous_val}\n"
        if forecast_val:
            message += f"🟢 التقدير: {forecast_val}\n"
        if actual_val:
            message += f"🟢 الحالي : {actual_val}\n"
        
        # Add empty line before result
        message += "\n"
        
        # Determine USD impact based on indicator type and sentiment
        usd_impact = self._analyze_usd_impact(data, sentiment, previous_val, forecast_val, actual_val)
        
        # Format the result with appropriate emoji and USD focus
        if usd_impact == 'positive':
            message += f"✅ النتيجة : إيجابي للدولار الأمريكي"
        elif usd_impact == 'negative':
            message += f"🟥 النتيجة: سلبي لأسعار الدولار"
        else:
            message += f"🟡 النتيجة : تأثير محايد على الدولار الأمريكي"
        
        return message
    
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
        message = f"{self.market_emojis['breaking']} عاجل: {asset_emoji}\n\n"
        message += f"{translation}\n\n"
        message += f"تابعنا لكل جديد : @news_news127"
        
        return message
    
    async def _format_simple_news(self, translation: str, analysis: Dict) -> str:
        """
        Simple fallback format
        """
        message = f"{self.market_emojis['breaking']} عاجل: {self.market_emojis['crypto']} {translation}\n\n"
        message += f"تابعنا لكل جديد : @news_news127"
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