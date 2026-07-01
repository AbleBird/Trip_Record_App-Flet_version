# components/pages/trip_top_page.py

import flet as ft
from components.toppage.basic_table import BasicTable
from components.toppage import row_manager
from components.toppage.table_state import init_state, toggle_middle, show_middle, rebuild
from components.others.sync_logic import is_sync, toggle_sync, should_sync
from components.others.counter import build_counter
from components.others.fix_dates import fix_dates_for_trip

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
    def on_add_row(insert_index, do_rebuild=True):
        if insert_index == 0:
            above_id = rows_data[0]["id"]
        else:
            above_id = rows_data[insert_index - 1]["id"]

        row_manager.add_middle_row(trip_id, above_id)

        # ★ 行追加は常に同期（sync_logic 側で always_sync に設定済）
        if do_rebuild and should_sync("trip_top", "add_row"):
            rebuild(page, trip_id, TripTopPage)

    #　複数行追加
    def on_add_rows(insert_index, count):
        # まとめて追加（rebuild は最後に 1 回だけ）
        for _ in range(count):
            on_add_row(insert_index)

        rebuild(page, trip_id, TripTopPage)

    # -----------------------------------------------------
    # ★ セル編集
    # -----------------------------------------------------
    def on_edit(row_index, column_name, new_value):
        row_id = rows_data[row_index]["id"]
        row_manager.update_cell(row_id, column_name, new_value)

        # ★ TripTopPage の編集は同期/非同期ボタンに従う
        if should_sync("trip_top", "edit", column_name):
            rebuild(page, trip_id, TripTopPage)

    # -----------------------------------------------------
    # ★ 行削除
    # -----------------------------------------------------
    def on_delete(row_index):
        row_id = rows_data[row_index]["id"]
        row_manager.delete_row(row_id)

        # ★ 行削除は常に同期（sync_logic 側で always_sync に設定済）
        if should_sync("trip_top", "delete_row"):
            rebuild(page, trip_id, TripTopPage)

    # -----------------------------------------------------
    # ★ 茶色ボタン（部分展開）
    # -----------------------------------------------------
    def on_show(idx):
        show_middle(page, idx)
        rebuild(page, trip_id, TripTopPage)

    # ★ 黄色ボタン（全折りたたみ／全展開）
    def on_toggle(e):
        toggle_middle(page)
        rebuild(page, trip_id, TripTopPage)

    toggle_button = ft.ElevatedButton(
        "全ての中間行を非表示／収納" if not page.hide_middle else "全ての中間行を表示／展開",
        bgcolor=ft.Colors.YELLOW,
        color=ft.Colors.BLACK,
        on_click=on_toggle,
    )

    # ★ 同期/非同期切り替え
    def build_sync_button():
        mode = is_sync()
        bg = ft.Colors.LIGHT_GREEN_200 if mode else ft.Colors.PINK_200

        def on_toggle_sync(e):
            toggle_sync()
            rebuild(page, trip_id, TripTopPage)

        return ft.ElevatedButton(
            f"同期モード：{'ON' if mode else 'OFF'}",
            bgcolor=bg,
            color=ft.Colors.BLACK,
            on_click=on_toggle_sync,
            height=40,
        )
    
    sync_button = build_sync_button()

    #追加行数カウンター
    add_count = 1

    def get_add_count():
        return add_count

    def set_add_count(v):
        nonlocal add_count
        add_count = v
        page.update()   # ← ★ これが絶対に必要

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
        bgcolor=ft.Colors.ORANGE,
        color=ft.Colors.WHITE,
        on_click=lambda e: page.go(f"/trip/{trip_id}/cost"),
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
                on_add_rows=on_add_rows,   # ★ これを追加
                on_edit=on_edit,
                on_delete=on_delete,
                hide_middle=page.hide_middle,
                expand_target=page.expand_target,
                on_show_middle=on_show,
                add_count_getter=get_add_count,    # ★ 必須
                set_add_count=set_add_count,   # ← これが必須
                on_fix_dates=lambda: (
                    fix_dates_for_trip(trip_id),
                    rebuild(page, trip_id, TripTopPage)
                )
            )
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    # debug
    print("TripTopPage rendered")

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
                controls=[
                    trip_title, toggle_button, sync_button,
                    ft.Container(expand=True),  # ← 左右を分離するためのスペーサー
                    build_counter(get_add_count, set_add_count),  # ← カウンターを右端へ
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=20,
            ),
            ft.Container(content=table, expand=True),
        ],
        expand=True,
    )
