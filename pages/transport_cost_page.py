# pages/transport_cost_page.py

import flet as ft
import sqlite3

from components.cost.transport_cost_table import TransportCostTable
from db.transport_database import (
    get_transport_costs_by_date,
    get_transport_total_for_trip,
    add_transport_cost,
    delete_transport_cost,
    update_transport_cost,
)
from components.cost.transport_handlers import (
    handle_add,
    handle_edit,
    handle_delete,
)
from components.others.sync_logic import is_sync, toggle_sync, should_sync
from components.others.counter import build_counter
from components.cost.common.rebuild_transport import rebuild_transport  # Transport 用に後で rename 予定

TRAVEL_DB_PATH = "travel.db"
COST_DB_PATH = "cost.db"


def get_trip_name(trip_id: int) -> str | None:
    conn = sqlite3.connect(TRAVEL_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM trips WHERE id = ?", (trip_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def get_trip_dates(trip_id: int):
    conn = sqlite3.connect(COST_DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT date FROM transport_costs WHERE trip_id = ? GROUP BY date ORDER BY date",
        (trip_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]


def TransportCostModePage(page, trip_id, clicked_date):

    # その日の行を取得（なければ初期行を作る）
    rows = get_transport_costs_by_date(trip_id, clicked_date)
    if len(rows) == 0:
        add_transport_cost(trip_id, clicked_date)
        rows = get_transport_costs_by_date(trip_id, clicked_date)

    # Trip 情報
    trip_name = get_trip_name(trip_id) or "（名称未設定）"
    trip_total = get_transport_total_for_trip(trip_id)

    # 追加行数カウンター
    add_count = 1

    def get_add_count():
        return add_count

    def set_add_count(v):
        nonlocal add_count
        add_count = v
        page.update()

    counter = build_counter(get_add_count, set_add_count)


    # 上部 UI
    top_buttons = ft.Row(
        [
            ft.ElevatedButton(
                "金額計算モード（メイン）に戻る",
                bgcolor=ft.Colors.ORANGE,
                color=ft.Colors.WHITE,
                on_click=lambda e: page.go(f"/trip/{trip_id}/cost"),
            ),
        ],
        spacing=20,
    )

    title_row_1 = ft.Row([
        ft.Text("交通費専用モード", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
    ])

    def build_sync_button():
        mode = is_sync()
        bg = ft.Colors.LIGHT_GREEN_200 if mode else ft.Colors.PINK_200

        def on_toggle_sync(e):
            toggle_sync()
            rebuild_transport(page, trip_id, clicked_date)

        return ft.ElevatedButton(
            f"同期モード：{'ON' if mode else 'OFF'}",
            bgcolor=bg,
            color=ft.Colors.BLACK,
            on_click=on_toggle_sync,
            height=40,
        )

    sync_button = build_sync_button()

    title_row_2 = ft.Row(
        [
            ft.Text(
                trip_name,
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
                expand=1,
            ),

            sync_button,
            counter,

            ft.Container(width=20),  # スペーサー

            ft.Text(
                f"交通費総額：{trip_total:,} 円",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
            ),

        ],
        spacing=20,
    )

    # handlers生成
    add_handler = handle_add(page, trip_id, clicked_date)
    edit_handler = handle_edit(page, trip_id, clicked_date)
    delete_handler = handle_delete(page, trip_id, clicked_date)

    def on_add_wrapper(date, count, _sync_flag_from_table):
        sync_flag = should_sync("transport_cost", "add_row")
        for _ in range(count):
            add_handler(date, sync_flag)

    def on_edit_wrapper(row_id, col, val, _sync_flag_from_table):
        sync_flag = should_sync("transport_cost", "edit", col)
        edit_handler(row_id, col, val, sync_flag)

    def on_delete_wrapper(row_id, _sync_flag_from_table):
        sync_flag = should_sync("transport_cost", "delete_row")
        delete_handler(row_id, sync_flag)



    # 1日分の TransportCostTable
    table = TransportCostTable(
        page=page,
        trip_id=trip_id,
        date=clicked_date,
        rows=rows,
        on_add=on_add_wrapper,      # sync_flag は TransportCostPage 側で決める
        on_delete=on_delete_wrapper,
        on_edit=on_edit_wrapper,
        get_add_count=get_add_count,  #カウンターを渡す
    )

    return ft.Column(
        controls=[
            top_buttons,
            title_row_1,
            title_row_2,
            ft.Divider(height=10),

            # ★ TripTopPage と同じ構造
            ft.Container(
                content=ft.Column(
                    controls=[table],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
            ),
        ],
        expand=True,
    )
