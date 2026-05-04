#components/cost/cost_table.py

import flet as ft
from components.cost.cost_logic import (
    init_row_state, toggle_reorder_state, make_up_handler, make_down_handler
)
from components.cost.cost_rows import (
    make_date_row,
    make_transport_row,
    make_add_row,
    make_other_cost_row
)
from components.cost.common.cost_elements import cell
from components.cost.common.cost_elements import make_icon_button
from components.cost.common.cost_elements import COL_WIDTHS, TYPE_OPTIONS


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
    on_reorder=None,
):

    # -------------------------
    # Table 外のヘッダー
    # -------------------------
    header_controls = ft.Row(
        [
            ft.Container(
                content=ft.Text(
                    "詳細を入力",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK,
                ),
                width=sum(COL_WIDTHS[:5]) + 135,
                alignment=ft.alignment.center_left,
            ),
            ft.Container(
                content=ft.TextField(
                    value=currency,
                    width=200,
                    height=40,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.BLACK,
                ),
                width=COL_WIDTHS[4],
                alignment=ft.alignment.center_right,
            ),
        ],
        spacing=0,
    )

    # -------------------------
    # ここから 6 列 Table
    # -------------------------
    table_rows = []

    for date in date_list:

        rows = grouped_rows.get(date, [])
        transport_amount = transport_totals.get(date, 0)

        # -------------------------
        # 日付内の総額（交通費 + その他費用）
        # -------------------------
        daily_total = transport_amount + sum(r["amount"] for r in rows)

        # -------------------------
        # 日付行（5列目に日付合計を表示）
        # -------------------------
        table_rows.append(
            ft.Row(
                [
                    ft.Container(width=84),
                    cell(
                        ft.Text(date, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        width=sum(COL_WIDTHS[:4]),
                        bgcolor=ft.Colors.GREY_200,
                    ),
                    cell(
                        ft.Text(
                            f"{daily_total:,} 円", 
                            color=ft.Colors.BLACK, 
                            weight=ft.FontWeight.BOLD,   # ← ★これを追加
                        ),
                        width=COL_WIDTHS[4],
                        bgcolor=ft.Colors.GREY_200,
                        align=ft.alignment.center_right,
                    ),
                    cell(ft.Text(""), width=COL_WIDTHS[5], bgcolor=ft.Colors.GREY_200),
                ],
                spacing=0,
            )
        )

        # -------------------------
        # 交通費行
        # -------------------------
        table_rows.append(make_transport_row(date, transport_amount, on_open_transport))

        # -------------------------
        # その他費用行（累計 running_total を計算しながら表示）
        # -------------------------
        running_total = transport_amount

        for idx, row in enumerate(rows):
            row_id = row["id"]

            running_total += row["amount"]  # ← 累計を更新

            can_up = idx > 0
            can_down = idx < len(rows) - 1

            init_row_state(row)

            # ▼ 並べ替えトグル
            def toggle_reorder(e, r=row):
                new_state = toggle_reorder_state(r)
                up_btn.visible = new_state
                down_btn.visible = new_state
                handle_btn.visible = True
                page.update()

            # ▼ 並べ替えボタン
            handle_btn = make_icon_button(
                ft.Icons.DRAG_HANDLE,
                on_click=toggle_reorder,
                visible=True,
            )

            up_btn = make_icon_button(
                ft.Icons.ARROW_UPWARD,
                on_click=make_up_handler(on_reorder, date, idx),
                visible=row["reorder_open"],
                disabled=not can_up,
            )

            down_btn = make_icon_button(
                ft.Icons.ARROW_DOWNWARD,
                on_click=make_down_handler(on_reorder, date, idx),
                visible=row["reorder_open"],
                disabled=not can_down,
            )

            # ▼ 操作列
            operation_column = ft.Container(
                content=ft.Row(
                    [up_btn, down_btn, handle_btn],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.END,
                ),
                width=84,
                padding=0,
            )

            # -------------------------
            # ▼ 2列目（店名 / ホテル名）
            # -------------------------
            label_2 = "ホテル名" if row["type"] == "宿泊費" else "店名"

            title_cell = cell(
                ft.TextField(
                    label=label_2,
                    value=row["title"],
                    width=COL_WIDTHS[1] - 10,
                    border=ft.InputBorder.NONE,
                    color=ft.Colors.BLACK,
                    on_blur=lambda e, rid=row_id: on_edit(rid, "title", e.control.value),
                ),
                width=COL_WIDTHS[1],
            )

            # -------------------------
            # ▼ 3列目（商品名 or 無効）
            # -------------------------
            if row["type"] == "宿泊費":
                item_cell = cell(
                    ft.TextField(
                        value="",
                        disabled=True,
                        border=ft.InputBorder.NONE,
                        width=COL_WIDTHS[2] - 10,
                        color=ft.Colors.GREY_600,
                    ),
                    width=COL_WIDTHS[2],
                    bgcolor=ft.Colors.BROWN_100,
                )
            else:
                item_cell = cell(
                    ft.TextField(
                        label="商品名",
                        value=row["item"],
                        width=COL_WIDTHS[2] - 10,
                        border=ft.InputBorder.NONE,
                        color=ft.Colors.BLACK,
                        on_blur=lambda e, rid=row_id: on_edit(rid, "item", e.control.value),
                    ),
                    width=COL_WIDTHS[2],
                )

            # -------------------------
            # ▼ Row に組み込む
            # -------------------------
            table_rows.append(
                make_other_cost_row(
                    page,
                    row,
                    idx,
                    date,
                    trip_id,
                    on_edit,
                    on_delete,
                    on_reorder,
                    make_icon_button,
                    operation_column,
                    TYPE_OPTIONS,
                    running_total,  # ← 累計
                )
            )


        # -------------------------
        # 行追加ボタン
        # -------------------------
        table_rows.append(make_add_row(date, on_add))

    return ft.Column(
        [
            header_controls,
            ft.Column(table_rows, spacing=0),
        ],
        spacing=10,
    )
