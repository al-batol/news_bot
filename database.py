"""
Simple file-based database for tracking seen articles
"""
import json
import os
from datetime import datetime, timezone
from typing import Set, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ArticleDatabase:
    """Simple file-based database for tracking seen articles"""
    
    def __init__(self, db_file: str = "seen_articles.json"):
        self.db_file = db_file
        self.seen_articles: Set[str] = set()
        self.article_metadata: Dict[str, Dict[str, Any]] = {}
        self.load_database()
    
    def load_database(self):
        """Load seen articles from file"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.seen_articles = set(data.get('seen_articles', []))
                    self.article_metadata = data.get('article_metadata', {})
                    logger.info(f"Loaded {len(self.seen_articles)} seen articles from database")
            else:
                logger.info("Database file not found, starting with empty database")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            self.seen_articles = set()
            self.article_metadata = {}
    
    def save_database(self):
        """Save seen articles to file"""
        try:
            data = {
                'seen_articles': list(self.seen_articles),
                'article_metadata': self.article_metadata,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # Create backup of existing file
            if os.path.exists(self.db_file):
                backup_file = f"{self.db_file}.backup"
                os.rename(self.db_file, backup_file)
            
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(self.seen_articles)} seen articles to database")
            
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def is_article_seen(self, article_id: str) -> bool:
        """Check if an article has been seen before"""
        return article_id in self.seen_articles
    
    def mark_article_seen(self, article_id: str, title: str = "", link: str = "", timestamp: str = ""):
        """Mark an article as seen and save metadata"""
        self.seen_articles.add(article_id)
        self.article_metadata[article_id] = {
            'title': title,
            'link': link,
            'timestamp': timestamp,
            'seen_at': datetime.now(timezone.utc).isoformat()
        }
        self.save_database()
    
    def get_article_count(self) -> int:
        """Get total number of seen articles"""
        return len(self.seen_articles)
    
    def cleanup_old_articles(self, max_articles: int = 10000):
        """Remove oldest articles if database gets too large"""
        if len(self.seen_articles) > max_articles:
            # Sort by seen_at timestamp and keep most recent
            sorted_articles = sorted(
                self.article_metadata.items(),
                key=lambda x: x[1].get('seen_at', ''),
                reverse=True
            )
            
            # Keep only the most recent articles
            articles_to_keep = dict(sorted_articles[:max_articles])
            
            self.seen_articles = set(articles_to_keep.keys())
            self.article_metadata = articles_to_keep
            
            self.save_database()
            logger.info(f"Cleaned up database, kept {len(self.seen_articles)} most recent articles")
    
    def get_recent_articles(self, limit: int = 10) -> list:
        """Get recently seen articles"""
        sorted_articles = sorted(
            self.article_metadata.items(),
            key=lambda x: x[1].get('seen_at', ''),
            reverse=True
        )
        
        return [
            {
                'id': article_id,
                'title': metadata.get('title', ''),
                'link': metadata.get('link', ''),
                'timestamp': metadata.get('timestamp', ''),
                'seen_at': metadata.get('seen_at', '')
            }
            for article_id, metadata in sorted_articles[:limit]
        ]
    
    def reset_database(self):
        """Clear all seen articles (useful for testing)"""
        self.seen_articles.clear()
        self.article_metadata.clear()
        self.save_database()
        logger.info("Database reset - all articles cleared")

# Global database instance
article_db = ArticleDatabase() 