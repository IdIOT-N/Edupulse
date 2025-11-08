"""
Bookmarking Module
Manages saving and retrieving bookmarked articles
"""

import json
import os
from datetime import datetime


class BookmarkManager:
    """Handles bookmark operations"""
    
    def __init__(self, filename='bookmarks.json'):
        self.filename = filename
        self.bookmarks = self.load_bookmarks()
    
    def load_bookmarks(self):
        """Load bookmarks from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading bookmarks: {e}")
                return []
        return []
    
    def save_bookmarks(self):
        """Save bookmarks to JSON file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, indent=4, ensure_ascii=False)
            print(f"Bookmarks saved: {len(self.bookmarks)} items")
        except Exception as e:
            print(f"Error saving bookmarks: {e}")
    
    def add_bookmark(self, article):
        """Add an article to bookmarks"""
        # Check if already bookmarked
        for bookmark in self.bookmarks:
            if bookmark.get('url') == article.get('url'):
                print("Article already bookmarked")
                return False
        
        # Create bookmark entry with all required fields
        bookmark = {
            'title': article.get('title', 'No Title'),
            'description': article.get('description', ''),
            'content': article.get('content', ''),  # Added content field
            'url': article.get('url', ''),
            'source': article.get('source', {}),    # Full source object
            'publishedAt': article.get('publishedAt', ''),
            'saved_at': datetime.now().isoformat(),
            'urlToImage': article.get('urlToImage', '')
        }
        
        self.bookmarks.insert(0, bookmark)
        self.save_bookmarks()
        return True
    
    def remove_bookmark(self, url):
        """Remove a bookmark by URL"""
        self.bookmarks = [b for b in self.bookmarks if b.get('url') != url]
        self.save_bookmarks()
        print(f"Removed bookmark: {url}")
    
    def get_bookmarks(self):
        """Get all bookmarks"""
        return self.bookmarks
    
    def is_bookmarked(self, url):
        """Check if an article is already bookmarked"""
        return any(b.get('url') == url for b in self.bookmarks)
    
    def clear_all_bookmarks(self):
        """Clear all bookmarks"""
        self.bookmarks = []
        self.save_bookmarks()
        print("All bookmarks cleared")
    
    def get_bookmark_count(self):
        """Get total number of bookmarks"""
        return len(self.bookmarks)