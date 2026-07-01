# components/toppage/basic_cells.py

import flet as ft

def safe(v):
    return "" if v in (None, "None") else str(v)

def build_textfield_cell(value, width, on_blur):
    return ft.TextField(
        value=safe(value),
        width=width,
        height=48,
        on_blur=on_blur,
        color=ft.Colors.BLACK,
    )

# 各セルビルダー（BasicTable から import して使う）
def planned_time_cell(row, col_width, on_edit, idx):
    return build_textfield_cell(
        row.get("planned_time"),
        col_width,
        lambda e: on_edit(idx, "planned_time", e.control.value)
    )

def actual_time_cell(row, col_width, on_edit, idx):
    return build_textfield_cell(
        row.get("actual_time"),
        col_width,
        lambda e: on_edit(idx, "actual_time", e.control.value)
    )

def place_cell(row, col_width, on_edit, idx):
    return build_textfield_cell(
        row.get("place"),
        col_width,
        lambda e: on_edit(idx, "place", e.control.value)
    )

def by_cell(row, col_width, on_edit, idx):
    return build_textfield_cell(
        row.get("by"),
        col_width,
        lambda e: on_edit(idx, "by", e.control.value)
    )

def point_cell(row, col_width, on_edit, idx):
    return build_textfield_cell(
        row.get("point"),
        col_width,
        lambda e: on_edit(idx, "point", e.control.value)
    )

def note_cell(row, col_width, on_edit, idx):
    return build_textfield_cell(
        row.get("note"),
        col_width,
        lambda e: on_edit(idx, "note", e.control.value)
    )

def image_cell(row, col_width, on_edit, idx):
    return build_textfield_cell(
        row.get("image"),
        col_width,
        lambda e: on_edit(idx, "image", e.control.value)
    )

def video_cell(row, col_width, on_edit, idx):
    return build_textfield_cell(
        row.get("video"),
        col_width,
        lambda e: on_edit(idx, "video", e.control.value)
    )
