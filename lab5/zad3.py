import socket

HOST = "127.0.0.1"

valid_ports = []

for port in range(1000, 10000):
    if str(port).endswith("666"):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(0.5)
            try:
                s.sendto(b"PING", (HOST, port))
                data, _ = s.recvfrom(1024)
                if data.decode() == "PONG":
                    print("Znaleziony port:", port)
                    valid_ports.append(port)
            except:
                pass

print("Sekwencja:", valid_ports)