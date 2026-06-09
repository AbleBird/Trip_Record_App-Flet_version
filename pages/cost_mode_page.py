# pages/cost_mode_page.py

import flet as ft
import sqlite3
from components.cost.cost_table import CostTable
from db.cost_database import get_other_costs, get_transport_totals
from components.cost.cost_handlers import (
    handle_edit,
    handle_add,
    handle_delete,
)
from components.others.date_manager import get_date_list_from_rows   # ★ 追加
from components.cost.common.cost_cross_table import build_cross_table
from components.others.counter import build_counter
from utils.number import to_int
from components.others.sync_logic import is_sync, toggle_sync, should_sync
from components.cost.common.rebuild_cost import rebuild_cost

TRAVEL_DB_PATH = "travel.db"


def sanitize_cost_rows(rows):
    sanitized = []
    for r in rows:
        sanitized.append({
            "id": r["id"],
            "date": r["date"],
            "type": r.get("type", ""),       # ← そのまま使う
            "title": r.get("title", ""),     # ← そのまま使う
            "item": r.get("item", ""),       # ← そのまま使う
            "amount": to_int(r.get("amount", 0)),
            "note": r.get("note", ""),
        })
    return sanitized

def to_int(v):
    try:
        return int(v)
    except:
        return 0


# ---------------------------------------------------------
# 金額計算モード（メインページ）
# ---------------------------------------------------------
def CostModePage(page, trip_id):

    # -----------------------------------------------------
    # ★ 追加行数カウンター（必ず最初に置く）
    # -----------------------------------------------------
    add_count = 1

    def get_add_count():
        return add_count

    def set_add_count(v):
        nonlocal add_count
        add_count = v
        page.update()

    counter = build_counter(get_add_count, set_add_count)

    # Trip名取得
    def get_trip_name(trip_id):
        conn = sqlite3.connect(TRAVEL_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name FROM trips WHERE id = ?", (trip_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else "Trip"

    # -----------------------------------------------------
    # ★ TripTopPage と同じ日付行を取得（trip_rows）
    # -----------------------------------------------------
    date_list = get_date_list_from_rows(trip_id)

    # -----------------------------------------------------
    # DB からデータ取得
    # -----------------------------------------------------
    other_costs = sanitize_cost_rows(get_other_costs(trip_id))
    transport_totals = get_transport_totals(trip_id)

    for d in list(transport_totals.keys()):
        try:
            transport_totals[d] = int(transport_totals[d])
        except:
            transport_totals[d] = 0

    # -----------------------------------------------------
    # 日付ごとに other_costs をグループ化
    # -----------------------------------------------------
    grouped_rows = {d: [] for d in date_list}
    for r in other_costs:
        if r["date"] in grouped_rows:
            grouped_rows[r["date"]].append(r)

    # -----------------------------------------------------
    # 総額計算
    # -----------------------------------------------------
    total_amount = sum(
        sum(to_int(r["amount"]) for r in grouped_rows.get(d, []))
        + to_int(transport_totals.get(d, 0))
        for d in date_list
    )

    # -----------------------------------------------------
    # 上部ボタン
    # -----------------------------------------------------
    top_buttons = ft.Row(
        [
            ft.ElevatedButton(
                "TripTopPageに戻る",
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                on_click=lambda e: page.go(f"/trip/{trip_id}")
            ),
            ft.ElevatedButton(
                "Mediaモード",
                bgcolor=ft.Colors.PURPLE,
                color=ft.Colors.WHITE,
                on_click=lambda e: page.go(f"/trip/{trip_id}/media")
            ),
        ],
        spacing=20,
    )

    def build_sync_button():
        mode = is_sync()
        bg = ft.Colors.LIGHT_GREEN_200 if mode else ft.Colors.PINK_200

        def on_toggle_sync(e):
            toggle_sync()
            rebuild_cost(page, trip_id, CostModePage)

        sync_button = ft.ElevatedButton(
            f"同期モード：{'ON' if is_sync() else 'OFF'}",
            bgcolor=bg,
            color=ft.Colors.BLACK,
            on_click=on_toggle_sync,
            height=40,
        )

        return sync_button


    sync_button = build_sync_button()

    trip_name = get_trip_name(trip_id)

    # -----------------------------------------------------
    # ページタイトル行
    # -----------------------------------------------------
    title_row = ft.Row(
        [
            ft.Text(
                "金額計算モード（メイン）",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
            ),
        ],
        spacing=20,
    )

    # Trip 名＋総額行（2 行目）
    trip_info_row = ft.Row(
        [
            # 左：Trip 名
            ft.Text(
                trip_name,
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
            ),

            # 右：Trip 内総額（右揃え）
            ft.Container(
                content=ft.Text(
                    f"Trip内総額：{total_amount:,} 円",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK,
                ),
                expand=True,
                alignment=ft.alignment.center_right,
            ),
        ],
        spacing=20,
    )


    # -----------------------------------------------------
    # handlers 生成（★ on_add を count 対応に修正）
    # -----------------------------------------------------
    edit_handler = handle_edit(page, grouped_rows, transport_totals, date_list, trip_id, CostModePage)
    delete_handler = handle_delete(page, trip_id, CostModePage)
    add_handler = handle_add(page, trip_id, CostModePage)

    # 編集
    def on_edit_wrapper(row_id, col, val, _sync_flag_from_table):
        sync_flag = should_sync("cost_mode", "edit", col)
        edit_handler(row_id, col, val, sync_flag)

    # 削除
    def on_delete_wrapper(row_id, _sync_flag_from_table):
        sync_flag = should_sync("cost_mode", "delete_row")
        delete_handler(row_id, sync_flag)

    # 追加（複数行対応）
    def on_add_wrapper(date, count, _sync_flag_from_table):
        sync_flag = should_sync("cost_mode", "add_row")
        for _ in range(count):
            add_handler(date, sync_flag)

    # -----------------------------------------------------
    # 詳細入力テーブル
    # -----------------------------------------------------
    detail_table = CostTable(
        page=page,
        trip_id=trip_id,
        grouped_rows=grouped_rows,
        transport_totals=transport_totals,
        date_list=date_list,
        on_add=on_add_wrapper,      # sync_flag は CostModePage 側で決める
        on_delete=on_delete_wrapper,
        on_edit=on_edit_wrapper,
        on_open_transport=lambda d: page.go(f"/trip/{trip_id}/cost/transport/{d}"),
        get_add_count=get_add_count,
        counter_control=counter,   # ★ ここで渡す
        sync_control=sync_button,      # ← 追加
    )

    # CostTable 部分だけをスクロールさせる Column にする
    detail_scroll = ft.Column(
        controls=[detail_table],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Column(
        expand=True,
        spacing=10,
        controls=[
            top_buttons,
            title_row,
            trip_info_row,
            ft.Divider(height=10),

            # クロス表は固定
            build_cross_table(grouped_rows, transport_totals),

            # TripTopPage と同じ構造でスクロール領域を作る
            ft.Container(
                content=detail_scroll,
                expand=True,
            ),
        ],
    )
