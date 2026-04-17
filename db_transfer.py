import sqlite3

old = sqlite3.connect("travel_old.db")
new = sqlite3.connect("travel.db")

old_cur = old.cursor()
new_cur = new.cursor()

# trips の移行
rows = old_cur.execute("SELECT id, name, date_start, date_end, hidden FROM trips").fetchall()
new_cur.executemany(
    "INSERT INTO trips (id, name, date_start, date_end, hidden) VALUES (?, ?, ?, ?, ?)",
    rows
)

# trip_rows の移行（cost を除く）
rows = old_cur.execute("""
    SELECT id, trip_id, class_id, order_base, order_index,
           planned_time, actual_time, place, by, point, note, image, video
    FROM trip_rows
""").fetchall()

new_cur.executemany("""
    INSERT INTO trip_rows
    (id, trip_id, class_id, order_base, order_index,
     planned_time, actual_time, place, by, point, note, image, video)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

new.commit()
old.close()
new.close()

print("Transfered data from travel_old.db to travel.db")