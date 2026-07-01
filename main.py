# main.py

import flet as ft
from pages.home_page import HomePage
from pages.trip_top_page import TripTopPage
from db.travel_database import init_travel_db
from db.cost_database import init_cost_db
from pages.cost_mode_page import CostModePage
from pages.transport_cost_page import TransportCostModePage

def main(page: ft.Page):
    print("MAIN STARTED")
    init_travel_db()
    init_cost_db()

    page.bgcolor = ft.Colors.WHITE
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

        # ホーム
        if page.route == "/":
            page.views.append(
                ft.View("/", controls=[HomePage(page)], bgcolor=ft.Colors.WHITE)
            )

        # 交通費モード
        elif "/cost/transport/" in page.route:
            parts = page.route.split("/")
            trip_id = int(parts[2])
            date = "/".join(parts[5:8])

            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[TransportCostModePage(page, trip_id, date)],
                    bgcolor=ft.Colors.WHITE,
                )
            )

        # cost モード
        elif page.route.startswith("/trip/") and page.route.endswith("/cost"):
            trip_id = int(page.route.split("/")[2])
            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[CostModePage(page, trip_id)],
                    bgcolor=ft.Colors.WHITE,
                )
            )

        # TripTopPage
        elif page.route.startswith("/trip/"):
            trip_id = int(page.route.split("/")[2])
            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[TripTopPage(page, trip_id)],
                    bgcolor=ft.Colors.WHITE,
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main)
