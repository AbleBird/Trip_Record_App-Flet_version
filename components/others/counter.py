# components/others/counter.py

import flet as ft

def build_counter(add_count_getter, set_add_count):
    field = ft.TextField(
        value=str(add_count_getter()),
        width=60,
        height=30,
        read_only=True,
        text_align=ft.TextAlign.CENTER,
        color=ft.Colors.BLACK,
    )

    def inc(e):
        v = min(10, add_count_getter() + 1)
        set_add_count(v)
        field.value = str(v)
        field.update()

    def dec(e):
        v = max(1, add_count_getter() - 1)
        set_add_count(v)
        field.value = str(v)
        field.update()

    return ft.Row(
        [
            ft.Container(expand=True),
            ft.Text("追加行数：", size=14, color=ft.Colors.BLACK),
            field,
            ft.IconButton(icon=ft.Icons.ADD, on_click=inc),
            ft.IconButton(icon=ft.Icons.REMOVE, on_click=dec),
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=10,
    )
