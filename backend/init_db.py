#!/usr/bin/env python3
"""
Database initialization script for Smart Feedback System
Run this once to set up the database with admin user
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Feedback
from config import Config
from datetime import datetime

def init_database():
    with app.app_context():
        print("🔄 Initializing database...")
        
        # Drop all tables to start fresh (removes old schema)
        db.drop_all()
        print("✅ Dropped existing tables")
        
        # Create all tables with new schema
        db.create_all()
        print("✅ Created new tables with updated schema")
        
        # Check if admin user exists
        admin_user = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
        
        if not admin_user:
            # Create admin user
            admin_user = User(
                email=Config.ADMIN_EMAIL,
                role='admin'
            )
            admin_user.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created:")
            print(f"   Email: {Config.ADMIN_EMAIL}")
            print(f"   Password: {Config.ADMIN_PASSWORD}")
            print("   Please change the password after first login!")
        else:
            print("✅ Admin user already exists")
        
        # Count existing feedbacks
        feedback_count = Feedback.query.count()
        print(f"📊 Existing feedbacks in database: {feedback_count}")
        
        print("\n🎉 Database initialization completed!")
        print("You can now run the application with: python app.py")

if __name__ == '__main__':
    init_database()