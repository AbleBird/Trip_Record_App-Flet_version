import sqlite3

DB_PATH = "travel.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE events RENAME COLUMN place2 TO by;")
    print("place2 → by に変更しました")
except Exception as e:
    print("エラー:", e)

conn.commit()
conn.close()