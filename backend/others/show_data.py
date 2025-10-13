import sqlite3
import os

def show_all_data():
    db_path = 'feedback.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all feedbacks
        cursor.execute("""
            SELECT id, name, email, category, rating, sentiment, polarity, 
                   analysis_method, created_at, message 
            FROM feedbacks 
            ORDER BY created_at DESC;
        """)
        
        feedbacks = cursor.fetchall()
        
        print(f"💾 STORED FEEDBACKS: {len(feedbacks)} total")
        print("=" * 100)
        
        for fb in feedbacks:
            id, name, email, category, rating, sentiment, polarity, method, created_at, message = fb
            stars = '★' * rating + '☆' * (5 - rating)
            print(f"ID: {id} | {name or 'Anonymous':<15} | {category:<10} | {stars} | {sentiment:<8} | {method}")
            print(f"    Message: {message}")
            print(f"    Date: {created_at} | Polarity: {polarity:.3f}")
            print("-" * 100)
            
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("❌ No feedbacks table found - submit feedback through the web form first")
        else:
            print(f"❌ Error: {e}")
    
    conn.close()

if __name__ == "__main__":
    show_all_data()