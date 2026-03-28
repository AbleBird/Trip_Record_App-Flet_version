import flet as ft

def CalcModePage(page, rows_data, on_back, on_media):
    """
    金額計算特化モード（UIのみ）
    rows_data: TripTopPage と同じ rows_data を受け取る
    """

    # 列幅
    col_widths = [
        80,   # actual_time
        150,  # place
        150,  # by
        80,   # cost
        120,  # type（プルダウン）
        250,  # detail
        100,  # amount
        120,  # type累積
        120,  # total累積
    ]

    # ヘッダー
    header_labels = [
        "actual",
        "place",
        "by",
        "cost",
        "type",
        "detail",
        "amount",
        "type累積",
        "total累積",
    ]

    header_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(
                    header_labels[i],
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK,
                ),
                width=col_widths[i],
                height=40,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.Colors.BLACK),
            )
            for i in range(len(col_widths))
        ],
        spacing=0,
    )

    table_rows = [header_row]

    # テーブル本体（UIのみ）
    for i, row in enumerate(rows_data):

        # BasicTable と共通の4列
        actual_cell = ft.TextField(
            value=row.get("actual_time", ""),
            width=col_widths[0],
            height=40,
            color=ft.Colors.BLACK,
            read_only=True,
        )

        place_cell = ft.TextField(
            value=row.get("place", ""),
            width=col_widths[1],
            height=40,
            color=ft.Colors.BLACK,
            read_only=True,
        )

        by_cell = ft.TextField(
            value=row.get("by", ""),
            width=col_widths[2],
            height=40,
            color=ft.Colors.BLACK,
            read_only=True,
        )

        cost_cell = ft.TextField(
            value=row.get("cost", ""),
            width=col_widths[3],
            height=40,
            color=ft.Colors.BLACK,
            read_only=True,
        )

        # 追加列（編集可能）
        type_cell = ft.Dropdown(
            width=col_widths[4],
            height=40,
            options=[
                ft.dropdown.Option("乗車券"),
                ft.dropdown.Option("特急券"),
                ft.dropdown.Option("グリーン券"),
                ft.dropdown.Option("指定席券"),
                ft.dropdown.Option("その他"),
            ],
        )

        detail_cell = ft.TextField(
            value="",
            width=col_widths[5],
            height=40,
            color=ft.Colors.BLACK,
        )

        amount_cell = ft.TextField(
            value="",
            width=col_widths[6],
            height=40,
            color=ft.Colors.BLACK,
        )

        # 累積列（まだロジックなし）
        type_sum_cell = ft.Container(
            content=ft.Text(""),
            width=col_widths[7],
            height=40,
            alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.BLACK),
        )

        total_sum_cell = ft.Container(
            content=ft.Text(""),
            width=col_widths[8],
            height=40,
            alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.BLACK),
        )

        table_rows.append(
            ft.Row(
                [
                    actual_cell,
                    place_cell,
                    by_cell,
                    cost_cell,
                    type_cell,
                    detail_cell,
                    amount_cell,
                    type_sum_cell,
                    total_sum_cell,
                ],
                spacing=0,
            )
        )

    # 上部ボタン
    top_buttons = ft.Row(
        [
            ft.ElevatedButton("TripTopPageに戻る", on_click=on_back),
            ft.ElevatedButton("Mediaモード", on_click=on_media),
        ],
        spacing=20,
    )

    # 総額表示（まだロジックなし）
    total_display = ft.Text("総額：—— 円", size=20, weight=ft.FontWeight.BOLD)

    return ft.Column(
        [
            top_buttons,
            total_display,
            ft.ListView(controls=table_rows, spacing=0, expand=True),
        ],
        expand=True,
    )
