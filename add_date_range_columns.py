import sqlite3

DB_PATH = "travel.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

for col in ("date_start", "date_end"):
    try:
        cur.execute(f"ALTER TABLE trips ADD COLUMN {col} TEXT DEFAULT ''")
        print(f"{col} カラムを追加しました。")
    except Exception as e:
        print(f"{col} 追加時のエラー:", e)

conn.commit()
conn.close()