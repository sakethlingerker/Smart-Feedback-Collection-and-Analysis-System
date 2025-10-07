from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=False, default='general')
    rating = db.Column(db.Integer, nullable=False, default=0)
    message = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    polarity = db.Column(db.Float, nullable=False)
    subjectivity = db.Column(db.Float, nullable=False)
    analysis_method = db.Column(db.String(20), default='textblob')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'category': self.category,
            'rating': self.rating,
            'message': self.message,
            'sentiment': self.sentiment,
            'polarity': round(self.polarity, 3),
            'subjectivity': round(self.subjectivity, 3),
            'analysis_method': self.analysis_method,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Feedback {self.id} - {self.sentiment} ({self.analysis_method})>'