# components/row_manager.py

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "travel.db"


# ---------------------------------------------------------
# 指定日の行を 0,1,2,3... と再採番する
# ---------------------------------------------------------
def reindex_day(conn, trip_id, day_index):
    cur = conn.cursor()

    base_prefix = (day_index + 1) * 1000  # 1日目→1000, 2日目→2000...

    # その日の行を取得
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
# Trip の開始日・終了日から日付行をプリセット
# ---------------------------------------------------------
def initialize_trip(trip_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # すでに行がある場合は何もしない
    cur.execute("SELECT COUNT(*) FROM trip_rows WHERE trip_id = ?", (trip_id,))
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    # Trip の開始日・終了日を取得
    cur.execute("SELECT date_start, date_end FROM trips WHERE id = ?", (trip_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return

    ds, de = row
    ds_date = datetime.strptime(ds, "%Y/%m/%d")
    de_date = datetime.strptime(de, "%Y/%m/%d")

    delta = (de_date - ds_date).days + 1
    dates = [(ds_date + timedelta(days=i)).strftime("%Y/%m/%d") for i in range(delta)]

    # 各日付について初期行を挿入
    for day_index, date_str in enumerate(dates):
        base_prefix = (day_index + 1) * 1000

        # date 行
        order_base = base_prefix + 0
        cur.execute("""
            INSERT INTO trip_rows
            (trip_id, class_id, order_base, order_index,
             planned_time, actual_time, place, by, cost, point, note, image, video)
            VALUES (?, 0, ?, ?, ?, ?, '', '', '', '', '', '', '')
        """, (trip_id, order_base, order_base + 0.0, date_str, date_str))

        # fixed（上）
        order_base = base_prefix + 1
        cur.execute("""
            INSERT INTO trip_rows
            (trip_id, class_id, order_base, order_index,
             planned_time, actual_time, place, by, cost, point, note, image, video)
            VALUES (?, 1, ?, ?, '', '', '', '', '', '', '', '', '')
        """, (trip_id, order_base, order_base + 0.1))

        # middle
        order_base = base_prefix + 2
        cur.execute("""
            INSERT INTO trip_rows
            (trip_id, class_id, order_base, order_index,
             planned_time, actual_time, place, by, cost, point, note, image, video)
            VALUES (?, 2, ?, ?, '', '', '', '', '', '', '', '', '')
        """, (trip_id, order_base, order_base + 0.2))

        # fixed（下）
        order_base = base_prefix + 3
        cur.execute("""
            INSERT INTO trip_rows
            (trip_id, class_id, order_base, order_index,
             planned_time, actual_time, place, by, cost, point, note, image, video)
            VALUES (?, 1, ?, ?, '', '', '', '', '', '', '', '', '')
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
               planned_time, actual_time, place, by, cost, point, note, image, video
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

    # 上の行の情報を取得
    cur.execute("""
        SELECT order_base, order_index, by
        FROM trip_rows
        WHERE id = ?
    """, (above_row_id,))
    order_base, order_index, by_value = cur.fetchone()

    # 新しい middle 行の order_base は一時的に +0.5
    new_order_base = order_base + 0.5
    new_order_index = new_order_base + 0.2  # class_id=2

    # middle の by 継承
    new_by = by_value if by_value else ""

    cur.execute("""
        INSERT INTO trip_rows
        (trip_id, class_id, order_base, order_index,
         planned_time, actual_time, place, by, cost, point, note, image, video)
        VALUES (?, 2, ?, ?, '', '', '', ?, '', '', '', '', '')
    """, (trip_id, new_order_base, new_order_index, new_by))

    # 追加した日の day_index を求める
    day_index = (int(order_base) // 1000) - 1

    # 再採番
    reindex_day(conn, trip_id, day_index)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# middle 行のみ削除
# ---------------------------------------------------------
def delete_row(row_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # class_id を取得
    cur.execute("SELECT class_id, order_base, trip_id FROM trip_rows WHERE id = ?", (row_id,))
    class_id, order_base, trip_id = cur.fetchone()

    if class_id != 2:  # middle 以外は削除不可
        conn.close()
        return

    cur.execute("DELETE FROM trip_rows WHERE id = ?", (row_id,))

    # 再採番
    day_index = (int(order_base) // 1000) - 1
    reindex_day(conn, trip_id, day_index)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# セル編集（on_blur）
# ---------------------------------------------------------
def update_cell(row_id: int, column: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # class_id を取得
    cur.execute("SELECT class_id FROM trip_rows WHERE id = ?", (row_id,))
    class_id = cur.fetchone()[0]

    # date 行は編集不可
    if class_id == 0:
        conn.close()
        return

    # F → fixed
    if column == "place" and value.strip().upper() == "F":
        cur.execute("""
            UPDATE trip_rows
            SET class_id = 1, place = ''
            WHERE id = ?
        """, (row_id,))

    # 空欄 → middle に戻す
    elif column == "place" and value.strip() == "":
        cur.execute("""
            UPDATE trip_rows
            SET class_id = 2, place = ''
            WHERE id = ?
        """, (row_id,))

    else:
        cur.execute(f"""
            UPDATE trip_rows
            SET {column} = ?
            WHERE id = ?
        """, (value, row_id))

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
            planned, actual, place, by, cost, point, note, image, video
        ) = row

        result.append({
            "id": row_id,
            "type": class_id,
            "order_base": order_base,
            "planned_time": planned or "",
            "actual_time": actual or "",
            "place": place or "",
            "by": by or "",
            "cost": cost or "",
            "point": point or "",
            "note": note or "",
            "image": image or "",
            "video": video or "",
        })

    return result