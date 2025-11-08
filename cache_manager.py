"""
Cache Manager
Manages offline caching of articles
"""

import json
import os
from datetime import datetime, timedelta


class CacheManager:
    """Manages article caching for offline access"""
    
    def __init__(self, cache_file='cache.json', cache_duration_hours=6):
        """Initialize cache manager"""
        self.cache_file = cache_file
        self.cache_duration = timedelta(hours=cache_duration_hours)
    
    def save_cache(self, articles, metadata=None):
        """Save articles to cache with metadata"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {},
                'articles': articles
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Cache saved: {len(articles)} articles")
            return True
        
        except Exception as e:
            print(f"❌ Cache save error: {e}")
            return False
    
    def load_cache(self):
        """Load cached articles if still valid"""
        try:
            if not os.path.exists(self.cache_file):
                print("📭 No cache file found")
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check cache age
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            age = datetime.now() - cache_time
            
            if age > self.cache_duration:
                print(f"⏰ Cache expired ({age.total_seconds() / 3600:.1f} hours old)")
                return None
            
            articles = cache_data.get('articles', [])
            print(f"📦 Cache loaded: {len(articles)} articles")
            return articles
        
        except Exception as e:
            print(f"❌ Cache load error: {e}")
            return None
    
    def clear_cache(self):
        """Clear the cache file"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                print("🗑️ Cache cleared")
                return True
        except Exception as e:
            print(f"❌ Cache clear error: {e}")
            return False
    
    def is_cache_valid(self):
        """Check if cache exists and is still valid"""
        try:
            if not os.path.exists(self.cache_file):
                return False
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            age = datetime.now() - cache_time
            
            return age <= self.cache_duration
        
        except:
            return False
    
    def get_cache_info(self):
        """Get information about cached data"""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            age = datetime.now() - cache_time
            
            return {
                'timestamp': cache_time,
                'age_hours': age.total_seconds() / 3600,
                'article_count': len(cache_data.get('articles', [])),
                'metadata': cache_data.get('metadata', {}),
                'is_valid': age <= self.cache_duration
            }
        
        except Exception as e:
            print(f"❌ Cache info error: {e}")
            return None