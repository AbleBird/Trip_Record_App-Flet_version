#components/cost/common/cost_elements.py

import flet as ft

TYPE_OPTIONS = ["食費", "宿泊費", "お土産代", "その他諸費"]

# 6列構造
COL_WIDTHS = [140, 200, 200, 150, 150, 200]   # Type, Title, Item, Amount, Cumulative, Note
DELETE_WIDTH = 50
HANDLE_WIDTH = 80

# ▼ ボタンサイズ（完全固定）
BTN_SIZE = 28
ICON_SIZE = 20     # ← 見た目の大きさ（小さく見える）

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