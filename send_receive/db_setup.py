import sqlite3 as sql

conn = sql.connect('lots.db')
c = conn.cursor()

c.execute('SELECT lotStatus FROM parkingLots WHERE name = ?', ('1',))
row = c.fetchone()
print(row)

conn.commit()
conn.close()