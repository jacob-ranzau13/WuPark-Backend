'''
receiver.py receives data from the sender.py script and updates the SQLite database accordingly.
'''

import socket as sock
import sqlite3 as sql

conn = sql.connect('lots.db')
cursor = conn.cursor()

socket = sock.socket()
port = 12345

socket.bind(('127.0.0.1', port))
socket.listen(5)

for i in range(5):
    while True:
        print("waiting for connection " + str(i))
        c, addr = socket.accept()
        print("Got connection from", addr)

        data = c.recv(1024)
        bytenum = 0
        lotnumber = 0

        for byte in data:
            if(bytenum == 0): # first byte is holds number of packets (mostly unused, may be useful later)
                bytenum += 1
            elif(bytenum == 1): # second byte is lot number
                lotnumber = int(byte)
                cursor.execute('UPDATE parkingLots SET lotStatus = ? WHERE name = ?', (b'', str(lotnumber))) # reset lotStatus to empty bytes
                # header = len(data).to_bytes(1,'big') + lotnumber.to_bytes(1,'big') # build a header out of the first two bytes
                # cursor.execute('UPDATE parkingLots SET lotStatus = ? WHERE name = ?', (header, str(lotnumber))) # insert header into db
                conn.commit()
                bytenum += 1
            else: # all further bytes refer to whether a space is taken (1) or free (0)
                cursor.execute('SELECT lotStatus FROM parkingLots WHERE name = ?', (str(lotnumber),)) # get the header from the db
                row = cursor.fetchone()
                existing_bytes = row[0] if row and row[0] else b''
                combined_bytes = existing_bytes + byte.to_bytes(1, 'big') # add data bytes to the header
                cursor.execute('UPDATE parkingLots SET lotStatus = ? WHERE name = ?', (combined_bytes, str(lotnumber)))
                conn.commit()

        cursor.execute('SELECT lotStatus FROM parkingLots WHERE name = ?', (str(lotnumber),))
        row = cursor.fetchone()
        print(row)

        c.close()
        break

conn.commit()
conn.close()
socket.close()