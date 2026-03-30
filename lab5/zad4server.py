import socket
import threading

HOST = "0.0.0.0"
PORT = 5001

def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print("TCP serwer działa")

        conn, addr = s.accept()
        with conn:
            print("TCP połączenie:", addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break

def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print("UDP serwer działa")

        while True:
            data, addr = s.recvfrom(1024)
            # nic nie robimy, tylko odbieramy

# ================= MAIN =================
threading.Thread(target=tcp_server, daemon=True).start()
threading.Thread(target=udp_server, daemon=True).start()

input("Serwer działa\n")