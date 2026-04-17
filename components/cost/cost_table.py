import flet as ft

TYPE_OPTIONS = ["食費", "宿泊費", "お土産代", "その他諸費"]

# 6列構造
COL_WIDTHS = [140, 200, 200, 150, 150, 200]   # Type, Title, Item, Amount, Cumulative, Note
DELETE_WIDTH = 50
HANDLE_WIDTH = 80

# ▼ ボタンサイズ（完全固定）
BTN_SIZE = 28
ICON_SIZE = 20     # ← 見た目の大きさ（小さく見える）

def make_icon_button(icon, on_click, visible=True, disabled=False):
    return ft.Container(
        width=BTN_SIZE,
        height=BTN_SIZE,
        visible=visible,
        alignment=ft.alignment.center,
        padding=0,
        content=ft.TextButton(
            content=ft.Icon(
                icon,
                size=ICON_SIZE,
                color=ft.Colors.GREY_700 if not disabled else ft.Colors.GREY_400,
            ),
            style=ft.ButtonStyle(
                padding=0,
                bgcolor={ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
                overlay_color=ft.Colors.TRANSPARENT,
                shape=ft.RoundedRectangleBorder(radius=0),
            ),
            on_click=on_click if (visible and not disabled) else None,
        ),
    )

def cell(content, width, bgcolor=None, align=ft.alignment.center_left):
    return ft.Container(
        content=content,
        width=width,
        height=56,
        bgcolor=bgcolor,
        padding=5,
        alignment=align,
        border=ft.border.all(1, ft.Colors.BLACK),
    )


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
                width=sum(COL_WIDTHS[:4]),
                alignment=ft.alignment.center_left,
            ),
            ft.Container(
                content=ft.TextField(
                    value=currency,
                    width=120,
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
        table_rows.append(
            ft.Row(
                [
                    ft.Container(width=84),  # 操作列は空
                    cell(
                        ft.Text(date, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        width=sum(COL_WIDTHS[:3]),
                        bgcolor=ft.Colors.GREY_200,
                    ),
                    cell(ft.Text(""), width=COL_WIDTHS[3], bgcolor=ft.Colors.GREY_200),
                    cell(ft.Text(""), width=COL_WIDTHS[4], bgcolor=ft.Colors.GREY_200),
                    cell(ft.Text(""), width=COL_WIDTHS[5], bgcolor=ft.Colors.GREY_200),
                ],
                spacing=0,
            )
        )

        # -------------------------
        # 交通費行（6列）
        # -------------------------
        table_rows.append(
            ft.Row(
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
        )

        def make_up_handler(d, i):
            return lambda e: on_reorder(d, i, i-1)

        def make_down_handler(d, i):
            return lambda e: on_reorder(d, i, i+1)

        # -------------------------
        # その他費用行（操作列は枠線なし）
        # -------------------------
        for idx, row in enumerate(rows):
            row_id = row["id"]

            can_move_up = idx > 0
            can_move_down = idx < len(rows) - 1

            # ▼ 並べ替え状態
            if "reorder_open" not in row:
                row["reorder_open"] = False

            def toggle_reorder(e, r=row):
                r["reorder_open"] = not r["reorder_open"]
                up_btn.visible = r["reorder_open"]
                down_btn.visible = r["reorder_open"]
                page.update()

            # ▼ ボタン定義（IconButton を使わない）
            handle_btn = make_icon_button(
                ft.Icons.DRAG_HANDLE,
                on_click=toggle_reorder,
                visible=True,
            )

            up_btn = make_icon_button(
                ft.Icons.ARROW_UPWARD,
                on_click=lambda e, d=date, i=idx: on_reorder(d, i, i-1),
                visible=row["reorder_open"],
                disabled=not can_move_up,
            )

            down_btn = make_icon_button(
                ft.Icons.ARROW_DOWNWARD,
                on_click=lambda e, d=date, i=idx: on_reorder(d, i, i+1),
                visible=row["reorder_open"],
                disabled=not can_move_down,
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
        table_rows.append(
            ft.Row(
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
        )


    return ft.Column(
        [
            header_controls,
            ft.Column(table_rows, spacing=0),
        ],
        spacing=10,
    )
