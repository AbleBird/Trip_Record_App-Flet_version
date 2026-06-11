#components/cost/transport_cost_table.py

import flet as ft
from components.cost.common.cost_elements import cell

MAIN_CATEGORY = ["鉄道", "バス", "タクシー", "船", "その他通行料等"]

RAIL_SUB = [
    "乗車券",
    "座席指定券",
    "自由席特急券",
    "立席特急券",
    "指定席特急券",
    "グリーン券",
    "その他特別券",
]

TICKET_TYPES = [
    "紙チケット",
    "紙切符",
    "現金",
    "交通系IC",
    "クレカ（タッチ）",
    "QR決済",
    "チケレス",
    "モバチケ",
    "その他",
]

TC_COLS = [
    40,   # ＋
    100,  # 大区分
    160,  # 中区分
    120,  # 名称
    100,  # 出発
    100,  # 到着
    100,  # 経由
    160,  # 路線名
    160,  # チケット種別
    80,  # 金額
    80,  # 累計
    40,   # 削除
]


def TransportCostTable(
        page, 
        trip_id, 
        date, 
        rows, 
        on_add, 
        on_delete, 
        on_edit, 
        get_add_count
    ):

    table_rows = []

    # -------------------------
    # 日付行（CostTable と同じ）
    # -------------------------
    table_rows.append(
        ft.Row(
            [
                ft.Container(width=TC_COLS[0]),
                cell(
                    ft.Text(date, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    width=sum(TC_COLS[1:9]),
                    bgcolor=ft.Colors.GREY_200,
                ),
                cell(
                    ft.Text("合計", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    width=TC_COLS[9],
                    bgcolor=ft.Colors.GREY_200,
                    align=ft.alignment.center,
                ),
                cell(
                    ft.Text("0 円", color=ft.Colors.BLACK),
                    width=TC_COLS[10],
                    bgcolor=ft.Colors.GREY_200,
                    align=ft.alignment.center,
                ),
                ft.Container(width=TC_COLS[11]),
            ],
            spacing=0,
        )
    )

    # -------------------------
    # rows が空なら初期行を 1 行作る
    # -------------------------
    if not rows:
        rows = [{
            "id": -1,
            "category": "",
            "subcategory": "",
            "name": "",
            "from_station": "",
            "to_station": "",
            "via": "",
            "line": "",
            "ticket_type": "",
            "amount": 0,
        }]

    # -------------------------
    # データ行
    # -------------------------
    cumulative = 0

    for row in rows:
        row_id = row["id"]
        cumulative += row["amount"]

        table_rows.append(
            ft.Row(
                [
                    # 0: ＋ボタン（枠線なし）
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_color=ft.Colors.BLUE,
                            on_click=lambda e, d=date: on_add(d, get_add_count(), False)  # ← とりあえず sync_flag は False（ページ側で上書き）,
                        ),
                        width=TC_COLS[0],
                        alignment=ft.alignment.center,
                    ),

                    # 1: 大区分（Dropdown）
                    cell(
                        ft.Dropdown(
                            value=row["category"],
                            options=[ft.dropdown.Option(c) for c in MAIN_CATEGORY],
                            bgcolor=ft.Colors.WHITE,
                            color=ft.Colors.BLACK,
                            border=ft.InputBorder.NONE,     # ← 追加
                            on_change=lambda e, rid=row_id: on_edit(rid, "category", e.control.value, False),
                        ),
                        width=TC_COLS[1],
                    ),

                    # 2: 中区分（Dropdown）
                    cell(
                        ft.Dropdown(
                            value=row["subcategory"],
                            options=[
                                ft.dropdown.Option(s)
                                for s in (
                                    RAIL_SUB if row["category"] in ["", "鉄道"]     # ★ 初期値 "" を鉄道扱いに
                                    else ["運賃"] if row["category"] in ["バス", "タクシー"]
                                    else ["乗船券"] if row["category"] == "船"
                                    else ["通行料"]
                                )
                            ],
                            bgcolor=ft.Colors.WHITE,
                            color=ft.Colors.BLACK,
                            border=ft.InputBorder.NONE,     # ← 追加
                            on_change=lambda e, rid=row_id: on_edit(rid, "subcategory", e.control.value, False),
                        ),
                        width=TC_COLS[2],
                    ),

                    # 3: 名称（TextField + label）
                    cell(
                        ft.TextField(
                            label="名称",
                            value=row["name"],
                            color=ft.Colors.BLACK,
                            border=ft.InputBorder.NONE,     # ← 追加
                            disabled = (
                                (row["category"] in ["バス", "タクシー"] and row["subcategory"] == "運賃") or
                                (row["category"] == "船" and row["subcategory"] == "乗船券") or
                                (row["category"] == "その他通行料等" and row["subcategory"] == "通行料")
                            ),
                            on_blur=lambda e, rid=row_id: on_edit(rid, "name", e.control.value, False),
                        ),
                        width=TC_COLS[3],
                    ),

                    # 4: 出発
                    cell(
                        ft.TextField(
                            label="出発駅/地点",
                            value=row["from_station"],
                            color=ft.Colors.BLACK,
                            border=ft.InputBorder.NONE,     # ← 追加
                            on_blur=lambda e, rid=row_id: on_edit(rid, "from_station", e.control.value, False),
                        ),
                        width=TC_COLS[4],
                    ),

                    # 5: 到着
                    cell(
                        ft.TextField(
                            label="到着駅/地点",
                            value=row["to_station"],
                            color=ft.Colors.BLACK,
                            border=ft.InputBorder.NONE,     # ← 追加
                            on_blur=lambda e, rid=row_id: on_edit(rid, "to_station", e.control.value, False),
                        ),
                        width=TC_COLS[5],
                    ),

                    # 6: 経由
                    cell(
                        ft.TextField(
                            label="経由",
                            value=row["via"],
                            color=ft.Colors.BLACK,
                            border=ft.InputBorder.NONE,     # ← 追加
                            on_blur=lambda e, rid=row_id: on_edit(rid, "via", e.control.value, False),
                        ),
                        width=TC_COLS[6],
                    ),

                    # 7: 路線名
                    cell(
                        ft.TextField(
                            label="路線名",
                            value=row["line"],
                            color=ft.Colors.BLACK,
                            border=ft.InputBorder.NONE,     # ← 追加
                            on_blur=lambda e, rid=row_id: on_edit(rid, "line", e.control.value, False),
                        ),
                        width=TC_COLS[7],
                    ),

                    # 8: チケット種別（Dropdown）
                    cell(
                        ft.Dropdown(
                            value=row["ticket_type"],
                            options=[ft.dropdown.Option(t) for t in TICKET_TYPES],
                            bgcolor=ft.Colors.WHITE,
                            color=ft.Colors.BLACK,
                            border=ft.InputBorder.NONE,     # ← 追加
                            on_change=lambda e, rid=row_id: on_edit(rid, "ticket_type", e.control.value, False),
                        ),
                        width=TC_COLS[8],
                    ),

                    # 9: 金額
                    cell(
                        ft.TextField(
                            label="金額",
                            value=str(row["amount"]),
                            text_align=ft.TextAlign.RIGHT,
                            color=ft.Colors.BLACK,
                            border=ft.InputBorder.NONE,     # ← 追加
                            on_blur=lambda e, rid=row_id: on_edit(rid, "amount", e.control.value, False),
                        ),
                        width=TC_COLS[9],
                    ),

                    # 10: 累計
                    cell(
                        ft.Text(f"{cumulative:,}", color=ft.Colors.BLACK),
                        width=TC_COLS[10],
                        align=ft.alignment.center,
                    ),

                    # 11: 削除（枠線なし）
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, rid=row_id: on_delete(rid, False),
                        ),
                        width=TC_COLS[11],
                        alignment=ft.alignment.center,
                    ),
                ],
                spacing=0,
            )
        )

    return ft.Column(table_rows, spacing=0)
