# cost_state.py

def init_reorder_state(row):
    if "reorder_open" not in row:
        row["reorder_open"] = False


def toggle_reorder_state(row):
    row["reorder_open"] = not row["reorder_open"]
    return row["reorder_open"]


def can_move_up(index):
    return index > 0


def can_move_down(index, total):
    return index < total - 1
