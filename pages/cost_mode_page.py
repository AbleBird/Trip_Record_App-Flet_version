# import flet as ft
# import sqlite3
# from db.database import DB_NAME

# class FormPage(ft.Column):
#     def __init__(self, page):
#         print("FormPage loaded")

#         super().__init__()

#         self.page = page

#         self.time_field = ft.TextField(label="時刻")
#         self.place_field = ft.TextField(label="場所")
#         self.cost_field = ft.TextField(label="費用")
#         self.note_field = ft.TextField(label="見どころ", multiline=True, min_lines=3, max_lines=8, expand=True)
#         self.photo_field = ft.TextField(label="写真ファイル名（カンマ区切り）", multiline=True)
#         self.video_field = ft.TextField(label="動画ファイル名（カンマ区切り）", multiline=True)

#         def save_data(e):
#             conn = sqlite3.connect(DB_NAME)
#             cur = conn.cursor()
#             cur.execute("""
#                 INSERT INTO logs (time, place, cost, note, photo_files, video_files)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             """, (
#                 self.time_field.value,
#                 self.place_field.value,
#                 self.cost_field.value,
#                 self.note_field.value,
#                 self.photo_field.value,
#                 self.video_field.value
#             ))
#             conn.commit()
#             conn.close()

#             page.snack_bar = ft.SnackBar(ft.Text("保存しました"))
#             page.snack_bar.open = True
#             page.update()

#         self.controls += [
#             ft.Text("入力ページ", size=30),
#             self.time_field,
#             self.place_field,
#             self.cost_field,
#             self.note_field,
#             self.photo_field,
#             self.video_field,
#             ft.ElevatedButton("保存", on_click=save_data),
#             ft.ElevatedButton("戻る", on_click=lambda _: page.go("/")),
#         ]