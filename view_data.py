import sqlite3

conn = sqlite3.connect("deepshield.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM predictions")

rows = cursor.fetchall()

if rows:
    for row in rows:
        print(row)
else:
    print("No records found.")

conn.close()