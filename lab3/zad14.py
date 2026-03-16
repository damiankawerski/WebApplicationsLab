import socket

hex_data = """
ed 74 0b 55 00 24 ef fd
70 72 6f 67 72 61 6d 6d 69 6e 67 20 69 6e 20 70
79 74 68 6f 6e 20 69 73 20 66 75 6e
"""

data = bytes.fromhex(hex_data)

src_port = int.from_bytes(data[0:2], "big")
dst_port = int.from_bytes(data[2:4], "big")
length = int.from_bytes(data[4:6], "big")

payload = data[8:]
payload_text = payload.decode()

msg = f"zad14odp;src;{src_port};dst;{dst_port};data;{payload_text}"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(msg.encode(), ("127.0.0.1", 2910))

resp, _ = sock.recvfrom(1024)
print(resp.decode())