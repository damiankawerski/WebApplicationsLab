import socket

HOST = "127.0.0.1"
PORT = 9003

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        server_sock.bind((HOST, PORT))
        print(f"[*] Serwer echo (UDP) nasłuchuje na {HOST}:{PORT}")

        while True:
            data, addr = server_sock.recvfrom(1024)
            print(f"[>] Odebrano od {addr}: {data.decode(errors='replace')}")

            server_sock.sendto(data, addr)
            print(f"[<] Odesłano do {addr}: {data.decode(errors='replace')}")

if __name__ == "__main__":
    main()