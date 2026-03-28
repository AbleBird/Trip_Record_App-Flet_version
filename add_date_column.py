import sqlite3

conn = sqlite3.connect("travel.db")
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE trips ADD COLUMN date TEXT DEFAULT ''")
    print("date カラムを追加しました。")
except Exception as e:
    print("エラー:", e)

conn.commit()
conn.close()