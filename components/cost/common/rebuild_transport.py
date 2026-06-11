# components/cost/common/rebuild_transport.py

def rebuild_transport(page, trip_id, clicked_date):
    from pages.transport_cost_page import TransportCostModePage

    new_view = TransportCostModePage(page, trip_id, clicked_date)

    page.views[-1].controls = new_view.controls
    page.update()
