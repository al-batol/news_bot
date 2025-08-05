#!/usr/bin/env python3
"""
AI-powered translation module using Groq API
Supports high-quality Arabic translation for crypto and financial news
"""
import os
import logging
import asyncio
from typing import Optional
from groq import AsyncGroq

logger = logging.getLogger(__name__)

class AITranslator:
    """AI-powered translator using Groq's free API with Arabic-optimized models"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.client = None
        self.model = "llama-3.3-70b-versatile"  # Stable model that should work
        
        if self.api_key:
            try:
                self.client = AsyncGroq(api_key=self.api_key)
                logger.info("AI Translator initialized with Groq API (Arabic optimized)")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None
        else:
            logger.warning("No GROQ_API_KEY found - AI translation disabled")
    
    async def translate_to_arabic(self, text: str, context: str = "financial news") -> str:
        """
        Translate text to Arabic using AI with financial/crypto context understanding
        """
        if not self.client:
            logger.warning("AI translator not available - returning original text")
            return text
        
        try:
            # Clean and prepare text
            text = text.strip()
            if len(text) > 1000:
                text = text[:1000] + "..."
            
            # Create context-aware prompt for better translation
            system_prompt = f"""أنت مترجم محترف متخصص في الأخبار المالية والعملات المشفرة. 
قم بترجمة النص التالي إلى العربية مع مراعاة:
1. استخدام المصطلحات المالية العربية الصحيحة
2. الحفاظ على المعنى المالي والاقتصادي
3. جعل النص طبيعي ومفهوم للقارئ العربي
4. استخدام تعبيرات مالية مناسبة للسوق العربي

قم بالترجمة فقط بدون أي تفسيرات إضافية."""

            user_prompt = f"ترجم هذا النص من {context}:\n\n{text}"
            
            # Make API call
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent translation
                max_tokens=1024,
                top_p=0.9
            )
            
            translation = completion.choices[0].message.content.strip()
            logger.info("AI translation successful")
            return translation
            
        except Exception as e:
            logger.error(f"AI translation failed: {e}")
            # Fallback to original text
            return text
    
    async def analyze_market_impact(self, title: str, summary: str = "") -> dict:
        """
        Analyze market impact and sentiment for crypto/financial news
        """
        if not self.client:
            return {"impact": "محايد", "currency": "الدولار الأمريكي", "sentiment": "محايد"}
        
        try:
            content = f"{title} {summary}"
            
            system_prompt = """أنت محلل أسواق مالية متخصص في العملات المشفرة والأسواق المالية.
حلل النص المعطى وأعطني:
1. التأثير على السوق (إيجابي/سلبي/محايد)
2. العملة/الأصل المتأثر الرئيسي
3. قوة التأثير (قوي/متوسط/ضعيف)

أجب بصيغة JSON فقط:
{"impact": "إيجابي/سلبي/محايد", "currency": "البيتكوين/الدولار الأمريكي/الذهب/الأسهم", "strength": "قوي/متوسط/ضعيف"}"""

            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                temperature=0.1,
                max_tokens=256
            )
            
            result_text = completion.choices[0].message.content.strip()
            
            # Try to parse JSON response
            import json
            try:
                result = json.loads(result_text)
                return result
            except:
                # Fallback response
                return {"impact": "محايد", "currency": "السوق", "strength": "متوسط"}
                
        except Exception as e:
            logger.error(f"Market impact analysis failed: {e}")
            return {"impact": "محايد", "currency": "السوق", "strength": "متوسط"}

# Test function
async def test_ai_translator():
    """Test the AI translator functionality"""
    translator = AITranslator()
    
    test_text = "Bitcoin reaches new all-time high as institutional investors show strong interest in cryptocurrency markets"
    
    if translator.client:
        print("Testing AI Translation...")
        arabic_text = await translator.translate_to_arabic(test_text, "cryptocurrency news")
        print(f"Original: {test_text}")
        print(f"Arabic: {arabic_text}")
        
        print("\nTesting Market Impact Analysis...")
        impact = await translator.analyze_market_impact(test_text)
        print(f"Impact Analysis: {impact}")
    else:
        print("AI Translator not available - please set GROQ_API_KEY")

if __name__ == "__main__":
    asyncio.run(test_ai_translator())