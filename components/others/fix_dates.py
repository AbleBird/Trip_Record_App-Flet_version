# components/others/fix_dates.py

from components.others.date_manager import update_date_rows
from components.others.sync_dates import sync_cost_dates

def fix_dates_for_trip(trip_id):
    # travel.db の日付行だけ更新する
    update_date_rows(trip_id)

    # cost.db 側の更新は今は行わない（後で sync_dates.py で対応）
    sync_cost_dates(trip_id)