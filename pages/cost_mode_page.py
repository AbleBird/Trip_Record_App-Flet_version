# pages/cost_mode_page.py

import flet as ft
from components.cost.cost_table import CostTable
from db.cost_database import get_other_costs, get_transport_totals, update_other_cost
from db.cost_database import add_other_cost, delete_other_cost
import sqlite3
from datetime import datetime, timedelta

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


print("CostModePage loaded")


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
# クロス表の構築（空データ対策つき）
# ---------------------------------------------------------
def build_cross_table(grouped_rows, transport_totals):

    # ★ 空データ対策：費用が1件もない場合はメッセージ表示
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

    # 列タイトル
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

    # 日付ごとの行（grouped_rows は日付順にソート済みを想定）
    for date, items in grouped_rows.items():

        # 各カテゴリの合計
        food = sum(r["amount"] for r in items if r["type"] == "食費")
        hotel = sum(r["amount"] for r in items if r["type"] == "宿泊費")
        gift = sum(r["amount"] for r in items if r["type"] == "お土産代")
        other = sum(r["amount"] for r in items if r["type"] == "その他諸費")

        transport = transport_totals.get(date, 0)

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

    # Trip 全体の合計行
    total_transport = sum(transport_totals.values())
    total_food = sum(
        r["amount"] for rows in grouped_rows.values() for r in rows if r["type"] == "食費"
    )
    total_hotel = sum(
        r["amount"] for rows in grouped_rows.values() for r in rows if r["type"] == "宿泊費"
    )
    total_gift = sum(
        r["amount"] for rows in grouped_rows.values() for r in rows if r["type"] == "お土産代"
    )
    total_other = sum(
        r["amount"] for rows in grouped_rows.values() for r in rows if r["type"] == "その他諸費"
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


# ---------------------------------------------------------
# 金額計算モード（メインページ）
# ---------------------------------------------------------
def CostModePage(page, trip_id):

    # Trip の日付リスト（TripTopPage と同じ基準）
    date_list = get_trip_dates(trip_id)

    # -------------------------
    # DB からデータ取得
    # -------------------------
    other_costs = get_other_costs(trip_id)
    transport_totals = get_transport_totals(trip_id)

    # other_costs を日付ごとにグループ化
    grouped_rows = group_by_date(other_costs)

    # ★ 日付プリセット：Trip の全日付について、費用がなくても空リストを用意
    if date_list:
        for d in date_list:
            if d not in grouped_rows:
                grouped_rows[d] = []

        # ★ 日付順にソートしておく（クロス表・入力テーブル両方の順序を揃える）
        grouped_rows = dict(sorted(grouped_rows.items(), key=lambda x: x[0]))

    # Trip 全体の総額（date_list があればそれを基準に計算）
    if date_list:
        total_amount = 0
        for d in date_list:
            rows = grouped_rows.get(d, [])
            total_amount += sum(r["amount"] for r in rows)
            total_amount += transport_totals.get(d, 0)
    else:
        # date_list が取れなかった場合のフォールバック
        total_amount = sum(
            sum(r["amount"] for r in rows) + transport_totals.get(date, 0)
            for date, rows in grouped_rows.items()
        )

    # -------------------------
    # 上部ボタン
    # -------------------------
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

    # -------------------------
    # タイトル + 総額
    # -------------------------
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

    # -------------------------
    # クロス表
    # -------------------------
    cross_table = build_cross_table(grouped_rows, transport_totals)

    # -------------------------
    # 編集ハンドラ
    # -------------------------
    def handle_other_cost_edit(row_id, col, val):
        print("EDIT", row_id, col, val)
        update_other_cost(row_id, col, val)

    # -------------------------
    # 並べ替えハンドラ（メモリ上のみ）
    # -------------------------
    def on_reorder(date, old_index, new_index):
        rows = grouped_rows.get(date, [])
        if not rows:
            return

        # その他費用行（＝全行）を対象に単純に並べ替え
        if old_index < 0 or old_index >= len(rows):
            return
        if new_index < 0 or new_index >= len(rows):
            return

        item = rows.pop(old_index)
        rows.insert(new_index, item)
        grouped_rows[date] = rows

        page.update()

    # -------------------------
    # 詳細入力テーブル（交通費以外）
    # -------------------------
    detail_table = CostTable(
        page=page,
        trip_id=trip_id,
        grouped_rows=grouped_rows,
        transport_totals=transport_totals,
        date_list=date_list,
        on_add=lambda date: (
            add_other_cost(trip_id, date),
            page.go(f"/trip/{trip_id}/cost")
        ),
        on_delete=lambda row_id: (
            delete_other_cost(row_id),
            page.go(f"/trip/{trip_id}/cost")
        ),
        on_edit=handle_other_cost_edit,
        on_open_transport=lambda date: page.go(f"/trip/{trip_id}/cost/transport/{date}"),
        on_reorder=on_reorder,
    )

    # -------------------------
    # ページ全体
    # -------------------------
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
