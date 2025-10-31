import sqlite3
import sqlite3

conn = sqlite3.connect('instance/feedback.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM users WHERE id = 6;")

conn.commit()
conn.close()
