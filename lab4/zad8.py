import socket

HOST = "127.0.0.1"
PORT = 9008
REQUIRED_LEN = 20

def recv_exact(conn: socket.socket, length: int) -> bytes:
    buffer = b""
    while len(buffer) < length:
        chunk = conn.recv(length - len(buffer))
        if not chunk:
            break  # Klient rozłączył się
        buffer += chunk
    return buffer

def send_exact(conn: socket.socket, data: bytes) -> int:
    total_sent = 0
    while total_sent < len(data):
        sent = conn.send(data[total_sent:])
        if sent == 0:
            raise RuntimeError("Gniazdo zostało zamknięte")
        total_sent += sent
    return total_sent

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(1)
        print(f"[*] Serwer echo TCP (dokładnie {REQUIRED_LEN} znaków) nasłuchuje na {HOST}:{PORT}")
        print(f"[*] Wiadomości krótsze niż {REQUIRED_LEN} znaków są uzupełniane spacjami")

        while True:
            conn, addr = server_sock.accept()
            with conn:
                print(f"[+] Połączono z: {addr}")

                while True:
                    data = recv_exact(conn, REQUIRED_LEN)
                    if not data:
                        print("[-] Klient zakończył połączenie.")
                        break

                    received_len = len(data)
                    message = data.decode(errors='replace')
                    print(f"[>] Odebrano ({received_len}/{REQUIRED_LEN} bajtów): '{message}'")

                    if received_len < REQUIRED_LEN:
                        print(f"[!] Odebrano mniej niż {REQUIRED_LEN} bajtów!")

                    response = message.ljust(REQUIRED_LEN)[:REQUIRED_LEN]
                    response_bytes = response.encode()

                    sent_len = send_exact(conn, response_bytes)
                    print(f"[<] Wysłano ({sent_len}/{REQUIRED_LEN} bajtów): '{response}'")

                    if sent_len != REQUIRED_LEN:
                        print(f"[!] Wysłano mniej niż {REQUIRED_LEN} bajtów!")

if __name__ == "__main__":
    main()