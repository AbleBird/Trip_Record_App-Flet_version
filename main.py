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

        # ★ 交通費専用モード
        elif "/cost/transport/" in page.route:
            try:
                parts = page.route.split("/")
                trip_id = int(parts[2])
                date = parts[5]
            except:
                trip_id = None
                date = None

            # TransportCostModePage は View を返すので、そのまま append する
            page.views.append(
                TransportCostModePage(page, trip_id, date)
            )


        # ★ まず cost モードを先に判定
        elif page.route.startswith("/trip/") and page.route.endswith("/cost"):
            try:
                trip_id = int(page.route.split("/")[2])
            except:
                trip_id = None

            page.views.append(
                ft.View(
                    route=f"/trip/{trip_id}/cost",
                    controls=[CostModePage(page, trip_id)],
                    bgcolor=ft.Colors.WHITE,
                )
            )

        # ★ 次に TripTopPage（/trip/<id>）
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