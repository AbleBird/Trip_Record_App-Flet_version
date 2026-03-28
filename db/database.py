import sqlite3

DB_PATH = "travel.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # -------------------------
    # Trip 一覧テーブル
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date_start TEXT,
            date_end TEXT,
            hidden INTEGER DEFAULT 0
        );
    """)

    # -------------------------
    # Trip 内行テーブル（新仕様）
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trip_rows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,

            -- 行種別: 0=date, 1=fixed, 2=middle
            class_id INTEGER NOT NULL,

            -- 5桁の順序（例：02015 → 2015 として保持）
            order_base INTEGER NOT NULL,

            -- 並び替え用（order_base + class_id/10）
            order_index REAL NOT NULL,

            planned_time TEXT,
            actual_time TEXT,
            place TEXT,
            by TEXT,
            cost TEXT,
            point TEXT,
            note TEXT,
            image TEXT,
            video TEXT
        );
    """)

    conn.commit()
    conn.close()