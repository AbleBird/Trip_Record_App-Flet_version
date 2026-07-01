# components/home_logic.py

import sqlite3
from db.transport_database import init_transport_rows_for_trip
from db.cost_database import init_other_cost_rows_for_trip
from db.transport_database import delete_transport_costs_for_trip
from db.cost_database import delete_other_costs_for_trip
from components.others.date_manager import insert_date_rows
from components.others.sync_dates import sync_cost_dates

DB_PATH = "travel.db"


# -------------------------
# 日付正規化
# -------------------------
def normalize_date(date_str: str) -> str:
    parts = date_str.split("/")
    if len(parts) != 3:
        return date_str
    y, m, d = parts
    return f"{int(y):04d}/{int(m):02d}/{int(d):02d}"


# -------------------------
# 表示名生成
# -------------------------
def make_display_name(ds: str, de: str, place: str) -> str:
    if ds == de:
        return f"{ds} {place}"

    ys, ms, ds_day = ds.split("/")
    ye, me, de_day = de.split("/")

    if ys != ye:
        return f"{ds}〜{de} {place}"

    if ms == me:
        return f"{ds}〜{de_day} {place}"

    return f"{ds}〜{me}/{de_day} {place}"


# -------------------------
# Trip一覧取得
# -------------------------
def fetch_trips(sort_desc: bool):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    order = "DESC" if sort_desc else "ASC"

    cur.execute(
        f"""
        SELECT id, name, date_start, date_end, hidden
        FROM trips
        WHERE hidden = 0
        ORDER BY date_start {order}
        """
    )
    trips = cur.fetchall()
    conn.close()
    return trips


# -------------------------
# Trip追加
# -------------------------
def add_trip_to_db(display_name, ds, de):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO trips (name, date_start, date_end, hidden) VALUES (?, ?, ?, 0)",
        (display_name, ds, de),
    )
    trip_id = cur.lastrowid
    conn.commit()
    conn.close()

    # ★ travel.db 側の日付行生成（最重要）
    insert_date_rows(trip_id)

    # ★ cost.db 側の初期行生成
    init_transport_rows_for_trip(trip_id)
    init_other_cost_rows_for_trip(trip_id)


# -------------------------
# Trip名変更（travel.db のみ）
# -------------------------
def rename_trip(trip_id, new_name):
    import re
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("UPDATE trips SET name = ? WHERE id = ?", (new_name, trip_id))

    m = re.match(r"(\d{4}/\d{2}/\d{2})(?:〜(\d{4}/\d{2}/\d{2}|\d{2}/\d{2}))?", new_name)

    if m:
        ds = m.group(1)
        de = m.group(2) if m.group(2) else ds

        if len(de) == 5:
            year = ds.split("/")[0]
            de = f"{year}/{de}"

        cur.execute(
            "UPDATE trips SET date_start = ?, date_end = ? WHERE id = ?",
            (ds, de, trip_id)
        )

    conn.commit()
    conn.close()

    # 基本は自動で同期
    sync_cost_dates(trip_id)


# -------------------------
# Trip非表示
# -------------------------
def hide_trip(trip_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE trips SET hidden = 1 WHERE id = ?", (trip_id,))
    conn.commit()
    conn.close()


# -------------------------
# Trip削除
# -------------------------
def delete_trip(trip_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # travel.db 側
    cur.execute("DELETE FROM trip_rows WHERE trip_id = ?", (trip_id,))
    cur.execute("DELETE FROM trips WHERE id = ?", (trip_id,))

    conn.commit()
    conn.close()

    # ★ cost.db 側も削除
    delete_transport_costs_for_trip(trip_id)
    delete_other_costs_for_trip(trip_id)


# -------------------------
# 全て非表示/表示
# -------------------------
def toggle_all_trips():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM trips WHERE hidden = 0")
    visible_count = cur.fetchone()[0]

    if visible_count > 0:
        cur.execute("UPDATE trips SET hidden = 1")
    else:
        cur.execute("UPDATE trips SET hidden = 0")

    conn.commit()
    conn.close()
