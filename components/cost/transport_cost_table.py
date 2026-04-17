# components/transport_cost_table.py

import flet as ft

MAIN_CATEGORY = ["鉄道", "バス", "タクシー", "船", "その他通行料等"]

RAIL_SUB = [
    "乗車券",
    "座席指定券",
    "自由席特急券",
    "指定席特急券",
    "グリーン券",
    "その他特別券",
]

TICKET_TYPES = [
    "紙のチケット",
    "現金",
    "交通系ICカード",
    "クレジットカード（タッチ）",
    "QR決済",
    "チケットレス",
    "モバイルチケット",
    "その他",
]

def TransportCostTable(page, trip_id, date, rows, on_add, on_delete, on_edit):

    table_controls = []

    # -------------------------
    # 日付行（プリセット）
    # -------------------------
    table_controls.append(
        ft.Container(
            content=ft.Text(
                f"{date} の交通費",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            padding=10,
            bgcolor=ft.Colors.GREY_300,
            border=ft.border.all(1, ft.Colors.BLACK),
        )
    )

    # -------------------------
    # 各行の描画
    # -------------------------
    for row in rows:
        row_id = row["id"]

        # 累計金額（ここでは rows の順番で累計）
        sorted_rows = sorted(rows, key=lambda r: r["id"])  # or order_index
        cumulative = 0
        for r in sorted_rows:
            cumulative += r["amount"]
            if r["id"] == row_id:
                break


        table_controls.append(
            ft.Row(
                [
                    # ＋ボタン（行追加）
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=ft.Colors.BLUE,
                        on_click=lambda e: on_add(),
                    ),

                    # 1列目：大区分
                    ft.Dropdown(
                        value=row["category"],
                        options=[ft.dropdown.Option(c) for c in MAIN_CATEGORY],
                        width=120,
                        on_change=lambda e, rid=row_id: on_edit(rid, "category", e.control.value),
                    ),

                    # 2列目：中区分（大区分に応じて変化）
                    ft.Dropdown(
                        value=row["subcategory"],
                        options=[
                            ft.dropdown.Option(s)
                            for s in (
                                RAIL_SUB if row["category"] == "鉄道"
                                else ["運賃"] if row["category"] in ["バス", "タクシー"]
                                else ["乗船券"] if row["category"] == "船"
                                else ["通行料"]
                            )
                        ],
                        width=150,
                        on_change=lambda e, rid=row_id: on_edit(rid, "subcategory", e.control.value),
                    ),

                    # 3列目：名称（鉄道の特別券など）
                    ft.TextField(
                        value=row["name"],
                        width=150,
                        on_blur=lambda e, rid=row_id: on_edit(rid, "name", e.control.value),
                        disabled=(
                            row["category"] != "鉄道" or row["subcategory"] == "乗車券"
                        ),
                    ),

                    # 4列目：出発地点
                    ft.TextField(
                        value=row["from_station"],
                        width=150,
                        on_blur=lambda e, rid=row_id: on_edit(rid, "from_station", e.control.value),
                    ),

                    # 5列目：到着地点
                    ft.TextField(
                        value=row["to_station"],
                        width=150,
                        on_blur=lambda e, rid=row_id: on_edit(rid, "to_station", e.control.value),
                    ),

                    # 6列目：経由
                    ft.TextField(
                        value=row["via"],
                        width=150,
                        on_blur=lambda e, rid=row_id: on_edit(rid, "via", e.control.value),
                    ),

                    # 7列目：路線名
                    ft.TextField(
                        value=row["line"],
                        width=150,
                        on_blur=lambda e, rid=row_id: on_edit(rid, "line", e.control.value),
                    ),

                    # 8列目：チケット種別
                    ft.Dropdown(
                        value=row["ticket_type"],
                        options=[ft.dropdown.Option(t) for t in TICKET_TYPES],
                        width=150,
                        on_change=lambda e, rid=row_id: on_edit(rid, "ticket_type", e.control.value),
                    ),

                    # 9列目：金額
                    ft.TextField(
                        value=f"{row['amount']:,}",
                        width=120,
                        text_align=ft.TextAlign.RIGHT,
                        on_blur=lambda e, rid=row_id: on_edit(rid, "amount", e.control.value),
                    ),

                    # 10列目：累計（読み取り専用）
                    ft.Container(
                        content=ft.Text(f"{cumulative:,}"),
                        width=120,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, ft.Colors.BLACK),
                    ),

                    # 削除ボタン
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        on_click=lambda e, rid=row_id: on_delete(rid),
                    ),
                ],
                spacing=0,
            )
        )

    return ft.Column(table_controls, spacing=10)
