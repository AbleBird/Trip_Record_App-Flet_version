# db/cost_database.py

import sqlite3

COST_DB_PATH = "cost.db"


# =========================================================
# 初期化
# =========================================================
def init_cost_db():
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    # -------------------------
    # 交通費テーブル
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transport_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            order_index INTEGER NOT NULL,

            category TEXT NOT NULL,
            subcategory TEXT,
            name TEXT,

            from_station TEXT,
            to_station TEXT,
            via TEXT,
            line TEXT,

            ticket_type TEXT,
            amount INTEGER NOT NULL DEFAULT 0,
            memo TEXT
        );
    """)

    # -------------------------
    # その他費用テーブル
    # -------------------------
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
# 交通費（transport_costs）
# =========================================================

def add_transport_cost(trip_id, date):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transport_costs
        (trip_id, date, order_index, category, subcategory, name,
         from_station, to_station, via, line, ticket_type, amount, memo)
        VALUES (?, ?, 0, '', '', '', '', '', '', '', '', 0, '')
    """, (trip_id, date))

    conn.commit()
    conn.close()


def delete_transport_cost(row_id):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM transport_costs WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()


def update_transport_cost(row_id, column, value):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE transport_costs SET {column} = ? WHERE id = ?", (value, row_id))
    conn.commit()
    conn.close()


def get_transport_costs_by_date(trip_id, date):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT id, category, subcategory, name,
               from_station, to_station, via, line,
               ticket_type, amount, memo
        FROM transport_costs
        WHERE trip_id = ? AND date = ?
        ORDER BY id ASC
    """, (trip_id, date)).fetchall()

    conn.close()

    return [
        {
            "id": r[0],
            "category": r[1],
            "subcategory": r[2],
            "name": r[3],
            "from_station": r[4],
            "to_station": r[5],
            "via": r[6],
            "line": r[7],
            "ticket_type": r[8],
            "amount": r[9],
            "memo": r[10],
        }
        for r in rows
    ]


def get_transport_totals(trip_id):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT date, SUM(amount)
        FROM transport_costs
        WHERE trip_id = ?
        GROUP BY date
    """, (trip_id,)).fetchall()

    conn.close()

    return {date: total for date, total in rows}


def get_transport_total_for_trip(trip_id):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    total = cur.execute("""
        SELECT SUM(amount)
        FROM transport_costs
        WHERE trip_id = ?
    """, (trip_id,)).fetchone()[0]

    conn.close()
    return total or 0


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
