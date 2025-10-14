from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import jwt
from datetime import datetime, timedelta
from flask import current_app

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship
    feedbacks = db.relationship('Feedback', backref='author', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self, expires_in=3600):
        return jwt.encode(
            {
                'user_id': self.id,
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'role': self.role
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return User.query.get(data['user_id'])
        except:
            return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.email} - {self.role}>'

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
    
    # New field for user association (nullable for guest submissions)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
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
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'is_owner': False  # Will be set by API based on current user
        }
    
    def __repr__(self):
        return f'<Feedback {self.id} - {self.sentiment} ({self.analysis_method})>'