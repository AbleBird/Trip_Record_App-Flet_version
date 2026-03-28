import sqlite3

DB_PATH = "travel.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE events ADD COLUMN actual_order TEXT")
    print("actual_order カラムを追加しました")
except Exception as e:
    print("エラー:", e)

conn.commit()
conn.close()