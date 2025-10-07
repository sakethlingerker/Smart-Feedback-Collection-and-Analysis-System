
import sqlite3
import os

db_path = 'feedback.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
    tables = cursor.fetchall()
    print('📋 Tables in database:')
    if tables:
        for table in tables:
            print('  -', table[0])
    else:
        print('  ❌ No tables found')
    conn.close()
else:
    print('❌ No database file')



from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Tables created')
    
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print('📋 Tables:', tables)



import sqlite3
conn = sqlite3.connect('feedback.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
tables = [table[0] for table in cursor.fetchall()]
print('📋 Tables:', tables)
if 'feedbacks' in tables:
    print('✅ feedbacks table exists!')
else:
    print('❌ feedbacks table missing')
conn.close()
