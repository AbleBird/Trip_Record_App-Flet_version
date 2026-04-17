# components/table_state.py

def init_state(page):
    """
    TripTopPage が呼ばれたときに状態を初期化する。
    page.go() を使わず、page 内に状態を保持する。
    """
    if not hasattr(page, "hide_middle"):
        page.hide_middle = False
    if not hasattr(page, "expand_target"):
        page.expand_target = None


def toggle_middle(page):
    """
    黄色ボタン用：全ての中間行を折りたたむ／展開。
    expand_target はリセットする。
    """
    page.hide_middle = not page.hide_middle
    page.expand_target = None


def show_middle(page, idx):
    """
    茶色ボタン用：押された行だけ展開する。
    hide_middle を False にし、expand_target に行番号を記録。
    """
    page.hide_middle = True
    page.expand_target = idx


def rebuild(page, trip_id, TripTopPage):
    """
    TripTopPage の UI をその場で再構築して即時反映する。
    page.go() を使わないのがポイント。
    """
    new_view = TripTopPage(page, trip_id)
    page.views[-1].controls = new_view.controls
    page.update()
