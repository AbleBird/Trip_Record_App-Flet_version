#components/cost/cost_handlers.py

import sqlite3
from db.cost_database import (
    update_other_cost,
    add_other_cost,
    delete_other_cost,
)

TRAVEL_DB_PATH = "travel.db"


# ---------------------------------------------------------
# 編集（on_edit）
# ---------------------------------------------------------
def handle_edit(page, grouped_rows, transport_totals, date_list, trip_id):

    def _edit(row_id, col, val):
        # DB 更新
        update_other_cost(row_id, col, val)

        # メモリ更新
        for date, rows in grouped_rows.items():
            for r in rows:
                if r["id"] == row_id:
                    if col == "amount":
                        try:
                            r[col] = int(val.replace(",", ""))
                        except:
                            r[col] = 0
                    else:
                        r[col] = val

        # CostModePage を再構築
        page.go(f"/trip/{trip_id}/cost")

    return _edit

# ---------------------------------------------------------
# 行追加（on_add）
# ---------------------------------------------------------
def handle_add(page, trip_id):

    def _add(date):
        add_other_cost(trip_id, date)
        page.go(f"/trip/{trip_id}/cost")

    return _add


# ---------------------------------------------------------
# 行削除（on_delete）
# ---------------------------------------------------------
def handle_delete(page, trip_id):

    def _delete(row_id):
        delete_other_cost(row_id)
        page.go(f"/trip/{trip_id}/cost")

    return _delete


# ---------------------------------------------------------
# 並べ替え（on_reorder）
# ---------------------------------------------------------
def handle_reorder(page, grouped_rows, trip_id):

    def _reorder(date, old_index, new_index):
        rows = grouped_rows.get(date, [])
        if not rows:
            return
        if old_index < 0 or old_index >= len(rows):
            return
        if new_index < 0 or new_index >= len(rows):
            return

        item = rows.pop(old_index)
        rows.insert(new_index, item)
        grouped_rows[date] = rows

        # 並べ替え後もページ再構築（他と同じ）
        page.go(f"/trip/{trip_id}/cost")

    return _reorder

