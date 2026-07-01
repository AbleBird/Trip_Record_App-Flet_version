# components/row_manager.py

import sqlite3
from datetime import datetime, timedelta
from components.others.date_manager import build_date_list

DB_PATH = "travel.db"

# ---------------------------------------------------------
# 指定日の行を 0,1,2,3... と再採番する
# ---------------------------------------------------------
def reindex_day(conn, trip_id, day_index):
    cur = conn.cursor()

    base_prefix = (day_index + 1) * 1000

    cur.execute("""
        SELECT id, class_id
        FROM trip_rows
        WHERE trip_id = ?
          AND order_base BETWEEN ? AND ?
        ORDER BY order_index ASC
    """, (trip_id, base_prefix, base_prefix + 999))

    rows = cur.fetchall()

    new_order = 0
    for row_id, class_id in rows:
        new_base = base_prefix + new_order
        new_index = new_base + class_id / 10

        cur.execute("""
            UPDATE trip_rows
            SET order_base = ?, order_index = ?
            WHERE id = ?
        """, (new_base, new_index, row_id))

        new_order += 1


# ---------------------------------------------------------
# Trip 初期化（fixed/middle のみ生成）
# 日付行は date_manager が担当
# ---------------------------------------------------------
def initialize_trip(trip_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # すでに行がある場合は何もしない
    cur.execute("SELECT COUNT(*) FROM trip_rows WHERE trip_id = ?", (trip_id,))
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    # 日付リストを取得（date_manager）
    dates = build_date_list(trip_id)
    if not dates:
        conn.close()
        return

    # fixed/middle のみ生成（date 行は date_manager が挿入）
    for day_index, _ in enumerate(dates):
        base_prefix = (day_index + 1) * 1000

        # fixed（上）
        order_base = base_prefix + 1
        cur.execute("""
            INSERT INTO trip_rows
            (trip_id, class_id, order_base, order_index,
             planned_time, actual_time, place, by, point, note, image, video)
            VALUES (?, 1, ?, ?, '', '', '', '', '', '', '', '')
        """, (trip_id, order_base, order_base + 0.1))

        # middle
        order_base = base_prefix + 2
        cur.execute("""
            INSERT INTO trip_rows
            (trip_id, class_id, order_base, order_index,
             planned_time, actual_time, place, by, point, note, image, video)
            VALUES (?, 2, ?, ?, '', '', '', '', '', '', '', '')
        """, (trip_id, order_base, order_base + 0.2))

        # fixed（下）
        order_base = base_prefix + 3
        cur.execute("""
            INSERT INTO trip_rows
            (trip_id, class_id, order_base, order_index,
             planned_time, actual_time, place, by, point, note, image, video)
            VALUES (?, 1, ?, ?, '', '', '', '', '', '', '', '')
        """, (trip_id, order_base, order_base + 0.1))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Trip の行一覧を取得
# ---------------------------------------------------------
def fetch_rows(trip_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, class_id, order_base, order_index,
               planned_time, actual_time, place, by, point, note, image, video
        FROM trip_rows
        WHERE trip_id = ?
        ORDER BY order_index ASC
    """, (trip_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------
# 中間行追加
# ---------------------------------------------------------
def add_middle_row(trip_id: int, above_row_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT order_base, order_index, by
        FROM trip_rows
        WHERE id = ?
    """, (above_row_id,))
    order_base, order_index, by_value = cur.fetchone()

    new_order_base = order_base + 0.5
    new_order_index = new_order_base + 0.2

    new_by = by_value if by_value else ""

    cur.execute("""
        INSERT INTO trip_rows
        (trip_id, class_id, order_base, order_index,
         planned_time, actual_time, place, by, point, note, image, video)
        VALUES (?, 2, ?, ?, '', '', '', ?, '', '', '', '')
    """, (trip_id, new_order_base, new_order_index, new_by))

    day_index = (int(order_base) // 1000) - 1
    reindex_day(conn, trip_id, day_index)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# middle 行のみ削除
# ---------------------------------------------------------
def delete_row(row_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT class_id, order_base, trip_id FROM trip_rows WHERE id = ?", (row_id,))
    class_id, order_base, trip_id = cur.fetchone()

    if class_id != 2:
        conn.close()
        return

    cur.execute("DELETE FROM trip_rows WHERE id = ?", (row_id,))

    day_index = (int(order_base) // 1000) - 1
    reindex_day(conn, trip_id, day_index)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# セル編集
# ---------------------------------------------------------
def update_cell(row_id: int, column: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT class_id FROM trip_rows WHERE id = ?", (row_id,))
    class_id = cur.fetchone()[0]

    if class_id == 0:
        conn.close()
        return

    if column == "place" and value.strip().upper() == "F":
        cur.execute("UPDATE trip_rows SET class_id = 1 WHERE id = ?", (row_id,))
    elif column == "place" and value.strip() == "":
        cur.execute("UPDATE trip_rows SET class_id = 2 WHERE id = ?", (row_id,))
    else:
        if column != "cost":
            cur.execute(f"UPDATE trip_rows SET {column} = ? WHERE id = ?", (value, row_id))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# rows_data を BasicTable 用に整形
# ---------------------------------------------------------
def sanitize_rows(rows):
    result = []
    for row in rows:
        (
            row_id, class_id, order_base, order_index,
            planned, actual, place, by, point, note, image, video
        ) = row

        result.append({
            "id": row_id,
            "type": class_id,
            "order_base": order_base,
            "planned_time": planned or "",
            "actual_time": actual or "",
            "place": place or "",
            "by": by or "",
            "point": point or "",
            "note": note or "",
            "image": image or "",
            "video": video or "",
        })

    return result

def fetch_point(row_id: int) -> str:
    import sqlite3
    conn = sqlite3.connect("travel.db")
    cur = conn.cursor()
    cur.execute("SELECT point FROM trip_rows WHERE id = ?", (row_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row and row[0] else ""

def update_point(row_id: int, new_text: str):
    import sqlite3
    conn = sqlite3.connect("travel.db")
    cur = conn.cursor()
    cur.execute("UPDATE trip_rows SET point = ? WHERE id = ?", (new_text, row_id))
    conn.commit()
    conn.close()
