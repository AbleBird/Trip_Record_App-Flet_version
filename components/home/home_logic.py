# components/home_logic.py

import sqlite3
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
    conn.commit()
    conn.close()


# -------------------------
# Trip名変更
# -------------------------
def rename_trip(trip_id, new_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE trips SET name = ? WHERE id = ?", (new_name, trip_id))
    conn.commit()
    conn.close()


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

    # trip_rows を先に削除
    cur.execute("DELETE FROM trip_rows WHERE trip_id = ?", (trip_id,))

    # trips を削除
    cur.execute("DELETE FROM trips WHERE id = ?", (trip_id,))

    conn.commit()
    conn.close()

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