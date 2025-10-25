import sqlite3
from datetime import datetime

def view_database():
    # Connect to database
    conn = sqlite3.connect('instance/feedback.db')
    cursor = conn.cursor()
    
    print("=" * 50)
    print("SMART FEEDBACK SYSTEM DATABASE VIEWER")
    print("=" * 50)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📊 Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # View Users table
    print(f"\n👥 USERS TABLE:")
    print("-" * 40)
    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()
    
    if users:
        print(f"{'ID':<3} {'Email':<25} {'Role':<10} {'Created At'}")
        print("-" * 60)
        for user in users:
            user_id, email, password_hash, role, created_at, is_active = user
            created_str = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M')
            print(f"{user_id:<3} {email:<25} {role:<10} {created_str}")
    else:
        print("No users found")
    
    # View Feedbacks table
    print(f"\n💬 FEEDBACKS TABLE:")
    print("-" * 40)
    cursor.execute("""
        SELECT f.id, f.name, f.email, f.category, f.rating, f.sentiment, 
               f.polarity, f.message, f.created_at, u.email as user_email
        FROM feedbacks f 
        LEFT JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
        LIMIT 10;
    """)
    feedbacks = cursor.fetchall()
    
    if feedbacks:
        print(f"{'ID':<3} {'Name':<15} {'Category':<10} {'Rating':<6} {'Sentiment':<10} {'User'}")
        print("-" * 70)
        for fb in feedbacks:
            fb_id, name, email, category, rating, sentiment, polarity, message, created_at, user_email = fb
            name_display = name if name else 'Anonymous'
            user_display = user_email if user_email else 'Guest'
            created_str = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f').strftime('%m-%d %H:%M')
            print(f"{fb_id:<3} {name_display:<15} {category:<10} {rating:<6} {sentiment:<10} {user_display}")
    else:
        print("No feedbacks found")
    
    # Statistics
    print(f"\n📈 STATISTICS:")
    print("-" * 40)
    
    # Total counts
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM feedbacks;")
    feedback_count = cursor.fetchone()[0]
    
    # Sentiment distribution
    cursor.execute("SELECT sentiment, COUNT(*) FROM feedbacks GROUP BY sentiment;")
    sentiment_stats = cursor.fetchall()
    
    print(f"Total Users: {user_count}")
    print(f"Total Feedbacks: {feedback_count}")
    print("\nSentiment Distribution:")
    for sentiment, count in sentiment_stats:
        percentage = (count / feedback_count * 100) if feedback_count > 0 else 0
        print(f"  {sentiment}: {count} ({percentage:.1f}%)")
    
    # Rating distribution
    cursor.execute("SELECT rating, COUNT(*) FROM feedbacks GROUP BY rating ORDER BY rating;")
    rating_stats = cursor.fetchall()
    
    print("\nRating Distribution:")
    for rating, count in rating_stats:
        print(f"  {rating}★: {count}")
    
    conn.close()

if __name__ == "__main__":
    view_database()