#!/usr/bin/env python3
"""
Fix bot timing: News every 3 minutes, Economic calendar every 1h 2m
"""

def fix_timing():
    with open('free_arabic_bot.py', 'r') as f:
        content = f.read()
    
    # Remove economic calendar from check_for_news
    old_text = '''            logger.info("📰 PROFESSIONAL: Checking for breaking financial news...")
            
            # Check economic calendar first (higher priority)
            await self.check_economic_calendar()
            
            # 🚀 ENHANCED: Get new articles with professional anti-detection scraping'''
    
    new_text = '''            logger.info("📰 PROFESSIONAL: Checking for breaking financial news...")
            
            # 🚀 ENHANCED: Get new articles with professional anti-detection scraping'''
    
    if old_text in content:
        content = content.replace(old_text, new_text)
        print("✅ Removed economic calendar from news check")
    else:
        print("❌ Could not find economic calendar in news check")
    
    # Add economic calendar task method before run method
    economic_task_method = '''
    async def economic_calendar_task(self):
        """📊 SEPARATE TASK: Economic calendar checker (every 1 hour 2 minutes)"""
        while self.running:
            try:
                logger.info("📊 ECONOMIC CALENDAR: Checking for economic events...")
                await self.check_economic_calendar()
                
                # Wait 1 hour 2 minutes for next economic calendar check
                economic_wait = 3720  # 1 hour 2 minutes
                logger.info(f"📊 ECONOMIC CALENDAR: Waiting {economic_wait} seconds (1h 2m) until next economic calendar check...")
                await asyncio.sleep(economic_wait)
                
            except Exception as e:
                logger.error(f"💥 Error in economic calendar task: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    '''
    
    # Find where to insert the method (before run method)
    run_method_start = content.find('    async def run(self):')
    if run_method_start != -1:
        content = content[:run_method_start] + economic_task_method + '\n' + content[run_method_start:]
        print("✅ Added economic calendar task method")
    else:
        print("❌ Could not find run method")
    
    # Update the main loop to start economic task
    old_main_loop = '''            # Main loop for NEWS (every 3 minutes as before)
            while self.running:
                try:
                    await self.check_for_news()
                    
                    # Wait for next NEWS cycle (3 minutes as before)
                    news_wait = 180  # 3 minutes for news (as requested by user)
                    logger.info(f"📰 NEWS: Waiting {news_wait} seconds (3m) until next news check...")
                    await asyncio.sleep(news_wait)'''
    
    new_main_loop = '''            # Start economic calendar task separately (1h 2m intervals)
            economic_task = asyncio.create_task(self.economic_calendar_task())
            logger.info("📊 ECONOMIC CALENDAR: Started separate task (1h 2m intervals)")
            
            # Main loop for NEWS (every 3 minutes as before)
            while self.running:
                try:
                    await self.check_for_news()
                    
                    # Wait for next NEWS cycle (3 minutes as before)
                    news_wait = 180  # 3 minutes for news (as requested by user)
                    logger.info(f"📰 NEWS: Waiting {news_wait} seconds (3m) until next news check...")
                    await asyncio.sleep(news_wait)'''
    
    if old_main_loop in content:
        content = content.replace(old_main_loop, new_main_loop)
        print("✅ Updated main loop to start economic task")
    else:
        print("❌ Could not find main loop to update")
    
    # Also update the KeyboardInterrupt handler
    old_interrupt = '''                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    economic_task.cancel()  # Cancel economic task
                    break'''
    
    new_interrupt = '''                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    if 'economic_task' in locals():
                        economic_task.cancel()  # Cancel economic task
                    break'''
    
    if old_interrupt in content:
        content = content.replace(old_interrupt, new_interrupt)
        print("✅ Updated interrupt handler")
    
    with open('free_arabic_bot.py', 'w') as f:
        f.write(content)
    
    print("\n🎉 Bot timing fixed!")
    print("📰 News: Every 3 minutes")
    print("📊 Economic Calendar: Every 1 hour 2 minutes")

if __name__ == "__main__":
    fix_timing()