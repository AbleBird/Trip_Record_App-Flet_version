# pages/transport_cost_page.py

import flet as ft
import sqlite3
from urllib.parse import urlencode, parse_qs
from functools import partial

from components.cost.transport_cost_table import TransportCostTable
from db.cost_database import (
    get_transport_costs_by_date,
    get_transport_total_for_trip,
    add_transport_cost,
    delete_transport_cost,
    update_transport_cost,
)

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

    # -------------------------
    # URL クエリ解析（YYYY/MM/DD のまま扱う）
    # -------------------------
    qs = parse_qs(str(page.query))
    open_dates = set(qs.get("open", [""])[0].split(",")) if "open" in qs else set()
    open_dates.discard("")

    # 最初に押された日付は必ず展開
    open_dates.add(clicked_date)

    # -------------------------
    # Trip の全日付（初期行が無い場合は作る）
    # -------------------------
    date_list = get_trip_dates(trip_id)

    if clicked_date not in date_list:
        add_transport_cost(trip_id, clicked_date)
        date_list = get_trip_dates(trip_id)

    # -------------------------
    # Trip 情報
    # -------------------------
    trip_name = get_trip_name(trip_id) or "（名称未設定）"
    trip_total = get_transport_total_for_trip(trip_id)

    # -------------------------
    # URL 更新（YYYY/MM/DD のまま）
    # -------------------------
    def go_with_open():
        q = urlencode({"open": ",".join(sorted(open_dates))})
        page.go(f"/trip/{trip_id}/cost/transport/{clicked_date}?{q}")

    # -------------------------
    # 展開/折りたたみ
    # -------------------------
    def expand_date(d):
        open_dates.add(d)
        go_with_open()

    def collapse_date(d):
        open_dates.discard(d)
        go_with_open()

    # -------------------------
    # CRUD
    # -------------------------
    def handle_add(d):
        add_transport_cost(trip_id, d)
        go_with_open()

    def handle_delete(d, row_id):
        delete_transport_cost(row_id)
        go_with_open()

    def handle_edit(d, row_id, col, val):
        update_transport_cost(row_id, col, val)

        if col in ("category", "amount"):
            go_with_open()
            return

    # -------------------------
    # 上部 UI
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

    title_row_1 = ft.Row([ft.Text("交通費専用モード", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)])
    title_row_2 = ft.Row(
        [
            ft.Text(trip_name, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, expand=1),
            ft.Text(f"交通費総額：{trip_total:,} 円", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
        ]
    )

    # -------------------------
    # 日付ごとの UI
    # -------------------------
    date_blocks = []

    for d in date_list:

        if d in open_dates:
            # 非表示ボタン
            date_blocks.append(
                ft.ElevatedButton(
                    f"{d} の交通費を非表示",
                    bgcolor=ft.Colors.GREY_300,
                    color=ft.Colors.BLACK,
                    on_click=partial(lambda _e, dd: collapse_date(dd), dd=d),
                )
            )

            # 行取得（初期行生成）
            rows = get_transport_costs_by_date(trip_id, d)
            if len(rows) == 0:
                add_transport_cost(trip_id, d)
                rows = get_transport_costs_by_date(trip_id, d)

            # テーブル
            date_blocks.append(
                TransportCostTable(
                    page=page,
                    trip_id=trip_id,
                    date=d,
                    rows=rows,
                    on_add=lambda dd=d: handle_add(dd),
                    on_delete=lambda row_id, dd=d: handle_delete(dd, row_id),
                    on_edit=lambda row_id, col, val, dd=d: handle_edit(dd, row_id, col, val),
                )
            )

        else:
            # 表示ボタン
            date_blocks.append(
                ft.ElevatedButton(
                    f"{d} の交通費を表示",
                    bgcolor=ft.Colors.BLUE_100,
                    color=ft.Colors.BLACK,
                    on_click=partial(lambda _e, dd: expand_date(dd), dd=d),
                )
            )

    # -------------------------
    # View
    # -------------------------
    return ft.View(
        route=f"/trip/{trip_id}/cost/transport/{clicked_date}",
        controls=[
            top_buttons,
            title_row_1,
            title_row_2,
            ft.Divider(height=10),
            ft.Column(date_blocks, spacing=20),
        ],
        scroll=ft.ScrollMode.AUTO,
        bgcolor=ft.Colors.WHITE,
    )
