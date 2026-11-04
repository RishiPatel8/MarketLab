import sqlite3

conn = sqlite3.connect("backend/marketlab.db")
c = conn.cursor()
for r in c.execute("SELECT name, sql FROM sqlite_master WHERE tbl_name = 'instruments'"):
    print(r[0])
    print(r[1])
    print("-" * 40)
