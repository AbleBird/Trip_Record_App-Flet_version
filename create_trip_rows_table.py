import sqlite3

DB_PATH = "travel.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS trip_rows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    row_type TEXT NOT NULL,
    planned_time TEXT,
    actual_time TEXT,
    place TEXT,
    `by` TEXT,
    cost TEXT,
    point TEXT,
    note TEXT,
    image TEXT,
    video TEXT
)
""")

conn.commit()
conn.close()

print("trip_rows テーブル作成完了")