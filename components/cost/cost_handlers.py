#components/cost/cost_handlers.py

import sqlite3
from db.cost_database import (
    update_other_cost,
    add_other_cost,
    delete_other_cost,
)
from components.others.sync_logic import should_sync

TRAVEL_DB_PATH = "travel.db"


# ---------------------------------------------------------
# 編集（on_edit）
# ---------------------------------------------------------
def handle_edit(page, grouped_rows, transport_totals, date_list, trip_id):

    def _edit(row_id, col, val, sync_flag):
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

        # 同期ONのときだけページ再構築
        if sync_flag:
            page.go(f"/trip/{trip_id}/cost")

    return _edit


# ---------------------------------------------------------
# 行追加（on_add）
# ---------------------------------------------------------
def handle_add(page, trip_id):

    def _add(date, sync_flag):
        add_other_cost(trip_id, date)

        # 同期ONのときだけページ再構築
        if sync_flag:
            page.go(f"/trip/{trip_id}/cost")

    return _add


# ---------------------------------------------------------
# 行削除（on_delete）
# ---------------------------------------------------------
def handle_delete(page, trip_id):

    def _delete(row_id, sync_flag):
        delete_other_cost(row_id)

        # 同期ONのときだけページ再構築
        if sync_flag:
            page.go(f"/trip/{trip_id}/cost")

    return _delete