import flet as ft
from components.cost.cost_logic import (
    init_row_state, toggle_reorder_state, make_up_handler, make_down_handler, reorder_row,
)
from components.cost.cost_state import (
    init_reorder_state, toggle_reorder_state
)

from components.cost.cost_rows import (
    make_date_row,
    make_transport_row,
    make_other_cost_row,
    make_add_row,
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
    on_reorder=None,   # ★ これを追加!
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
                width=sum(COL_WIDTHS[:5])+ 135,
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
        # 日付行（外枠のみ）
        # -------------------------
        table_rows.append(make_date_row(date))

        # -------------------------
        # 交通費行（6列）
        # -------------------------
        table_rows.append(make_transport_row(date, transport_amount, on_open_transport))

        # -------------------------
        # その他費用行（操作列は枠線なし）
        # -------------------------
        for idx, row in enumerate(rows):
            row_id = row["id"]

            can_up = idx > 0
            can_down = idx < len(rows) - 1

            # ▼ 状態初期化
            init_row_state(row)
            
            can_move_up_flag = can_up
            can_move_down_flag = can_down

            # ▼ 並べ替えモード切り替え
            def toggle_reorder(e, r=row):
                new_state = toggle_reorder_state(r)  # ← ロジックは cost_logic に任せる
                up_btn.visible = new_state
                down_btn.visible = new_state
                handle_btn.visible = True
                page.update()

            # ▼ ボタン定義（IconButton を使わない）
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

            # ▼ 三本線を押したときの動作
            def toggle_reorder(e, r=row):
                r["reorder_open"] = not r["reorder_open"]

                # 表示切り替え（UI 再構築なし）
                up_btn.visible = r["reorder_open"]
                down_btn.visible = r["reorder_open"]
                handle_btn.visible = True  # ← 常に表示（戻るため）

                page.update()

            # 三本線ボタンに toggle を割り当て
            handle_btn.on_click = toggle_reorder

            # ▼ 操作列（幅84px固定）
            operation_column = ft.Container(
                content=ft.Row(
                    [up_btn, down_btn, handle_btn],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.END,  # ← これが必須
                ),
                width=84,
                padding=0,
            )

            # ▼ Row に組み込む
            table_rows.append(
                ft.Row(
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
                    spacing=0,
                )
            )

        # -------------------------
        # 行追加ボタン（6列）
        # -------------------------
        table_rows.append(make_add_row(date, on_add))


    return ft.Column(
        [
            header_controls,
            ft.Column(table_rows, spacing=0),
        ],
        spacing=10,
    )
