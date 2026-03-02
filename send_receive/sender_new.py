import socket as sock

for _ in range(5):
    socket = sock.socket()
    port = 12345
    socket.connect(('127.0.0.1', port))

    numBytes = int(input("Enter number of bytes to send (including this byte and lot number, minimum 3): "))
    lotNum = int(input("Enter lot number: "))
    data = bytearray()

    data.extend(numBytes.to_bytes(1, 'big'))  # 1 byte, big-endian
    data.extend(lotNum.to_bytes(1, 'big'))

    for _ in range(numBytes - 2):
        value = int(input("Enter byte value (0-255): "))
        data.extend(value.to_bytes(1, 'big'))

    while True:
        socket.sendall(data) # sending bytes, no encoding necessary
        socket.close()
        break