import socket

hex_data = """
0b 54 89 8b 1f 9a 18 ec bb b1 64 f2 80 18
00 e3 67 71 00 00 01 01 08 0a 02 c1 a4 ee
00 1a 4c ee 68 65 6c 6c 6f 20 3a 29
"""

data = bytes.fromhex(hex_data)

src_port = int.from_bytes(data[0:2], "big")
dst_port = int.from_bytes(data[2:4], "big")

data_offset = (data[12] >> 4) * 4

payload = data[data_offset:]
payload_text = payload.decode()

msg = f"zad13odp;src;{src_port};dst;{dst_port};data;{payload_text}"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(msg.encode(), ("127.0.0.1", 2909))

resp, _ = sock.recvfrom(1024)
print(resp.decode())