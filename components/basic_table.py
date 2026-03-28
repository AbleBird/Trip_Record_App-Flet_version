import flet as ft
from components.table_logic import should_collapse, should_show_collapsed_row, build_collapsed_row

print("BasicTable loaded from:", __file__)


def BasicTable(
    rows_data,
    on_add_row,
    on_edit,
    on_delete,
    hide_middle=False,
    expand_target=None,
    on_show_middle=None,
):

    def safe(v):
        return "" if v in (None, "None") else str(v)

    # -------------------------
    # 代表行 UI（折り畳み時）
    # -------------------------
    def build_collapsed_row_ui(i, plus_cell, type_cell):
        planned_cell = ft.Container(
            content=ft.Text("-", size=14),
            width=col_widths[2],
            height=48,
            alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.BLACK),
        )

        actual_cell = ft.Container(
            content=ft.Text("-", size=14),
            width=col_widths[3],
            height=48,
            alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.BLACK),
        )

        place_cell = ft.Container(
            content=ft.ElevatedButton(
                "この行を表示",
                bgcolor=ft.Colors.BROWN,
                color=ft.Colors.WHITE,
                on_click=lambda e, idx=i: on_show_middle(idx),
            ),
            width=col_widths[4],
            height=48,
            alignment=ft.alignment.center,
        )

        empty_cells = [
            ft.Container(width=col_widths[5], height=48),
            ft.Container(width=col_widths[6], height=48),
            ft.Container(width=col_widths[7], height=48),
            ft.Container(width=col_widths[8], height=48),
            ft.Container(width=col_widths[9], height=48),
            ft.Container(width=col_widths[10], height=48),
        ]

        delete_cell = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.RED,
                on_click=lambda e, idx=i: on_delete(idx),
            ),
            width=col_widths[-1],
            height=48,
            alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.BLACK),
        )

        return ft.Row(
            [plus_cell, type_cell, planned_cell, actual_cell, place_cell]
            + empty_cells
            + [delete_cell],
            spacing=0,
        )

    # -------------------------
    # 列幅
    # -------------------------
    col_widths = [
        50, 50, 70, 70, 150, 180, 80, 80, 250, 80, 80, 50
    ]

    # -------------------------
    # ヘッダー
    # -------------------------
    header_labels = ["", "種別", "planned", "actual", "place", "by",
                     "cost", "point", "note", "image", "video", ""]

    header_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(
                    header_labels[i],
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK,
                    text_align=ft.TextAlign.CENTER,
                ),
                width=col_widths[i],
                height=50,
                alignment=ft.alignment.center,
                border=None if header_labels[i] == "" else ft.border.all(1, ft.Colors.BLACK),
            )
            for i in range(len(col_widths))
        ],
        spacing=0,
    )

    table_rows = [header_row]

    # -------------------------
    # 各行の描画
    # -------------------------
    for i, row in enumerate(rows_data):

        row_type = row.get("type")

        plus_cell = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.ADD,
                icon_color=ft.Colors.BLUE,
                on_click=lambda e, idx=i: on_add_row(idx),
            ),
            width=col_widths[0],
            height=48,
            alignment=ft.alignment.center,
        )

        # 日付行
        if row_type == 0:
            type_cell = ft.Container(
                content=ft.Text("D", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                width=col_widths[1],
                height=48,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.Colors.BLACK),
            )

            date_cell = ft.Container(
                content=ft.Text(safe(row.get("planned_time")), size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                width=sum(col_widths[2:-1]),
                height=48,
                bgcolor=ft.Colors.GREY_200,
                alignment=ft.alignment.center_left,
                padding=10,
                border=ft.border.all(1, ft.Colors.BLACK),
            )

            delete_cell = ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED,
                    on_click=lambda e, idx=i: on_delete(idx),
                ),
                width=col_widths[-1],
                height=48,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.Colors.BLACK),
            )

            table_rows.append(ft.Row([plus_cell, type_cell, date_cell, delete_cell], spacing=0))
            continue

        # 種別列
        type_value = "F" if row_type == 1 else ""
        type_cell = ft.TextField(
            value=type_value,
            width=col_widths[1],
            height=48,
            text_align=ft.TextAlign.CENTER,
            on_blur=lambda e, idx=i: on_edit(idx, "place", e.control.value),
            color=ft.Colors.BLACK
        )

        # -------------------------
        # ★ 折り畳み判定（table_logic に移動）
        # -------------------------
        # ① 代表行を表示すべき場合（middle グループの先頭）
        if should_show_collapsed_row(i, hide_middle, expand_target, rows_data):
            info = build_collapsed_row(i)
            table_rows.append(build_collapsed_row_ui(info["index"], plus_cell, type_cell))
            continue

        # ② 折り畳むべき middle 行だが、代表行ではない → 完全にスキップ
        if should_collapse(row_type, i, hide_middle, expand_target, rows_data):
            continue

        # -------------------------
        # 通常行の描画
        # -------------------------
        event_cells = [
            type_cell,
            ft.TextField(
                value=safe(row.get("planned_time")),
                width=col_widths[2],
                height=48,
                on_blur=lambda e, idx=i: on_edit(idx, "planned_time", e.control.value),
                color=ft.Colors.BLACK,
            ),
            ft.TextField(
                value=safe(row.get("actual_time")),
                width=col_widths[3],
                height=48,
                on_blur=lambda e, idx=i: on_edit(idx, "actual_time", e.control.value),
                color=ft.Colors.BLACK,
            ),
            ft.TextField(
                value=safe(row.get("place")),
                width=col_widths[4],
                height=48,
                on_blur=lambda e, idx=i: on_edit(idx, "place", e.control.value),
                color=ft.Colors.BLACK,
            ),
            ft.TextField(
                value=safe(row.get("by")),
                width=col_widths[5],
                height=48,
                on_blur=lambda e, idx=i: on_edit(idx, "by", e.control.value),
                color=ft.Colors.BLACK,
            ),
            ft.TextField(
                value=safe(row.get("cost")),
                width=col_widths[6],
                height=48,
                on_blur=lambda e, idx=i: on_edit(idx, "cost", e.control.value),
                color=ft.Colors.BLACK,
            ),
            ft.TextField(
                value=safe(row.get("point")),
                width=col_widths[7],
                height=48,
                on_blur=lambda e, idx=i: on_edit(idx, "point", e.control.value),
                color=ft.Colors.BLACK,
            ),
            ft.TextField(
                value=safe(row.get("note")),
                width=col_widths[8],
                height=48,
                on_blur=lambda e, idx=i: on_edit(idx, "note", e.control.value),
                color=ft.Colors.BLACK,
            ),
            ft.TextField(
                value=safe(row.get("image")),
                width=col_widths[9],
                height=48,
                on_blur=lambda e, idx=i: on_edit(idx, "image", e.control.value),
                color=ft.Colors.BLACK,
            ),
            ft.TextField(
                value=safe(row.get("video")),
                width=col_widths[10],
                height=48,
                on_blur=lambda e, idx=i: on_edit(idx, "video", e.control.value),
                color=ft.Colors.BLACK,
            ),
        ]

        delete_cell = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.RED,
                on_click=lambda e, idx=i: on_delete(idx),
            ),
            width=col_widths[-1],
            height=48,
            alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.BLACK),
        )

        table_rows.append(ft.Row([plus_cell] + event_cells + [delete_cell], spacing=0))

    # 末尾の＋ボタン
    last_plus = ft.Container(
        content=ft.IconButton(
            icon=ft.Icons.ADD,
            icon_color=ft.Colors.BLUE,
            on_click=lambda e: on_add_row(len(rows_data)),
        ),
        width=col_widths[0],
        height=48,
        alignment=ft.alignment.center,
    )

    table_rows.append(ft.Row([last_plus], spacing=0))

    return ft.ListView(controls=table_rows, spacing=0, expand=True)
