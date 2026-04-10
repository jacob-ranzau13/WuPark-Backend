#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sx126x as lora
import time

PACKET_PAYLOAD = 222  # 240 max payload - 6 bytes routing header - 13 bytes custom header
"""
routing header layout (6 bytes):
    [0:2]  destination address (uint16, big-endian)
    [2:4]  source address      (uint16, big-endian)
    [4:6]  frequency offset    (uint16, MHz offset from base frequency, e.g. 65 for 915 MHz if base is 850 MHz)

custom header layout (13 bytes):
    [0:2]  packet number   (uint16, big-endian)
    [2:4]  checksum        (uint16, sum of data bytes & 0xFFFF)
    [4:6]  total packets   (uint16, big-endian)
    [6:8]  node id          (uint16, big-endian, optional for tracking)
    [8:9]  node status     (uint8, e.g. 0 for normal, 1 for warning, 2 for error)
    [9:13] timestamp       (uint32, seconds since epoch, optional for tracking)
"""

class sender_node():
    def __init__(self, addr: int = 0):
        self.node = lora.sx126x(serial_num="/dev/ttyS0", freq=915, addr=addr, power=22, rssi=True, air_speed=2400, relay=False)
        self.addr = addr
    
    def send_file(self, dest_addr: int, filepath: str, lot_id: int = 0, node_status: int = 0):

        with open(filepath, "rb") as f:
            data = bytearray(f.read())

        chunks = [data[i:i + PACKET_PAYLOAD] for i in range(0, len(data), PACKET_PAYLOAD)]
        total_packets = len(chunks)

        for packet_num, chunk in enumerate(chunks):
            checksum = sum(chunk) & 0xFFFF

            header = (
                packet_num.to_bytes(2, "big") +
                checksum.to_bytes(2, "big") +
                total_packets.to_bytes(2, "big") +
                lot_id.to_bytes(1, "big") +
                node_status.to_bytes(1, "big") +
                int(time.time()).to_bytes(4, "big")
            )

            print(f"sending packet {packet_num}/{total_packets}")
            self.send_bytes(dest_addr, bytearray(header + chunk), 915)
            time.sleep(5)               # brief gap between packets

    def send_bytes(self, dest_addr: int, payload: bytearray, dest_freq: int = 915):
        offset_freq = dest_freq - (850 if dest_freq > 850 else 410)

        header = bytes([
            dest_addr >> 8,
            dest_addr & 0xFF,
            self.node.addr >> 8,
            self.node.addr & 0xFF,
            offset_freq >> 8,
            offset_freq & 0xFF,
        ])

        self.node.send(header + bytes(payload))

class receiver_node():
    def __init__(self, addr: int = 0):
        self.node = lora.sx126x(serial_num="/dev/ttyS0", freq=915, addr=addr, power=22, rssi=True, air_speed=2400, relay=False)
        self.addr = addr
    
    def receive_file(self, output_path: str):
        """ nstruct a file.

        Args:
            output_path: Where to write the reconstructed file.
        """
        packets = {}
        total_packets = None
        dest_addr = self.addr

        while total_packets is None or len(packets) < total_packets:
            raw = self.node.receive()
            if raw is None:
                continue
            print("Received")
            # routing header: [dst_addr(2), src_addr(2), freq_offset(2)] = 6 bytes
            # custom header:  [packet_num(2), checksum(2), total_packets(2), lot_id(2), node_status(1), timestamp(4)] = 13 bytes
            if len(raw) < 18:  # 6 bytes routing header + 13 bytes custom header
                print("Packet too short, skipping.")
                continue

            dst_addr = (raw[0] << 8) + raw[1]
            print(str(dst_addr))
            if dst_addr != dest_addr and dst_addr != 65535:
                print("Skipped")
                continue  # not for us

            packet_num    = int.from_bytes(raw[6:8],   "big")
            checksum      = int.from_bytes(raw[8:10],  "big")
            total_packets = int.from_bytes(raw[10:12], "big")
            lot_id        = int.from_bytes(raw[12], "big")
            node_status   = raw[13]
            timestamp     = int.from_bytes(raw[14:18], "big")
            chunk         = raw[18:]

            if packet_num in packets:
                print(f"Duplicate packet {packet_num}, ignoring.")
                continue

            expected_checksum = sum(chunk) & 0xFFFF
            if checksum != expected_checksum:
                print(f"Checksum mismatch on packet {packet_num}, discarding.")
                continue

            packets[packet_num] = chunk
            print(f"Received packet {packet_num + 1}/{total_packets}")

        with open(output_path, "wb") as f:
            for i in range(total_packets):
                f.write(packets[i])

        print(f"File reconstructed: {output_path}")
        return (lot_id, node_status, timestamp, output_path)

def main():
    nodetype = int(input("Enter node type (1 for sender, 2 for receiver): "))
    addr = int(input("Enter node address (0-65535): "))
    if nodetype == 1:
        sender = sender_node(addr)
        dest_addr = int(input("Enter destination address (0-65535, 65535 for broadcast): "))
        filepath = "error.jpg"
        lot_id = int(input("Enter lot ID (0-255): "))
        node_status = int(input("Enter node status (0=normal, 1=warning, 2=error): "))
        sender.send_file(dest_addr, filepath, lot_id, node_status)
    elif nodetype == 2:
        receiver = receiver_node(addr)
        output_path = "received_file.jpg"
        receiver.receive_file(output_path)
    else:
        print("Invalid node type")
        main()

if __name__ == "__main__":
    main()
