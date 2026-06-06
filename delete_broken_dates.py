# delete_broken_dates.py

import sqlite3

conn = sqlite3.connect("cost.db")
cur = conn.cursor()

# 壊れた日付を削除（? を含むもの）
cur.execute("DELETE FROM transport_costs WHERE date LIKE '%?%'")

# 年だけの壊れた日付（例: '2026'）を削除
cur.execute("DELETE FROM transport_costs WHERE length(date) < 8")

conn.commit()
conn.close()

print("Cleanup complete.")
