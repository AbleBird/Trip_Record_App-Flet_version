# pages/cost_mode_page.py

import flet as ft
import sqlite3
from datetime import datetime, timedelta

from components.cost.cost_table import CostTable
from db.cost_database import get_other_costs, get_transport_totals
from components.cost.cost_handlers import (
    handle_edit,
    handle_add,
    handle_delete,
    handle_reorder,
)

TRAVEL_DB_PATH = "travel.db"


def get_trip_dates(trip_id: int):
    conn = sqlite3.connect(TRAVEL_DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT date_start, date_end FROM trips WHERE id = ?", (trip_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return []

    ds, de = row
    ds_date = datetime.strptime(ds, "%Y/%m/%d")
    de_date = datetime.strptime(de, "%Y/%m/%d")

    delta = (de_date - ds_date).days + 1
    return [
        (ds_date + timedelta(days=i)).strftime("%Y/%m/%d")
        for i in range(delta)
    ]


# ---------------------------------------------------------
# 日付ごとに other_costs をグループ化
# ---------------------------------------------------------
def group_by_date(other_costs):
    grouped = {}
    for row in other_costs:
        date = row["date"]
        if date not in grouped:
            grouped[date] = []
        grouped[date].append(row)
    return grouped


# ---------------------------------------------------------
# クロス表の構築
# ---------------------------------------------------------
def build_cross_table(grouped_rows, transport_totals):

    if not grouped_rows:
        return ft.Container(
            content=ft.Text(
                "まだ費用が入力されていません",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
            ),
            padding=10,
            bgcolor=ft.Colors.GREY_200,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
        )

    columns = [
        ft.DataColumn(ft.Text("日付", color=ft.Colors.BLACK)),
        ft.DataColumn(ft.Text("交通費", color=ft.Colors.BLACK)),
        ft.DataColumn(ft.Text("食費", color=ft.Colors.BLACK)),
        ft.DataColumn(ft.Text("宿泊費", color=ft.Colors.BLACK)),
        ft.DataColumn(ft.Text("お土産", color=ft.Colors.BLACK)),
        ft.DataColumn(ft.Text("その他", color=ft.Colors.BLACK)),
        ft.DataColumn(ft.Text("合計", color=ft.Colors.BLACK)),
    ]

    rows = []

    for date, items in grouped_rows.items():

        food = sum(to_int(r["amount"]) for r in items if r["type"] == "食費")
        hotel = sum(to_int(r["amount"]) for r in items if r["type"] == "宿泊費")
        gift = sum(to_int(r["amount"]) for r in items if r["type"] == "お土産代")
        other = sum(to_int(r["amount"]) for r in items if r["type"] == "その他諸費")

        transport = to_int(transport_totals.get(date, 0))
        total = food + hotel + gift + other + transport


        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(date, color=ft.Colors.BLACK)),
                    ft.DataCell(ft.Text(f"{transport:,}", color=ft.Colors.BLACK)),
                    ft.DataCell(ft.Text(f"{food:,}", color=ft.Colors.BLACK)),
                    ft.DataCell(ft.Text(f"{hotel:,}", color=ft.Colors.BLACK)),
                    ft.DataCell(ft.Text(f"{gift:,}", color=ft.Colors.BLACK)),
                    ft.DataCell(ft.Text(f"{other:,}", color=ft.Colors.BLACK)),
                    ft.DataCell(ft.Text(f"{total:,}", color=ft.Colors.BLACK)),
                ]
            )
        )

    # ★ ここから下をすべて to_int 経由にする
    total_transport = sum(to_int(v) for v in transport_totals.values())
    total_food = sum(
        to_int(r["amount"])
        for rows in grouped_rows.values()
        for r in rows
        if r["type"] == "食費"
    )
    total_hotel = sum(
        to_int(r["amount"])
        for rows in grouped_rows.values()
        for r in rows
        if r["type"] == "宿泊費"
    )
    total_gift = sum(
        to_int(r["amount"])
        for rows in grouped_rows.values()
        for r in rows
        if r["type"] == "お土産代"
    )
    total_other = sum(
        to_int(r["amount"])
        for rows in grouped_rows.values()
        for r in rows
        if r["type"] == "その他諸費"
    )

    total_all = total_transport + total_food + total_hotel + total_gift + total_other

    rows.append(
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("合計", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
                ft.DataCell(ft.Text(f"{total_transport:,}", color=ft.Colors.BLACK)),
                ft.DataCell(ft.Text(f"{total_food:,}", color=ft.Colors.BLACK)),
                ft.DataCell(ft.Text(f"{total_hotel:,}", color=ft.Colors.BLACK)),
                ft.DataCell(ft.Text(f"{total_gift:,}", color=ft.Colors.BLACK)),
                ft.DataCell(ft.Text(f"{total_other:,}", color=ft.Colors.BLACK)),
                ft.DataCell(ft.Text(f"{total_all:,}", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
            ]
        )
    )

    return ft.DataTable(columns=columns, rows=rows)

def to_int(v):
    try:
        return int(v)
    except Exception:
        return 0

# ---------------------------------------------------------
# 金額計算モード（メインページ）
# ---------------------------------------------------------
def CostModePage(page, trip_id):

    # Trip の日付リスト
    date_list = get_trip_dates(trip_id)

    # DB からデータ取得
    other_costs = get_other_costs(trip_id)
    transport_totals = get_transport_totals(trip_id)

    # transport_totals の値を int に統一
    for d in list(transport_totals.keys()):
        try:
            transport_totals[d] = int(transport_totals[d])
        except:
            transport_totals[d] = 0

    # other_costs を日付ごとにグループ化
    grouped_rows = group_by_date(other_costs)

    # Trip の全日付をプリセット
    if date_list:
        for d in date_list:
            if d not in grouped_rows:
                grouped_rows[d] = []
        grouped_rows = dict(sorted(grouped_rows.items(), key=lambda x: x[0]))

    # 総額計算（文字列混入対策で必ず int に変換してから足す）
    total_amount = sum(
        sum(to_int(r["amount"]) for r in grouped_rows.get(d, []))
        + to_int(transport_totals.get(d, 0))
        for d in date_list
    )


    # 上部ボタン
    top_buttons = ft.Row(
        [
            ft.ElevatedButton(
                "TripTopPageに戻る",
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                on_click=lambda e: page.go(f"/trip/{trip_id}")
            ),
            ft.ElevatedButton(
                "Mediaモード",
                bgcolor=ft.Colors.PURPLE,
                color=ft.Colors.WHITE,
                on_click=lambda e: page.go(f"/trip/{trip_id}/media")
            ),
        ],
        spacing=20,
    )

    # タイトル + 総額
    title_row = ft.Row(
        [
            ft.Text(
                "金額計算モード（メイン）",
                size=22,
                weight=ft.FontWeight.BOLD,
                expand=1,
                color=ft.Colors.BLACK,
            ),
            ft.Text(
                f"総額：{total_amount:,} 円",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
            ),
        ]
    )

    # クロス表
    cross_table = build_cross_table(grouped_rows, transport_totals)

    # handlers 生成
    on_edit = handle_edit(page, grouped_rows, transport_totals, date_list, trip_id)
    on_add = handle_add(page, trip_id)
    on_delete = handle_delete(page, trip_id)
    on_reorder = handle_reorder(page, grouped_rows, trip_id)

    # 詳細入力テーブル
    detail_table = CostTable(
        page=page,
        trip_id=trip_id,
        grouped_rows=grouped_rows,
        transport_totals=transport_totals,
        date_list=date_list,
        on_add=on_add,
        on_delete=on_delete,
        on_edit=on_edit,
        on_open_transport=lambda d: page.go(f"/trip/{trip_id}/cost/transport/{d}"),
        on_reorder=on_reorder,
    )

    return ft.ListView(
        expand=True,
        spacing=10,
        controls=[
            top_buttons,
            title_row,
            ft.Divider(height=10),
            cross_table,
            ft.Divider(height=20),
            detail_table,
        ]
    )
