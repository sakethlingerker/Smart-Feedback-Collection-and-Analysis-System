from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Feedback
from sentiment_analysis import analyze_sentiment
from wordcloud_generator import wordcloud_gen
from email_notifier import init_email, send_negative_feedback_alert
from config import Config
import logging
from datetime import datetime, timedelta

# ----------------- Setup logging -----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# ----------------- Routes -----------------
@app.route('/')
def home():
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

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        if not data or not data.get('message'):
            return jsonify({"error": "Feedback message is required"}), 400

        # Analyze sentiment
        sentiment_result = analyze_sentiment(data['message'])
        logger.info(f"Feedback sentiment: {sentiment_result['sentiment']}")

        # Save to database
        feedback = Feedback(
            name=data.get('name', 'Anonymous'),
            email=data.get('email'),
            category=data.get('category', 'general'),
            rating=data.get('rating', 0),
            message=data['message'],
            sentiment=sentiment_result['sentiment'],
            polarity=sentiment_result['polarity'],
            subjectivity=sentiment_result['subjectivity'],
            analysis_method=sentiment_result['method']
        )
        db.session.add(feedback)
        db.session.commit()

        # Send alert if negative
        if sentiment_result['sentiment'] == 'negative' and sentiment_result['polarity'] < app.config['NEGATIVE_SENTIMENT_THRESHOLD']:
            logger.info(f"Sending negative feedback email for ID: {feedback.id}")
            send_negative_feedback_alert(feedback)

        return jsonify({
            "message": "Feedback submitted successfully",
            "sentiment": sentiment_result['sentiment'],
            "polarity": round(sentiment_result['polarity'], 3),
            "analysis_method": sentiment_result['method'],
            "id": feedback.id
        }), 201

    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback', methods=['GET'])
def get_all_feedback():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return jsonify({
            "feedbacks": [f.to_dict() for f in feedbacks.items],
            "total": feedbacks.total,
            "pages": feedbacks.pages,
            "current_page": page
        })
    except Exception as e:
        logger.error(f"Error fetching feedbacks: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
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

        # Add new data for alternative visualizations
        sentiment_by_day = db.session.query(
            db.func.date(Feedback.created_at),
            Feedback.sentiment,
            db.func.count(Feedback.id)
        ).filter(
            Feedback.created_at >= datetime.utcnow().date() - timedelta(days=30)
        ).group_by(db.func.date(Feedback.created_at), Feedback.sentiment).all()
        
        # Category distribution over time
        category_trend = db.session.query(
            db.func.date(Feedback.created_at),
            Feedback.category,
            db.func.count(Feedback.id)
        ).filter(
            Feedback.created_at >= datetime.utcnow().date() - timedelta(days=30)
        ).group_by(db.func.date(Feedback.created_at), Feedback.category).all()
        

        return jsonify({
            "sentiment_distribution": dict(sentiment_stats),
            "rating_distribution": dict(rating_stats),
            "category_distribution": dict(category_stats),
            "method_distribution": dict(method_stats),
            "recent_trend": [{"date": str(date), "count": count} for date, count in recent_feedback],
            "sentiment_trend": [{"date": str(date), "sentiment": sentiment, "count": count} 
                                for date, sentiment, count in sentiment_trend],
            "total_feedbacks": Feedback.query.count(),
            "average_rating": round(db.session.query(db.func.avg(Feedback.rating)).scalar() or 0, 2),
            "average_polarity": round(db.session.query(db.func.avg(Feedback.polarity)).scalar() or 0, 3)
        })
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        return jsonify({"error": str(e)}), 500
# Add these new endpoints to your backend

# Add these endpoints to your backend
# Add these new endpoints to your backend

@app.route('/api/analytics/emotion-distribution')
def get_emotion_distribution():
    """Get emotion distribution from feedback analysis"""
    try:
        # Sample emotion analysis - replace with your actual emotion detection
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
        
        # Analyze recent feedback for emotions
        recent_feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).limit(100).all()
        
        for feedback in recent_feedbacks:
            # Simple keyword-based emotion detection (replace with ML model)
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/priority-matrix')
def get_priority_matrix():
    """Get priority matrix data based on feedback analysis"""
    try:
        priority_matrix = [
            {
                'name': 'Slow Website Performance',
                'impact': 9,  # High impact on user experience
                'frequency': 8,  # Frequently mentioned
                'urgency': 7,   # Moderate urgency
                'category': 'performance'
            },
            {
                'name': 'Poor Customer Support',
                'impact': 8,
                'frequency': 6,
                'urgency': 9,   # High urgency for customer retention
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
            },
            {
                'name': 'Limited Payment Options',
                'impact': 6,
                'frequency': 5,
                'urgency': 4,
                'category': 'features'
            },
            {
                'name': 'High Pricing',
                'impact': 8,
                'frequency': 3,
                'urgency': 3,
                'category': 'pricing'
            },
            {
                'name': 'Lack of Dark Mode',
                'impact': 4,
                'frequency': 6,
                'urgency': 2,
                'category': 'features'
            },
            {
                'name': 'Spam Emails',
                'impact': 5,
                'frequency': 2,
                'urgency': 6,
                'category': 'communication'
            }
        ]
        
        # You can enhance this with actual analysis of feedback data
        # Count occurrences of issues in feedback messages
        feedbacks = Feedback.query.all()
        for feedback in feedbacks:
            text_lower = feedback.message.lower()
            
            # Simple keyword matching to count issue frequency
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
        return jsonify({'error': str(e)}), 500
@app.route('/api/analytics/sentiment-trend')
def get_sentiment_trend():
    """Get sentiment trend over the last 7 days"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        sentiment_trend = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            daily_feedbacks = Feedback.query.filter(
                Feedback.created_at >= current_date,
                Feedback.created_at < next_date
            ).all()
            
            positive = sum(1 for f in daily_feedbacks if f.sentiment == 'positive')
            negative = sum(1 for f in daily_feedbacks if f.sentiment == 'negative')
            neutral = sum(1 for f in daily_feedbacks if f.sentiment == 'neutral')
            
            sentiment_trend.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'total': len(daily_feedbacks)
            })
            
            current_date = next_date
        
        return jsonify(sentiment_trend)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# Add these new endpoints

@app.route('/api/analytics/historical-trend')
def get_historical_trend():
    """Get historical sentiment trend data"""
    try:
        return jsonify({
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'current': [65, 72, 68, 75],
            'previous': [58, 64, 62, 60]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/sentiment-meter')
def get_sentiment_meter():
    """Get current sentiment meter data"""
    try:
        # Calculate current sentiment percentages
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/topic-sentiment')
def get_topic_sentiment():
    """Get topic-sentiment correlation data"""
    try:
        return jsonify({
            'topics': ['Product', 'Support', 'Price', 'Features', 'UI/UX'],
            'positive': [65, 45, 30, 55, 70],
            'negative': [15, 35, 50, 25, 10]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/sentiment-intensity')
def get_sentiment_intensity():
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
        return jsonify({'error': str(e)}), 500
@app.route('/api/analytics/weekly-distribution')
def get_weekly_distribution():
    """Get feedback distribution by day of week"""
    try:
        # Get data from last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        weekly_data = {
            'Monday': 0,
            'Tuesday': 0,
            'Wednesday': 0,
            'Thursday': 0,
            'Friday': 0,
            'Saturday': 0,
            'Sunday': 0
        }
        
        feedbacks = Feedback.query.filter(
            Feedback.created_at >= start_date,
            Feedback.created_at <= end_date
        ).all()
        
        for feedback in feedbacks:
            day_name = feedback.created_at.strftime('%A')
            weekly_data[day_name] += 1
        
        return jsonify(weekly_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/heatmap')
def get_heatmap_data():
    """Get heatmap data for the last 30 days"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        heatmap_data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            daily_count = Feedback.query.filter(
                Feedback.created_at >= current_date,
                Feedback.created_at < next_date
            ).count()
            
            heatmap_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': daily_count,
                'day_of_week': current_date.strftime('%A'),
                'week_number': current_date.isocalendar()[1]
            })
            
            current_date = next_date
        
        return jsonify(heatmap_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/wordcloud', methods=['GET'])
def generate_wordcloud():
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
        logger.error(f"Error generating wordcloud: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        logger.info(f"Feedback {feedback_id} deleted")
        return jsonify({"message": "Feedback deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting feedback {feedback_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection - fixed for SQLAlchemy 2.0+
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
    
@app.route('/api/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """Get detailed statistics for dashboard"""
    try:
        total_feedbacks = Feedback.query.count()
        positive_count = Feedback.query.filter_by(sentiment='positive').count()
        negative_count = Feedback.query.filter_by(sentiment='negative').count()
        neutral_count = Feedback.query.filter_by(sentiment='neutral').count()
        
        # Calculate percentages
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
        logger.error(f"Error fetching stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-email', methods=['GET'])
def test_email():
    """Test email configuration"""
    try:
        from email_notifier import send_negative_feedback_alert
        from models import Feedback
        
        # Create a test feedback object
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
        return jsonify({"success": result, "message": "Test email sent" if result else "Email failed"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

import csv
import io
import json
from datetime import datetime
from flask import Response, make_response

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export all feedback as CSV"""
    try:
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Name', 'Email', 'Category', 'Rating', 'Sentiment', 
            'Polarity', 'Subjectivity', 'Analysis Method', 'Message', 'Created At'
        ])
        
        # Write data
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
                feedback.message.replace('\n', ' '),  # Remove newlines for CSV
                feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=feedback_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/json', methods=['GET'])
def export_json():
    """Export all feedback as JSON"""
    try:
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
        
        # Convert to list of dictionaries
        data = {
            'export_date': datetime.now().isoformat(),
            'total_feedbacks': len(feedbacks),
            'feedbacks': [feedback.to_dict() for feedback in feedbacks]
        }
        
        # Create response with pretty JSON
        response = make_response(json.dumps(data, indent=2, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=feedback_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        return response
        
    except Exception as e:
        logger.error(f"JSON export error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    """Export summary as PDF (basic text version)"""
    try:
        from io import BytesIO
        
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
        
        # Generate simple text report (in real app, use reportlab or weasyprint)
        report_content = generate_text_report(feedbacks)
        
        # For now, return as text file (PDF would require additional libraries)
        response = make_response(report_content)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=feedback_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        return response
        
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        return jsonify({"error": str(e)}), 500

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
    
    for i, feedback in enumerate(feedbacks[:10], 1):  # Show last 10
        report.append(f"{i}. [{feedback.sentiment.upper()}] ⭐{feedback.rating}/5 - {feedback.category}")
        report.append(f"   From: {feedback.name or 'Anonymous'}")
        report.append(f"   Date: {feedback.created_at.strftime('%Y-%m-%d %H:%M')}")
        report.append(f"   Message: {feedback.message}")
        report.append("")
    
    report.append("=" * 60)
    report.append("End of Report")
    
    return "\n".join(report)

# ----------------- Run the app -----------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
from flask import send_from_directory

@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)
