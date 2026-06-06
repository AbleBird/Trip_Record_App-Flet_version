# components/others/sync_logic.py

"""
3ページ共通の同期/非同期ロジックを管理するモジュール。

・同期/非同期モードの切り替え
・ページごとの「常に同期すべき操作」の定義
・ページごとの「同期すべきカラム」の定義
・Undo（元に戻す）用の一時保存領域（将来拡張）
"""

# ----------------------------------------
# 同期モード（True = 同期 / False = 非同期）
# ----------------------------------------
_sync_mode = True


def is_sync() -> bool:
    """現在の同期モードを返す"""
    return _sync_mode


def toggle_sync() -> bool:
    """同期モードを切り替えて返す"""
    global _sync_mode
    _sync_mode = not _sync_mode
    return _sync_mode


# ----------------------------------------
# ページごとの同期ルール
# ----------------------------------------
SYNC_RULES = {
    "trip_top": {
        # 行追加/削除/日付行操作は常に同期
        "always_sync": {"add_row", "delete_row", "add_date", "delete_date"},
        "sync_columns": set(),  # TripTopPage はカラム編集なし
    },

    "cost_mode": {
        "always_sync": {"add_row", "delete_row"},
        "sync_columns": {"amount"},  # 金額は常に同期
    },

    "transport_cost": {
        "always_sync": {"add_row", "delete_row"},
        "sync_columns": {"amount", "category"},  # 金額と大区分は常に同期
    },
}


# ----------------------------------------
# 同期すべきかどうか判定する関数
# ----------------------------------------
def should_sync(page_type: str, action: str, column: str | None = None) -> bool:
    """
    page_type: "trip_top" / "cost_mode" / "transport_cost"
    action: "add_row" / "delete_row" / "add_date" / "delete_date" / "edit"
    column: 編集対象カラム（edit の場合のみ）
    """

    rules = SYNC_RULES.get(page_type)
    if rules is None:
        raise ValueError(f"Unknown page_type: {page_type}")


    # 行追加/削除などの強制同期
    if action in rules["always_sync"]:
        return True

    # カラム編集で強制同期
    if action == "edit" and column in rules["sync_columns"]:
        return True

    # それ以外は同期モードに従う
    return is_sync()


# ----------------------------------------
# Undo（元に戻す）用の一時保存領域（将来拡張）
# ----------------------------------------
# UNDO_STACK = []


# def push_undo(data: dict):
#     """将来のUndo機能用：変更前の状態を保存"""
#     UNDO_STACK.append(data)


# def pop_undo() -> dict | None:
#     """Undo実行用"""
#     if UNDO_STACK:
#         return UNDO_STACK.pop()
#     return None
