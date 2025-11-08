"""
EduPulse - Educational News Aggregator
Main Application File
"""

import os
from dotenv import load_dotenv
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import requests
import json
from datetime import datetime
import webbrowser

# Import custom modules
from field_selection import FieldSelectionScreen
from bookmarking import BookmarkManager
from summarization import ArticleSummarizer
from notifications import NotificationManager
from tutorial_links import TutorialLinkManager
from cache_manager import CacheManager
from rss_fetcher import RSSNewsFetcher

# Load environment variables
load_dotenv()

class NewsScreen(Screen):
    """Main news feed screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.news_fetcher = RSSNewsFetcher()
        self.bookmark_manager = BookmarkManager()
        self.summarizer = ArticleSummarizer()
        self.tutorial_manager = TutorialLinkManager()
        self.cache_manager = CacheManager()
        self.current_articles = []
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical')
        
        # Header
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Content area
        self.content_scroll = ScrollView()
        self.content_layout = GridLayout(cols=1, spacing=15, padding=20, size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        self.content_scroll.add_widget(self.content_layout)
        main_layout.add_widget(self.content_scroll)
        
        # Bottom navigation
        nav_bar = self.create_navigation_bar()
        main_layout.add_widget(nav_bar)
        
        self.add_widget(main_layout)
        
        # Load news on screen load
        Clock.schedule_once(lambda dt: self.load_news(), 0.5)
    
    def create_header(self):
        """Create modern header with gradient"""
        header = BoxLayout(orientation='horizontal', size_hint_y=0.12, padding=20, spacing=15)
        
        # Gradient background
        with header.canvas.before:
            Color(0.08, 0.08, 0.15, 1)
            self.header_rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[15])
        
        header.bind(pos=lambda instance, value: setattr(self.header_rect, 'pos', instance.pos))
        header.bind(size=lambda instance, value: setattr(self.header_rect, 'size', instance.size))
        
        # Logo and title
        title_box = BoxLayout(orientation='horizontal', size_hint_x=0.7, spacing=10)
        
        logo = Label(
            text='🎓',
            font_size='36sp',
            size_hint_x=0.2
        )
        
        title_text = Label(
            text='[b]EduPulse[/b]\n[size=12sp]Stay Informed[/size]',
            markup=True,
            font_size='24sp',
            color=(0.3, 0.85, 1, 1),
            size_hint_x=0.8,
            halign='left'
        )
        title_text.bind(size=title_text.setter('text_size'))
        
        title_box.add_widget(logo)
        title_box.add_widget(title_text)
        
        # Refresh button with icon
        refresh_btn = Button(
            text='🔄 Refresh',
            size_hint_x=0.3,
            background_color=(0.2, 0.7, 1, 1),
            color=(1, 1, 1, 1),
            font_size='15sp'
        )
        refresh_btn.bind(on_press=lambda x: self.load_news())
        
        header.add_widget(title_box)
        header.add_widget(refresh_btn)
        
        return header
    
    def create_navigation_bar(self):
        """Create bottom navigation bar"""
        nav = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=5, padding=5)
        
        with nav.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.nav_rect = RoundedRectangle(pos=nav.pos, size=nav.size)
        
        nav.bind(pos=lambda instance, value: setattr(self.nav_rect, 'pos', instance.pos))
        nav.bind(size=lambda instance, value: setattr(self.nav_rect, 'size', instance.size))
        
        # Navigation buttons
        buttons = [
            ('🏠 Home', 'news'),
            ('📚 Bookmarks', 'bookmarks'),
            ('⚙ Settings', 'settings')
        ]
        
        for text, screen in buttons:
            btn = Button(
                text=text,
                background_color=(0, 0.5, 0.9, 1) if screen == 'news' else (0.2, 0.2, 0.3, 1)
            )
            btn.bind(on_press=lambda x, s=screen: self.navigate_to(s))
            nav.add_widget(btn)
        
        return nav
    
    def navigate_to(self, screen_name):
        """Navigate to different screens"""
        self.manager.current = screen_name
    
    def load_news(self, force_refresh=False):
        """Fetch news articles from multiple sources"""
        self.content_layout.clear_widgets()
        
        # Show loading message
        loading = Label(
            text='🔄 Loading latest news...',
            font_size='18sp',
            color=(1, 1, 1, 0.7),
            size_hint_y=None,
            height=100
        )
        self.content_layout.add_widget(loading)
        
        # Get user's field preference
        field_category = self.get_user_field()
        
        # Only use cache if not forcing refresh and cache exists
        if not force_refresh:
            cached_articles = self.cache_manager.load_cache()
            if cached_articles:
                print("📦 Loading from cache...")
                self.display_articles(cached_articles)
                return
        
        try:
            # Get search query based on field
            query = self.get_search_query(field_category)
            print(f"🔍 Fetching news for field: {field_category}")
            
            # Use multi-source fetcher
            articles = self.news_fetcher.fetch_news(query, max_results=20)
            
            if articles:
                # Cache the articles
                self.cache_manager.save_cache(articles, {'field': field_category})
                self.display_articles(articles)
            else:
                self.show_error("No articles found. Try selecting a different field.")
        
        except Exception as e:
            print(f"Error: {e}")
            self.show_error("Failed to load news. Check your internet connection.")
    
    def get_user_field(self):
        """Get user's selected field from preferences"""
        try:
            with open('user_preferences.json', 'r') as f:
                prefs = json.load(f)
                return prefs.get('field', 'technology')
        except:
            return 'technology'
    
    def get_search_query(self, field):
        """Get search query based on field"""
        queries = {
            'Artificial Intelligence': 'artificial intelligence OR AI OR machine learning',
            'Finance & Economics': 'finance OR economics OR business OR stock market',
            'Science & Research': 'science OR research OR scientific discovery',
            'Technology & Engineering': 'technology OR engineering OR innovation',
            'Health & Medicine': 'health OR medicine OR medical research OR healthcare',
            'Space & Astronomy': 'space OR astronomy OR NASA OR space exploration',
            # Default fallback
            'technology': 'technology OR innovation'
        }
        return queries.get(field, field)  # Use the field itself as query if not in mapping
    def display_articles(self, articles):
        """Display articles in the UI"""
        self.content_layout.clear_widgets()
        self.current_articles = articles
        
        if not articles:
            self.show_error("No articles available")
            return
        
        for article in articles:
            article_widget = self.create_article_widget(article)
            self.content_layout.add_widget(article_widget)
    
    def create_article_widget(self, article):
        """Create modern article card with better design"""
        article_box = BoxLayout(orientation='vertical', size_hint_y=None, height=220, padding=18, spacing=12)
        
        # Modern card background with shadow effect
        with article_box.canvas.before:
            Color(0.12, 0.12, 0.18, 1)
            rect = RoundedRectangle(pos=article_box.pos, size=article_box.size, radius=[12])
            # Border/accent
            Color(0.2, 0.7, 1, 0.3)
            border = RoundedRectangle(pos=article_box.pos, size=article_box.size, radius=[12])
        
        def update_graphics(instance, value):
            rect.pos = (instance.x, instance.y)
            rect.size = instance.size
            border.pos = (instance.x - 1, instance.y - 1)
            border.size = (instance.width + 2, instance.height + 2)
        
        article_box.bind(pos=update_graphics, size=update_graphics)
        
        # Source badge
        source_name = article.get('source', {}).get('name', 'Unknown')
        source_label = Label(
            text=f"📰 {source_name}",
            font_size='11sp',
            color=(0.5, 0.8, 1, 0.8),
            size_hint_y=0.12,
            halign='left'
        )
        source_label.bind(size=source_label.setter('text_size'))
        
        # Title with better formatting
        title = Label(
            text=f"[b]{article.get('title', 'No Title')}[/b]",
            markup=True,
            font_size='15sp',
            color=(1, 1, 1, 0.95),
            size_hint_y=0.28,
            halign='left',
            valign='top'
        )
        title.bind(size=title.setter('text_size'))
        
        # Smart summary
        summary_text = self.summarizer.summarize(article, max_sentences=2, max_length=180)
        summary = Label(
            text=summary_text,
            font_size='12sp',
            color=(1, 1, 1, 0.65),
            size_hint_y=0.32,
            halign='left',
            valign='top'
        )
        summary.bind(size=summary.setter('text_size'))
        
        # Action buttons with icons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.28, spacing=8)
        
        # Read button
        read_btn = Button(
            text='📖 Read',
            background_color=(0.2, 0.65, 1, 1),
            font_size='13sp'
        )
        read_btn.bind(on_press=lambda x: self.open_article(article))
        
        # Bookmark button
        is_bookmarked = self.bookmark_manager.is_bookmarked(article.get('url'))
        bookmark_btn = Button(
            text='⭐' if not is_bookmarked else '✓',
            background_color=(1, 0.6, 0.1, 1) if not is_bookmarked else (0.2, 0.8, 0.3, 1),
            font_size='13sp'
        )
        bookmark_btn.bind(on_press=lambda x: self.toggle_bookmark(article, bookmark_btn))
        
        btn_layout.add_widget(read_btn)
        btn_layout.add_widget(bookmark_btn)
        
        # Only add Learn button if content is educational
        if self.tutorial_manager.should_show_learn_button(article):
            tutorial_btn = Button(
                text='📚 Learn',
                background_color=(0.3, 0.75, 0.3, 1),
                font_size='13sp'
            )
            tutorial_btn.bind(on_press=lambda x: self.open_tutorial(article))
            btn_layout.add_widget(tutorial_btn)
        
        article_box.add_widget(source_label)
        article_box.add_widget(title)
        article_box.add_widget(summary)
        article_box.add_widget(btn_layout)
        
        return article_box
    
    def open_article(self, article):
        """Open article in browser"""
        url = article.get('url')
        if url:
            webbrowser.open(url)
    
    def toggle_bookmark(self, article, button):
        """Toggle bookmark with visual feedback"""
        if self.bookmark_manager.is_bookmarked(article.get('url')):
            self.bookmark_manager.remove_bookmark(article.get('url'))
            button.text = '⭐'
            button.background_color = (1, 0.6, 0.1, 1)
        else:
            self.bookmark_manager.add_bookmark(article)
            button.text = '✓'
            button.background_color = (0.2, 0.8, 0.3, 1)
    
    def open_tutorial(self, article):
        """Open tutorial link"""
        link = self.tutorial_manager.get_tutorial_link(article)
        webbrowser.open(link)
    
    def show_error(self, message):
        """Display error message"""
        self.content_layout.clear_widgets()
        error_label = Label(
            text=message,
            font_size='16sp',
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=100
        )
        self.content_layout.add_widget(error_label)


class BookmarksScreen(Screen):
    """Bookmarks screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bookmark_manager = BookmarkManager()
        
        main_layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=15)
        title = Label(text='[b]📚 Bookmarks[/b]', markup=True, font_size='28sp', color=(1, 0.5, 0, 1))
        back_btn = Button(text='← Back', size_hint_x=0.3, background_color=(0.3, 0.3, 0.4, 1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'news'))
        
        header.add_widget(title)
        header.add_widget(back_btn)
        main_layout.add_widget(header)
        
        # Content
        self.scroll_view = ScrollView()
        self.content_layout = GridLayout(cols=1, spacing=15, padding=20, size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        self.scroll_view.add_widget(self.content_layout)
        main_layout.add_widget(self.scroll_view)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Load bookmarks when screen is entered"""
        self.load_bookmarks()
    
    def load_bookmarks(self):
        """Display all bookmarks"""
        self.content_layout.clear_widgets()
        bookmarks = self.bookmark_manager.get_bookmarks()
        
        if not bookmarks:
            no_bookmarks = Label(
                text='No bookmarks yet!\nStart saving articles from the home screen.',
                font_size='16sp',
                color=(1, 1, 1, 0.5),
                halign='center'
            )
            self.content_layout.add_widget(no_bookmarks)
            return
        
        for bookmark in bookmarks:
            bookmark_widget = self.create_bookmark_widget(bookmark)
            self.content_layout.add_widget(bookmark_widget)
    
    def create_bookmark_widget(self, bookmark):
        """Create widget for each bookmark"""
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=150, padding=15, spacing=10)
        
        with box.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[10])
        
        box.bind(
            pos=lambda instance, value, r=rect: setattr(r, 'pos', instance.pos),
            size=lambda instance, value, r=rect: setattr(r, 'size', instance.size)
        )
        
        title = Label(text=f"[b]{bookmark.get('title')}[/b]", markup=True, font_size='14sp', size_hint_y=0.5)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.5, spacing=10)
        
        open_btn = Button(text='Open', background_color=(0, 0.6, 1, 1))
        open_btn.bind(on_press=lambda x: webbrowser.open(bookmark.get('url')))
        
        delete_btn = Button(text='Delete', background_color=(1, 0.3, 0.3, 1))
        delete_btn.bind(on_press=lambda x: self.delete_bookmark(bookmark))
        
        btn_layout.add_widget(open_btn)
        btn_layout.add_widget(delete_btn)
        
        box.add_widget(title)
        box.add_widget(btn_layout)
        
        return box
    
    def delete_bookmark(self, bookmark):
        """Delete a bookmark"""
        self.bookmark_manager.remove_bookmark(bookmark.get('url'))
        self.load_bookmarks()


class SettingsScreen(Screen):
    """Settings screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        title = Label(text='[b]⚙ Settings[/b]', markup=True, font_size='28sp')
        back_btn = Button(text='← Back', size_hint_x=0.3, background_color=(0.3, 0.3, 0.4, 1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'news'))
        
        header.add_widget(title)
        header.add_widget(back_btn)
        
        # Settings options
        settings_box = BoxLayout(orientation='vertical', spacing=15, size_hint_y=0.8)
        
        change_field_btn = Button(
            text='Change Interest Field',
            size_hint_y=None,
            height=60,
            background_color=(0, 0.6, 1, 1)
        )
        change_field_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'field_selection'))
        
        clear_cache_btn = Button(
            text='Clear Cache',
            size_hint_y=None,
            height=60,
            background_color=(1, 0.5, 0, 1)
        )
        clear_cache_btn.bind(on_press=self.clear_cache)
        
        about_btn = Button(
            text='About EduPulse',
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        
        settings_box.add_widget(change_field_btn)
        settings_box.add_widget(clear_cache_btn)
        settings_box.add_widget(about_btn)
        
        main_layout.add_widget(header)
        main_layout.add_widget(settings_box)
        
        self.add_widget(main_layout)
    
    def clear_cache(self, instance):
        """Clear cached articles and reload news"""
        cache_manager = CacheManager()
        cache_manager.clear_cache()  # Use clear_cache instead of save_cache([])
        
        # Force reload news in NewsScreen
        news_screen = self.manager.get_screen('news')
        news_screen.load_news()


class EduPulseApp(App):
    """Main application class"""
    
    def build(self):
        # Initialize notification manager
        self.notification_manager = NotificationManager()
        self.notification_manager.schedule_notifications()
        
        # Screen manager
        sm = ScreenManager(transition=SlideTransition())
        
        # Add screens
        sm.add_widget(FieldSelectionScreen(name='field_selection'))
        sm.add_widget(NewsScreen(name='news'))
        sm.add_widget(BookmarksScreen(name='bookmarks'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        # Check if user has selected a field
        if os.path.exists('user_preferences.json'):
            sm.current = 'news'
        else:
            sm.current = 'field_selection'
        
        return sm
    
    def on_stop(self):
        """Cleanup on app close"""
        self.notification_manager.stop_notifications()


if __name__ == '__main__':
    EduPulseApp().run()