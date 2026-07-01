# db/cost_database.py

import sqlite3
from components.others.date_manager import build_date_list

COST_DB_PATH = "cost.db"


# =========================================================
# 初期化（other_costs のみ）
# =========================================================
def init_cost_db():
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    # その他費用テーブル
    cur.execute("""
        CREATE TABLE IF NOT EXISTS other_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            date TEXT NOT NULL,

            type TEXT NOT NULL,
            title TEXT,
            item TEXT,
            amount INTEGER NOT NULL DEFAULT 0,
            note TEXT
        );
    """)

    conn.commit()
    conn.close()


# =========================================================
# その他費用（other_costs）
# =========================================================

def get_other_costs(trip_id):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT id, date, type, title, item, amount, note
        FROM other_costs
        WHERE trip_id = ?
        ORDER BY date ASC, id ASC
    """, (trip_id,)).fetchall()

    conn.close()

    return [
        {
            "id": r[0],
            "date": r[1],
            "type": r[2],
            "title": r[3],
            "item": r[4],
            "amount": r[5],
            "note": r[6],
        }
        for r in rows
    ]


def update_other_cost(row_id, column, value):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE other_costs SET {column} = ? WHERE id = ?", (value, row_id))
    conn.commit()
    conn.close()


def add_other_cost(trip_id, date):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO other_costs
        (trip_id, date, type, title, item, amount, note)
        VALUES (?, ?, '食費', '', '', 0, '')
    """, (trip_id, date))

    conn.commit()
    conn.close()


def delete_other_cost(row_id):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM other_costs WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()


# =========================================================
# 日付リスト（other_costs 専用）
# =========================================================
def get_cost_dates(trip_id):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT date FROM other_costs WHERE trip_id = ?", (trip_id,))
    dates = [r[0] for r in cur.fetchall()]

    conn.close()

    return sorted(dates)


# =========================================================
# 新規 Trip 用：other_costs の初期行生成
# =========================================================
def init_other_cost_rows_for_trip(trip_id):
    """
    新規 Trip 作成時に other_costs の初期行を生成する。
    travel.db の日付行（trip_rows）を正本として使用する。
    """
    dates = build_date_list(trip_id)
    if not dates:
        return

    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    for d in dates:
        cur.execute("""
            INSERT INTO other_costs
            (trip_id, date, type, title, item, amount, note)
            VALUES (?, ?, '食費', '', '', 0, '')
        """, (trip_id, d))

    conn.commit()
    conn.close()

def delete_other_costs_for_trip(trip_id):
    """
    Trip 削除時に other_costs の該当データを全削除する
    """
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM other_costs WHERE trip_id = ?", (trip_id,))

    conn.commit()
    conn.close()