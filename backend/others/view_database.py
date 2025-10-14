import sqlite3
import os

def view_feedbacks():
    db_path = 'feedback.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("❌ Database file 'feedback.db' not found!")
        print("💡 Submit some feedback through the web form first")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if feedbacks table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedbacks';")
        if not cursor.fetchone():
            print("❌ 'feedbacks' table not found!")
            print("💡 Submit some feedback through the web form first")
            return
        
        # Count total feedbacks
        cursor.execute("SELECT COUNT(*) FROM feedbacks;")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 TOTAL FEEDBACKS RECEIVED: {total_count}")
        
        if total_count == 0:
            print("💡 No feedbacks yet. Submit some through the web form!")
            return
        
        # Get all feedbacks
        cursor.execute("""
            SELECT id, name, category, rating, sentiment, polarity, 
                   analysis_method, created_at, message 
            FROM feedbacks 
            ORDER BY created_at DESC;
        """)
        feedbacks = cursor.fetchall()
        
        print(f"\n🎯 ALL FEEDBACKS (Latest first):")
        print("=" * 130)
        print(f"{'ID':<3} {'Name':<12} {'Category':<10} {'Rating':<6} {'Sentiment':<10} {'Method':<12} {'Date':<16} {'Message'}")
        print("=" * 130)
        
        for feedback in feedbacks:
            id, name, category, rating, sentiment, polarity, method, created_at, message = feedback
            stars = '★' * rating + '☆' * (5 - rating)
            date_str = created_at[:16] if created_at else "N/A"
            short_message = (message[:50] + '...') if len(message) > 53 else message
            print(f"{id:<3} {name or 'Anonymous':<12} {category:<10} {stars:<6} {sentiment:<10} {method:<12} {date_str:<16} {short_message}")
        
        # Show summary statistics
        print(f"\n📈 SUMMARY:")
        print("-" * 40)
        
        # Sentiment distribution
        cursor.execute("SELECT sentiment, COUNT(*) FROM feedbacks GROUP BY sentiment;")
        sentiment_stats = cursor.fetchall()
        for sentiment, count in sentiment_stats:
            percentage = (count / total_count) * 100
            print(f"  {sentiment:<10}: {count:>2} feedbacks ({percentage:.1f}%)")
        
        # Average rating
        cursor.execute("SELECT AVG(rating) FROM feedbacks;")
        avg_rating = cursor.fetchone()[0]
        print(f"  Average Rating: {avg_rating:.1f}⭐")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    view_feedbacks()