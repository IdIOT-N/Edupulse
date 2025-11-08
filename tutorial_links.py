"""
Tutorial Link Manager
Provides relevant learning resources for articles
"""

import re
from urllib.parse import quote_plus


class TutorialLinkManager:
    """Manages tutorial links for educational content"""
    
    def __init__(self):  # FIXED: Double underscores
        # Educational keywords that indicate learning content
        self.educational_keywords = {
            'learn', 'tutorial', 'course', 'education', 'study', 'training',
            'guide', 'teaching', 'lesson', 'university', 'college', 'school',
            'research', 'science', 'technology', 'programming', 'coding',
            'development', 'engineering', 'mathematics', 'physics', 'chemistry',
            'biology', 'history', 'language', 'skill', 'knowledge'
        }
        
        # Non-educational keywords (news, politics, etc)
        self.non_educational_keywords = {
            'politics', 'election', 'war', 'crime', 'murder', 'death',
            'scandal', 'controversy', 'celebrity', 'gossip', 'sports',
            'weather', 'traffic', 'stock', 'market crash', 'lawsuit'
        }
        
        # Tutorial platforms by topic
        self.tutorial_platforms = {
            'programming': [
                'https://www.freecodecamp.org/learn',
                'https://www.codecademy.com',
                'https://www.w3schools.com'
            ],
            'science': [
                'https://www.khanacademy.org/science',
                'https://www.coursera.org',
                'https://www.edx.org'
            ],
            'technology': [
                'https://www.udemy.com',
                'https://www.pluralsight.com',
                'https://www.linkedin.com/learning'
            ],
            'general': [
                'https://www.youtube.com/results?search_query=',
                'https://www.coursera.org',
                'https://www.khanacademy.org'
            ]
        }
    
    def should_show_learn_button(self, article):
        """Determine if article is educational and should show Learn button"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = article.get('content', '').lower()
        
        full_text = f"{title} {description} {content}"
        
        # Count educational keywords with boosted scoring
        educational_score = 0
        for keyword in self.educational_keywords:
            if keyword in full_text:
                if keyword in title:  # Extra weight for keywords in title
                    educational_score += 2
                else:
                    educational_score += 1
        
        # Show Learn button if educational score is high enough
        if educational_score >= 2:
            print(f"✅ Learn button - educational score: {educational_score}")
            return True
        
        print(f"❌ No Learn button - educational score too low: {educational_score}")
        return False
    
    def get_tutorial_link(self, article):
        """Generate relevant tutorial link based on article topic"""
        title = article.get('title', '')
        description = article.get('description', '')
        
        # Detect topic
        topic = self.detect_topic(title, description)
        
        # Get search query
        search_query = self.extract_key_terms(title)
        
        # Generate YouTube tutorial link (most comprehensive)
        youtube_search = f"https://www.youtube.com/results?search_query={quote_plus(search_query + ' tutorial')}"
        
        return youtube_search
    
    def detect_topic(self, title, description):
        """Detect main topic of article"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['python', 'javascript', 'java', 'code', 'programming']):
            return 'programming'
        elif any(word in text for word in ['physics', 'chemistry', 'biology', 'science']):
            return 'science'
        elif any(word in text for word in ['ai', 'machine learning', 'technology', 'computer']):
            return 'technology'
        else:
            return 'general'
    
    def extract_key_terms(self, title):
        """Extract key terms for search query"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        words = re.findall(r'\w+', title.lower())
        key_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Return top 3 words
        return ' '.join(key_words[:3])
    
    def get_coursera_link(self, topic):
        """Get Coursera link for topic"""
        return f"https://www.coursera.org/search?query={quote_plus(topic)}"
    
    def get_khan_academy_link(self, topic):
        """Get Khan Academy link"""
        return f"https://www.khanacademy.org/search?page_search_query={quote_plus(topic)}"
    
    def get_youtube_playlist(self, topic):
        """Get YouTube educational playlist"""
        return f"https://www.youtube.com/results?search_query={quote_plus(topic + ' full course')}&sp=EgIQAw%253D%253D"