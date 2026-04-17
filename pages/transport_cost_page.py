# pages/transport_cost_page.py

import flet as ft

from components.cost.transport_cost_table import TransportCostTable
from db.cost_database import (
    get_transport_costs_by_date,
    get_transport_total_for_trip,
    add_transport_cost,
    delete_transport_cost,
    update_transport_cost,
)


def TransportCostMode(page, trip_id, date):

    # -------------------------
    # 最新データ取得
    # -------------------------
    rows = get_transport_costs_by_date(trip_id, date)
    trip_total = get_transport_total_for_trip(trip_id)

    # -------------------------
    # DB 接続済みハンドラ
    # -------------------------
    def handle_add():
        add_transport_cost(trip_id, date)
        page.go(f"/trip/{trip_id}/cost/transport/{date}")

    def handle_delete(row_id):
        delete_transport_cost(row_id)
        page.go(f"/trip/{trip_id}/cost/transport/{date}")

    def handle_edit(row_id, col, val):
        update_transport_cost(row_id, col, val)

        # category を変更した場合は subcategory の選択肢を更新するため再読み込み
        if col == "category":
            page.go(f"/trip/{trip_id}/cost/transport/{date}")

    # -------------------------
    # 上部ボタン
    # -------------------------
    top_buttons = ft.Row(
        [
            ft.ElevatedButton(
                "金額計算モード（メイン）に戻る",
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                on_click=lambda e: page.go(f"/trip/{trip_id}/cost")
            ),
        ],
        spacing=20,
    )

    # -------------------------
    # タイトル + Trip全体の交通費総額
    # -------------------------
    title_row = ft.Row(
        [
            ft.Text("交通費専用モード", size=22, weight=ft.FontWeight.BOLD, expand=1),
            ft.Text(f"交通費総額：{trip_total:,} 円", size=20, weight=ft.FontWeight.BOLD),
        ]
    )

    # -------------------------
    # テーブル本体
    # -------------------------
    table = TransportCostTable(
        page=page,
        trip_id=trip_id,
        date=date,
        rows=rows,
        on_add=handle_add,
        on_delete=handle_delete,
        on_edit=handle_edit,
    )

    return ft.View(
        route=f"/trip/{trip_id}/cost/transport/{date}",
        controls=[
            top_buttons,
            title_row,
            ft.Divider(height=10),
            table,
        ],
        scroll=ft.ScrollMode.AUTO,
    )
