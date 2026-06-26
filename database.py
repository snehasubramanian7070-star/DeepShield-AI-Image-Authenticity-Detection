import sqlite3

conn = sqlite3.connect("deepshield.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_name TEXT,
    prediction TEXT,
    confidence REAL,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Database created successfully!")