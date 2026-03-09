import socket


def zad10(hostname: str, host: str = "127.0.0.1", port: int = 2907, timeout: float = 5.0) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            s.sendto(hostname.encode("utf-8"), (host, port))
            response, _ = s.recvfrom(1024)
            return response.decode("utf-8", errors="replace")
    except OSError as exc:
        return f"Blad komunikacji z serwerem {host}:{port} - {exc}"


if __name__ == "__main__":
    hostname = input("Podaj hostname do sprawdzenia: ")
    ip = zad10(hostname)
    print(f"Adres IP dla {hostname}: {ip}")
    