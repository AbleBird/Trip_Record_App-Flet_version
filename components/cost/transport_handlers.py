# components/cost/transport_handlers.py

from db.transport_database import (
    add_transport_cost,
    update_transport_cost,
    delete_transport_cost,
)
from components.cost.common.rebuild_transport import rebuild_transport


# ---------------------------------------------------------
# 編集（on_edit）
# ---------------------------------------------------------
def handle_edit(page, trip_id, clicked_date):

    def _edit(row_id, col, val, sync_flag):
        # DB 更新
        update_transport_cost(row_id, col, val)

        # 同期ONのときだけページ再構築
        if sync_flag:
            rebuild_transport(page, trip_id, clicked_date)

    return _edit


# ---------------------------------------------------------
# 行追加（on_add）
# ---------------------------------------------------------
def handle_add(page, trip_id, clicked_date):

    def _add(date, sync_flag):
        add_transport_cost(trip_id, date)

        if sync_flag:
            rebuild_transport(page, trip_id, clicked_date)

    return _add


# ---------------------------------------------------------
# 行削除（on_delete）
# ---------------------------------------------------------
def handle_delete(page, trip_id, clicked_date):

    def _delete(row_id, sync_flag):
        delete_transport_cost(row_id)

        if sync_flag:
            rebuild_transport(page, trip_id, clicked_date)

    return _delete
