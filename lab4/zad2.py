import socket

HOST = "127.0.0.1"
PORT = 9002

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(1)
        print(f"[*] Serwer echo (TCP) nasłuchuje na {HOST}:{PORT}")

        while True:
            conn, addr = server_sock.accept()
            with conn:
                print(f"[+] Połączono z: {addr}")

                while True:
                    data = conn.recv(1024)
                    if not data:
                        print("[-] Klient zakończył połączenie.")
                        break

                    print(f"[>] Odebrano: {data.decode(errors='replace')}")
                    conn.sendall(data)
                    print(f"[<] Odesłano: {data.decode(errors='replace')}")

if __name__ == "__main__":
    main()