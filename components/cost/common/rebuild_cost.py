# components/cost/common/rebuild_cost.py

def rebuild_cost(page, trip_id, page_builder):
    """
    page_builder: CostModePage や TransportCostPage など、
                  ページを構築する関数そのもの
    """
    new_view = page_builder(page, trip_id)

    page.views[-1].controls = new_view.controls
    page.update()
