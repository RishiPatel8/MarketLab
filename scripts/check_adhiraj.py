import sqlite3

conn = sqlite3.connect("backend/marketlab.db")
c = conn.cursor()
rows = c.execute("SELECT id, exchange, symbol, isin, bse_code FROM instruments WHERE symbol in ('ADHIRAJ', 'WEBSL', 'GCMCAPI')").fetchall()
print('Matches in DB:', rows)

# Also check all BSE records currently in DB
bse_in_db = c.execute("SELECT symbol, bse_code FROM instruments WHERE exchange = 'BSE'").fetchall()
print('Total BSE in DB:', len(bse_in_db))
for r in bse_in_db[:10]:
    print('BSE row in DB:', r)
