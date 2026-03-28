import flet as ft
from components.basic_table import BasicTable
from components import row_manager
from components.table_state import init_state, toggle_middle, show_middle, rebuild


# ---------------------------------------------------------
# Trip名取得
# ---------------------------------------------------------
def get_trip_name(trip_id):
    import sqlite3
    conn = sqlite3.connect("travel.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM trips WHERE id = ?", (trip_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else "Unknown Trip"


# ---------------------------------------------------------
# TripTopPage 本体（即時反映対応版）
# ---------------------------------------------------------
def TripTopPage(page: ft.Page, trip_id: int):

    page.bgcolor = ft.Colors.WHITE

    # -----------------------------------------------------
    # ★ 折りたたみ状態の初期化（page に保持）
    # -----------------------------------------------------
    init_state(page)

    # -----------------------------------------------------
    # ★ DB から行データを取得
    # -----------------------------------------------------
    raw_rows = row_manager.fetch_rows(trip_id)

    if len(raw_rows) == 0:
        row_manager.initialize_trip(trip_id)
        raw_rows = row_manager.fetch_rows(trip_id)

    rows_data = row_manager.sanitize_rows(raw_rows)

    # -----------------------------------------------------
    # ★ 行追加（中間行）
    # -----------------------------------------------------
    def on_add_row(insert_index):
        if insert_index == 0:
            above_id = rows_data[0]["id"]
        else:
            above_id = rows_data[insert_index - 1]["id"]

        row_manager.add_middle_row(trip_id, above_id)
        rebuild(page, trip_id, TripTopPage)

    # -----------------------------------------------------
    # ★ セル編集
    # -----------------------------------------------------
    def on_edit(row_index, column_name, new_value):
        row_id = rows_data[row_index]["id"]
        row_manager.update_cell(row_id, column_name, new_value)
        rebuild(page, trip_id, TripTopPage)

    # -----------------------------------------------------
    # ★ 行削除
    # -----------------------------------------------------
    def on_delete(row_index):
        row_id = rows_data[row_index]["id"]
        row_manager.delete_row(row_id)
        rebuild(page, trip_id, TripTopPage)

    # -----------------------------------------------------
    # ★ 茶色ボタン（部分展開）
    # -----------------------------------------------------
    def on_show(idx):
        show_middle(page, idx)
        rebuild(page, trip_id, TripTopPage)

    # -----------------------------------------------------
    # ★ 黄色ボタン（全折りたたみ／全展開）
    # -----------------------------------------------------
    def on_toggle(e):
        toggle_middle(page)
        rebuild(page, trip_id, TripTopPage)

    toggle_button = ft.ElevatedButton(
        "全ての中間行を非表示／収納" if not page.hide_middle else "全ての中間行を表示／展開",
        bgcolor=ft.Colors.YELLOW,
        color=ft.Colors.BLACK,
        on_click=on_toggle,
    )

    # -----------------------------------------------------
    # 上部ボタン
    # -----------------------------------------------------
    back_button = ft.ElevatedButton(
        "ホーム画面に戻る",
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        on_click=lambda e: page.go("/"),
    )

    calc_mode_button = ft.ElevatedButton(
        "金額計算モード",
        bgcolor=ft.Colors.GREEN,
        color=ft.Colors.WHITE,
    )

    media_mode_button = ft.ElevatedButton(
        "写真・動画特化モード",
        bgcolor=ft.Colors.PURPLE,
        color=ft.Colors.WHITE,
    )

    trip_title = ft.Text(
        get_trip_name(trip_id),
        size=24,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLACK,
    )

    # -----------------------------------------------------
    # ★ BasicTable（折りたたみ＋部分展開対応）
    # -----------------------------------------------------
    table = ft.Column(
        controls=[
            BasicTable(
                rows_data,
                on_add_row=on_add_row,
                on_edit=on_edit,
                on_delete=on_delete,
                hide_middle=page.hide_middle,
                expand_target=page.expand_target,
                on_show_middle=on_show,
            )
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    # -----------------------------------------------------
    # ★ レイアウト
    # -----------------------------------------------------
    return ft.Column(
        controls=[
            ft.Row(
                controls=[back_button, calc_mode_button, media_mode_button],
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.Row(
                controls=[trip_title, toggle_button],
                alignment=ft.MainAxisAlignment.START,
                spacing=20,
            ),
            ft.Container(
                content=table,
                expand=True,
            ),
        ],
        expand=True,
    )
