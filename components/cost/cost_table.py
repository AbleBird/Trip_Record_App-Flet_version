# components/cost/cost_table.py

import flet as ft
from components.cost.cost_rows import (
    make_transport_row,
    make_other_cost_row
)
from components.cost.common.cost_elements import cell
from components.cost.common.cost_elements import COL_WIDTHS, TYPE_OPTIONS

PLUS_COL_WIDTH = 50

def CostTable(
    page,
    trip_id,
    grouped_rows,
    transport_totals,
    date_list,
    currency="日本円/JPY",
    on_add=None,
    on_delete=None,
    on_edit=None,
    on_open_transport=None,
    get_add_count=None,
):

    # -------------------------
    # 左端の + ボタン
    # -------------------------
    def make_plus_cell(date):
        return ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.ADD,
                icon_color=ft.Colors.BLUE,
                on_click=lambda e, d=date: on_add(
                    d,
                    get_add_count() if get_add_count else 1,
                    False,   # sync_flag は CostModePage 側で決める
                ),
            ),
            width=PLUS_COL_WIDTH,
            height=48,
            alignment=ft.alignment.center,
        )


    # -------------------------
    # Table 本体
    # -------------------------
    table_rows = []

    for date in date_list:

        rows = grouped_rows.get(date, [])
        transport_amount = transport_totals.get(date, 0)

        daily_total = transport_amount + sum(r["amount"] for r in rows)

        # 日付行
        table_rows.append(
            ft.Row(
                [
                    make_plus_cell(date),
                    cell(
                        ft.Text(date, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        width=sum(COL_WIDTHS[:4]),
                        bgcolor=ft.Colors.GREY_200,
                    ),
                    cell(
                        ft.Text(f"{daily_total:,} 円", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        width=COL_WIDTHS[4],
                        bgcolor=ft.Colors.GREY_200,
                        align=ft.alignment.center_right,
                    ),
                    cell(ft.Text(""), width=COL_WIDTHS[5], bgcolor=ft.Colors.GREY_200),
                ],
                spacing=0,
            )
        )

        # 交通費行
        transport_row = make_transport_row(
            date,
            transport_amount,
            on_open_transport,   # ← そのまま渡す
        )


        table_rows.append(
            ft.Row(
                [
                    make_plus_cell(date),
                    transport_row,
                ],
                spacing=0,
            )
        )

        # その他費用行
        running_total = transport_amount

        for idx, row in enumerate(rows):
            running_total += row["amount"]

            other_row = make_other_cost_row(
                page,
                row,
                idx,
                date,
                trip_id,
                on_edit,
                on_delete,
                TYPE_OPTIONS,
                running_total,
            )

            table_rows.append(
                ft.Row(
                    [
                        make_plus_cell(date),
                        other_row,   # ★ controls を展開しない
                    ],
                    spacing=0,
                )
            )

        # 末尾の + ボタン
        table_rows.append(
            ft.Row(
                [
                    make_plus_cell(date),
                ],
                spacing=0,
            )
        )

    return ft.Column(
        [
            # header_controls,
            ft.Column(table_rows, spacing=0),
        ],
        spacing=10,
    )
