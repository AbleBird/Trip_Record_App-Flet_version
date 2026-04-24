# cost_rows.py

import flet as ft
from components.cost.common.cost_elements import (cell, make_icon_button, COL_WIDTHS, TYPE_OPTIONS)

# 日付行（外枠のみ）
def make_date_row(date):
    return ft.Row(
                [
                    ft.Container(width=84),  # 操作列は空
                    cell(
                        ft.Text(date, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        width=sum(COL_WIDTHS[:4]),
                        bgcolor=ft.Colors.GREY_200,
                    ),
                    cell(ft.Text(""), width=COL_WIDTHS[4], bgcolor=ft.Colors.GREY_200),
                    cell(ft.Text(""), width=COL_WIDTHS[5], bgcolor=ft.Colors.GREY_200),
                ],
                spacing=0,
            )

# 交通費行（6列）
def make_transport_row(date, transport_amount, on_open_transport):
    return ft.Row(
                [
                    ft.Container(width=84),  # 操作列は空
                    cell(
                        ft.Text("交通費", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        width=COL_WIDTHS[0],
                        bgcolor=ft.Colors.ORANGE_100,
                        align=ft.alignment.center,
                    ),
                    cell(
                        ft.ElevatedButton(
                            "交通費専用モードへ",
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                            on_click=lambda e, d=date: on_open_transport(d),
                        ),
                        width=COL_WIDTHS[1],
                        bgcolor=ft.Colors.ORANGE_100,
                    ),
                    cell(
                        ft.Text("総額", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        width=COL_WIDTHS[2],
                        bgcolor=ft.Colors.ORANGE_100,
                    ),
                    cell(
                        ft.Text(f"{transport_amount:,} 円", color=ft.Colors.BLACK),
                        width=COL_WIDTHS[3],
                        bgcolor=ft.Colors.ORANGE_100,
                        align=ft.alignment.center_right,
                    ),
                    cell(ft.Text(""), width=COL_WIDTHS[4], bgcolor=ft.Colors.ORANGE_100),
                    cell(ft.Text(""), width=COL_WIDTHS[5], bgcolor=ft.Colors.ORANGE_100),
                ],
                spacing=0,
            )

def make_other_cost_row(
    page,
    row,
    idx,
    date,
    on_edit,
    on_delete,
    on_reorder,
    make_icon_button,
    operation_column,   # ← 追加
    TYPE_OPTIONS,       # ← 追加
):
    row_id = row["id"]  # ← row_id をここで定義
    
    return ft.Row(
        [
            operation_column,

            # 1列目：Type（cell）
            cell(
                ft.Container(
                    content=ft.Dropdown(
                        value=row["type"],
                        options=[
                            ft.dropdown.Option(t, text_style=ft.TextStyle(color=ft.Colors.BLACK))
                            for t in TYPE_OPTIONS
                        ],
                        width=COL_WIDTHS[0] - 10,
                        border=ft.InputBorder.NONE,
                        bgcolor=ft.Colors.WHITE,
                        color=ft.Colors.BLACK,
                        text_style=ft.TextStyle(color=ft.Colors.BLACK),
                    ),
                    height=48,
                    alignment=ft.alignment.center,
                ),
                width=COL_WIDTHS[0],
            ),

            # 2列目：タイトル
            cell(
                ft.TextField(
                    value=row["title"],
                    width=COL_WIDTHS[1] - 10,
                    border=ft.InputBorder.NONE,
                    color=ft.Colors.BLACK,
                    on_blur=lambda e, rid=row_id: on_edit(rid, "title", e.control.value),
                ),
                width=COL_WIDTHS[1],
            ),

            # 3列目：商品名
            cell(
                ft.TextField(
                    value=row["item"],
                    width=COL_WIDTHS[2] - 10,
                    disabled=(row["type"] == "宿泊費"),
                    border=ft.InputBorder.NONE,
                    color=ft.Colors.BLACK,
                    on_blur=lambda e, rid=row_id: on_edit(rid, "item", e.control.value),
                ),
                width=COL_WIDTHS[2],
            ),

            # 4列目：金額
            cell(
                ft.TextField(
                    value=f"{row['amount']:,}",
                    width=COL_WIDTHS[3] - 10,
                    text_align=ft.TextAlign.RIGHT,
                    border=ft.InputBorder.NONE,
                    color=ft.Colors.BLACK,
                    on_blur=lambda e, rid=row_id: on_edit(rid, "amount", e.control.value),
                ),
                width=COL_WIDTHS[3],
                align=ft.alignment.center_right,
            ),

            # 5列目：累計金額（後で実装）
            cell(
                ft.Text(""),
                width=COL_WIDTHS[4],
                align=ft.alignment.center_right,
            ),

            # 6列目：備考
            cell(
                ft.TextField(
                    value=row["note"],
                    width=COL_WIDTHS[5] - 10,
                    border=ft.InputBorder.NONE,
                    color=ft.Colors.BLACK,
                    on_blur=lambda e, rid=row_id: on_edit(rid, "note", e.control.value),
                ),
                width=COL_WIDTHS[5],
            ),

            # 7列目：削除（枠線なし）
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED,
                    on_click=lambda e, rid=row_id: on_delete(rid),
                ),
                width=50,
                alignment=ft.alignment.center,
                bgcolor=None,
                padding=0,
            ),
        ],   
    )

# 行追加ボタン（6列）
def make_add_row(date, on_add):
    return ft.Row(
                [
                    ft.Container(width=84),  # 操作列は空
                    cell(
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_color=ft.Colors.GREEN,
                            on_click=lambda e, d=date: on_add(d),
                        ),
                        width=COL_WIDTHS[0],
                        align=ft.alignment.center,
                    ),
                    cell(ft.Text(f"{date} の費用を追加", color=ft.Colors.BLACK), width=COL_WIDTHS[1]),
                    cell(ft.Text(""), width=COL_WIDTHS[2]),
                    cell(ft.Text(""), width=COL_WIDTHS[3]),
                    cell(ft.Text(""), width=COL_WIDTHS[4]),
                    cell(ft.Text(""), width=COL_WIDTHS[5]),
                ],
                spacing=0,
            )