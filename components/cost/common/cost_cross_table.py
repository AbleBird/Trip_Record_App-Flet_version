# components/cost/common/cost_cross_table.py

import flet as ft
from utils.number import to_int

# CostTable と同じ総幅（1140px）になるように調整
CROSS_COL_WIDTHS = [140, 150, 150, 150, 150, 200, 200]

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
                    ft.DataCell(ft.Container(ft.Text(date, color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[0])),
                    ft.DataCell(ft.Container(ft.Text(f"{transport:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[1])),
                    ft.DataCell(ft.Container(ft.Text(f"{food:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[2])),
                    ft.DataCell(ft.Container(ft.Text(f"{hotel:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[3])),
                    ft.DataCell(ft.Container(ft.Text(f"{gift:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[4])),
                    ft.DataCell(ft.Container(ft.Text(f"{other:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[5])),
                    ft.DataCell(ft.Container(ft.Text(f"{total:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[6])),
                ]
            )
        )

    # 合計行
    total_transport = sum(to_int(v) for v in transport_totals.values())
    total_food = sum(to_int(r["amount"]) for rows in grouped_rows.values() for r in rows if r["type"] == "食費")
    total_hotel = sum(to_int(r["amount"]) for rows in grouped_rows.values() for r in rows if r["type"] == "宿泊費")
    total_gift = sum(to_int(r["amount"]) for rows in grouped_rows.values() for r in rows if r["type"] == "お土産代")
    total_other = sum(to_int(r["amount"]) for rows in grouped_rows.values() for r in rows if r["type"] == "その他諸費")

    total_all = total_transport + total_food + total_hotel + total_gift + total_other

    rows.append(
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Container(ft.Text("合計", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[0])),
                ft.DataCell(ft.Container(ft.Text(f"{total_transport:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[1])),
                ft.DataCell(ft.Container(ft.Text(f"{total_food:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[2])),
                ft.DataCell(ft.Container(ft.Text(f"{total_hotel:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[3])),
                ft.DataCell(ft.Container(ft.Text(f"{total_gift:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[4])),
                ft.DataCell(ft.Container(ft.Text(f"{total_other:,}", color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[5])),
                ft.DataCell(ft.Container(ft.Text(f"{total_all:,}", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK), width=CROSS_COL_WIDTHS[6])),
            ]
        )
    )

    return ft.DataTable(
        columns=columns,
        rows=rows,
        heading_row_color=ft.Colors.GREY_200,
        data_row_color={"hovered": ft.Colors.GREY_100},
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=5,
    )
