#!/usr/bin/env python3
"""
Add test feedback data
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Feedback, User
from sentiment_analysis import analyze_sentiment

def add_test_feedbacks():
    with app.app_context():
        print("🔄 Adding test feedback data...")
        
        test_data = [
            {
                "name": "Alice Johnson",
                "email": "alice@test.com", 
                "category": "product",
                "rating": 5,
                "message": "Absolutely love this product! The quality is outstanding and it works perfectly. Highly recommended!"
            },
            {
                "name": "Bob Smith",
                "email": "bob@test.com",
                "category": "service", 
                "rating": 4,
                "message": "Good service overall. The support team was helpful and responsive to my questions."
            },
            {
                "name": "Carol Davis",
                "email": "carol@test.com",
                "category": "website",
                "rating": 2, 
                "message": "The website is very slow and difficult to navigate. Needs improvement in user experience."
            },
            {
                "name": "David Wilson",
                "email": "david@test.com",
                "category": "support",
                "rating": 5,
                "message": "Excellent customer support! They went above and beyond to solve my issue quickly."
            },
            {
                "name": "Eva Brown", 
                "email": "eva@test.com",
                "category": "general",
                "rating": 3,
                "message": "It's okay, nothing special. Does the job but could be better with more features."
            },
            {
                "name": "Frank Miller",
                "email": "frank@test.com",
                "category": "product",
                "rating": 1,
                "message": "Terrible product! Stopped working after 2 days. Waste of money, would not recommend to anyone."
            },
            {
                "name": "Grace Lee",
                "email": "grace@test.com", 
                "category": "service",
                "rating": 5,
                "message": "Outstanding service! The team was professional, efficient, and very friendly. Exceeded all expectations!"
            },
            {
                "name": "Henry Taylor",
                "email": "henry@test.com",
                "category": "website", 
                "rating": 4,
                "message": "Nice website design and easy to use. The mobile version works great too."
            }
        ]
        
        added_count = 0
        for i, data in enumerate(test_data):
            # Check if similar feedback already exists by message content
            existing = Feedback.query.filter(
                Feedback.message.like(f"%{data['message'][:30]}%")
            ).first()
            
            if not existing:
                # Analyze sentiment
                sentiment_result = analyze_sentiment(data['message'])
                
                # Create feedback
                feedback = Feedback(
                    name=data['name'],
                    email=data['email'],
                    category=data['category'],
                    rating=data['rating'],
                    message=data['message'],
                    sentiment=sentiment_result['sentiment'],
                    polarity=sentiment_result['polarity'],
                    subjectivity=sentiment_result['subjectivity'],
                    analysis_method=sentiment_result['method'],
                    created_at=datetime.utcnow() - timedelta(hours=i*3)
                )
                
                db.session.add(feedback)
                added_count += 1
                print(f"✅ Added: {data['name']} - Rating: {data['rating']}★ - Sentiment: {sentiment_result['sentiment']}")
            else:
                print(f"⏩ Skipped: {data['name']} (already exists)")
        
        db.session.commit()
        print(f"\n🎉 Added {added_count} new test feedbacks!")
        
        # Show updated stats
        total = Feedback.query.count()
        positive = Feedback.query.filter_by(sentiment='positive').count()
        negative = Feedback.query.filter_by(sentiment='negative').count() 
        neutral = Feedback.query.filter_by(sentiment='neutral').count()
        
        print(f"📊 Database Statistics:")
        print(f"   Total feedbacks: {total}")
        print(f"   Positive: {positive} ({positive/total*100:.1f}%)")
        print(f"   Negative: {negative} ({negative/total*100:.1f}%)")
        print(f"   Neutral:  {neutral} ({neutral/total*100:.1f}%)")

if __name__ == '__main__':
    add_test_feedbacks()