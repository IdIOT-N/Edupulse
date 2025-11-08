"""
Enhanced Summarization Module
Provides smart AI-powered article summarization
"""

import re
from collections import Counter


class ArticleSummarizer:
    """Enhanced extractive summarizer with better logic"""
    
    def __init__(self):  # FIXED: Double underscores on both sides
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'said', 'says'
        }
        
        # Important keywords that boost sentence scores
        self.important_keywords = {
            'new', 'research', 'study', 'discover', 'found', 'reveal', 'show',
            'develop', 'create', 'build', 'launch', 'announce', 'release',
            'important', 'significant', 'major', 'breakthrough', 'innovation',
            'first', 'latest', 'update', 'improve', 'advance', 'technology'
        }
    
    def summarize(self, article, max_sentences=3, max_length=250):
        """Generate an intelligent summary of the article"""
        # Get text content
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        
        # Combine all available text
        full_text = f"{title}. {description}. {content}"
        
        # If text is too short, return as is
        if len(full_text) < 100:
            return full_text[:max_length] + "..." if len(full_text) > max_length else full_text
        
        # Extract sentences
        sentences = self.split_into_sentences(full_text)
        
        if len(sentences) == 0:
            return description[:max_length] + "..." if len(description) > max_length else description
        
        if len(sentences) <= max_sentences:
            summary = ' '.join(sentences)
            return summary[:max_length] + "..." if len(summary) > max_length else summary
        
        # Score sentences intelligently
        scored_sentences = self.score_sentences_advanced(sentences, title)
        
        # Get top sentences
        top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:max_sentences]
        
        # Sort by original order to maintain flow
        top_sentences = sorted(top_sentences, key=lambda x: sentences.index(x[0]))
        
        # Create summary
        summary = ' '.join([sent[0] for sent in top_sentences])
        
        # Ensure summary doesn't exceed max length
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(' ', 1)[0] + "..."
        
        return summary
    
    def split_into_sentences(self, text):
        """Split text into clean sentences"""
        # Split on sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter
        clean_sentences = []
        for sent in sentences:
            sent = sent.strip()
            # Keep sentences with reasonable length
            if len(sent) > 20 and len(sent) < 300:
                clean_sentences.append(sent)
        
        return clean_sentences
    
    def score_sentences_advanced(self, sentences, title=''):
        """Advanced sentence scoring with multiple factors"""
        # Get all words for frequency analysis
        all_words = []
        for sentence in sentences:
            words = self.tokenize(sentence)
            all_words.extend(words)
        
        # Calculate word frequencies
        word_freq = Counter(all_words)
        
        # Remove stop words but keep important ones
        word_freq = {
            word: freq for word, freq in word_freq.items() 
            if word.lower() not in self.stop_words or word.lower() in self.important_keywords
        }
        
        # Boost important keywords
        for word in self.important_keywords:
            if word in word_freq:
                word_freq[word] *= 2
        
        # Extract title keywords for relevance boost
        title_words = set(self.tokenize(title))
        
        # Score each sentence
        scored = []
        for i, sentence in enumerate(sentences):
            words = self.tokenize(sentence)
            
            if len(words) == 0:
                continue
            
            # Base score from word frequency
            base_score = sum(word_freq.get(word, 0) for word in words) / len(words)
            
            # Position bonus (first sentences are often important)
            position_bonus = 1.0 if i < 3 else 0.5
            
            # Title relevance bonus
            title_overlap = len(set(words) & title_words)
            title_bonus = title_overlap * 0.5
            
            # Length penalty (avoid very short or very long sentences)
            length_penalty = 1.0
            if len(words) < 5:
                length_penalty = 0.5
            elif len(words) > 40:
                length_penalty = 0.7
            
            # Important keyword bonus
            keyword_bonus = sum(1 for word in words if word.lower() in self.important_keywords) * 0.3
            
            # Calculate final score
            final_score = (base_score + position_bonus + title_bonus + keyword_bonus) * length_penalty
            
            scored.append((sentence, final_score))
        
        return scored
    
    def tokenize(self, text):
        """Tokenize text into clean words"""
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.lower().split()
        
        # Filter short words and numbers-only
        words = [w for w in words if len(w) > 2 and not w.isdigit()]
        
        return words
    
    def get_key_phrases(self, article, num_phrases=5):
        """Extract key phrases from article"""
        content = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
        
        # Extract bigrams and trigrams
        words = self.tokenize(content)
        
        phrases = []
        for i in range(len(words) - 1):
            if words[i] not in self.stop_words:
                bigram = f"{words[i]} {words[i+1]}"
                phrases.append(bigram)
        
        # Count phrase frequencies
        phrase_freq = Counter(phrases)
        
        # Return top phrases
        return [phrase for phrase, _ in phrase_freq.most_common(num_phrases)]