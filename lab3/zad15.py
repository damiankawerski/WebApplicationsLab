import socket

hex_data = """
45 00 00 4e f7 fa 40 00 38 06 9d 33 d4 b6 18 1b
c0 a8 00 02 0b 54 b9 a6 fb f9 3c 57 c1 0a 06 c1
80 18 00 e3 ce 9c 00 00 01 01 08 0a 03 a6 eb 01
00 0b f8 e5 6e 65 74 77 6f 72 6b 20 70 72 6f
67 72 61 6d 6d 69 6e 67 20 69 73 20 66 75 6e
"""

data = bytes.fromhex(hex_data)

version = data[0] >> 4
ihl = (data[0] & 0xF) * 4
protocol = data[9]

src_ip = ".".join(map(str, data[12:16]))
dst_ip = ".".join(map(str, data[16:20]))

if protocol == 6:
    protocol_name = "TCP"
elif protocol == 17:
    protocol_name = "UDP"
else:
    protocol_name = "INNY"

layer4_start = ihl
src_port = int.from_bytes(data[layer4_start:layer4_start + 2], "big")
dst_port = int.from_bytes(data[layer4_start + 2:layer4_start + 4], "big")

if protocol == 6:
    layer4_header_len = (data[layer4_start + 12] >> 4) * 4
elif protocol == 17:
    layer4_header_len = 8
else:
    layer4_header_len = 0

payload = data[layer4_start + layer4_header_len:]
payload_len = len(payload)
payload_text = payload.decode("utf-8", errors="replace")

print(f"IPv{version}, src={src_ip}, dst={dst_ip}, proto={protocol} ({protocol_name})")
print(f"src_port={src_port}, dst_port={dst_port}, data_bytes={payload_len}")
print(f"data='{payload_text}'")

msgA = f"zad15odpA;ver;{version};srcip;{src_ip};dstip;{dst_ip};type;{protocol}"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 2911

sock.sendto(msgA.encode(), (SERVER_HOST, SERVER_PORT))

resp, _ = sock.recvfrom(1024)
print(resp.decode())

if resp.decode() == "TAK":
    msgB = f"zad15odpB;srcport;{src_port};dstport;{dst_port};data;{payload_text}"

    sock.sendto(msgB.encode(), (SERVER_HOST, SERVER_PORT))

    resp, _ = sock.recvfrom(1024)
    print(resp.decode())

sock.close()