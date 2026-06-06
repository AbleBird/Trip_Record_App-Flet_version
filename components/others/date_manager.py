# components/others/date_manager.py

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "travel.db"

# ---------------------------------------------------------
# Trip の開始日・終了日を取得
# ---------------------------------------------------------
def get_trip_dates(trip_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT date_start, date_end FROM trips WHERE id = ?", (trip_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None, None

    ds, de = row
    ds_date = datetime.strptime(ds, "%Y/%m/%d")
    de_date = datetime.strptime(de, "%Y/%m/%d")

    return ds_date, de_date


# ---------------------------------------------------------
# Trip の日付リストを生成
# ---------------------------------------------------------
def build_date_list(trip_id: int):
    ds_date, de_date = get_trip_dates(trip_id)
    if not ds_date:
        return []

    delta = (de_date - ds_date).days + 1
    return [(ds_date + timedelta(days=i)).strftime("%Y/%m/%d") for i in range(delta)]


# ---------------------------------------------------------
# 日付行（type=0）を削除
# ---------------------------------------------------------
def delete_date_rows(trip_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM trip_rows
        WHERE trip_id = ? AND class_id = 0
    """, (trip_id,))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# 日付行（type=0）を生成
# ---------------------------------------------------------
def insert_date_rows(trip_id: int):
    dates = build_date_list(trip_id)
    if not dates:
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for day_index, date_str in enumerate(dates):
        base_prefix = (day_index + 1) * 1000
        order_base = base_prefix + 0

        cur.execute("""
            INSERT INTO trip_rows
            (trip_id, class_id, order_base, order_index,
             planned_time, actual_time, place, by, point, note, image, video)
            VALUES (?, 0, ?, ?, ?, ?, '', '', '', '', '', '')
        """, (trip_id, order_base, order_base + 0.0, date_str, date_str))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Trip名（日付）変更時：日付行を更新
# ---------------------------------------------------------
def update_date_rows(trip_id: int):
    delete_date_rows(trip_id)
    insert_date_rows(trip_id)

def get_date_list_from_rows(trip_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT planned_time
        FROM trip_rows
        WHERE trip_id = ?
          AND class_id = 0
        ORDER BY order_index ASC
    """, (trip_id,))

    rows = cur.fetchall()
    conn.close()

    return [r[0] for r in rows]
