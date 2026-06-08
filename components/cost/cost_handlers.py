# components/cost/cost_handlers.py

import sqlite3
from db.cost_database import (
    update_other_cost,
    add_other_cost,
    delete_other_cost,
)
from components.cost.common.rebuild_cost import rebuild_cost

def handle_edit(page, grouped_rows, transport_totals, date_list, trip_id, page_builder):

    def _edit(row_id, col, val, sync_flag):
        update_other_cost(row_id, col, val)

        # メモリ更新
        ...

        if sync_flag:
            rebuild_cost(page, trip_id, page_builder)

    return _edit

def handle_add(page, trip_id, page_builder):
    def _add(date, sync_flag):
        add_other_cost(trip_id, date)
        if sync_flag:
            rebuild_cost(page, trip_id, page_builder)
    return _add

def handle_delete(page, trip_id, page_builder):
    def _delete(row_id, sync_flag):
        delete_other_cost(row_id)
        if sync_flag:
            rebuild_cost(page, trip_id, page_builder)
    return _delete
