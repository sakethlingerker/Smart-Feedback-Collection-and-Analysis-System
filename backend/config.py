from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///feedback.db")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email settings
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    # Hugging Face model for sentiment analysis
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL")
    
    # Threshold for detecting negative sentiment
    NEGATIVE_SENTIMENT_THRESHOLD = float(os.getenv("NEGATIVE_SENTIMENT_THRESHOLD", 0.0))
    
    # Debug mode
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # Admin user (for initial setup)
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@feedback.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")