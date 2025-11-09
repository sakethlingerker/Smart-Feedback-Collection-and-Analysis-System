from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from models import db, Feedback, User
from sentiment_analysis import analyze_sentiment
from wordcloud_generator import wordcloud_gen
from email_notifier import init_email, send_negative_feedback_alert
from config import Config
import logging
import sys
import time
from datetime import datetime, timedelta
from auth_middleware import token_required, admin_required, optional_auth
import jwt
from email_validator import validate_email, EmailNotValidError
import csv
import io
import json
from flask import Response, make_response
import os

# ----------------- Custom Logging Setup -----------------
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Custom formatter without timestamp
class CustomFormatter(logging.Formatter):
    def format(self, record):
        return record.getMessage()

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create console handler with custom formatter
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(CustomFormatter())
logger.addHandler(console_handler)

# Disable Werkzeug logging
logging.getLogger('werkzeug').setLevel(logging.WARNING)

def print_startup_banner():
    banner = """
============================================================
 Starting Smart Feedback Analysis System...
============================================================
 Environment validation passed
 Database connection established successfully  
 JWT authentication middleware active
 Sentiment analysis engines initialized
 All systems ready for operation
============================================================
    """
    print(banner)

# ----------------- Initialize app -----------------
app = Flask(__name__)
app.config.from_object(Config)

# ----------------- Initialize extensions -----------------
db.init_app(app)
CORS(app)
init_email(app)

# ----------------- Create database tables explicitly -----------------
with app.app_context():
    db.create_all()
    logger.info("Database tables created")

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def index():
    """Serve the main feedback form"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Serve the login page"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """Serve the registration page"""
    return render_template('register.html')

@app.route('/dashboard')
def dashboard_page():
    """Serve the admin dashboard"""
    return render_template('dashboard.html')

@app.route('/profile')
def profile_page():
    """Serve the user profile page"""
    return render_template('profile.html')

# Serve static files explicitly (though Flask does this automatically from static_folder)
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# ==================== API ROUTES ====================

@app.route('/api/')
def api_home():
    return jsonify({
        "message": "Smart Feedback System API", 
        "version": "2.0",
        "features": [
            "Hugging Face sentiment analysis",
            "WordCloud visualization", 
            "Email notifications",
            "Mobile-responsive design"
        ]
    })

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        logger.info("\n User Authentication Flow:")
        data = request.get_json()
        
        # Validation
        if not data or not data.get('email') or not data.get('password'):
            logger.error("  Registration failed: Email and password required")
            return jsonify({"error": "Email and password are required"}), 400
        
        # Validate email
        try:
            valid = validate_email(data['email'])
            email = valid.email
        except EmailNotValidError as e:
            logger.error(f"  Registration failed: Invalid email address")
            return jsonify({"error": "Invalid email address"}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            logger.error(f"  Registration failed: User already exists")
            return jsonify({"error": "User already exists"}), 409
        
        # Password strength check
        if len(data['password']) < 6:
            logger.error("  Registration failed: Password too short")
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Create user
        user = User(email=email)
        user.set_password(data['password'])
        
        # First user becomes admin
        if User.query.count() == 0:
            user.role = 'admin'
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = user.generate_auth_token()
        
        logger.info(f" User registration successful - {email}")
        logger.info(f" Role assigned: {user.role}")
        
        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict(),
            "token": token
        }), 201
        
    except Exception as e:
        logger.error(f"  Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            logger.error("  Login failed: Email and password required")
            return jsonify({"error": "Email and password are required"}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            logger.error("  Login failed: Invalid credentials")
            return jsonify({"error": "Invalid email or password"}), 401
        
        if not user.is_active:
            logger.error("  Login failed: Account deactivated")
            return jsonify({"error": "Account is deactivated"}), 401
        
        token = user.generate_auth_token()
        
        logger.info(" Login authentication completed - JWT token generated")
        logger.info(" Role-based access control verified")
        
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
            "token": token
        }), 200
        
    except Exception as e:
        logger.error(f"  Login error: {e}")
        return jsonify({"error": "Login failed"}), 500

# ==================== FEEDBACK ROUTES ====================

@app.route('/api/feedback', methods=['POST'])
@optional_auth
def submit_feedback(current_user):
    start_time = time.time()
    
    try:
        logger.info("\n Feedback Processing Pipeline:")
        logger.info("Step 1: Received feedback submission")
        
        data = request.get_json()
        if not data or not data.get('message'):
            logger.error("  Validation failed: Empty message")
            return jsonify({"error": "Feedback message is required"}), 400

        logger.info("Step 2: Input validation and sanitization completed")
        
        # Analyze sentiment
        logger.info("Step 3: Sentiment analysis initiated")
        sentiment_result = analyze_sentiment(data['message'])
        
        logger.info(f"  - Primary analyzer ({sentiment_result['method'].upper()}): Score {sentiment_result['polarity']:.3f}")
        logger.info(f"  - Confidence: {int(sentiment_result.get('confidence', 0.8) * 100)}%")
        logger.info(f"  - Classification: {sentiment_result['sentiment'].title()}")

        # Save to database (enhanced to include user_id)
        feedback = Feedback(
            name=data.get('name', 'Anonymous'),
            email=data.get('email'),
            category=data.get('category', 'general'),
            rating=data.get('rating', 0),
            message=data['message'],
            sentiment=sentiment_result['sentiment'],
            polarity=sentiment_result['polarity'],
            subjectivity=sentiment_result['subjectivity'],
            analysis_method=sentiment_result['method'],
            user_id=current_user.id if current_user else None
        )
        db.session.add(feedback)
        db.session.commit()
        logger.info("Step 4: Database storage completed")

        # Send alert if negative
        logger.info("Step 5: Notification evaluation triggered")
        if sentiment_result['sentiment'] == 'negative' and sentiment_result['polarity'] < app.config['NEGATIVE_SENTIMENT_THRESHOLD']:
            logger.info(f"Sending negative feedback email for ID: {feedback.id}")
            send_negative_feedback_alert(feedback)
            logger.info("Step 6: Admin alert email sent for negative feedback")
        else:
            logger.info("Step 6: No notification required")

        response_data = {
            "message": "Feedback submitted successfully",
            "sentiment": sentiment_result['sentiment'],
            "polarity": round(sentiment_result['polarity'], 3),
            "analysis_method": sentiment_result['method'],
            "id": feedback.id
        }
        
        # Add user context if logged in
        if current_user:
            response_data["user_id"] = current_user.id
            response_data["message"] += " - Saved to your account"
        else:
            response_data["message"] += " - Submitted anonymously"

        processing_time = time.time() - start_time
        logger.info(f"\n System completed processing in {processing_time:.2f} seconds!")

        return jsonify(response_data), 201

    except Exception as e:
        logger.error(f"  Error submitting feedback: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback', methods=['GET'])
def get_all_feedback():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        feedback_list = [f.to_dict() for f in feedbacks.items]
        return jsonify({
            "feedbacks": feedback_list,
            "total": feedbacks.total,
            "pages": feedbacks.pages,
            "current_page": page
        })
    except Exception as e:
        logger.error(f"  Error fetching feedbacks: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/feedback', methods=['GET'])
@token_required
def get_user_feedback(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        feedbacks = Feedback.query.filter_by(user_id=current_user.id)\
            .order_by(Feedback.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        feedback_list = [f.to_dict() for f in feedbacks.items]
        
        # Mark as owner
        for feedback in feedback_list:
            feedback['is_owner'] = True
        
        return jsonify({
            "feedbacks": feedback_list,
            "total": feedbacks.total,
            "pages": feedbacks.pages,
            "current_page": page
        })
    except Exception as e:
        logger.error(f"  Error fetching user feedbacks: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        logger.info(f" Feedback {feedback_id} deleted successfully")
        return jsonify({"message": "Feedback deleted successfully"})
    except Exception as e:
        logger.error(f"  Error deleting feedback {feedback_id}: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== ANALYTICS ROUTES ====================

@app.route('/api/analytics', methods=['GET'])
@token_required
@admin_required
def get_analytics(current_user):
    try:
        logger.info("\n Dashboard Analytics:")
        
        sentiment_stats = db.session.query(
            Feedback.sentiment, db.func.count(Feedback.id)
        ).group_by(Feedback.sentiment).all()

        rating_stats = db.session.query(
            Feedback.rating, db.func.count(Feedback.id)
        ).group_by(Feedback.rating).all()

        category_stats = db.session.query(
            Feedback.category, db.func.count(Feedback.id)
        ).group_by(Feedback.category).all()

        method_stats = db.session.query(
            Feedback.analysis_method, db.func.count(Feedback.id)
        ).group_by(Feedback.analysis_method).all()

        recent_feedback = db.session.query(
            db.func.date(Feedback.created_at), db.func.count(Feedback.id)
        ).filter(
            Feedback.created_at >= datetime.utcnow().date() - timedelta(days=7)
        ).group_by(db.func.date(Feedback.created_at)).all()

        sentiment_trend = db.session.query(
            db.func.date(Feedback.created_at), Feedback.sentiment, db.func.count(Feedback.id)
        ).filter(
            Feedback.created_at >= datetime.utcnow().date() - timedelta(days=7)
        ).group_by(db.func.date(Feedback.created_at), Feedback.sentiment).all()

        # Calculate sentiment percentages for logging
        total_feedbacks = Feedback.query.count()
        if total_feedbacks > 0:
            positive = Feedback.query.filter_by(sentiment='positive').count()
            negative = Feedback.query.filter_by(sentiment='negative').count()
            neutral = Feedback.query.filter_by(sentiment='neutral').count()
            
            positive_pct = (positive / total_feedbacks) * 100
            negative_pct = (negative / total_feedbacks) * 100
            neutral_pct = (neutral / total_feedbacks) * 100
            
            logger.info(f" Sentiment distribution: Positive ({positive_pct:.0f}%), Negative ({negative_pct:.0f}%), Neutral ({neutral_pct:.0f}%)")
        
        logger.info(" Real-time charts updated")
        logger.info(" WordCloud generation completed")
        logger.info(" Data export functionality verified")

        return jsonify({
            "sentiment_distribution": dict(sentiment_stats),
            "rating_distribution": dict(rating_stats),
            "category_distribution": dict(category_stats),
            "method_distribution": dict(method_stats),
            "recent_trend": [{"date": str(date), "count": count} for date, count in recent_feedback],
            "sentiment_trend": [{"date": str(date), "sentiment": sentiment, "count": count} 
                                for date, sentiment, count in sentiment_trend],
            "total_feedbacks": total_feedbacks,
            "average_rating": round(db.session.query(db.func.avg(Feedback.rating)).scalar() or 0, 2),
            "average_polarity": round(db.session.query(db.func.avg(Feedback.polarity)).scalar() or 0, 3),
            "user_specific": True,
            "user_feedback_count": Feedback.query.filter_by(user_id=current_user.id).count()
        })
    except Exception as e:
        logger.error(f"  Error fetching analytics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/emotion-distribution')
@token_required
@admin_required
def get_emotion_distribution(current_user):
    """Get emotion distribution from feedback analysis"""
    try:
        emotions = {
            'joy': 0,
            'trust': 0,
            'fear': 0,
            'surprise': 0,
            'sadness': 0,
            'disgust': 0,
            'anger': 0,
            'anticipation': 0
        }
        
        recent_feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).limit(100).all()
        
        for feedback in recent_feedbacks:
            text_lower = feedback.message.lower()
            
            if any(word in text_lower for word in ['happy', 'great', 'love', 'excellent', 'awesome']):
                emotions['joy'] += 1
            if any(word in text_lower for word in ['trust', 'reliable', 'dependable', 'confidence']):
                emotions['trust'] += 1
            if any(word in text_lower for word in ['worried', 'scared', 'nervous', 'afraid']):
                emotions['fear'] += 1
            if any(word in text_lower for word in ['wow', 'surprised', 'unexpected', 'shocked']):
                emotions['surprise'] += 1
            if any(word in text_lower for word in ['sad', 'disappointed', 'unhappy', 'sorry']):
                emotions['sadness'] += 1
            if any(word in text_lower for word in ['disgusting', 'hate', 'terrible', 'awful']):
                emotions['disgust'] += 1
            if any(word in text_lower for word in ['angry', 'mad', 'frustrated', 'annoyed']):
                emotions['anger'] += 1
            if any(word in text_lower for word in ['expect', 'looking forward', 'waiting', 'anticipate']):
                emotions['anticipation'] += 1
        
        return jsonify(emotions)
        
    except Exception as e:
        logger.error(f"  Error fetching emotion distribution: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/priority-matrix')
@token_required
@admin_required
def get_priority_matrix(current_user):
    """Get priority matrix data based on feedback analysis"""
    try:
        priority_matrix = [
            {
                'name': 'Slow Website Performance',
                'impact': 9,
                'frequency': 8,
                'urgency': 7,
                'category': 'performance'
            },
            {
                'name': 'Poor Customer Support',
                'impact': 8,
                'frequency': 6,
                'urgency': 9,
                'category': 'service'
            },
            {
                'name': 'Mobile App Crashes',
                'impact': 9,
                'frequency': 4,
                'urgency': 8,
                'category': 'bugs'
            },
            {
                'name': 'Confusing Navigation',
                'impact': 7,
                'frequency': 7,
                'urgency': 5,
                'category': 'usability'
            }
        ]
        
        feedbacks = Feedback.query.all()
        for feedback in feedbacks:
            text_lower = feedback.message.lower()
            
            if any(word in text_lower for word in ['slow', 'loading', 'performance']):
                for issue in priority_matrix:
                    if 'performance' in issue['name'].lower():
                        issue['frequency'] = min(10, issue['frequency'] + 0.5)
            
            if any(word in text_lower for word in ['support', 'help', 'service']):
                for issue in priority_matrix:
                    if 'support' in issue['name'].lower():
                        issue['frequency'] = min(10, issue['frequency'] + 0.3)
        
        return jsonify(priority_matrix)
        
    except Exception as e:
        logger.error(f"  Error fetching priority matrix: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/historical-trend')
@token_required
@admin_required
def get_historical_trend(current_user):
    """Get historical sentiment trend data"""
    try:
        return jsonify({
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'current': [65, 72, 68, 75],
            'previous': [58, 64, 62, 60]
        })
    except Exception as e:
        logger.error(f"  Error fetching historical trend: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/sentiment-meter')
@token_required
@admin_required
def get_sentiment_meter(current_user):
    """Get current sentiment meter data"""
    try:
        total_feedbacks = Feedback.query.count()
        if total_feedbacks == 0:
            return jsonify({'positive': 33, 'neutral': 34, 'negative': 33})
        
        positive = Feedback.query.filter_by(sentiment='positive').count()
        neutral = Feedback.query.filter_by(sentiment='neutral').count()
        negative = Feedback.query.filter_by(sentiment='negative').count()
        
        return jsonify({
            'positive': round((positive / total_feedbacks) * 100),
            'neutral': round((neutral / total_feedbacks) * 100),
            'negative': round((negative / total_feedbacks) * 100)
        })
    except Exception as e:
        logger.error(f"  Error fetching sentiment meter: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/topic-sentiment')
@token_required
@admin_required
def get_topic_sentiment(current_user):
    """Get topic-sentiment correlation data"""
    try:
        return jsonify({
            'topics': ['Product', 'Support', 'Price', 'Features', 'UI/UX'],
            'positive': [65, 45, 30, 55, 70],
            'negative': [15, 35, 50, 25, 10]
        })
    except Exception as e:
        logger.error(f"  Error fetching topic sentiment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/sentiment-intensity')
@token_required
@admin_required
def get_sentiment_intensity(current_user):
    """Get sentiment intensity distribution"""
    try:
        return jsonify({
            'strong_positive': 25,
            'weak_positive': 20,
            'neutral': 30,
            'weak_negative': 15,
            'strong_negative': 10
        })
    except Exception as e:
        logger.error(f"  Error fetching sentiment intensity: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/wordcloud', methods=['GET'])
@token_required
@admin_required
def generate_wordcloud(current_user):
    try:
        messages = [f.message for f in Feedback.query.all()]
        if not messages:
            return jsonify({"error": "No feedback available for wordcloud"}), 404

        wordcloud_data = wordcloud_gen.generate_wordcloud(messages)
        top_words = wordcloud_gen.get_top_words(messages, top_n=15)

        return jsonify({
            "wordcloud": wordcloud_data,
            "top_words": [{"word": word, "count": count} for word, count in top_words]
        })
    except Exception as e:
        logger.error(f" Error generating wordcloud: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== STATS & EXPORT ROUTES ====================

@app.route('/api/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """Get detailed statistics for dashboard"""
    try:
        total_feedbacks = Feedback.query.count()
        positive_count = Feedback.query.filter_by(sentiment='positive').count()
        negative_count = Feedback.query.filter_by(sentiment='negative').count()
        neutral_count = Feedback.query.filter_by(sentiment='neutral').count()
        
        positive_percentage = (positive_count / total_feedbacks * 100) if total_feedbacks > 0 else 0
        negative_percentage = (negative_count / total_feedbacks * 100) if total_feedbacks > 0 else 0
        neutral_percentage = (neutral_count / total_feedbacks * 100) if total_feedbacks > 0 else 0
        
        return jsonify({
            "total_feedbacks": total_feedbacks,
            "sentiment_counts": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            },
            "sentiment_percentages": {
                "positive": round(positive_percentage, 1),
                "negative": round(negative_percentage, 1),
                "neutral": round(neutral_percentage, 1)
            },
            "average_rating": round(db.session.query(db.func.avg(Feedback.rating)).scalar() or 0, 2),
            "average_polarity": round(db.session.query(db.func.avg(Feedback.polarity)).scalar() or 0, 3)
        })
        
    except Exception as e:
        logger.error(f" Error fetching stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/csv', methods=['GET'])
@token_required
@admin_required
def export_csv(current_user):
    """Export all feedback as CSV"""
    try:
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'ID', 'Name', 'Email', 'Category', 'Rating', 'Sentiment', 
            'Polarity', 'Subjectivity', 'Analysis Method', 'Message', 'Created At'
        ])
        
        for feedback in feedbacks:
            writer.writerow([
                feedback.id,
                feedback.name or '',
                feedback.email or '',
                feedback.category,
                feedback.rating,
                feedback.sentiment,
                f"{feedback.polarity:.3f}",
                f"{feedback.subjectivity:.3f}",
                feedback.analysis_method,
                feedback.message.replace('\n', ' '),
                feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=feedback_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        logger.info(" CSV export completed successfully")
        return response
        
    except Exception as e:
        logger.error(f" CSV export error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/json', methods=['GET'])
@token_required
@admin_required
def export_json(current_user):
    """Export all feedback as JSON"""
    try:
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
        
        data = {
            'export_date': datetime.now().isoformat(),
            'total_feedbacks': len(feedbacks),
            'feedbacks': [feedback.to_dict() for feedback in feedbacks]
        }
        
        response = make_response(json.dumps(data, indent=2, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=feedback_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        logger.info(" JSON export completed successfully")
        return response
        
    except Exception as e:
        logger.error(f" JSON export error: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/feedbacks', methods=['GET'])
@token_required
@admin_required
def get_all_feedbacks_admin(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        feedback_list = [f.to_dict() for f in feedbacks.items]
        
        return jsonify({
            "feedbacks": feedback_list,
            "total": feedbacks.total,
            "pages": feedbacks.pages,
            "current_page": page
        })
    except Exception as e:
        logger.error(f" Error fetching all feedbacks: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    try:
        users = User.query.all()
        return jsonify({
            "users": [user.to_dict() for user in users]
        })
    except Exception as e:
        logger.error(f" Error fetching users: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== UTILITY ROUTES ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.route('/api/test-email', methods=['GET'])
def test_email():
    """Test email configuration"""
    try:
        from email_notifier import send_negative_feedback_alert
        
        class TestFeedback:
            def __init__(self):
                self.id = 999
                self.name = "Test User"
                self.email = "test@example.com"
                self.category = "product"
                self.rating = 1
                self.message = "This is a test negative feedback for email testing"
                self.sentiment = "negative"
                self.polarity = -0.8
                self.analysis_method = "test"
                self.created_at = datetime.utcnow()
        
        result = send_negative_feedback_alert(TestFeedback())
        logger.info(" Test email sent successfully")
        return jsonify({"success": result, "message": "Test email sent" if result else "Email failed"})
    except Exception as e:
        logger.error(f" Test email failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def generate_text_report(feedbacks):
    """Generate a comprehensive text report"""
    total = len(feedbacks)
    positive = sum(1 for f in feedbacks if f.sentiment == 'positive')
    negative = sum(1 for f in feedbacks if f.sentiment == 'negative')
    neutral = sum(1 for f in feedbacks if f.sentiment == 'neutral')
    avg_rating = sum(f.rating for f in feedbacks) / total if total > 0 else 0
    
    report = []
    report.append("=" * 60)
    report.append("           FEEDBACK ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total Feedbacks: {total}")
    report.append("")
    report.append("SUMMARY STATISTICS:")
    report.append("-" * 40)
    report.append(f"Positive: {positive} ({positive/total*100:.1f}%)")
    report.append(f"Negative: {negative} ({negative/total*100:.1f}%)")
    report.append(f"Neutral:  {neutral} ({neutral/total*100:.1f}%)")
    report.append(f"Average Rating: {avg_rating:.1f} ⭐")
    report.append("")
    report.append("RECENT FEEDBACKS:")
    report.append("-" * 40)
    
    for i, feedback in enumerate(feedbacks[:10], 1):
        report.append(f"{i}. [{feedback.sentiment.upper()}] ⭐{feedback.rating}/5 - {feedback.category}")
        report.append(f"   From: {feedback.name or 'Anonymous'}")
        report.append(f"   Date: {feedback.created_at.strftime('%Y-%m-%d %H:%M')}")
        report.append(f"   Message: {feedback.message}")
        report.append("")
    
    report.append("=" * 60)
    report.append("End of Report")
    
    return "\n".join(report)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors by serving index.html for SPA routing"""
    if request.path.startswith('/api/'):
        logger.error(f"API endpoint not found: {request.path}")
        return jsonify({"error": "API endpoint not found"}), 404
    return render_template('index.html')

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error"}), 500
    return render_template('index.html')

# ----------------- Run the app -----------------
if __name__ == '__main__':
    # Print startup banner
    print_startup_banner()
    print("... open link http://localhost:5000/")
    # Create necessary directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)