import flet as ft
from pages.home_page import HomePage
from pages.trip_top_page import TripTopPage
from db.database import init_db

def main(page: ft.Page):
    print("MAIN STARTED")
    init_db()

    # ページ全体の背景を白に
    page.bgcolor = ft.Colors.WHITE

    # テーマも白背景・黒文字に統一
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLACK,
            on_primary=ft.Colors.WHITE,
            surface=ft.Colors.WHITE,
            on_surface=ft.Colors.BLACK,
        )
    )

    def route_change(e):
        print("ROUTE:", page.route)
        page.views.clear()

        # ホーム画面
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    controls=[HomePage(page)],
                    bgcolor=ft.Colors.WHITE,
                )
            )

        # TripTopPage（/trip/<id>）
        elif page.route.startswith("/trip/"):
            try:
                trip_id = int(page.route.split("/")[2])
            except:
                trip_id = None

            page.views.append(
                ft.View(
                    route=f"/trip/{trip_id}",
                    controls=[TripTopPage(page, trip_id)],
                    bgcolor=ft.Colors.WHITE,
                )
            )

        page.update()
        
    page.on_route_change = route_change

    page.go("/")

ft.app(target=main)