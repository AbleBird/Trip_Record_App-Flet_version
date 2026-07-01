# components/others/sync_dates.py

import sqlite3
from datetime import datetime
from components.others.date_manager import build_date_list

COST_DB_PATH = "cost.db"
TRAVEL_DB_PATH = "travel.db"


def sync_cost_dates(trip_id):
    """
    Trip の日付変更に合わせて cost.db の日付を同期する。
    ロジック：
      1. 旧Tripの日付 → Trip内で何日目かを計算
      2. 新Tripの日付リストの同じ日数位置へ移動
    """

    print("\n=== sync_cost_dates DEBUG START ===")
    print("trip_id:", trip_id)

    # ---------------------------------------------------------
    # 1. travel.db の新しい日付リスト（正本）
    # ---------------------------------------------------------
    new_dates = build_date_list(trip_id)
    print("new_dates (from travel.db):", new_dates)

    if not new_dates:
        print("ERROR: new_dates is empty. trip_rows が生成されていません。")
        print("=== sync_cost_dates DEBUG END ===\n")
        return

    # ---------------------------------------------------------
    # 2. travel.db から旧Tripの start_date を取得
    # ---------------------------------------------------------
    conn_t = sqlite3.connect(TRAVEL_DB_PATH)
    cur_t = conn_t.cursor()
    cur_t.execute("SELECT date_start FROM trips WHERE id = ?", (trip_id,))
    row = cur_t.fetchone()
    conn_t.close()

    if not row:
        print("ERROR: trips テーブルに trip_id が存在しません。")
        print("=== sync_cost_dates DEBUG END ===\n")
        return

    old_start = row[0]
    print("old_start:", old_start)

    old_start_dt = datetime.strptime(old_start, "%Y/%m/%d")

    # ---------------------------------------------------------
    # 3. cost.db 側の古い日付を取得
    # ---------------------------------------------------------
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT date FROM transport_costs WHERE trip_id = ?", (trip_id,))
    old_t = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT DISTINCT date FROM other_costs WHERE trip_id = ?", (trip_id,))
    old_o = [r[0] for r in cur.fetchall()]

    old_dates = sorted(set(old_t + old_o))
    print("old_dates (from cost.db):", old_dates)

    if not old_dates:
        print("WARNING: cost.db に日付がありません。初期行が生成されていません。")
        print("=== sync_cost_dates DEBUG END ===\n")
        return

    # ---------------------------------------------------------
    # 4. 旧日付 → 新日付 のマッピングを作る（Trip内日数方式）
    # ---------------------------------------------------------
    mapping = {}

    for old in old_dates:
        old_dt = datetime.strptime(old, "%Y/%m/%d")
        day_index = (old_dt - old_start_dt).days

        print(f"\n[OLD] {old} → day_index = {day_index}")

        if 0 <= day_index < len(new_dates):
            new_date = new_dates[day_index]
        else:
            new_date = new_dates[-1]

        print(f"[MAP] {old} → {new_date}")

        mapping[old] = new_date

    print("\nFinal mapping:", mapping)

    # ---------------------------------------------------------
    # 5. cost.db の日付を一括更新
    # ---------------------------------------------------------
    for old, new in mapping.items():
        cur.execute("UPDATE transport_costs SET date = ? WHERE trip_id = ? AND date = ?", (new, trip_id, old))
        cur.execute("UPDATE other_costs SET date = ? WHERE trip_id = ? AND date = ?", (new, trip_id, old))

    conn.commit()
    conn.close()

    print("=== sync_cost_dates DEBUG END ===\n")
