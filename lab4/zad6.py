import socket

HOST = "127.0.0.1"
PORT = 9006

def resolve_ip(hostname: str) -> str:
    hostname = hostname.strip()
    if not hostname:
        return "BŁĄD: Pusta nazwa hostname"

    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror:
        return f"BŁĄD: Nie znaleziono adresu IP dla hostname '{hostname}'"

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        server_sock.bind((HOST, PORT))
        print(f"[*] Serwer hostname->IP (UDP) nasłuchuje na {HOST}:{PORT}")

        while True:
            data, addr = server_sock.recvfrom(1024)
            hostname_str = data.decode(errors='replace').strip()
            print(f"[>] Odebrano od {addr}: {hostname_str}")

            response = resolve_ip(hostname_str)
            server_sock.sendto(response.encode(), addr)
            print(f"[<] Wysłano do {addr}: {response}")

if __name__ == "__main__":
    main()