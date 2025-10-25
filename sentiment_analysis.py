from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FixedSentimentAnalyzer:
    def __init__(self):
        try:
            self.sia = SentimentIntensityAnalyzer()
            logger.info("NLTK VADER sentiment analyzer initialized successfully")
        except Exception as e:
            logger.warning(f"VADER initialization failed: {e}")
            self.sia = None
    
    def analyze_with_textblob(self, text):
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
                
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': abs(polarity),
                'method': 'textblob'
            }
        except Exception as e:
            logger.error(f"TextBlob analysis failed: {e}")
            return self.fallback_analysis(text)
    
    def analyze_with_vader(self, text):
        """Analyze sentiment using VADER"""
        if not self.sia:
            return self.analyze_with_textblob(text)
        
        try:
            scores = self.sia.polarity_scores(text)
            compound = scores['compound']
            
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
                
            return {
                'sentiment': sentiment,
                'polarity': compound,
                'subjectivity': 1 - scores['neu'],
                'confidence': abs(compound),
                'method': 'vader'
            }
        except Exception as e:
            logger.error(f"VADER analysis failed: {e}")
            return self.analyze_with_textblob(text)
    
    def fallback_analysis(self, text):
        """Simple fallback sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'poor', 'disappointing']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            polarity = 0.5
        elif negative_count > positive_count:
            sentiment = 'negative'
            polarity = -0.5
        else:
            sentiment = 'neutral'
            polarity = 0
            
        return {
            'sentiment': sentiment,
            'polarity': polarity,
            'subjectivity': 0.5,
            'confidence': 0.5,
            'method': 'fallback'
        }
    
    def clean_text(self, text):
        """Clean and preprocess text"""
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text.lower()
    
    def analyze_sentiment(self, text):
        """Main sentiment analysis method"""
        cleaned_text = self.clean_text(text)
        
        # Try VADER first, then TextBlob, then fallback
        try:
            if self.sia:
                result = self.analyze_with_vader(cleaned_text)
            else:
                result = self.analyze_with_textblob(cleaned_text)
        except Exception as e:
            logger.error(f"All sentiment analysis methods failed: {e}")
            result = self.fallback_analysis(cleaned_text)
        
        result['cleaned_text'] = cleaned_text
        return result

# Global analyzer instance
analyzer = FixedSentimentAnalyzer()

def analyze_sentiment(text):
    """Convenience function to analyze sentiment"""
    return analyzer.analyze_sentiment(text)