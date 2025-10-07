import matplotlib
# Set the backend to Agg (non-interactive) BEFORE importing pyplot
matplotlib.use('Agg')  # Add this line first
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS
import io
import base64
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class WordCloudGenerator:
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))
        # Add custom stopwords
        self.stopwords.update(['thank', 'thanks', 'please', 'would', 'could', 'like', 'service', 'product', 'really', 'get'])
    
    def generate_wordcloud(self, texts, width=800, height=400):
        """Generate wordcloud from list of texts"""
        if not texts:
            return None
        
        # Combine all texts
        combined_text = ' '.join(texts)
        
        if not combined_text.strip():
            return None
        
        # Generate wordcloud
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color='white',
            stopwords=self.stopwords,
            max_words=100,
            colormap='viridis',
            contour_width=1,
            contour_color='steelblue',
            relative_scaling=0.5
        ).generate(combined_text)
        
        # Convert to base64
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        
        img_io = io.BytesIO()
        plt.savefig(img_io, format='PNG', bbox_inches='tight', pad_inches=0, dpi=150)
        img_io.seek(0)
        img_data = base64.b64encode(img_io.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_data}"
    
    def get_top_words(self, texts, top_n=20):
        """Get most frequent words from texts"""
        if not texts:
            return []
        
        combined_text = ' '.join(texts)
        
        # Tokenize and clean words
        words = word_tokenize(combined_text.lower())
        
        # Filter words
        filtered_words = [
            word for word in words 
            if (word not in self.stopwords and 
                word not in string.punctuation and
                len(word) > 2 and
                word.isalpha())
        ]
        
        word_freq = Counter(filtered_words)
        return word_freq.most_common(top_n)

# Global wordcloud generator
wordcloud_gen = WordCloudGenerator()