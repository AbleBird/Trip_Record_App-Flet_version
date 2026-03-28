import sqlite3

DB_PATH = "travel.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE events RENAME COLUMN place1 TO place;")
    print("place1 → place に変更しました")
except Exception as e:
    print("エラー:", e)

conn.commit()
conn.close()