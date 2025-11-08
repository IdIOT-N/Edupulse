"""
Multi-Source News Fetcher
Fetches full-text articles from free news sources
"""

import requests
from datetime import datetime, timedelta
import os


class NewsSourceFetcher:
    """Fetches news from multiple free sources with full text"""
    
    def __init__(self):
        self.newsapi_key = os.getenv('NEWS_API_KEY')
        self.guardian_key = os.getenv('GUARDIAN_API_KEY', 'test')  # Free tier
        
    def fetch_news(self, query='technology', max_articles=20):
        """
        Fetch news from multiple sources with fallback
        Returns list of articles with full content when available
        """
        articles = []
        
        # Try each source in order
        sources = [
            self._fetch_from_guardian,
            self._fetch_from_newsapi,
        ]
        
        for fetch_method in sources:
            try:
                print(f"Trying {fetch_method.__name__}...")
                fetched = fetch_method(query, max_articles)
                if fetched:
                    articles.extend(fetched)
                    print(f"✅ Got {len(fetched)} articles from {fetch_method.__name__}")
                    if len(articles) >= max_articles:
                        break
            except Exception as e:
                print(f"❌ {fetch_method.__name__} failed: {str(e)}")
                continue
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in articles:
            title = article.get('title', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles[:max_articles]
    
    def _fetch_from_guardian(self, query, max_articles):
        """
        Fetch from The Guardian (FREE with full text!)
        No API key needed for basic usage
        """
        url = 'https://content.guardianapis.com/search'
        
        params = {
            'q': query,
            'show-fields': 'bodyText,thumbnail,shortUrl,trailText',
            'page-size': min(max_articles, 50),
            'order-by': 'newest',
            'api-key': self.guardian_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        for item in data.get('response', {}).get('results', []):
            fields = item.get('fields', {})
            
            article = {
                'title': item.get('webTitle', 'No Title'),
                'description': fields.get('trailText', 'No description available'),
                'content': fields.get('bodyText', ''),  # FULL TEXT!
                'url': fields.get('shortUrl', item.get('webUrl', '')),
                'urlToImage': fields.get('thumbnail', ''),
                'publishedAt': item.get('webPublicationDate', ''),
                'source': {'name': 'The Guardian'},
                'has_full_content': True  # Flag for full content
            }
            articles.append(article)
        
        return articles
    
    def _fetch_from_newsapi(self, query, max_articles):
        """
        Fetch from NewsAPI (your existing source)
        No full text, but good for headlines
        """
        if not self.newsapi_key:
            return []
        
        url = 'https://newsapi.org/v2/everything'
        
        params = {
            'q': query,
            'sortBy': 'publishedAt',
            'pageSize': max_articles,
            'apiKey': self.newsapi_key,
            'language': 'en'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        for item in data.get('articles', []):
            article = {
                'title': item.get('title', 'No Title'),
                'description': item.get('description', 'No description available'),
                'content': item.get('content', ''),  # Limited content
                'url': item.get('url', ''),
                'urlToImage': item.get('urlToImage', ''),
                'publishedAt': item.get('publishedAt', ''),
                'source': item.get('source', {}),
                'has_full_content': False  # No full content
            }
            articles.append(article)
        
        return articles
    
    def get_article_preview(self, article, max_length=300):
        """
        Get preview text for article
        Uses full content if available, otherwise description
        """
        if article.get('has_full_content') and article.get('content'):
            # Has full text - create preview
            content = article['content']
            if len(content) > max_length:
                return content[:max_length] + '...'
            return content
        else:
            # No full text - use description
            description = article.get('description', '')
            if len(description) > max_length:
                return description[:max_length] + '...'
            return description
    
    def has_full_article(self, article):
        """Check if article has full text content"""
        return article.get('has_full_content', False)


class ArticleReader:
    """
    Read full article content
    """
    
    @staticmethod
    def get_full_text(article):
        """
        Get full article text if available
        Returns tuple: (has_full_text, content)
        """
        if article.get('has_full_content'):
            content = article.get('content', '')
            if content:
                return True, content
        
        return False, "Full article not available. Click 'Open in Browser' to read more."
    
    @staticmethod
    def format_article_for_display(article):
        """
        Format article for reading
        """
        title = article.get('title', 'No Title')
        source = article.get('source', {}).get('name', 'Unknown Source')
        published = article.get('publishedAt', '')
        
        # Parse date
        try:
            date_obj = datetime.fromisoformat(published.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%B %d, %Y at %I:%M %p')
        except:
            formatted_date = 'Recently'
        
        has_full, content = ArticleReader.get_full_text(article)
        
        formatted = f"""
{'='*60}
{title}
{'='*60}

Source: {source}
Published: {formatted_date}

{'─'*60}

{content}

{'='*60}
"""
        return formatted, has_full