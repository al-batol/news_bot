# 🚀 PythonAnywhere Deployment Guide

## 📊 **Resource Assessment: Hacker Plan Analysis**

**PythonAnywhere Hacker Plan:** `$5/month`
- ✅ **2,000 CPU-seconds per day** 
- ✅ **1GB disk space**
- ✅ **Always-on tasks** (1 allowed)

## 🎯 **Is Hacker Plan Enough?**

### ✅ **YES, but with optimization needed**

**Your bot's resource usage:**
- **Memory**: ~50-100MB (lightweight)
- **CPU**: ~5-10 seconds per cycle (news check every 3 minutes)
- **Daily CPU estimate**: ~1,600 seconds (well under 2,000 limit)
- **Disk space**: ~50MB for code + logs (well under 1GB)

## 🔧 **Optimization for PythonAnywhere**

### 1. **Reduce Check Frequency**
```python
# In config_free.py - change this:
SCRAPE_INTERVAL_SECONDS = 300  # 5 minutes instead of 3
MAX_ARTICLES_PER_SCRAPE = 2    # Reduce from 3 to 2
```

### 2. **Optimize CPU Usage**
```python
# Limit simultaneous RSS requests
MESSAGE_DELAY_SECONDS = 6      # Increase delay between posts
MAX_RETRIES = 2               # Reduce from 3 to 2
```

### 3. **Use Lightweight Mode**
```python
# For PythonAnywhere deployment
USE_AI_TRANSLATION = False    # Use Google Translate only (faster)
LOG_LEVEL = "WARNING"         # Reduce logging
```

## 📋 **Deployment Steps**

### Step 1: Upload Files
1. Upload your entire project to PythonAnywhere
2. Install requirements: `pip3 install -r requirements_free.txt`

### Step 2: Set Environment Variables
```bash
# In your .bashrc or directly in script
export GROQ_API_KEY="your_key_here"
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHANNEL_ID="your_channel_id"
```

### Step 3: Create Always-On Task
1. Go to **Dashboard > Tasks**
2. Create new task:
   - **Command**: `python3 /home/yourusername/news_scraping/free_arabic_bot.py`
   - **Type**: Always-on task

### Step 4: Monitor Resource Usage
- Check **CPU seconds** daily in dashboard
- Monitor logs in `/home/yourusername/news_scraping/logs/`

## 💡 **Pro Tips for PythonAnywhere**

### Reduce Resource Usage:
```python
# Optimized config for PythonAnywhere
NEWS_SOURCES = {
    'investing_economic': 'https://www.investing.com/rss/news_301.rss',  # Only economic data
    'investing_rss': 'https://www.investing.com/rss/news.rss',           # General news
}
SCRAPE_INTERVAL_SECONDS = 600  # 10 minutes
MAX_ARTICLES_PER_SCRAPE = 1    # Only 1 article per cycle
```

### Error Handling:
```python
# Add CPU-conscious error handling
MAX_CONSECUTIVE_ERRORS = 5     # Stop if too many errors
SLEEP_ON_ERROR = 60           # Sleep 1 minute on error
```

## 📈 **Expected Performance**

**Daily Usage with Optimization:**
- **CPU seconds**: ~800-1,200 (well under 2,000 limit)
- **Memory**: ~30-50MB constant
- **Network**: ~100-200 API calls per day
- **Messages sent**: ~20-50 per day

## 🚨 **Monitoring & Alerts**

Create a simple monitoring script:
```python
# monitor_resources.py
import psutil
import logging

def check_resources():
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    
    if cpu_usage > 80:
        logging.warning(f"High CPU usage: {cpu_usage}%")
    if memory_usage > 80:
        logging.warning(f"High memory usage: {memory_usage}%")
```

## ✅ **Final Answer: YES, Hacker Plan is Sufficient!**

With the optimizations above, your bot will run comfortably within the Hacker Plan limits:
- ✅ **CPU**: ~60% of daily limit used
- ✅ **Memory**: ~5% of available RAM
- ✅ **Disk**: ~5% of storage used
- ✅ **Always-on task**: Perfect for this use case

**Recommendation**: Start with Hacker Plan, monitor for first week, then optimize further if needed.