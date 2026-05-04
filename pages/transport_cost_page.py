# pages/transport_cost_page.py

import flet as ft
import sqlite3

from components.cost.transport_cost_table import TransportCostTable
from db.cost_database import (
    get_transport_costs_by_date,
    get_transport_total_for_trip,
    add_transport_cost,
    delete_transport_cost,
    update_transport_cost,
)

TRAVEL_DB_PATH = "travel.db"


# ---------------------------------------------------------
# Trip名取得（CostModePage と同じ思想で travel.db から直接読む）
# ---------------------------------------------------------
def get_trip_name(trip_id: int) -> str | None:
    conn = sqlite3.connect(TRAVEL_DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT name FROM trips WHERE id = ?", (trip_id,))
    row = cur.fetchone()

    conn.close()

    if not row:
        return None

    return row[0]


def TransportCostModePage(page, trip_id, date):

    # -------------------------
    # 最新データ取得
    # -------------------------
    rows = get_transport_costs_by_date(trip_id, date)
    trip_total = get_transport_total_for_trip(trip_id)

    # Trip名取得（null対策）
    trip_name = get_trip_name(trip_id) or "（名称未設定）"

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
                on_click=lambda e: page.go(f"/trip/{trip_id}/cost"),
            ),
        ],
        spacing=20,
    )

    # -------------------------
    # タイトル行（1段目：固定タイトル）
    # -------------------------
    title_row_1 = ft.Row(
        [
            ft.Text(
                "交通費専用モード",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
                expand=1,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # -------------------------
    # タイトル行（2段目：Trip名 + 交通費総額）
    # -------------------------
    title_row_2 = ft.Row(
        [
            ft.Text(
                trip_name,
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
                expand=1,
            ),
            ft.Text(
                f"交通費総額：{trip_total:,} 円",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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

    # -------------------------
    # View 全体
    # -------------------------
    return ft.View(
        route=f"/trip/{trip_id}/cost/transport/{date}",
        controls=[
            top_buttons,
            title_row_1,
            title_row_2,
            ft.Divider(height=10),
            table,
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=ft.Colors.WHITE,
    )
