import socket
from datetime import datetime

HOST = "127.0.0.1"
PORT = 9001

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(1)
        print(f"[*] Serwer nasłuchuje na {HOST}:{PORT}")

        while True:
            conn, addr = server_sock.accept()
            with conn:
                print(f"[+] Połączono z: {addr}")

                data = conn.recv(1024)
                if not data:
                    print("[-] Klient rozłączył się bez wysłania danych.")
                    continue

                print(f"[>] Odebrano od klienta: {data.decode(errors='replace')}")

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                response = f"Aktualna data i czas: {now}"
                conn.sendall(response.encode())
                print(f"[<] Wysłano: {response}")

if __name__ == "__main__":
    main()