import socket
import time

HOST = "127.0.0.1"
PORT = 5001
MESSAGE = b"x" * 1024
ITER = 1000

#TCP 
start = time.time()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    for _ in range(ITER):
        s.sendall(MESSAGE)

tcp_time = time.time() - start

# UDP
start = time.time()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    for _ in range(ITER):
        s.sendto(MESSAGE, (HOST, PORT))

udp_time = time.time() - start

print("TCP:", tcp_time)
print("UDP:", udp_time)