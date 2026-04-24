# cost_logic.py

# ▼ 並べ替え状態
def init_row_state(row):
    if "reorder_open" not in row:
        row["reorder_open"] = False


def toggle_reorder_state(row):
    row["reorder_open"] = not row["reorder_open"]
    return row["reorder_open"]


def make_up_handler(on_reorder, date, index):
    return lambda e: on_reorder(date, index, index - 1)


def make_down_handler(on_reorder, date, index):
    return lambda e: on_reorder(date, index, index + 1)


def reorder_row(on_reorder, date, old_index, new_index):
    on_reorder(date, old_index, new_index)
