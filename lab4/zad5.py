import socket

HOST = "127.0.0.1"
PORT = 9005

def resolve_hostname(ip_address: str) -> str:
    ip_address = ip_address.strip()
    try:
        socket.inet_aton(ip_address)
    except socket.error:
        return f"BŁĄD: '{ip_address}' nie jest poprawnym adresem IPv4"

    try:
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return hostname
    except socket.herror:
        return f"BŁĄD: Nie znaleziono hostname dla adresu {ip_address}"
    except socket.gaierror as e:
        return f"BŁĄD: {e}"

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        server_sock.bind((HOST, PORT))
        print(f"[*] Serwer IP->hostname (UDP) nasłuchuje na {HOST}:{PORT}")

        while True:
            data, addr = server_sock.recvfrom(1024)
            ip_str = data.decode(errors='replace').strip()
            print(f"[>] Odebrano od {addr}: {ip_str}")

            response = resolve_hostname(ip_str)
            server_sock.sendto(response.encode(), addr)
            print(f"[<] Wysłano do {addr}: {response}")

if __name__ == "__main__":
    main()