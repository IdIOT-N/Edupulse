"""
RSS Feed Aggregator
Fetches full articles from BBC, NPR, Reuters and other RSS feeds
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


class RSSNewsFetcher:
    """Fetch news from multiple RSS feeds"""
    
    def __init__(self):  # Changed from _init_ to __init__
        # Major RSS feeds with full content
        self.rss_feeds = {
            'bbc': [
                'http://feeds.bbci.co.uk/news/rss.xml',
                'http://feeds.bbci.co.uk/news/technology/rss.xml',
                'http://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
                'http://feeds.bbci.co.uk/news/business/rss.xml',
            ],
            'npr': [
                'https://feeds.npr.org/1001/rss.xml',  # News
                'https://feeds.npr.org/1019/rss.xml',  # Technology
                'https://feeds.npr.org/1007/rss.xml',  # Science
            ],
            'reuters': [
                'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
            ],
            'techcrunch': [
                'https://techcrunch.com/feed/',
            ],
            'sciencedaily': [
                'https://www.sciencedaily.com/rss/all.xml',
            ],
            'mit_news': [
                'https://news.mit.edu/rss/feed',
            ]
        }
    
    def fetch_news(self, query, max_results=20):
        """Fetch news from all RSS feeds with force refresh"""
        all_articles = []
        
        print(f"🔍 Searching for: {query}")
        
        # Try each feed source
        for source_name, feeds in self.rss_feeds.items():
            try:
                # No need to clear feedparser cache - just fetch directly
                articles = self.fetch_from_source(source_name, feeds, query, max_results)
                all_articles.extend(articles)
                
                if len(all_articles) >= max_results:
                    break
            except Exception as e:
                print(f"❌ {source_name} failed: {e}")
                continue
        
        # Sort by date (newest first)
        all_articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
        
        print(f"✅ Found {len(all_articles)} articles")
        return all_articles[:max_results]
    
    def fetch_from_source(self, source_name, feeds, query, max_results):
        """Fetch from a specific source's feeds"""
        articles = []
        query_lower = query.lower()
        
        for feed_url in feeds:
            try:
                print(f"  📡 Fetching from {source_name}...")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:max_results]:
                    # Check if article matches query
                    title = entry.get('title', '').lower()
                    summary = entry.get('summary', '').lower()
                    
                    if query_lower in title or query_lower in summary or self.query_matches(query_lower, title + ' ' + summary):
                        article = self.parse_entry(entry, source_name)
                        if article:
                            articles.append(article)
                
                if len(articles) >= max_results:
                    break
            
            except Exception as e:
                print(f"    ⚠ Feed error: {e}")
                continue
        
        return articles
    
    def query_matches(self, query, text):
        """Check if query words match text"""
        query_words = query.split()
        matches = sum(1 for word in query_words if word in text)
        return matches >= len(query_words) * 0.5  # 50% match
    
    def parse_entry(self, entry, source_name):
        """Parse RSS entry into article format"""
        try:
            # Extract full content
            content = self.extract_content(entry)
            
            # Parse date
            published = entry.get('published', entry.get('updated', ''))
            published_date = self.parse_date(published)
            
            article = {
                'title': entry.get('title', 'No Title'),
                'description': self.clean_html(entry.get('summary', '')),
                'content': content,
                'url': entry.get('link', ''),
                'urlToImage': self.extract_image(entry),
                'publishedAt': published,
                'published_date': published_date,
                'source': {'name': source_name.upper()},
                'author': entry.get('author', source_name)
            }
            
            return article
        
        except Exception as e:
            print(f"    ⚠ Parse error: {e}")
            return None
    
    def extract_content(self, entry):
        """Extract full article content"""
        # Try different content fields
        content = entry.get('content', [{}])[0].get('value', '')
        if not content:
            content = entry.get('summary', '')
        if not content:
            content = entry.get('description', '')
        
        # Clean HTML
        return self.clean_html(content)
    
    def clean_html(self, html_text):
        """Remove HTML tags and clean text"""
        if not html_text:
            return ''
        
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text(separator=' ')
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_image(self, entry):
        """Extract image URL from entry"""
        # Try media content
        if 'media_content' in entry:
            return entry.media_content[0].get('url', '')
        
        # Try media thumbnail
        if 'media_thumbnail' in entry:
            return entry.media_thumbnail[0].get('url', '')
        
        # Try enclosures
        if 'enclosures' in entry and entry.enclosures:
            for enc in entry.enclosures:
                if 'image' in enc.get('type', ''):
                    return enc.get('href', '')
        
        return ''
    
    def parse_date(self, date_str):
        """Parse date string to comparable format"""
        try:
            # Try parsing with feedparser
            from time import mktime
            parsed = feedparser._parse_date(date_str)
            if parsed:
                return datetime.fromtimestamp(mktime(parsed)).isoformat()
        except:
            pass
        
        return date_str


# Quick test
if __name__ == '__main__':
    fetcher = RSSNewsFetcher()
    articles = fetcher.fetch_news('artificial intelligence', max_results=5)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print(f"   Content length: {len(article['content'])} chars")