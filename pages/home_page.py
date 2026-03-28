# pages/home_page.py

import flet as ft
from components.home_state import HomeState
from components.home_logic import (
    normalize_date,
    make_display_name,
    fetch_trips,
    add_trip_to_db,
    rename_trip,
    hide_trip,
    delete_trip,
    toggle_all_trips,
)


def HomePage(page: ft.Page):

    state = HomeState()

    page.bgcolor = ft.Colors.WHITE
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLACK,
            on_primary=ft.Colors.WHITE,
            surface=ft.Colors.WHITE,
            on_surface=ft.Colors.BLACK,
        )
    )

    trip_list = ft.ListView(spacing=10)

    # -------------------------
    # 名前変更開始
    # -------------------------
    def start_rename(trip_id, current_name):
        state.editing_trip_id = trip_id
        state.rename_fields[trip_id] = ft.TextField(
            value=current_name,
            width=300,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLACK,
        )
        load_trips()

    # -------------------------
    # 名前変更確定
    # -------------------------
    def finish_rename(trip_id):
        new_name = state.rename_fields[trip_id].value.strip()
        if new_name != "":
            rename_trip(trip_id, new_name)

        state.editing_trip_id = None
        if trip_id in state.rename_fields:
            del state.rename_fields[trip_id]

        load_trips()

    # -------------------------
    # Trip一覧読み込み
    # -------------------------
    def load_trips():
        trip_list.controls.clear()

        trips = fetch_trips(state.sort_desc)

        for trip_id, name, ds, de, hidden in trips:

            is_editing = (state.editing_trip_id == trip_id)

            # Trip名部分
            if is_editing:
                name_control = state.rename_fields[trip_id]
            else:
                name_control = ft.TextButton(
                    name,
                    on_click=lambda e, tid=trip_id: page.go(f"/trip/{tid}"),
                    style=ft.ButtonStyle(color=ft.Colors.BLACK),
                )

            name_container = ft.Container(
                content=name_control,
                width=350,
                height=40,
                alignment=ft.alignment.center_left,
                border=ft.border.all(1, ft.Colors.GREY),
                padding=ft.padding.only(left=8, right=8),
            )

            # 決定ボタン
            decide_button = ft.ElevatedButton(
                "決定",
                bgcolor=ft.Colors.PURPLE,
                color=ft.Colors.WHITE,
                visible=is_editing,
                on_click=lambda e, tid=trip_id: finish_rename(tid),
            )

            decide_container = ft.Container(
                content=decide_button,
                width=100,
                height=40,
                alignment=ft.alignment.center,
            )

            # 名前を変更ボタン
            rename_button = ft.ElevatedButton(
                "名前を変更",
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                visible=not is_editing,
                on_click=lambda e, tid=trip_id, nm=name: start_rename(tid, nm),
            )

            rename_container = ft.Container(
                content=rename_button,
                width=120,
                height=40,
                alignment=ft.alignment.center,
            )

            # 非表示
            hide_btn = ft.ElevatedButton(
                "非表示",
                bgcolor=ft.Colors.YELLOW,
                color=ft.Colors.BLACK,
                on_click=lambda e, tid=trip_id: (hide_trip(tid), load_trips()),
            )

            hide_container = ft.Container(
                content=hide_btn,
                width=120,
                height=40,
                alignment=ft.alignment.center,
            )

            # 削除
            delete_btn = ft.ElevatedButton(
                "削除",
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                on_click=lambda e, tid=trip_id: (delete_trip(tid), load_trips()),
            )

            delete_container = ft.Container(
                content=delete_btn,
                width=120,
                height=40,
                alignment=ft.alignment.center,
            )

            trip_row = ft.Row(
                controls=[
                    name_container,
                    decide_container,
                    rename_container,
                    hide_container,
                    delete_container,
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )

            trip_list.controls.append(trip_row)

        trip_list.visible = len(trips) > 0
        page.update()

    # -------------------------
    # Trip追加
    # -------------------------
    def add_trip(e):
        ds = normalize_date(date_start_field.value.strip())
        de = normalize_date(date_end_field.value.strip())
        place = place_field.value.strip()

        if ds == "":
            return

        if de == "":
            de = ds

        display_name = make_display_name(ds, de, place)
        add_trip_to_db(display_name, ds, de)

        date_start_field.value = ""
        date_end_field.value = ""
        place_field.value = ""

        load_trips()
        trip_list.scroll_to(offset=1.0, duration=200)

    # 入力欄
    date_start_field = ft.TextField(label="開始日 (YYYY/MM/DD)", width=150, border_color=ft.Colors.BLUE, color=ft.Colors.BLACK)
    date_end_field = ft.TextField(label="終了日 (YYYY/MM/DD)", width=150, border_color=ft.Colors.BLUE, color=ft.Colors.BLACK)
    place_field = ft.TextField(label="地点名", width=200, border_color=ft.Colors.BLUE, color=ft.Colors.BLACK)

    add_section = ft.Row(
        controls=[
            date_start_field,
            date_end_field,
            place_field,
            ft.ElevatedButton("Trip を追加", on_click=add_trip, 
                color=ft.Colors.BLACK, bgcolor=ft.Colors.LIGHT_BLUE_300
            ),
            ft.Text("例）2026/02/17〜2026/02/18 Fukuoka", color=ft.Colors.BLACK),
        ]
    )

    # 並び替え
    sort_button = ft.ElevatedButton(
        "↑↓",
        bgcolor=ft.Colors.BROWN,
        color=ft.Colors.WHITE,
        on_click=lambda e: (setattr(state, "sort_desc", not state.sort_desc), load_trips()),
    )

    # 初期ロード
    load_trips()

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("Trip を選択", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    sort_button,
                    ft.ElevatedButton(
                        "全てのTripを非表示/表示",
                        bgcolor=ft.Colors.ORANGE,
                        color=ft.Colors.BLACK,
                        on_click=lambda e: (toggle_all_trips(), load_trips()),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(content=trip_list, height=400),
            add_section,
        ]
    )