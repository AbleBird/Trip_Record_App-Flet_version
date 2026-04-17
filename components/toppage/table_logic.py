# components/table_logic.py

"""
BasicTable をスリム化するための折り畳み／展開ロジック専用モジュール。
UI（TextField, Container など）はここには書かず、
あくまで「どの middle 行を折り畳むか」「代表行を作るか」だけを担当する。
"""


# ---------------------------------------------------------
# middle グループを取得（expand_target が属する範囲）
# ---------------------------------------------------------
def get_middle_group(rows, idx):
    n = len(rows)

    if rows[idx].get("type") != 2:
        return None

    start = idx
    while start > 0 and rows[start - 1].get("type") == 2:
        start -= 1

    end = idx
    while end < n - 1 and rows[end + 1].get("type") == 2:
        end += 1

    return (start, end)


# ---------------------------------------------------------
# middle 行を折り畳むべきかどうか
# ---------------------------------------------------------
def should_collapse(row_type, i, hide_middle, expand_target, rows):

    if row_type != 2:
        return False

    if not hide_middle:
        return False

    if expand_target is None:
        return True

    if rows[expand_target].get("type") != 2:
        return True

    group = get_middle_group(rows, expand_target)
    if group is None:
        return True

    start, end = group

    return not (start <= i <= end)


# ---------------------------------------------------------
# middle グループの先頭判定
# ---------------------------------------------------------
def is_group_head(i, rows):
    return rows[i].get("type") == 2 and (i == 0 or rows[i-1].get("type") != 2)


# ---------------------------------------------------------
# 折り畳み時に代表行を表示すべきかどうか
# ---------------------------------------------------------
def should_show_collapsed_row(i, hide_middle, expand_target, rows):
    # まず「折り畳むべき middle 行」であること
    if not should_collapse(rows[i].get("type"), i, hide_middle, expand_target, rows):
        return False

    # その middle グループの先頭行だけ代表行を作る
    return is_group_head(i, rows)


# ---------------------------------------------------------
# 代表行（折り畳み時に表示する行）のデータ構造
# ---------------------------------------------------------
def build_collapsed_row(i):
    return {
        "index": i,
        "type": "collapsed",
    }
