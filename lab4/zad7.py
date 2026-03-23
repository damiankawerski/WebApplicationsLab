import socket

HOST = "127.0.0.1"
PORT = 9007
MAX_LEN = 20

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(1)
        print(f"[*] Serwer echo TCP (max {MAX_LEN} znaków) nasłuchuje na {HOST}:{PORT}")

        while True:
            conn, addr = server_sock.accept()
            with conn:
                print(f"[+] Połączono z: {addr}")

                while True:
                    data = conn.recv(MAX_LEN)
                    if not data:
                        print("[-] Klient zakończył połączenie.")
                        break

                    message = data.decode(errors='replace')
                    if len(message) > MAX_LEN:
                        message = message[:MAX_LEN]
                        print(f"[!] Wiadomość przycięta do {MAX_LEN} znaków")

                    print(f"[>] Odebrano ({len(message)} znaków): {message}")

                    response = message[:MAX_LEN]
                    conn.sendall(response.encode())
                    print(f"[<] Odesłano ({len(response)} znaków): {response}")

if __name__ == "__main__":
    main()